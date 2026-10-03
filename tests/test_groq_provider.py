from __future__ import annotations

import sys
from pathlib import Path

import httpx
import pytest
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import brain.groq as groq_module
from brain.groq import GroqAPIError, GroqClient
from ai.provider import GroqProvider
import ai.provider as provider_module


class StubResponse:
    def __init__(self, status_code: int, data: dict, headers: dict | None = None) -> None:
        self.status_code = status_code
        self._data = data
        self.headers = headers or {}

    def json(self) -> dict:
        return self._data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
            response = httpx.Response(
                self.status_code,
                headers=self.headers,
                request=request,
            )
            raise httpx.HTTPStatusError("request failed", request=request, response=response)


class StubClient:
    response = StubResponse(200, {"choices": [{"message": {"content": '{"intent":"chat"}'}}]})
    calls: list[tuple[str, dict]] = []

    def __init__(self, **_kwargs) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        pass

    def post(self, url: str, **kwargs) -> StubResponse:
        self.calls.append((url, kwargs))
        return self.response


def test_groq_chat_uses_chat_completions_and_json_mode(monkeypatch):
    StubClient.calls = []
    monkeypatch.setattr(groq_module.httpx, "Client", StubClient)
    client = GroqClient(api_key="test-key", model="test-model")

    answer = GroqProvider(client).chat("system", "user", json_mode=True)

    url, request = StubClient.calls[0]
    assert url.endswith("/chat/completions")
    assert request["headers"]["Authorization"] == "Bearer test-key"
    assert request["json"]["model"] == "test-model"
    assert request["json"]["stream"] is False
    assert request["json"]["response_format"] == {"type": "json_object"}
    assert answer == '{"intent":"chat"}'


def test_groq_reports_rate_limit_without_exposing_response_body(monkeypatch):
    StubClient.response = StubResponse(429, {"error": {"message": "private detail"}}, {"retry-after": "30"})
    monkeypatch.setattr(groq_module.httpx, "Client", StubClient)

    with pytest.raises(GroqAPIError, match="Retry after 30 seconds") as exc:
        GroqClient(api_key="test-key").chat("system", "user")

    assert "private detail" not in str(exc.value)
    StubClient.response = StubResponse(200, {"choices": [{"message": {"content": '{"intent":"chat"}'}}]})


def test_groq_is_unavailable_without_api_key(monkeypatch):
    def unexpected_client(**_kwargs):
        raise AssertionError("HTTP client should not be created without an API key")

    monkeypatch.setattr(groq_module.httpx, "Client", unexpected_client)
    assert GroqClient(api_key="").available() is False


def test_provider_factory_selects_groq(monkeypatch):
    monkeypatch.setattr(provider_module, "settings", SimpleNamespace(llm_provider="groq"))
    assert isinstance(provider_module.get_ai_provider(), GroqProvider)