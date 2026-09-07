from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List
class BaseModelEndpoint(ABC):
"""Interface minimale : generate() ou chat()"""
@abstractmethod
async def generate(self, prompt: str, **kwargs) -> str: ...
@abstractmethod
async def chat(self, messages: List[Dict[str, str]]) -> Dict[str, Any]: ...
# src/shared/ollama_client/llm.py
import asyncio
from ..base import BaseModelEndpoint
from pydantic import BaseModel, Field
from typing import Any, Dict
class OllamaLLM(BaseModelEndpoint):
model: str
host: str = "http://localhost:11434"
async def generate(self, prompt: str, max_tokens: int = 256,
temperature: float = 0.7, **kw) -> str:
payload = {
"model": self.model,
"prompt": prompt,
"max_tokens": max_tokens,
"temperature": temperature,
"stream": False,
}
payload.update(kw)
resp = await self._post("/api/generate", payload)
return resp["response"]
# _post() is a private helper that does aiohttp request…