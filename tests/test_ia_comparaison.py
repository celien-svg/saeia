"""Tests de validation stricte des reponses JSON du VLM."""

import json
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock

from src.suivi_pret.ollama_client.ia_comparaison import (
    analyser_categorie,
    valider_reponse_json,
)


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

        resultat = valider_reponse_json(reponse)

        self.assertEqual(resultat["zones"][0]["gravite"], "legere")

    def test_refuse_un_json_syntaxiquement_invalide(self) -> None:
        with self.assertRaisesRegex(ValueError, "syntaxiquement invalide"):
            valider_reponse_json('{"zones": [}')

    def test_refuse_une_racine_qui_n_est_pas_un_objet(self) -> None:
        with self.assertRaises(ValueError):
            valider_reponse_json("[]")

    def test_refuse_une_racine_avec_zones_non_liste(self) -> None:
        with self.assertRaises(ValueError):
            valider_reponse_json('{"zones": {}}')

    def test_refuse_une_zone_incomplete(self) -> None:
        with self.assertRaises(ValueError):
            valider_reponse_json(
                '{"zones": [{"element": "ecran", "anomalie": "rayure"}]}'
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
            valider_reponse_json(json.dumps(reponse))

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
            valider_reponse_json(json.dumps(reponse))

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
            valider_reponse_json(json.dumps(reponse))

    def test_analyser_categorie_retourne_une_erreur_controlee(self) -> None:
        client = Mock()
        client.compare_images.return_value = SimpleNamespace(response="[]")
        categorie = {
            "zone": "ecran",
            "before": {"image_data": b"avant"},
            "after": {"image_data": b"apres", "id_photo": 1},
        }

        resultat = analyser_categorie(client, categorie, model="test-model")

        self.assertEqual(resultat["zone_analysee"], "ecran")
        self.assertEqual(resultat["zones"], [])
        self.assertIn("racine", resultat["error"])


if __name__ == "__main__":
    import unittest

    unittest.main()
