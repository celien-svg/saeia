import json
from pathlib import Path
from vlm import OllamaWrapper

def main():
    client = OllamaWrapper()

    print("Serveur dispo :", client.is_server_running())
    if not client.is_server_running():
        print("Ollama injoignable, on s'arrête.")
        return

    prompt = (
        "Voici deux photos du même ordinateur portable. "
        "La PREMIÈRE image montre l'état AVANT le prêt (référence). "
        "La SECONDE image montre l'état APRÈS restitution. "
        "Compare-les et identifie toute dégradation physique nouvelle. "
        "Réponds STRICTEMENT en JSON : "
        '{"zones": [{"element": "string", "anomalie": "string", "gravite": "string", "bbox": [0, 0, 0, 0]}]}'
    )

    image_dir = Path(__file__).parent / "testimage"

    result = client.compare_images(
        model="qwen3-vl:8b-instruct",
        prompt=prompt,
        image_before=image_dir / "test1.jpg",
        image_after=image_dir / "test2.jpg",
    )

    try:
        response_json = json.loads(result.response)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Ollama n'a pas renvoyé un JSON valide : {result.response!r}") from exc

    print("Réponse JSON :")
    print(json.dumps(response_json, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()