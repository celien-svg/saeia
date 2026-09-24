"""Tests du client HTTP asynchrone utilisé pour les comparaisons Ollama."""

import base64
import json
from unittest import IsolatedAsyncioTestCase

import httpx

from src.suivi_pret.ollama_client.vlm import (
    OllamaResponseError,
    OllamaWrapper,
)


class OllamaWrapperAsyncTest(IsolatedAsyncioTestCase):
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
            return httpx.Response(200, json={"response": '{"zones": []}'})

        async with OllamaWrapper(
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

    async def test_transforme_une_erreur_http_en_erreur_ollama(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, json={"error": "indisponible"})

        async with OllamaWrapper(
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
