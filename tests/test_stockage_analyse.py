"""Tests du stockage et du regroupement des photos pour l'analyse."""

from io import BytesIO
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock, MagicMock, Mock, patch
import asyncio
import json
import threading

import psycopg
from PIL import Image

from src.suivi_pret.ollama_client.ia_comparaison import (
    analyser_categorie,
    analyser_materiel,
    construire_categories,
    main,
)
from src.suivi_pret.storage.base import Storage, StorageError
from src.suivi_pret.storage.postgres import PostgresStorage


class CategoriesTest(TestCase):
    def test_associe_uniquement_les_zones_communes_dans_le_bon_ordre(self):
        avant = {"id_photo": 1, "type_photo": "ecran", "est_avant": True}
        apres = {"id_photo": 2, "type_photo": "ecran", "est_avant": False}
        photos = [
            apres,
            {"type_photo": "clavier", "est_avant": True},
            avant,
            {"type_photo": "dessous", "est_avant": False},
        ]
        self.assertEqual(
            construire_categories(photos),
            [{"zone": "ecran", "before": avant, "after": apres}],
        )
        self.assertEqual(construire_categories([]), [])


class PostgresAnalyseTest(TestCase):
    def setUp(self):
        self.storage = PostgresStorage(config=Mock())
        self.connexion = MagicMock()
        self.storage._connexion = Mock(return_value=self.connexion)
        self.curseur = self.connexion.__enter__.return_value.cursor.return_value.__enter__.return_value

    def test_lecture_avec_et_sans_filtre(self):
        photos = [{"id_photo": 1, "type_photo": "ecran", "est_avant": True}]
        self.curseur.fetchall.return_value = photos
        for filtre in (None, "ecran"):
            with self.subTest(filtre=filtre):
                self.assertEqual(
                    self.storage.recuperer_photos_comparaison(12, filtre), photos,
                )
                requete, params = self.curseur.execute.call_args.args
                self.assertEqual(params, (12,) if filtre is None else (12, filtre))
                self.assertEqual("AND type_photo = %s" in requete, filtre is not None)

    def test_enregistrement_png_sur_la_photo_indiquee(self):
        self.storage.enregistrer_image_annotee(42, b"image annotee")
        requete, params = self.curseur.execute.call_args.args
        self.assertIn("image_type = 'image/png'", requete)
        self.assertIn("WHERE id_photo = %s", requete)
        self.assertEqual(params, (b"image annotee", 42))

    def test_convertit_les_erreurs_postgres(self):
        self.storage._connexion.side_effect = psycopg.OperationalError("indisponible")
        with self.assertRaises(StorageError):
            self.storage.recuperer_photos_comparaison(12)
        with self.assertRaises(StorageError):
            self.storage.enregistrer_image_annotee(42, b"image")


class AnalyseStockageTest(IsolatedAsyncioTestCase):
    def verifier_boucle_disponible(self):
        """Construit une vérification appelée depuis une opération de stockage."""
        boucle = asyncio.get_running_loop()
        thread_boucle = threading.get_ident()

        def verifier(*args):
            self.assertNotEqual(threading.get_ident(), thread_boucle)
            # Le stockage attend cette tâche : elle doit pouvoir avancer sur la boucle.
            tache = asyncio.run_coroutine_threadsafe(asyncio.sleep(0), boucle)
            tache.result(timeout=2)

        return verifier

    async def test_annote_et_sauvegarde_uniquement_la_photo_apres(self):
        image = BytesIO()
        Image.new("RGB", (10, 10), "white").save(image, format="PNG")
        categorie = {
            "zone": "ecran",
            "before": {"id_photo": 1, "image_data": image.getvalue()},
            "after": {"id_photo": 2, "image_data": image.getvalue()},
        }
        storage = Mock(spec=Storage)
        storage.enregistrer_image_annotee.side_effect = self.verifier_boucle_disponible()
        client = Mock()
        client.compare_images = AsyncMock(return_value=SimpleNamespace(
            response=json.dumps({"zones": [{
                "element": "ecran", "anomalie": "rayure",
                "gravite": "legere", "bbox": [1, 1, 5, 5],
            }]}),
        ))
        resultat = await analyser_categorie(
            client, categorie, "modele-test", storage=storage,
        )
        storage.enregistrer_image_annotee.assert_called_once()
        id_photo, contenu = storage.enregistrer_image_annotee.call_args.args
        self.assertEqual(id_photo, 2)
        with Image.open(BytesIO(contenu)) as annotee:
            self.assertEqual(annotee.format, "PNG")
            self.assertEqual(annotee.getpixel((1, 1)), (255, 0, 0))
        self.assertEqual(resultat["image_annotee"], "enregistrée en base")

    async def test_aucune_paire_ne_declenche_pas_ollama(self):
        storage = Mock(spec=Storage)
        verifier = self.verifier_boucle_disponible()

        def lire(*args):
            verifier(*args)
            return []

        storage.recuperer_photos_comparaison.side_effect = lire
        module = "src.suivi_pret.ollama_client.ia_comparaison"
        with patch(f"{module}.get_settings"), patch(f"{module}.OllamaVLM") as vlm:
            resultat = await analyser_materiel(12, "ecran", storage=storage)
        storage.recuperer_photos_comparaison.assert_called_once_with(12, "ecran")
        vlm.assert_not_called()
        self.assertIn("Aucune photo commune", resultat)

    async def test_erreur_de_lecture_remonte_depuis_le_thread(self):
        storage = Mock(spec=Storage)
        erreur = StorageError("Base indisponible")
        storage.recuperer_photos_comparaison.side_effect = erreur
        with patch("src.suivi_pret.ollama_client.ia_comparaison.get_settings"):
            with self.assertRaises(StorageError) as resultat:
                await analyser_materiel(12, storage=storage)
        self.assertIs(resultat.exception, erreur)

    async def test_commande_cli_lit_hors_de_la_boucle(self):
        storage = Mock(spec=Storage)
        verifier = self.verifier_boucle_disponible()

        def lire(*args):
            verifier(*args)
            return []

        storage.recuperer_photos_comparaison.side_effect = lire
        with (
            patch("sys.argv", ["analyse", "--materiel-id", "12", "--type-photo", "ecran"]),
            patch("src.suivi_pret.ollama_client.ia_comparaison.get_settings"),
            patch("src.suivi_pret.storage.postgres.PostgresStorage", return_value=storage),
        ):
            await main()
        storage.recuperer_photos_comparaison.assert_called_once_with(12, "ecran")
