"""Vérifie le transport partagé, ses erreurs et la fermeture des connexions."""

from unittest import IsolatedAsyncioTestCase

import httpx

from src.suivi_pret.ollama_client.base import (
    BaseModelEndpoint,
    OllamaConnectionError,
    OllamaResponseError,
)


class BaseModelEndpointTest(IsolatedAsyncioTestCase):
    async def test_refuse_les_reponses_non_json_ou_non_objet(self):
        for contenu in ("pas du JSON", "[]", "null"):
            with self.subTest(contenu=contenu):
                def handler(request):
                    return httpx.Response(200, text=contenu)

                async with BaseModelEndpoint(
                    transport=httpx.MockTransport(handler),
                ) as client:
                    with self.assertRaises(OllamaResponseError):
                        await client._post("/api/generate", {})

    async def test_convertit_un_timeout_en_erreur_de_connexion(self):
        def handler(request):
            raise httpx.ReadTimeout("Délai dépassé", request=request)

        async with BaseModelEndpoint(
            transport=httpx.MockTransport(handler),
        ) as client:
            with self.assertRaises(OllamaConnectionError):
                await client._post("/api/generate", {})

    async def test_reutilise_le_transport_et_le_ferme_meme_en_cas_erreur(self):
        class Transport(httpx.AsyncBaseTransport):
            appels = 0
            ferme = False

            async def handle_async_request(self, request):
                self.appels += 1
                return httpx.Response(200, json={"response": "ok"})

            async def aclose(self):
                self.ferme = True

        transport = Transport()
        with self.assertRaisesRegex(RuntimeError, "analyse interrompue"):
            async with BaseModelEndpoint(transport=transport) as client:
                for _ in range(2):
                    resultat = await client._post("/api/generate", {})
                    self.assertEqual(resultat, {"response": "ok"})
                self.assertFalse(transport.ferme)
                raise RuntimeError("analyse interrompue")

        self.assertEqual(transport.appels, 2)
        self.assertTrue(transport.ferme)
