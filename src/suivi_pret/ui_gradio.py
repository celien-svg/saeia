"""Interface Gradio de gestion des matériels."""

import html
import logging
from io import BytesIO

import gradio as gr
from PIL import Image

from .ollama_client.ia_comparaison import analyser_materiel
from .service import SuiviPretService
from .storage import (
    DuplicateMaterielError,
    EntityNotFoundError,
    MaterielNotFoundError,
    PostgresStorage,
    StorageError,
)

ETATS = ["OK", "Réservé", "En réparation", "Endommagé", "Disparu"]

logger = logging.getLogger("gestion_materiels")
logging.basicConfig(level=logging.INFO)

service = SuiviPretService(PostgresStorage())


def echapper(texte):
    """Échappe le HTML pour éviter toute injection dans gr.Markdown."""
    if texte is None:
        return ""
    return html.escape(str(texte))


def recuperer_materiels():
    """Récupère tous les ordinateurs enregistrés."""
    try:
        return service.lister_materiels()
    except StorageError as exc:
        logger.exception("Erreur lors du chargement des matériels")
        raise gr.Error(str(exc)) from exc


def supprimer_materiel(id_materiel, version):
    """Supprime un ordinateur puis actualise la liste."""
    try:
        service.supprimer_materiel(id_materiel)
    except StorageError as exc:
        logger.exception("Erreur lors de la suppression du matériel %s", id_materiel)
        raise gr.Error(str(exc)) from exc

    gr.Info("Ordinateur supprimé.")
    return version + 1


def vider_formulaire():
    """Valeurs initiales du formulaire d'ajout."""
    return (
        "", "", None, "", "OK", "", "", "", None,
        None, None, None, None, None, None,
    )


def vider_formulaire_modif():
    """Valeurs initiales du formulaire de modification (id inclus)."""
    return (
        None, "", "", None, "", "OK", "", "", "", None,
        None, None, None, None, None, None,
    )


def vider_photos_analyse():
    """Réinitialise uniquement les six nouvelles photos d'analyse."""
    return (None, None, None, None, None, None)


TYPES_PHOTOS = (
    "dessus",
    "dessous",
    "ecran",
    "clavier",
    "connectique_gauche",
    "connectique_droite",
)


def ajouter_photos_analyse(id_materiel, *photos):
    """Valide et enregistre les six nouvelles photos pour comparaison."""
    if id_materiel is None:
        raise gr.Error("Aucun ordinateur n'est sélectionné.")

    photos_dict = {
        type_photo: chemin
        for type_photo, chemin in zip(TYPES_PHOTOS, photos)
        if chemin is not None
    }

    if not photos_dict:
        gr.Warning("Aucune photo fournie.")
        return "Aucune photo fournie."

    try:
        service.ajouter_photos_analyse(id_materiel, photos_dict)
    except StorageError as exc:
        logger.exception("Erreur lors de l'enregistrement des photos d'analyse")
        raise gr.Error(str(exc)) from exc

    gr.Info("Photos d'analyse enregistrées.")
    return " Photos enregistrées. La comparaison par l'IA est disponible ci-dessous."


async def lancer_analyse(id_materiel, *photos):
    """Compare les photos avant/après et prépare le rapport sans le sauvegarder."""
    if id_materiel is None:
        raise gr.Error("Aucun ordinateur n'est sélectionné.")

    try:
        return await analyser_materiel(id_materiel, storage=service.storage)
    except Exception as exc:
        logger.exception("Erreur lors de l'analyse du matériel %s", id_materiel)
        raise gr.Error(str(exc)) from exc


def sauvegarder_rapport(id_materiel, rapport):
    """Sauvegarde explicitement le rapport affiché dans la page d'analyse."""
    if id_materiel is None:
        raise gr.Error("Aucun ordinateur n'est sélectionné.")
    if not rapport or rapport.startswith("Aucun rapport enregistré"):
        gr.Warning("Lancez une analyse avant de sauvegarder un rapport.")
        return "Aucun rapport à sauvegarder."

    try:
        service.enregistrer_rapport(id_materiel, rapport)
    except StorageError as exc:
        logger.exception("Erreur lors de l'enregistrement du rapport %s", id_materiel)
        raise gr.Error(str(exc)) from exc

    gr.Info("Rapport sauvegardé.")
    return "Rapport sauvegardé dans l'historique."


