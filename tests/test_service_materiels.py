"""Tests unitaires du service, sans interface ni base de données."""

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Mapping
from unittest import TestCase

from PIL import Image

from src.suivi_pret.service import SuiviPretService
from src.suivi_pret.storage.base import Storage


class StockageMemoire(Storage):
    """Double minimal enregistrant la dernière commande reçue."""

    def __init__(self) -> None:
        self.donnees: dict[str, Any] | None = None
        self.materiel_id: int | None = None

    def lister_materiels(self) -> list[dict[str, Any]]:
        return []

    def creer_materiel(self, donnees: Mapping[str, Any]) -> None:
        self.donnees = dict(donnees)

    def modifier_materiel(self, materiel_id: int, donnees: Mapping[str, Any]) -> None:
        self.materiel_id = materiel_id
        self.donnees = dict(donnees)

    def supprimer_materiel(self, materiel_id: int) -> None:
        pass


class SuiviPretServiceTest(TestCase):
    def setUp(self) -> None:
        self.stockage = StockageMemoire()
        self.service = SuiviPretService(self.stockage)

    def test_normalise_le_formulaire_avant_stockage(self) -> None:
        with TemporaryDirectory() as dossier:
            image = Path(dossier) / "ordinateur.png"
            Image.new("RGB", (2000, 1000), "red").save(image)

            # les espaces avant et après les champs servent 
            # à tester le nettoyage des champs (espaces en trop, tabulation, etc.)
            self.service.creer_materiel(
                "  Portable  ",
                "  Modèle A ",
                2025.0,
                "  ULCO-42 ",
                "OK",
                "  S126  ",
                "",
                "  Rien à signaler ",
                1.0,
                {"dessus": str(image)},
            )

        assert self.stockage.donnees is not None
        self.assertEqual(self.stockage.donnees["nom"], "Portable")
        self.assertEqual(self.stockage.donnees["annee"], 2025)
        self.assertEqual(self.stockage.donnees["descriptif"], None)
        self.assertEqual(
            self.stockage.donnees["photos"][0]["image_type"],
            "image/png",
        )
        with Image.open(BytesIO(self.stockage.donnees["photos"][0]["image_data"])) as photo:
            self.assertEqual(photo.size, (1024, 512))

    def test_refuse_un_nom_vide(self) -> None:
        with self.assertRaisesRegex(ValueError, "nom"):
            self.service.creer_materiel(
                " ", "", None, "", "OK", "S126", "", "", 1, {}
            )

    def test_prepare_plusieurs_photos_avec_leur_type(self) -> None:
        # permet de faire un dossier temporaire pour créer des fausses images pour le test
        with TemporaryDirectory() as dossier:
            dessus = Path(dossier) / "dessus.png"
            clavier = Path(dossier) / "clavier.jpg"
            Image.new("RGB", (100, 200), "red").save(dessus)
            Image.new("RGB", (200, 100), "blue").save(clavier)

            self.service.creer_materiel(
                "Portable",
                "",
                None,
                "",
                "OK",
                "S126",
                "",
                "",
                1,
                {"dessus": str(dessus), "clavier": str(clavier)},
            )

        assert self.stockage.donnees is not None
        self.assertEqual(
            [photo["type_photo"] for photo in self.stockage.donnees["photos"]],
            ["dessus", "clavier"],
        )
        self.assertEqual(
            [photo["image_type"] for photo in self.stockage.donnees["photos"]],
            ["image/png", "image/jpeg"],
        )

    def test_normalise_la_modification_et_remplace_uniquement_les_photos_fournies(
        self,
    ) -> None:
        with TemporaryDirectory() as dossier:
            dessus = Path(dossier) / "nouveau-dessus.png"
            Image.new("RGB", (1200, 600), "green").save(dessus)

            # les espaces avant et après les champs servent 
            # à tester le nettoyage des champs (espaces en trop, tabulation, etc.)
            self.service.modifier_materiel(
                42,
                "  Portable modifié  ",
                "  Modèle B  ",
                2026.0,
                "  ULCO-43  ",
                "En réparation",
                "  S127  ",
                "  Écran remplacé  ",
                "",
                2.0,
                {"dessus": str(dessus), "clavier": None},
            )

        assert self.stockage.donnees is not None
        self.assertEqual(self.stockage.materiel_id, 42)
        self.assertEqual(self.stockage.donnees["nom"], "Portable modifié")
        self.assertEqual(self.stockage.donnees["modele"], "Modèle B")
        self.assertEqual(self.stockage.donnees["annee"], 2026)
        self.assertEqual(self.stockage.donnees["etiquette_ulco"], "ULCO-43")
        self.assertEqual(self.stockage.donnees["localisation"], "S127")
        self.assertEqual(self.stockage.donnees["descriptif"], "Écran remplacé")
        self.assertIsNone(self.stockage.donnees["remarque"])
        self.assertEqual(self.stockage.donnees["entite_id"], 2)
        self.assertEqual(len(self.stockage.donnees["photos"]), 1)
        self.assertEqual(
            self.stockage.donnees["photos"][0]["type_photo"],
            "dessus",
        )

        with Image.open(
            BytesIO(self.stockage.donnees["photos"][0]["image_data"])
        ) as photo:
            self.assertEqual(photo.size, (1024, 512))

    def test_modification_sans_nouvelle_photo_conserve_les_photos_existantes(
        self,
    ) -> None:
        self.service.modifier_materiel(
            7,
            "Portable",
            "",
            None,
            "",
            "OK",
            "S126",
            "",
            "",
            1,
            {
                "dessus": None,
                "dessous": None,
                "ecran": None,
                "clavier": None,
                "connectique_gauche": None,
                "connectique_droite": None,
            },
        )

        assert self.stockage.donnees is not None
        self.assertEqual(self.stockage.donnees["photos"], [])

    def test_refuse_la_modification_si_un_champ_obligatoire_est_vide(self) -> None:
        with self.assertRaisesRegex(ValueError, "localisation"):
            self.service.modifier_materiel(
                7,
                "Portable",
                "",
                None,
                "",
                "OK",
                " ",
                "",
                "",
                1,
                {},
            )

        self.assertIsNone(self.stockage.donnees)
