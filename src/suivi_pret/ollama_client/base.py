from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx


class BaseModelEndpoint(ABC):
    """Interface minimale pour les clients de modèles Ollama."""

    host: str

    @abstractmethod
    async def analyze_image(self, image: str | bytes, prompt: str) -> str:
        """Analyse une image avec une consigne et retourne du texte."""
        raise NotImplementedError

    async def _post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Envoie une requête JSON asynchrone à l'API Ollama."""
        async with httpx.AsyncClient(base_url=self.host, timeout=60.0) as client:
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()