def afficher_liste_rapports(id_materiel):
    """Affiche l'historique des rapports du matériel sélectionné."""
    if id_materiel is None:
        raise gr.Error("Aucun ordinateur n'est sélectionné.")

    try:
        rapports = service.lister_rapports(id_materiel)
    except StorageError as exc:
        logger.exception("Erreur lors du chargement des rapports %s", id_materiel)
        raise gr.Error(str(exc)) from exc

    if not rapports:
        return "Aucun rapport sauvegardé pour cet ordinateur."

    lignes = ["### Rapports sauvegardés"]
    for rapport in rapports:
        date = rapport["cree_le"].strftime("%d/%m/%Y %H:%M")
        lignes.append(f"#### Rapport du {date}\n\n{rapport['contenu']}")
    return "\n\n---\n\n".join(lignes)


def photos_en_data_uri(photos):
    """Convertit les photos enregistrées en images affichables par Gradio."""
    photos_par_type = {}
    for photo in photos or []:
        image_data = photo.get("image_data")
        type_photo = photo.get("type_photo")
        if image_data is None or type_photo is None:
            continue
        try:
            with Image.open(BytesIO(image_data)) as image:
                image.thumbnail((1024, 1024))
                photos_par_type[type_photo] = image.copy()
        except Exception:
            logger.warning("Photo invalide ignorée pour le type '%s'", type_photo)
            continue
    return tuple(photos_par_type.get(type_photo) for type_photo in TYPES_PHOTOS)


def ouvrir_analyse(id_materiel, nom):
    """Ouvre la collecte de photos liée à l'ordinateur sélectionné."""
    try:
        anciennes_photos = photos_en_data_uri(
            service.recuperer_photos(id_materiel)
        )
        photos_analyse = photos_en_data_uri(
            service.recuperer_photos_analyse(id_materiel)
        )
    except StorageError as exc:
        logger.exception("Erreur lors du chargement des photos du matériel %s", id_materiel)
        raise gr.Error(str(exc)) from exc

    return (
        gr.update(visible=False),
        gr.update(visible=True),
        id_materiel,
        gr.update(value=f"## Analyse de l'ordinateur : {echapper(nom)}"),
        *anciennes_photos,
        *photos_analyse,
        "",
        "",
        "",
    )


def retour_liste_depuis_analyse():
    """Retourne à la liste sans enregistrer les photos d'analyse."""
    return (
        gr.update(visible=True),
        gr.update(visible=False),
        None,
        gr.update(value="## Analyse de l'ordinateur"),
        *([None] * 6),
        *vider_photos_analyse(),
        "",
        "",  # zone réponse IA
        "",  # liste des rapports
    )


def ouvrir_liste():
    return (gr.update(visible=False), gr.update(visible=True))


def retour_accueil():
    return (gr.update(visible=True), gr.update(visible=False))


def ouvrir_formulaire():
    return (gr.update(visible=False), gr.update(visible=True), *vider_formulaire())


def annuler_formulaire():
    return (gr.update(visible=True), gr.update(visible=False), *vider_formulaire())


def enregistrer_materiel(
    nom, modele, annee, etiquette_ulco, etat,
    localisation, descriptif, remarque, entite_id,
    image, image2, image3, image4, image5, image6,
    version,
):
    """Confie au service métier l'enregistrement d'un ordinateur."""
    erreurs = []
    if not (nom or "").strip():
        erreurs.append("le nom")
    if not (localisation or "").strip():
        erreurs.append("la localisation")
    if entite_id is None:
        erreurs.append("l'identifiant de l'entité")
    if erreurs:
        gr.Warning(f"Champs obligatoires manquants : {', '.join(erreurs)}.")
        return (gr.update(), gr.update(), version, *([gr.update()] * 15))

    try:
        service.creer_materiel(
            nom, modele, annee, etiquette_ulco, etat,
            localisation, descriptif, remarque, entite_id,
            {
                "dessus": image, "dessous": image2, "ecran": image3,
                "clavier": image4, "connectique_gauche": image5,
                "connectique_droite": image6,
            },
        )
    except (ValueError, DuplicateMaterielError, EntityNotFoundError) as exc:
        gr.Warning(str(exc))
        return (gr.update(), gr.update(), version, *([gr.update()] * 15))
    except StorageError as exc:
        logger.exception("Erreur de stockage lors de l'enregistrement d'un matériel")
        raise gr.Error(str(exc)) from exc

    gr.Info("Ordinateur enregistré.")
    return (gr.update(visible=True), gr.update(visible=False), version + 1, *vider_formulaire())


