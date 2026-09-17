import json
import os
import tempfile
from pathlib import Path
from vlm import OllamaWrapper, OllamaResponseError, OllamaConnectionError

# --- Nom du modèle VLM ---------------------------------------------------
# le modele demander n'existe pas sur le serveur j'utilise donc le modele par defaut qwen3-vl:8b-instruct
MODEL = os.environ.get("VLM_MODEL", "qwen3-vl:8b-instruct")

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

# Une entrée par catégorie. Pour l'instant : écran + clavier.
# Ajoute simplement une ligne par nouvelle catégorie (jusqu'à 6).
CATEGORIES = [
    {
        "zone": "écran",
        "before": "test3.jpg",
        "after": "test4.jpg",
    },
    {
        "zone": "clavier",
        "before": "clavierbefore.jpg",
        "after": "clavierafter.jpg",
    }
    #{
    #    "zone": "dos",
    #    "before": "dosbefore.jpg",
    #    "after": "dosafter.jpg",
    #},
    #{
    #    "zone": "dessous",
    #    "before": "dessousbefore.jpg",
    #    "after": "dessousafter.jpg",
    #},
    #{
    #    "zone": "conecteurgauche",
    #    "before": "conecteurgauchebefore.jpg",
    #    "after": "conecteurgaucheafter.jpg",
    #},
    #{
    #    "zone": "conecteurdroit",
    #    "before": "conecteurdroitbefore.jpg",
    #    "after": "conecteurdroitafter.jpg",
    #}
    ]

from PIL import Image

def resize_exact(image_path, output_path, size=(1024, 1024)):
    image_path = Path(image_path)
    output_path = Path(output_path)
    temporary_path = None
    try:
        with Image.open(image_path) as img:
            img_resized = img.resize(size, Image.LANCZOS)  # Étire ou compresse
            with tempfile.NamedTemporaryFile(
                dir=output_path.parent,
                prefix=f".{output_path.stem}.",
                suffix=output_path.suffix,
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)

            img_resized.save(temporary_path, format=img.format)
            os.replace(temporary_path, output_path)
        print(f"Image forcée à {size[0]}x{size[1]} pixels : {output_path}")
    except Exception as e:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        print(f"Erreur : {e}")


def analyser_categorie(client: OllamaWrapper, image_dir: Path, categorie: dict) -> dict:
    """Appelle le VLM pour une seule catégorie (2 images) et retourne le JSON parsé."""
    resize_exact(image_dir/categorie["before"], image_dir/categorie["before"])
    resize_exact(image_dir/categorie["after"], image_dir/categorie["after"])
    zone = categorie["zone"]
    before_path = image_dir / categorie["before"]
    after_path = image_dir / categorie["after"]

    print(f"→ Analyse de la zone : {zone}...")

    try:
        result = client.compare_images(
            model=MODEL,
            prompt=PROMPT_TEMPLATE.format(zone=zone),
            image_before=before_path,
            image_after=after_path,
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
    return parsed

def conversion_texte(categorie: dict) -> str:
    """
    convertie le json en texte pour l'interface.
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

def main():
    client = OllamaWrapper(timeout_s=180.0)

    print("Serveur dispo :", client.is_server_running())
    if not client.is_server_running():
        print("Ollama injoignable, on s'arrête.")
        return

    image_dir = Path(__file__).parent / "testimage"

    rapport_global = []
    for categorie in CATEGORIES:
        resultat = analyser_categorie(client, image_dir, categorie)
        rapport_global.append(resultat)



    print("\n=== Rapport global ===")
    print(json.dumps(rapport_global, ensure_ascii=False, indent=2))

    print("\n=== Rapport texte ===")
    for resultat in rapport_global:
        print(conversion_texte(resultat))

if __name__ == "__main__":
    main()