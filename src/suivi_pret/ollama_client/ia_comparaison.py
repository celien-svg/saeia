import json
import asyncio
import math
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from ..config import get_settings
from ..storage.base import Storage
from .base import OllamaConnectionError, OllamaResponseError
from .vlm import OllamaVLM

PROMPT_TEMPLATE = (Path(__file__).with_name("prompt.md")).read_text(encoding="utf-8")

GRAVITES_AUTORISEES = {"aucune", "legere", "marquee", "importante"}
CHAMPS_ZONE_ATTENDUS = {"element", "anomalie", "gravite", "bbox"}


def _refuser_constante_json(valeur: str) -> None:
    raise ValueError(f"constante JSON non standard : {valeur}")


def valider_reponse_json(reponse: str) -> dict[str, Any]:
    """Parse et valide strictement la réponse JSON produite par le VLM."""
    try:
        donnees = json.loads(reponse, parse_constant=_refuser_constante_json)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError("JSON syntaxiquement invalide") from exc

    if not isinstance(donnees, dict) or set(donnees) != {"zones"}:
        raise ValueError("la racine doit être un objet contenant uniquement 'zones'")
    if not isinstance(donnees["zones"], list):
        raise ValueError("'zones' doit être une liste")

    for index, zone in enumerate(donnees["zones"]):
        if not isinstance(zone, dict) or set(zone) != CHAMPS_ZONE_ATTENDUS:
            raise ValueError(
                f"la zone {index} doit contenir exactement : "
                "element, anomalie, gravite et bbox"
            )
        if not isinstance(zone["element"], str) or not isinstance(zone["anomalie"], str):
            raise ValueError(f"les champs texte de la zone {index} sont invalides")
        if zone["gravite"] not in GRAVITES_AUTORISEES:
            raise ValueError(f"gravité inconnue pour la zone {index}")

        bbox = zone["bbox"]
        if (
            not isinstance(bbox, list)
            or len(bbox) != 4
            or any(isinstance(coord, bool) or not isinstance(coord, (int, float)) for coord in bbox)
            or any(not math.isfinite(coord) or coord < 0 for coord in bbox)
            or bbox[0] > bbox[2]
            or bbox[1] > bbox[3]
        ):
            raise ValueError(
                f"la bbox de la zone {index} doit contenir quatre coordonnées valides"
            )

    return donnees

def construire_categories(
    photos: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Associe les photos avant/après par zone, sans accès au stockage."""
    photos_avant = {p["type_photo"]: p for p in photos if p["est_avant"]}
    photos_apres = {p["type_photo"]: p for p in photos if not p["est_avant"]}

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


async def analyser_categorie(
    client: OllamaVLM,
    categorie: dict[str, Any],
    model: str,
    *,
    storage: Storage,
) -> dict:
    """Appelle le VLM pour une seule catégorie (2 images) et retourne le JSON parsé."""
    zone = categorie["zone"]
    before_photo = categorie["before"]
    after_photo = categorie["after"]

    print(f" Analyse de la zone : {zone}...")

    try:
        result = await client.compare_images(
            model=model,
            prompt=PROMPT_TEMPLATE.format(zone=zone),
            image_before=before_photo["image_data"],
            image_after=after_photo["image_data"],
        )
    except (OllamaConnectionError, OllamaResponseError) as exc:
        print(f"  Erreur pour la zone '{zone}' : {exc}")
        return {"zone": zone, "error": str(exc), "zones": []}

    try:
        parsed = valider_reponse_json(result.response)
    except ValueError as exc:
        print(f"  JSON invalide pour la zone '{zone}' : {result.response!r}")
        return {
            "zone": zone,
            "zone_analysee": zone,
            "error": str(exc),
            "zones": [],
        }

    parsed["zone_analysee"] = zone
    if parsed.get("zones"):
        image_annotee = affichage_defaut(
            after_photo["image_data"],
            parsed["zones"],
        )
        await asyncio.to_thread(
            storage.enregistrer_image_annotee,
            after_photo["id_photo"],
            image_annotee,
        )
        parsed["image_annotee"] = "enregistrée en base"
    return parsed

def conversion_texte(categorie: dict) -> str:
    """
    convertie le json en texte pour l'interface ce qui est le travail demandé.
    """
    zone = categorie.get("zone_analysee", categorie.get("zone", "inconnue"))

    if "error" in categorie:
        return f"Zone {zone} : Erreur - {categorie.get('error', 'inconnue')}"

    zones = categorie.get("zones", [])
    if "raw_response" in categorie and categorie["raw_response"]:
        return f"Zone {zone} : {categorie['raw_response']}"

    if not zones:
        return f"Zone {zone} : Aucune dégradation détectée."

    texte = f"Zone {zone} :\n"
    for z in zones:
        texte += (
            f"- Élément : {z.get('element', 'inconnu')}, "
            f"Anomalie : {z.get('anomalie', 'inconnue')}, "
            f"Gravité : {z.get('gravite', 'inconnue')}, "
            f"BBox : {z.get('bbox', [])}\n"
        )
    return texte.strip()


async def analyser_materiel(
    materiel_id: int,
    type_photo: str | None = None,
    *,
    storage: Storage,
) -> str:
    """Analyse les photos d'un matériel et retourne le rapport affichable."""
    settings = get_settings()
    # Le stockage ouvre et ferme sa connexion dans le thread de travail.
    photos = await asyncio.to_thread(
        storage.recuperer_photos_comparaison, materiel_id, type_photo,
    )
    categories = construire_categories(photos)
    if not categories:
        return "Aucune photo commune trouvée pour ce matériel."

    rapports = []
    async with OllamaVLM(
        base_url=settings.OLLAMA_HOST,
    ) as client:
        for categorie in categories:
            rapports.append(
                await analyser_categorie(
                    client,
                    categorie,
                    model=settings.OLLAMA_VLM_MODEL,
                    storage=storage,
                )
            )
    resultats = [conversion_texte(rapport) for rapport in rapports]
    return "\n\n".join(resultats)

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
