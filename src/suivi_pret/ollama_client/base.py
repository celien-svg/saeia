from __future__ import annotations

from typing import Any

import httpx


class OllamaError(RuntimeError):
    """Erreur générique pour les opérations Ollama."""


class OllamaConnectionError(OllamaError):
    """Erreur de connexion au serveur Ollama."""


class OllamaResponseError(OllamaError):
    """Erreur lorsque la réponse HTTP/JSON d'Ollama est invalide."""


class BaseModelEndpoint:
    """Transport HTTP asynchrone commun aux clients VLM, LLM et embedding."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout_s: float = 60.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """Configure le serveur, le délai maximal et le transport des tests."""
        self.host = base_url.rstrip("/")
        self._async_client = httpx.AsyncClient(
            base_url=self.host,
            timeout=timeout_s,
            transport=transport,
        )

    async def __aenter__(self) -> "BaseModelEndpoint":
        """Permet d'utiliser le client avec 'async with'"""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Permet de fermer proprement le client avec 'async with'"""
        await self.aclose()

    async def aclose(self) -> None:
        """Ferme les connexions HTTP conservées par le client."""
        await self._async_client.aclose()

    async def _post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Envoie une requête JSON asynchrone à l'API Ollama."""
        try:
            response = await self._async_client.post(endpoint, json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise OllamaResponseError(
                f"Erreur HTTP {exc.response.status_code} renvoyée par Ollama."
            ) from exc
        except httpx.RequestError as exc:
            raise OllamaConnectionError(
                f"Impossible de joindre Ollama à {self.host}."
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise OllamaResponseError("Ollama a renvoyé une réponse non JSON.") from exc

        if not isinstance(data, dict):
            raise OllamaResponseError(f"JSON inattendu depuis Ollama: {data!r}")
        return data
