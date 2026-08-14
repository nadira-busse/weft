from __future__ import annotations

import io
import json
import unittest
from urllib.error import HTTPError, URLError

from installer.clients import AmbiguousMutationError, MakeClient


class Response:
    def __init__(self, payload: dict, status: int = 200) -> None:
        self.payload = payload
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class ClientTests(unittest.TestCase):
    def test_get_rate_limit_retry_is_bounded_and_honors_header(self) -> None:
        calls = []
        sleeps = []

        def opener(request, **kwargs):
            calls.append(request)
            if len(calls) < 3:
                raise HTTPError(request.full_url, 429, "rate limited", {"Retry-After": "2"}, io.BytesIO(b'{"message":"slow down"}'))
            return Response({"ok": True})

        client = MakeClient("https://eu2.make.com/api/v2", "token", opener=opener, sleeper=sleeps.append)
        self.assertEqual(client.request("GET", "/scenarios"), {"ok": True})
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [2.0, 2.0])
        self.assertEqual(client.mutation_count, 0)

    def test_ambiguous_mutation_is_never_replayed(self) -> None:
        calls = []

        def opener(request, **kwargs):
            calls.append(request)
            raise URLError("connection reset")

        client = MakeClient("https://eu2.make.com/api/v2", "token", opener=opener, sleeper=lambda _: None)
        with self.assertRaises(AmbiguousMutationError):
            client.request("POST", "/scenarios", write=True, body={"teamId": 1})
        self.assertEqual(len(calls), 1)
        self.assertEqual(client.mutation_count, 1)

    def test_server_error_on_mutation_requires_readback_reconciliation(self) -> None:
        calls = []

        def opener(request, **kwargs):
            calls.append(request)
            raise HTTPError(request.full_url, 503, "unavailable", {}, io.BytesIO(b'{"message":"unknown outcome"}'))

        client = MakeClient("https://eu2.make.com/api/v2", "token", opener=opener, sleeper=lambda _: None)
        with self.assertRaises(AmbiguousMutationError):
            client.request("POST", "/data-structures", write=True, body={"teamId": 1})
        self.assertEqual(len(calls), 1)
        self.assertEqual(client.mutation_count, 1)


if __name__ == "__main__":
    unittest.main()
