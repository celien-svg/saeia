"""Adapters Ollama prévus par l'architecture du projet."""

from .base import BaseModelEndpoint
from .embedding import OllamaEmbedding
from .llm import OllamaLLM
from .vlm import OllamaWrapper

__all__ = [
    "BaseModelEndpoint",
    "OllamaEmbedding",
    "OllamaLLM",
    "OllamaWrapper",
]
