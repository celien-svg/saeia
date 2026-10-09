"""Tests de validation stricte des reponses JSON du VLM."""

import json
from io import BytesIO
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock, Mock
from PIL import Image

from src.suivi_pret.ollama_client.ia_comparaison import (
    analyser_categorie,
    valider_reponse_json,
)


def image_png(largeur: int = 600, hauteur: int = 600) -> bytes:
    image = BytesIO()
    Image.new("RGB", (largeur, hauteur), "white").save(image, format="PNG")
    return image.getvalue()


class ValidationJsonTest(TestCase):
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
    async def test_analyser_categorie_retourne_une_erreur_controlee(self) -> None:
        client = Mock()
        client.compare_images = AsyncMock(return_value=SimpleNamespace(response="[]"))
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
        })))
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
