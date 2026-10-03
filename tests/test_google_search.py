from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from agent.orchestrator import InformationRoute, plan_information_route
from tools.setup import build_registry


def test_google_search_tool_is_registered():
    registry = build_registry()
    assert registry.get("google_search") is not None
    assert registry.get("web_search") is not None


def test_general_question_does_not_trigger_google_search():
    plan = plan_information_route("What is the capital of France?")
    assert plan.route in (InformationRoute.RAG, InformationRoute.CHAT)
    assert plan.use_web is False


def test_current_question_uses_web_search():
    plan = plan_information_route("What is the latest AI news today?")
    assert plan.route == InformationRoute.WEB
    assert plan.use_web is True


def test_google_custom_search_is_used_when_configured(monkeypatch):
    import importlib

    import config
    import search.internet

    monkeypatch.setenv("RAYA_GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("RAYA_GOOGLE_CSE_ID", "test-cx")

    importlib.reload(config)
    importlib.reload(search.internet)
    from search.internet import fetch_web_results

    seen = {}

    class DummyResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def fake_get(url, params=None, timeout=None):
        seen["url"] = url
        seen["params"] = params
        return DummyResponse(
            {
                "items": [
                    {
                        "title": "Google result title",
                        "snippet": "Google result snippet",
                        "link": "https://example.com/google-result",
                    }
                ]
            }
        )

    monkeypatch.setattr("httpx.get", fake_get)

    results = fetch_web_results("latest AI news", max_results=2)

    assert results[0]["title"] == "Google result title"
    assert results[0]["url"] == "https://example.com/google-result"
    assert "googleapis.com/customsearch" in seen["url"]
    assert seen["params"]["q"] == "latest AI news"


def test_google_empty_results_fallback_to_duckduckgo(monkeypatch):
    import importlib

    import config
    import search.internet

    monkeypatch.setenv("RAYA_GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("RAYA_GOOGLE_CSE_ID", "test-cx")

    importlib.reload(config)
    importlib.reload(search.internet)
    from search.internet import fetch_web_results

    class DummyResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def fake_get(url, params=None, timeout=None):
        return DummyResponse({"items": []})

    class DummyDDGS:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def text(self, query, max_results=5):
            return [{
                "title": "Fallback result",
                "body": "Fallback snippet",
                "href": "https://example.com/fallback",
            }]

    monkeypatch.setattr("httpx.get", fake_get)
    monkeypatch.setattr("duckduckgo_search.DDGS", DummyDDGS)

    results = fetch_web_results("latest AI news", max_results=2)

    assert results[0]["title"] == "Fallback result"
    assert results[0]["url"] == "https://example.com/fallback"


def test_search_provider_does_not_open_browser_on_empty_results(monkeypatch):
    import search.provider as provider_module

    called = {"open": False}

    monkeypatch.setattr(provider_module.webbrowser, "open", lambda *args, **kwargs: called.__setitem__("open", True))
    monkeypatch.setattr(provider_module, "fetch_web_results", lambda *args, **kwargs: [])

    result = provider_module.GoogleSearchProvider().search("What are the latest technology updates?")

    assert result["ok"] is False
    assert result["provider"] == "google_no_results"
    assert called["open"] is False


def test_tool_web_search_uses_friendly_user_message(monkeypatch):
    from tools import browser as browser_module

    class DummyProvider:
        def search(self, query):
            return {
                "ok": True,
                "query": query,
                "results": [{
                    "title": "AI chip update",
                    "snippet": "New AI chips are expanding edge AI and inference performance.",
                    "url": "https://example.com/ai-chip-news",
                }],
            }

    monkeypatch.setattr(browser_module, "get_search_provider", lambda: DummyProvider())

    result = browser_module.tool_web_search({
        "query": "What are the latest technology updates?",
    })

    assert result["ok"] is True
    assert "Sure! I checked the latest information" in result["speak"]
    assert "Google" not in result["speak"]
    assert "browser" not in result["speak"].lower()