# ── Modification ──────────────────────────────────────────────────────────────

def ouvrir_modification(id_materiel, nom_materiel):
    """Charge les données du matériel et ouvre le formulaire de modification."""
    try:
        materiel = service.recuperer_materiel(id_materiel)
    except StorageError as exc:
        raise gr.Error(str(exc)) from exc

    if materiel is None:
        raise gr.Error("Matériel introuvable.")

    return (
        gr.update(visible=False),
        gr.update(visible=True),
        materiel["id_materiel"],
        materiel["nom"] or "",
        materiel["modele"] or "",
        materiel["annee"],
        materiel["etiquette_ulco"] or "",
        materiel["etat"] or "OK",
        materiel["localisation"] or "",
        materiel["descriptif"] or "",
        materiel["remarque"] or "",
        materiel["entite_id"],
        None, None, None, None, None, None,
    )


def annuler_modification():
    return (gr.update(visible=True), gr.update(visible=False), *vider_formulaire_modif())


def enregistrer_modification(
    id_materiel,
    nom, modele, annee, etiquette_ulco, etat,
    localisation, descriptif, remarque, entite_id,
    image, image2, image3, image4, image5, image6,
    version,
):
    """Enregistre les modifications d'un ordinateur."""
    erreurs = []
    if not (nom or "").strip():
        erreurs.append("le nom")
    if not (localisation or "").strip():
        erreurs.append("la localisation")
    if entite_id is None:
        erreurs.append("l'identifiant de l'entité")
    if erreurs:
        gr.Warning(f"Champs obligatoires manquants : {', '.join(erreurs)}.")
        return (gr.update(), gr.update(), version, *([gr.update()] * 16))

    try:
        service.modifier_materiel(
            id_materiel,
            nom, modele, annee, etiquette_ulco, etat,
            localisation, descriptif, remarque, entite_id,
            {
                "dessus": image, "dessous": image2, "ecran": image3,
                "clavier": image4, "connectique_gauche": image5,
                "connectique_droite": image6,
            },
        )
    except (ValueError, MaterielNotFoundError, EntityNotFoundError, DuplicateMaterielError) as exc:
        gr.Warning(str(exc))
        return (gr.update(), gr.update(), version, *([gr.update()] * 16))
    except StorageError as exc:
        logger.exception("Erreur de stockage lors de la modification d'un matériel")
        raise gr.Error(str(exc)) from exc

    gr.Info("Ordinateur modifié.")
    return (gr.update(visible=True), gr.update(visible=False), version + 1, *vider_formulaire_modif())


CSS = """
.gradio-container {
    max-width: none !important;
    background: #202020 !important;
    padding: 12px !important;
}

#page {
    min-height: 92vh;
    background: white;
    padding: 35px 12%;
}

#accueil {
    min-height: 75vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

#accueil button {
    max-width: 320px;
}

#page .image-container img {
    max-height: 420px !important;
    object-fit: contain !important;
}

#titre {
    text-align: center;
    margin-bottom: 25px;
}

#liste {
    margin-top: 24px;
    padding: 13px 25px;
    background: #dddddd;
}

.ligne-ordinateur {
    align-items: center;
    min-height: 38px;
    margin-bottom: 8px;
    padding: 0 18px;
    background: #646464;
}

.entetes-ordinateurs {
    align-items: center;
    min-height: 32px;
    padding: 0 18px;
    background: #dddddd;
}

.entetes-ordinateurs p {
    color: #202020 !important;
    font-size: 13px;
    font-weight: 700;
    margin: 0 !important;
}

#liste .colonne-nom { flex: 3 1 0 !important; }
#liste .colonne-etat,
#liste .colonne-localisation { flex: 2 1 0 !important; }
#liste .colonne-action { flex: 1 1 0 !important; min-width: 0; }

#liste .entetes-ordinateurs > *,
#liste .ligne-ordinateur > * {
    min-width: 0;
}

.ligne-ordinateur p {
    color: white !important;
    font-size: 13px;
    margin: 0 !important;
}

.ligne-ordinateur button {
    min-height: 30px !important;
    border: 0 !important;
    background: transparent !important;
    color: white !important;
    box-shadow: none !important;
}

.ligne-ordinateur button:hover {
    background: #4d4d4d !important;
}

#zone-ia {
    margin-top: 16px;
    border: 1px solid #d0d0d0;
    border-radius: 8px;
    padding: 12px;
    background: #f8f8f8;
}
"""


