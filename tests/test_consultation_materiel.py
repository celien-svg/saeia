"""Tests de la consultation Gradio, sans connexion à la base."""

from io import BytesIO
from unittest import TestCase
from unittest.mock import call, create_autospec, patch

from PIL import Image

from src.suivi_pret.service import SuiviPretService
from src.suivi_pret.storage import StorageError

with patch("src.suivi_pret.storage.PostgresStorage"):
    from src.suivi_pret import ui_gradio as ui


class ConsultationMaterielTest(TestCase):
    def setUp(self):
        self.service = create_autospec(SuiviPretService, instance=True)
        remplacement = patch.object(ui, "service", self.service)
        remplacement.start()
        self.addCleanup(remplacement.stop)
        self.materiel = {
            "id_materiel": 42, "nom": "Portable", "modele": "Modèle A",
            "annee": 2025, "etiquette_ulco": "ULCO-42", "etat": "OK",
            "localisation": "S126", "descriptif": "Écran 15 pouces",
            "remarque": "Rien à signaler", "entite_id": 1, "entite_nom": "ULCO",
        }
        self.service.recuperer_materiel.return_value = self.materiel
        self.service.recuperer_photos.return_value = []
        self.service.lister_entites.return_value = [
            {"id": 4, "nom": "IUT"}, {"id": 1, "nom": "ULCO"},
        ]

    def test_charge_tous_les_champs_sans_ecriture(self):
        resultat = ui.ouvrir_consultation(42)

        self.assertFalse(resultat[0]["visible"])
        self.assertTrue(resultat[1]["visible"])
        self.assertEqual(resultat[2:12], (
            "42", "Portable", "Modèle A", "2025", "ULCO-42", "OK",
            "S126", "Écran 15 pouces", "Rien à signaler", "ULCO",
        ))
        self.assertEqual(resultat[12:], (None,) * 6)
        self.assertEqual(self.service.mock_calls, [
            call.recuperer_materiel(42), call.recuperer_photos(42),
        ])

    def test_affiche_les_photos_dans_le_bon_angle(self):
        donnees = BytesIO()
        Image.new("RGB", (20, 10), "red").save(donnees, format="PNG")
        self.service.recuperer_photos.return_value = [
            {"type_photo": "clavier", "image_data": donnees.getvalue()},
        ]

        photos = ui.ouvrir_consultation(42)[12:]

        self.assertEqual(photos[:3], (None,) * 3)
        self.assertEqual(photos[3].size, (20, 10))
        self.assertEqual(photos[4:], (None,) * 2)

    def test_champs_optionnels_absents_et_valeur_zero(self):
        self.materiel.update(modele=None, annee=0, remarque=None)

        resultat = ui.ouvrir_consultation(42)

        self.assertEqual(resultat[4:6], ("", "0"))
        self.assertEqual(resultat[10:12], ("", "ULCO"))

    def test_creation_charge_les_noms_et_transmet_les_identifiants(self):
        resultat = ui.ouvrir_formulaire()
        self.assertEqual(resultat[10]["choices"], [("IUT", 4), ("ULCO", 1)])
        self.assertIsNone(resultat[10]["value"])
        self.assertEqual(len(resultat), 17)
        self.service.lister_entites.assert_called_once_with()
        self.assertTrue(ui.entite_id.interactive)

    def test_modification_preselectionne_entite_actuelle(self):
        resultat = ui.ouvrir_modification(42, "Portable")
        self.assertEqual(resultat[11]["choices"], [("IUT", 4), ("ULCO", 1)])
        self.assertEqual(resultat[11]["value"], 1)
        self.assertEqual(len(resultat), 18)
        self.assertTrue(ui.modif_entite_id.interactive)

    def test_liste_entites_vide_est_signalee(self):
        self.service.lister_entites.return_value = []
        with patch.object(ui.gr, "Warning") as avertissement:
            self.assertEqual(ui.ouvrir_formulaire()[10]["choices"], [])
        avertissement.assert_called_once()

    def test_erreur_chargement_entites_est_signalee(self):
        self.service.lister_entites.side_effect = StorageError("Base indisponible")
        with self.assertLogs(ui.logger, level="ERROR"), self.assertRaisesRegex(
            ui.gr.Error, "Base indisponible",
        ):
            ui.ouvrir_formulaire()

    def test_materiel_supprime_depuis_affichage_liste(self):
        self.service.recuperer_materiel.return_value = None

        with self.assertRaisesRegex(ui.gr.Error, "Matériel introuvable"):
            ui.ouvrir_consultation(42)

        self.service.recuperer_photos.assert_not_called()

    def test_erreurs_stockage_signalees(self):
        for methode in ("recuperer_materiel", "recuperer_photos"):
            with self.subTest(methode=methode):
                fonction = getattr(self.service, methode)
                fonction.side_effect = StorageError("Base indisponible")
                with self.assertLogs(ui.logger, level="ERROR"), self.assertRaisesRegex(
                    ui.gr.Error, "Base indisponible",
                ):
                    ui.ouvrir_consultation(42)
                fonction.side_effect = None

    def test_champs_et_photos_non_interactifs(self):
        self.assertEqual(len(ui.champs_consultation), 10)
        self.assertEqual(len(ui.photos_consultation), 6)
        for composant in (*ui.champs_consultation, *ui.photos_consultation):
            self.assertFalse(composant.interactive)

    def test_retour_vide_la_fiche_sans_acces_au_service(self):
        resultat = ui.retour_liste_depuis_consultation()

        self.assertTrue(resultat[0]["visible"])
        self.assertFalse(resultat[1]["visible"])
        self.assertEqual(resultat[2:12], ("",) * 10)
        self.assertEqual(resultat[12:], (None,) * 6)
        self.assertEqual(
            len(resultat), 2 + len(ui.champs_consultation) + len(ui.photos_consultation),
        )
        self.assertEqual(self.service.mock_calls, [])
