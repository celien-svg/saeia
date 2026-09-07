import base64
from dataclasses import dataclass
from pathlib import Path

from ..config import settings
from .base import BaseModelEndpoint


@dataclass
class OllamaVLM(BaseModelEndpoint):
    """Adapter du modèle de vision Ollama configuré dans `.env`."""

    model: str = settings.OLLAMA_VLM_MODEL
    host: str = settings.OLLAMA_HOST

    async def analyze_image(self, image: str | bytes, prompt: str) -> str:
        """Encode l'image, l'envoie au VLM et retourne sa réponse textuelle."""
        image_data = Path(image).read_bytes() if isinstance(image, str) else image
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [base64.b64encode(image_data).decode("ascii")],
            "stream": False,
        }

        response = await self._post("/api/generate", payload)

        if not isinstance(response.get("response"), str):
            raise ValueError("Réponse Ollama invalide : texte absent.")

        return response["response"]