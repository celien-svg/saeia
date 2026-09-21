import json
import argparse
from io import BytesIO
from typing import Any

import psycopg
from PIL import Image, ImageDraw

from ..config import settings
from .vlm import OllamaConnectionError, OllamaResponseError, OllamaWrapper

MODEL = settings.OLLAMA_VLM_MODEL

PROMPT_TEMPLATE = (
    "Voici deux photos du même {zone} d'un ordinateur portable. "
    "La PREMIÈRE image montre l'état AVANT le prêt (référence). "
    "La SECONDE image montre l'état APRÈS restitution. "
    "Compare-les et identifie toute dégradation physique nouvelle "
    "(rayure, déformation, casse, tache...). "
    "Si aucune différence n'est visible, renvoie une liste vide. "
    "Réponds STRICTEMENT en JSON, sans texte autour : "
    '{{"zones": [{{"element": "string", "anomalie": "string", "gravite": "aucune|legere|marquee|importante", "bbox": [0,0,0,0]}}]}}'
)

def recuperer_photos(
    materiel_id: int,
    type_photo: str | None = None,
) -> dict[bool, dict[str, dict[str, Any]]]:
    """Charge les photos d'un matériel, séparées par avant/après."""
    requete = (
        "SELECT id_photo, type_photo, image_data, image_type, est_avant "
        "FROM photos_materiels WHERE id_materiel = %s"
    )
    parametres: tuple[Any, ...] = (materiel_id,)
    if type_photo:
        requete += " AND type_photo = %s"
        parametres += (type_photo,)

    try:
        with psycopg.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            dbname=settings.POSTGRES_DB,
        ) as connexion, connexion.cursor() as curseur:
            curseur.execute(requete, parametres)
            photos: dict[bool, dict[str, dict[str, Any]]] = {
                False: {},
                True: {},
            }
            for id_photo, type_photo, image_data, image_type, est_avant in curseur.fetchall():
                photos[est_avant][type_photo] = {
                    "id_photo": id_photo,
                    "type_photo": type_photo,
                    "image_data": image_data,
                    "image_type": image_type,
                    "est_avant": est_avant,
                }
            return photos
    except psycopg.Error as exc:
        raise RuntimeError("Impossible de récupérer les photos en base.") from exc


def construire_categories(
    materiel_id: int,
    type_photo: str | None = None,
) -> list[dict[str, Any]]:
    """Construit les comparaisons à partir des photos présentes en base."""
    photos = recuperer_photos(materiel_id, type_photo)
    photos_avant = photos[True]
    photos_apres = photos[False]

    categories = []
    for zone in sorted(photos_avant.keys() & photos_apres.keys()):
        categories.append(
            {
                "zone": zone,
                "before": photos_avant[zone],
                "after": photos_apres[zone],
            }
        )
    return categories


def enregistrer_image_annotee(id_photo: int, image_data: bytes) -> None:
    """Remplace en base l'image de restitution par sa version annotée."""
    try:
        with psycopg.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            dbname=settings.POSTGRES_DB,
        ) as connexion, connexion.cursor() as curseur:
            curseur.execute(
                """UPDATE photos_materiels
                SET image_data = %s, image_type = 'image/png'
                WHERE id_photo = %s""",
                (image_data, id_photo),
            )
    except psycopg.Error as exc:
        raise RuntimeError("Impossible d'enregistrer l'image annotée en base.") from exc


def analyser_categorie(client: OllamaWrapper, categorie: dict[str, Any]) -> dict:
    """Appelle le VLM pour une seule catégorie (2 images) et retourne le JSON parsé."""
    zone = categorie["zone"]
    before_photo = categorie["before"]
    after_photo = categorie["after"]

    print(f" Analyse de la zone : {zone}...")

    try:
        result = client.compare_images(
            model=MODEL,
            prompt=PROMPT_TEMPLATE.format(zone=zone),
            image_before=before_photo["image_data"],
            image_after=after_photo["image_data"],
        )
    except (OllamaConnectionError, OllamaResponseError) as exc:
        print(f"  Erreur pour la zone '{zone}' : {exc}")
        return {"zone": zone, "error": str(exc), "zones": []}

    try:
        parsed = json.loads(result.response)
    except json.JSONDecodeError:
        print(f"  JSON invalide pour la zone '{zone}' : {result.response!r}")
        return {"zone": zone, "error": "JSON invalide", "zones": []}

    parsed["zone_analysee"] = zone
    if parsed.get("zones"):
        image_annotee = affichage_defaut(
            after_photo["image_data"],
            parsed["zones"],
        )
        enregistrer_image_annotee(
            after_photo["id_photo"],
            image_annotee,
        )
        parsed["image_annotee"] = "enregistrée en base"
    return parsed

def conversion_texte(categorie: dict) -> str:
    """
    convertie le json en texte pour l'interface ce qui est le travail demandé.
    """
    if "error" in categorie:
        return f"Zone {categorie['zone_analysee']} : Erreur - {categorie['error']}"

    zones = categorie.get("zones", [])
    if not zones:
        return f"Zone {categorie['zone_analysee']} : Aucune dégradation détectée."

    texte = f"Zone {categorie['zone_analysee']} :\n"
    for z in zones:
        texte += (
            f"- Élément : {z['element']}, Anomalie : {z['anomalie']}, "
            f"Gravité : {z['gravite']}, BBox : {z['bbox']}\n"
        )
    return texte.strip()

def affichage_defaut(image_data: bytes, zones: list[dict[str, Any]],)-> bytes:
    """Dessine en rouge les BBoxes des défaut de l'ordinateur et retourne l'image annotée en octets."""
    with Image.open(BytesIO(image_data)) as image:
        image_annotee = image.convert("RGB")

    dessin = ImageDraw.Draw(image_annotee)
    for zone in zones:
        bbox = zone.get("bbox")
        if not isinstance(bbox, list) or len(bbox) != 4:
            continue
        if not all(isinstance(coord, (int, float)) for coord in bbox):
            continue

        dessin.rectangle(tuple(bbox), outline="red", width=4)

    image_sortie = BytesIO()
    image_annotee.save(image_sortie, format="PNG")
    return image_sortie.getvalue()

def main():
    parser = argparse.ArgumentParser(
        description="Compare les photos d'un matériel avec celles d'une référence en base."
    )
    parser.add_argument("--materiel-id", type=int, required=True)
    parser.add_argument(
        "--type-photo",
        help="Ne comparer qu'une zone, par exemple 'ecran' ou 'clavier'.",
    )
    args = parser.parse_args()

    client = OllamaWrapper(base_url=settings.OLLAMA_HOST, timeout_s=180.0)

    print("Serveur dispo :", client.is_server_running())
    if not client.is_server_running():
        print("Ollama injoignable, on s'arrête.")
        return

    rapport_global = []
    categories = construire_categories(
        args.materiel_id,
        args.type_photo,
    )
    if not categories:
        print("Aucune photo commune trouvée pour ces matériels.")
        return

    for categorie in categories:
        resultat = analyser_categorie(client, categorie)
        rapport_global.append(resultat)



    # print("\n Rapport global :")
    # print(json.dumps(rapport_global, ensure_ascii=False, indent=2))

    print("\n Rapport texte :")
    for resultat in rapport_global:
        print(conversion_texte(resultat))

if __name__ == "__main__":
    main()