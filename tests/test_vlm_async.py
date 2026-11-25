"""Tests du client HTTP asynchrone utilisé pour les comparaisons Ollama."""

import base64
import json
from unittest import IsolatedAsyncioTestCase

import httpx

from src.suivi_pret.ollama_client.base import OllamaResponseError
from src.suivi_pret.ollama_client.vlm import OllamaVLM


class OllamaVLMAsyncTest(IsolatedAsyncioTestCase):
    async def test_envoie_les_images_dans_l_ordre_avant_apres(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/api/generate")
            payload = json.loads(request.content)
            self.assertEqual(payload["model"], "modele-test")
            self.assertEqual(payload["prompt"], "Compare les images")
            self.assertEqual(
                payload["images"],
                [
                    base64.b64encode(b"avant").decode("ascii"),
                    base64.b64encode(b"apres").decode("ascii"),
                ],
            )
            self.assertFalse(payload["stream"])
            return httpx.Response(200, json={
                "response": '{"zones": []}',
                "eval_duration": 2_000_000_000,
                "total_duration": 3_000_000_000,
                "prompt_eval_count": 120,
                "eval_count": 15,
            })

        async with OllamaVLM(
            "http://ollama.test",
            transport=httpx.MockTransport(handler),
        ) as client:
            resultat = await client.compare_images(
                model="modele-test",
                prompt="Compare les images",
                image_before=b"avant",
                image_after=b"apres",
            )

        self.assertEqual(resultat.response, '{"zones": []}')
        self.assertEqual(resultat.eval_duration, 2_000_000_000)
        self.assertEqual(resultat.total_duration, 3_000_000_000)
        self.assertEqual(resultat.prompt_eval_count, 120)
        self.assertEqual(resultat.eval_count, 15)

    async def test_transforme_une_erreur_http_en_erreur_ollama(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, json={"error": "indisponible"})

        async with OllamaVLM(
            "http://ollama.test",
            transport=httpx.MockTransport(handler),
        ) as client:
            with self.assertRaisesRegex(OllamaResponseError, "500"):
                await client.compare_images(
                    model="modele-test",
                    prompt="Compare",
                    image_before=b"avant",
                    image_after=b"apres",
                )


if __name__ == "__main__":
    import unittest

    unittest.main()
