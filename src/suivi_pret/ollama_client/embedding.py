"""Adapter embedding réservé aux évolutions futures du sujet."""

from .base import BaseModelEndpoint


class OllamaEmbedding(BaseModelEndpoint):
    """Squelette de l'adapter de vectorisation."""

    async def analyze_image(self, image: str | bytes, prompt: str) -> str:
        """Réserve l'opération d'analyse pour une future implémentation."""
        _ = (image, prompt)
        raise NotImplementedError
