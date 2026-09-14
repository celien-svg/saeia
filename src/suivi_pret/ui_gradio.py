"""Interface Gradio de gestion des matériels."""

import html
import logging

import gradio as gr

from .service import SuiviPretService
from .storage import (
    DuplicateMaterielError,
    EntityNotFoundError,
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


def creer_callback_confirmation(id_materiel):
    """Crée le callback du bouton Supprimer : première pression = demande
    de confirmation, seconde pression = suppression effective."""

    def callback(version):
        return gr.update(value="Confirmer la suppression ?", variant="stop"), version

    return callback


def creer_callback_suppression(id_materiel):
    """Crée le callback de suppression effective (bouton de confirmation)."""

    def callback(version):
        return supprimer_materiel(id_materiel, version)

    return callback


def vider_formulaire():
    """Valeurs initiales du formulaire."""
    return ("","",None,"","OK","","","",None,None,    
    )


def ouvrir_liste():
    return (gr.update(visible=False),gr.update(visible=True),)


def retour_accueil():
    return (gr.update(visible=True),gr.update(visible=False),)


def ouvrir_formulaire():
    return (gr.update(visible=False),gr.update(visible=True),*vider_formulaire(),)


def annuler_formulaire():
    return (gr.update(visible=True),gr.update(visible=False),*vider_formulaire(),)


def enregistrer_materiel(
    nom,
    modele,
    annee,
    etiquette_ulco,
    etat,
    localisation,
    descriptif,
    remarque,
    entite_id,
    image_path,
    version,
):
    """Confie au service métier l'enregistrement d'un ordinateur."""
    try:
        service.creer_materiel(
            nom,
            modele,
            annee,
            etiquette_ulco,
            etat,
            localisation,
            descriptif,
            remarque,
            entite_id,
            image_path,
        )
    except (ValueError, DuplicateMaterielError, EntityNotFoundError) as exc:
        raise gr.Error(str(exc)) from exc
    except StorageError as exc:
        logger.exception("Erreur de stockage lors de l'enregistrement d'un matériel")
        raise gr.Error(str(exc)) from exc

    gr.Info("Ordinateur enregistré.")

    return (
        gr.update(visible=True),
        gr.update(visible=False),
        version + 1,
        *vider_formulaire(),
    )


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
"""


with gr.Blocks(title="Gestion des ordinateurs") as demo:

    actualisation = gr.State(0)

    with gr.Column(elem_id="page"):

        # Page d'accueil
        with gr.Column(elem_id="accueil") as page_accueil:
            bouton_voir_liste = gr.Button(
                "Voir la liste des ordinateurs",
                variant="primary",
            )

        # Page de liste
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
                            # Contenu utilisateur échappé pour empêcher toute
                            # injection HTML/JS via gr.Markdown (XSS stocké).
                            gr.Markdown(echapper(materiel["nom"]), scale=3)
                            gr.Markdown(echapper(materiel["etat"]), scale=2)
                            gr.Markdown(echapper(materiel["localisation"]), scale=2)

                            bouton_supprimer = gr.Button(
                                "Supprimer",
                                scale=1,
                                key=f"supprimer-{identifiant}",
                            )

                            # 1er clic : demande de confirmation.
                            # 2e clic : suppression effective.
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

        # Page du formulaire
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

            entite_id = gr.Number(
                label="Identifiant de l'entité *",
                precision=0,
            )

            image = gr.Image(
                label="Photo de l'ordinateur",
                type="filepath",
            )

            with gr.Row():
                bouton_enregistrer = gr.Button(
                    "Enregistrer",
                    variant="primary",
                )
                bouton_annuler = gr.Button("Annuler")


    # Accueil -> liste
    bouton_voir_liste.click(
        fn=ouvrir_liste,
        inputs=None,
        outputs=[page_accueil, page_liste],
    )

    # Liste -> accueil
    bouton_retour_accueil.click(
        fn=retour_accueil,
        inputs=None,
        outputs=[page_accueil, page_liste],
    )

    # Liste -> formulaire
    bouton_ajouter.click(
        fn=ouvrir_formulaire,
        inputs=None,
        outputs=[
            page_liste,
            page_formulaire,
            nom,
            modele,
            annee,
            etiquette_ulco,
            etat,
            localisation,
            descriptif,
            remarque,
            entite_id,
            image,
        ],
    )

    # Formulaire -> liste sans sauvegarde
    bouton_annuler.click(
        fn=annuler_formulaire,
        inputs=None,
        outputs=[
            page_liste,
            page_formulaire,
            nom,
            modele,
            annee,
            etiquette_ulco,
            etat,
            localisation,
            descriptif,
            remarque,
            entite_id,
            image,
        ],
    )

    # Formulaire -> service métier -> liste
    bouton_enregistrer.click(
        fn=enregistrer_materiel,
        inputs=[
            nom,
            modele,
            annee,
            etiquette_ulco,
            etat,
            localisation,
            descriptif,
            remarque,
            entite_id,
            image,
            actualisation,
        ],
        outputs=[
            page_liste,
            page_formulaire,
            actualisation,
            nom,
            modele,
            annee,
            etiquette_ulco,
            etat,
            localisation,
            descriptif,
            remarque,
            entite_id,
            image,
        ],
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
