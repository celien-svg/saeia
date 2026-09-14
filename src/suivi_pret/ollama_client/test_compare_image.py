import json
import os
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
        "before": "ecranbefore.jpg",
        "after": "ecranafter.jpg",
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
def analyser_categorie(client: OllamaWrapper, image_dir: Path, categorie: dict) -> dict:
    """Appelle le VLM pour une seule catégorie (2 images) et retourne le JSON parsé."""
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


if __name__ == "__main__":
    main()