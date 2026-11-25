"""Tests de validation stricte des reponses JSON du VLM."""

import json
from io import BytesIO
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock, Mock, patch
from PIL import Image

from src.suivi_pret.ollama_client.ia_comparaison import (
    GRAVITES_AUTORISEES,
    PROMPT_TEMPLATE,
    analyser_categorie,
    analyser_materiel,
    valider_reponse_json,
)


def image_png(largeur: int = 600, hauteur: int = 600) -> bytes:
    image = BytesIO()
    Image.new("RGB", (largeur, hauteur), "white").save(image, format="PNG")
    return image.getvalue()


class ValidationJsonTest(TestCase):
    def test_prompt_formate_conserve_json_et_gravites_valides(self) -> None:
        prompt = PROMPT_TEMPLATE.format(zone="ecran", largeur=600, hauteur=400)

        self.assertIn('exactement : {"zones": []}', prompt)
        self.assertIn("600x400 pixels", prompt)
        self.assertIn("du même ecran", prompt)
        exemple = prompt.split("Format attendu :\n", 1)[1].strip()
        for coordonnee, valeur in (
            ("x_min", "10"), ("y_min", "20"),
            ("x_max", "100"), ("y_max", "200"),
        ):
            exemple = exemple.replace(coordonnee, valeur)
        gravites = json.loads(exemple)["zones"][0]["gravite"].split("|")
        self.assertEqual(set(gravites), GRAVITES_AUTORISEES - {"aucune"})
        for gravite in gravites:
            valider_reponse_json(
                exemple.replace("|".join(gravites), gravite),
                largeur_image=600, hauteur_image=400,
            )

    def test_accepte_une_reponse_valide(self) -> None:
        reponse = json.dumps({
            "zones": [{
                "element": "charniere",
                "anomalie": "rayure",
                "gravite": "legere",
                "bbox": [1, 2, 30, 40],
            }],
        })

        resultat = valider_reponse_json(
            reponse, largeur_image=1024, hauteur_image=1024,
        )

        self.assertIsInstance(resultat, dict)
        self.assertIsInstance(resultat["zones"], list)
        self.assertIsInstance(resultat["zones"][0], dict)
        self.assertIsInstance(resultat["zones"][0]["bbox"], list)
        self.assertTrue(all(isinstance(coord, (int, float)) for coord in resultat["zones"][0]["bbox"]))
        self.assertEqual(resultat["zones"][0]["gravite"], "legere")

    def test_refuse_un_json_syntaxiquement_invalide(self) -> None:
        with self.assertRaisesRegex(ValueError, "syntaxiquement invalide"):
            valider_reponse_json(
                '{"zones": [}', largeur_image=1024, hauteur_image=1024,
            )

    def test_refuse_une_racine_qui_n_est_pas_un_objet(self) -> None:
        with self.assertRaises(ValueError):
            valider_reponse_json("[]", largeur_image=1024, hauteur_image=1024)

    def test_refuse_une_racine_avec_zones_non_liste(self) -> None:
        with self.assertRaises(ValueError):
            valider_reponse_json(
                '{"zones": {}}', largeur_image=1024, hauteur_image=1024,
            )

    def test_refuse_une_zone_incomplete(self) -> None:
        with self.assertRaises(ValueError):
            valider_reponse_json(
                '{"zones": [{"element": "ecran", "anomalie": "rayure"}]}',
                largeur_image=1024,
                hauteur_image=1024,
            )

    def test_refuse_une_gravite_inconnue(self) -> None:
        reponse = {
            "zones": [{
                "element": "ecran",
                "anomalie": "casse",
                "gravite": "critique",
                "bbox": [0, 0, 10, 10],
            }],
        }

        with self.assertRaisesRegex(ValueError, "gravité inconnue"):
            valider_reponse_json(
                json.dumps(reponse), largeur_image=1024, hauteur_image=1024,
            )

    def test_refuse_une_bbox_qui_n_a_pas_quatre_coordonnees(self) -> None:
        reponse = {
            "zones": [{
                "element": "ecran",
                "anomalie": "tache",
                "gravite": "marquee",
                "bbox": [0, 0, 10],
            }],
        }

        with self.assertRaises(ValueError):
            valider_reponse_json(
                json.dumps(reponse), largeur_image=1024, hauteur_image=1024,
            )

    def test_refuse_une_bbox_incoherente(self) -> None:
        reponse = {
            "zones": [{
                "element": "ecran",
                "anomalie": "tache",
                "gravite": "marquee",
                "bbox": [10, 0, 1, 10],
            }],
        }

        with self.assertRaises(ValueError):
            valider_reponse_json(
                json.dumps(reponse), largeur_image=1024, hauteur_image=1024,
            )

    def test_refuse_une_bbox_au_dela_des_dimensions_reelles(self) -> None:
        reponse = {
            "zones": [{
                "element": "ecran",
                "anomalie": "tache",
                "gravite": "marquee",
                "bbox": [0, 0, 601, 400],
            }],
        }

        with self.assertRaises(ValueError):
            valider_reponse_json(
                json.dumps(reponse), largeur_image=600, hauteur_image=600,
            )

    def test_accepte_une_bbox_dans_une_image_plus_petite_que_1024(self) -> None:
        reponse = {
            "zones": [{
                "element": "ecran",
                "anomalie": "rayure",
                "gravite": "legere",
                "bbox": [10, 20, 590, 580],
            }],
        }

        resultat = valider_reponse_json(
            json.dumps(reponse), largeur_image=600, hauteur_image=600,
        )

        self.assertEqual(resultat["zones"][0]["bbox"], [10, 20, 590, 580])


