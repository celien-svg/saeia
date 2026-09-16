"""Tests unitaires du service, sans interface ni base de données."""

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Mapping
from unittest import TestCase

from src.suivi_pret.service import SuiviPretService
from src.suivi_pret.storage.base import Storage


class StockageMemoire(Storage):
    """Double minimal enregistrant la dernière commande reçue."""

    def __init__(self) -> None:
        self.donnees: dict[str, Any] | None = None

    def lister_materiels(self) -> list[dict[str, Any]]:
        return []

    def creer_materiel(self, donnees: Mapping[str, Any]) -> None:
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
            image.write_bytes(b"image")

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

    def test_refuse_un_nom_vide(self) -> None:
        with self.assertRaisesRegex(ValueError, "nom"):
            self.service.creer_materiel(
                " ", "", None, "", "OK", "S126", "", "", 1, {}
            )

    def test_prepare_plusieurs_photos_avec_leur_type(self) -> None:
        with TemporaryDirectory() as dossier:
            dessus = Path(dossier) / "dessus.png"
            clavier = Path(dossier) / "clavier.jpg"
            dessus.write_bytes(b"dessus")
            clavier.write_bytes(b"clavier")

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
