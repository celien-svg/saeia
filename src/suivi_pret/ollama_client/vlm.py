"""Client asynchrone de comparaison d'images via Ollama."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .base import BaseModelEndpoint, OllamaResponseError

# ------------------------------
# Dataclasses pour structurer les réponses (lisible + typé)
# ------------------------------
@dataclass(frozen=True, slots=True)
class OllamaGenerateResult:
    """Résultat simplifié de /api/generate en mode stream=false."""
    response: str
    model: str | None = None
    done: bool | None = None
    total_duration: int | None = None
    load_duration: int | None = None
    prompt_eval_count: int | None = None
    eval_count: int | None = None


# ------------------------------
# Wrapper principal
# ------------------------------

class OllamaVLM(BaseModelEndpoint):
    """Client HTTP asynchrone pour comparer deux images avec Ollama."""

    async def compare_images(
        self,
        *,
        prompt: str,
        model: str,
        image_before: str | Path | bytes,
        image_after: str | Path | bytes,
        system: str | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> OllamaGenerateResult:
        """Compare deux images avec Ollama sans bloquer la boucle asyncio."""
        # Convertit les images en bytes.
        def to_bytes(image: str | Path | bytes) -> bytes:
            if isinstance(image, (str, Path)):
                return Path(image).read_bytes()
            if isinstance(image, (bytes, bytearray)):
                return bytes(image)
            raise TypeError("image doit être un chemin (str/Path) ou des bytes.")

        images_b64 = [
            base64.b64encode(to_bytes(image_before)).decode("ascii"),
            base64.b64encode(to_bytes(image_after)).decode("ascii"),
        ]

        body: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "images": images_b64,   # [avant, après] dans cet ordre
            "stream": False,
        }
        if system is not None:
            body["system"] = system

        # Ajoute les options avancées si fournies.
        if options is not None:
            body["options"] = dict(options)

        payload = await self._post("/api/generate", body)

        response_text = payload.get("response")
        if not isinstance(response_text, str):
            raise OllamaResponseError(f"Réponse /api/generate (comparaison) inattendue: {payload!r}")

        return OllamaGenerateResult(
            response=response_text,
            model=payload.get("model") if isinstance(payload.get("model"), str) else None,
            done=payload.get("done") if isinstance(payload.get("done"), bool) else None,
            total_duration=payload.get("total_duration") if isinstance(payload.get("total_duration"), int) else None,
            load_duration=payload.get("load_duration") if isinstance(payload.get("load_duration"), int) else None,
            prompt_eval_count=payload.get("prompt_eval_count") if isinstance(payload.get("prompt_eval_count"), int) else None,
            eval_count=payload.get("eval_count") if isinstance(payload.get("eval_count"), int) else None,
        )