class AnalyseCategorieTest(IsolatedAsyncioTestCase):
    async def test_analyser_materiel_agrege_les_metriques_des_zones(self) -> None:
        client = Mock()
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=None)
        client.compare_images = AsyncMock(side_effect=[
            SimpleNamespace(
                response='{"zones": []}',
                prompt_eval_count=100,
                eval_count=10,
                eval_duration=2_000_000_000,
                total_duration=3_000_000_000,
            ),
            SimpleNamespace(
                response='{"zones": []}',
                prompt_eval_count=200,
                eval_count=20,
                eval_duration=4_000_000_000,
                total_duration=5_000_000_000,
            ),
        ])
        photos = []
        for type_photo in ("ecran", "clavier"):
            photos.extend([
                {
                    "type_photo": type_photo,
                    "est_avant": True,
                    "image_data": image_png(),
                },
                {
                    "type_photo": type_photo,
                    "est_avant": False,
                    "image_data": image_png(),
                    "id_photo": type_photo,
                },
            ])

        with (
            patch(
                "src.suivi_pret.ollama_client.ia_comparaison.get_settings",
                return_value=SimpleNamespace(
                    OLLAMA_HOST="http://ollama.test",
                    OLLAMA_VLM_MODEL="test-model",
                ),
            ),
            patch(
                "src.suivi_pret.ollama_client.ia_comparaison.OllamaVLM",
                return_value=client,
            ),
        ):
            resultat = await analyser_materiel(1, storage=Mock(), photos_comparaison=photos)

        self.assertEqual(resultat.metriques.jetons_entree, 300)
        self.assertEqual(resultat.metriques.jetons_generes, 30)
        self.assertEqual(resultat.metriques.duree_generation_ns, 6_000_000_000)
        self.assertEqual(resultat.metriques.duree_totale_ns, 8_000_000_000)

    async def test_analyser_categorie_retourne_une_erreur_controlee(self) -> None:
        client = Mock()
        client.compare_images = AsyncMock(return_value=SimpleNamespace(
            response="[]",
            prompt_eval_count=None,
            eval_count=None,
            eval_duration=None,
            total_duration=None,
        ))
        categorie = {
            "zone": "ecran",
            "before": {"image_data": b"avant"},
            "after": {"image_data": image_png(), "id_photo": 1},
        }

        resultat = await analyser_categorie(
            client, categorie, model="test-model", storage=Mock(),
        )

        self.assertEqual(resultat["zone_analysee"], "ecran")
        self.assertEqual(resultat["zones"], [])
        self.assertIn("racine", resultat["error"])

    async def test_bbox_hors_image_retourne_une_erreur_sans_annotation(self) -> None:
        client = Mock()
        client.compare_images = AsyncMock(return_value=SimpleNamespace(response=json.dumps({
            "zones": [{
                "element": "ecran",
                "anomalie": "rayure",
                "gravite": "legere",
                "bbox": [10, 10, 601, 100],
            }],
        }), prompt_eval_count=None, eval_count=None, eval_duration=None, total_duration=None))
        storage = Mock()
        categorie = {
            "zone": "ecran",
            "before": {"image_data": b"avant"},
            "after": {"image_data": image_png(), "id_photo": 1},
        }

        resultat = await analyser_categorie(
            client, categorie, model="test-model", storage=storage,
        )

        self.assertIn("error", resultat)
        self.assertEqual(resultat["zones"], [])
        storage.enregistrer_image_annotee.assert_not_called()
        self.assertIn("600x600", client.compare_images.await_args.kwargs["prompt"])


if __name__ == "__main__":
    import unittest

    unittest.main()