with gr.Blocks(title="Gestion des ordinateurs") as demo:

    actualisation = gr.State(0)
    analyse_id_materiel = gr.State(None)

    with gr.Column(elem_id="page"):

        # ── Page d'accueil ───────────────────────────────────────────────────
        with gr.Column(elem_id="accueil") as page_accueil:
            bouton_voir_liste = gr.Button(
                "Voir la liste des ordinateurs",
                variant="primary",
            )

        # ── Page d'analyse ───────────────────────────────────────────────────
        with gr.Column(visible=False) as page_analyse:
            titre_analyse = gr.Markdown("## Analyse de l'ordinateur")

            with gr.Row():
                gr.Markdown("### Photo avant")
                gr.Markdown("### Nouvelle photo")

            anciennes_images = []
            nouvelles_images = []
            labels_photos = (
                "dessus", "dessous", "ecran",
                "clavier", "connectique gauche", "connectique droite",
            )
            for label_photo in labels_photos:
                with gr.Row():
                    anciennes_images.append(
                        gr.Image(label=f"Photo avant - {label_photo}", interactive=False)
                    )
                    nouvelles_images.append(
                        gr.Image(label=f"Photo après - {label_photo}", type="filepath")
                    )

            statut_photos_analyse = gr.Markdown()

            with gr.Row():
                bouton_ajouter_photos = gr.Button("Ajouter les photos", variant="primary")
                bouton_lancer_analyse = gr.Button("Lancer l'analyse", variant="primary")
                bouton_sauvegarder_rapport = gr.Button("Sauvegarder le rapport")
                bouton_liste_rapports = gr.Button("Liste des rapports")
                bouton_retour_analyse = gr.Button("Retour à la liste")

            # Zone de réponse de l'IA
            with gr.Column(elem_id="zone-ia"):
                gr.Markdown("### 🤖 Réponse de l'IA")
                reponse_ia = gr.Textbox(
                    label="Analyse comparative",
                    interactive=False,
                    lines=6,
                    placeholder="La réponse de l'IA apparaîtra ici après l'analyse des photos avant/après...",
                )
                liste_rapports = gr.Markdown()

        # ── Page de liste ────────────────────────────────────────────────────
        with gr.Column(visible=False) as page_liste:
            gr.Markdown("## Liste des ordinateurs", elem_id="titre")

            with gr.Row():
                bouton_ajouter = gr.Button("Ajouter un ordinateur")
                gr.Column(scale=3)
                bouton_retour_accueil = gr.Button("Accueil")

            @gr.render(inputs=actualisation)
            def afficher_liste(_):
                materiels = recuperer_materiels()

                with gr.Column(elem_id="liste"):
                    with gr.Row(elem_classes="entetes-ordinateurs"):
                        gr.Markdown("Nom", elem_classes="colonne-nom")
                        gr.Markdown("État", elem_classes="colonne-etat")
                        gr.Markdown("Localisation", elem_classes="colonne-localisation")
                        gr.Markdown("Modifier", elem_classes="colonne-action")
                        gr.Markdown("Supprimer", elem_classes="colonne-action")
                        gr.Markdown("Analyse", elem_classes="colonne-action")

                    if not materiels:
                        gr.Markdown(
                            """
                            <div style="text-align: center; padding: 25px;">
                                Aucun ordinateur enregistré pour le moment.
                            </div>
                            """
                        )

                    for materiel in materiels:
                        identifiant = materiel["id_materiel"]

                        with gr.Row(
                            elem_classes="ligne-ordinateur",
                            key=f"materiel-{identifiant}",
                        ):
                            gr.Markdown(echapper(materiel["nom"]), elem_classes="colonne-nom")
                            gr.Markdown(echapper(materiel["etat"]), elem_classes="colonne-etat")
                            gr.Markdown(echapper(materiel["localisation"]), elem_classes="colonne-localisation")

                            bouton_modifier = gr.Button(
                                "Modifier", elem_classes="colonne-action",
                                key=f"modifier-{identifiant}",
                            )
                            bouton_supprimer = gr.Button(
                                "Supprimer", elem_classes="colonne-action",
                                key=f"supprimer-{identifiant}",
                            )
                            bouton_analyse = gr.Button(
                                "Analyse", elem_classes="colonne-action",
                                key=f"analyse-{identifiant}",
                            )

                            bouton_analyse.click(
                                fn=lambda id_m=identifiant, n=materiel["nom"]: ouvrir_analyse(id_m, n),
                                inputs=None,
                                outputs=[
                                    page_liste, page_analyse,
                                    analyse_id_materiel, titre_analyse,
                                    *anciennes_images, *nouvelles_images,
                                    statut_photos_analyse, reponse_ia,
                                    liste_rapports,
                                ],
                            )

                            bouton_modifier.click(
                                fn=lambda id_m=identifiant, n=materiel["nom"]: ouvrir_modification(id_m, n),
                                inputs=None,
                                outputs=[
                                    page_liste, page_modification,
                                    modif_id, modif_nom, modif_modele, modif_annee,
                                    modif_etiquette_ulco, modif_etat, modif_localisation,
                                    modif_descriptif, modif_remarque, modif_entite_id,
                                    modif_image, modif_image2, modif_image3,
                                    modif_image4, modif_image5, modif_image6,
                                ],
                            )

                            etat_confirmation = gr.State(False)

                            def gerer_clic(confirme, version, id_materiel=identifiant):
                                if not confirme:
                                    return (
                                        gr.update(value="Confirmer ?", variant="stop"),
                                        True,
                                        version,
                                    )
                                nouvelle_version = supprimer_materiel(id_materiel, version)
                                return (
                                    gr.update(value="Supprimer", variant="secondary"),
                                    False,
                                    nouvelle_version,
                                )

                            bouton_supprimer.click(
                                fn=gerer_clic,
                                inputs=[etat_confirmation, actualisation],
                                outputs=[bouton_supprimer, etat_confirmation, actualisation],
                            )

        # ── Page formulaire ajout ────────────────────────────────────────────
        with gr.Column(visible=False) as page_formulaire:
            gr.Markdown("## Ajouter un ordinateur")

            nom = gr.Textbox(label="Nom *")
            modele = gr.Textbox(label="Modèle")
            annee = gr.Number(label="Année", precision=0)
            etiquette_ulco = gr.Textbox(label="Étiquette ULCO")
            etat = gr.Dropdown(ETATS, value="OK", label="État *")
            localisation = gr.Textbox(label="Localisation *")
            descriptif = gr.Textbox(label="Descriptif", lines=3)
            remarque = gr.Textbox(label="Remarque", lines=3)
            entite_id = gr.Number(label="Identifiant de l'entité *", precision=0)

            image = gr.Image(label="Photo dessus de l'ordinateur", type="filepath")
            image2 = gr.Image(label="Photo dessous de l'ordinateur", type="filepath")
            image3 = gr.Image(label="Photo ecran de l'ordinateur", type="filepath")
            image4 = gr.Image(label="Photo clavier de l'ordinateur", type="filepath")
            image5 = gr.Image(label="Photo connectique gauche de l'ordinateur", type="filepath")
            image6 = gr.Image(label="Photo connectique droite de l'ordinateur", type="filepath")

            with gr.Row():
                bouton_enregistrer = gr.Button("Enregistrer", variant="primary")
                bouton_annuler = gr.Button("Annuler")

        # ── Page formulaire modification ─────────────────────────────────────
        with gr.Column(visible=False) as page_modification:
            gr.Markdown("## Modifier un ordinateur")

            modif_id = gr.State(None)
            modif_nom = gr.Textbox(label="Nom *")
            modif_modele = gr.Textbox(label="Modèle")
            modif_annee = gr.Number(label="Année", precision=0)
            modif_etiquette_ulco = gr.Textbox(label="Étiquette ULCO")
            modif_etat = gr.Dropdown(ETATS, value="OK", label="État *")
            modif_localisation = gr.Textbox(label="Localisation *")
            modif_descriptif = gr.Textbox(label="Descriptif", lines=3)
            modif_remarque = gr.Textbox(label="Remarque", lines=3)
            modif_entite_id = gr.Number(label="Identifiant de l'entité *", precision=0)

            gr.Markdown("*Laissez les photos vides pour conserver les photos actuelles.*")
            modif_image = gr.Image(label="Photo dessus de l'ordinateur", type="filepath")
            modif_image2 = gr.Image(label="Photo dessous de l'ordinateur", type="filepath")
            modif_image3 = gr.Image(label="Photo ecran de l'ordinateur", type="filepath")
            modif_image4 = gr.Image(label="Photo clavier de l'ordinateur", type="filepath")
            modif_image5 = gr.Image(label="Photo connectique gauche de l'ordinateur", type="filepath")
            modif_image6 = gr.Image(label="Photo connectique droite de l'ordinateur", type="filepath")

            with gr.Row():
                bouton_enregistrer_modif = gr.Button("Enregistrer les modifications", variant="primary")
                bouton_annuler_modif = gr.Button("Annuler")


    # ── Câblage des événements ───────────────────────────────────────────────

    _champs_formulaire = [
        nom, modele, annee, etiquette_ulco, etat,
        localisation, descriptif, remarque, entite_id,
        image, image2, image3, image4, image5, image6,
    ]

    _champs_modif = [
        modif_id, modif_nom, modif_modele, modif_annee, modif_etiquette_ulco,
        modif_etat, modif_localisation, modif_descriptif, modif_remarque,
        modif_entite_id, modif_image, modif_image2, modif_image3,
        modif_image4, modif_image5, modif_image6,
    ]

    # Accueil -> liste
    bouton_voir_liste.click(fn=ouvrir_liste, inputs=None, outputs=[page_accueil, page_liste])

    # Liste -> accueil
    bouton_retour_accueil.click(fn=retour_accueil, inputs=None, outputs=[page_accueil, page_liste])

    # Analyse -> liste sans sauvegarde
    bouton_retour_analyse.click(
        fn=retour_liste_depuis_analyse,
        inputs=None,
        outputs=[
            page_liste, page_analyse,
            analyse_id_materiel, titre_analyse,
            *anciennes_images, *nouvelles_images,
            statut_photos_analyse, reponse_ia, liste_rapports,
        ],
    )

    bouton_ajouter_photos.click(
        fn=ajouter_photos_analyse,
        inputs=[analyse_id_materiel, *nouvelles_images],
        outputs=[statut_photos_analyse],
    )

    bouton_lancer_analyse.click(
        fn=lancer_analyse,
        inputs=[analyse_id_materiel, *anciennes_images, *nouvelles_images],
        outputs=[reponse_ia],
    )

    bouton_sauvegarder_rapport.click(
        fn=sauvegarder_rapport,
        inputs=[analyse_id_materiel, reponse_ia],
        outputs=[statut_photos_analyse],
    )

    bouton_liste_rapports.click(
        fn=afficher_liste_rapports,
        inputs=[analyse_id_materiel],
        outputs=[liste_rapports],
    )

    # Liste -> formulaire ajout
    bouton_ajouter.click(
        fn=ouvrir_formulaire,
        inputs=None,
        outputs=[page_liste, page_formulaire, *_champs_formulaire],
    )

    # Formulaire ajout -> liste sans sauvegarde
    bouton_annuler.click(
        fn=annuler_formulaire,
        inputs=None,
        outputs=[page_liste, page_formulaire, *_champs_formulaire],
    )

    # Formulaire ajout -> service -> liste
    bouton_enregistrer.click(
        fn=enregistrer_materiel,
        inputs=[*_champs_formulaire, actualisation],
        outputs=[page_liste, page_formulaire, actualisation, *_champs_formulaire],
    )

    # Formulaire modification -> liste sans sauvegarde
    bouton_annuler_modif.click(
        fn=annuler_modification,
        inputs=None,
        outputs=[page_liste, page_modification, *_champs_modif],
    )

    # Formulaire modification -> service -> liste
    bouton_enregistrer_modif.click(
        fn=enregistrer_modification,
        inputs=[*_champs_modif, actualisation],
        outputs=[page_liste, page_modification, actualisation, *_champs_modif],
    )


demo.launch(
    # Dans Docker, l'application doit écouter sur toutes les interfaces pour
    # que le port publié par Compose soit accessible depuis la machine hôte.
    server_name="0.0.0.0",
    server_port=7860,
    theme=gr.Theme.from_hub("harsh8001/skymist"),
    css=CSS,
    show_error=False,
)
