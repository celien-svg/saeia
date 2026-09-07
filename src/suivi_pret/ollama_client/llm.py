"""Adapter LLM réservé aux évolutions futures du sujet."""

from typing import Any

from .base import BaseModelEndpoint


class OllamaLLM(BaseModelEndpoint):
    """Squelette de l'adapter texte."""

    async def analyze_image(self, image: str | bytes, prompt: str) -> str:
        """Réserve l'opération d'analyse pour une future implémentation."""
        _ = (image, prompt)
        raise NotImplementedError
