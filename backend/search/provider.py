# AI-ASSISTED: Cursor
# PROMPT: Web search fetch vs browser-open modes for Jarvis
# ACCEPTED-BY: vignesh

from __future__ import annotations

import webbrowser
from typing import Protocol
from urllib.parse import quote_plus

from config import settings
from search.internet import fetch_web_results, format_web_context


class SearchProvider(Protocol):
    def search(self, query: str) -> dict: ...


class BrowserSearchProvider:
    def __init__(self, base_url: str = "https://www.google.com/search?q=") -> None:
        self.base_url = base_url

    def search(self, query: str) -> dict:
        q = query.strip()
        url = f"{self.base_url}{quote_plus(q)}"
        webbrowser.open(url)
        return {
            "ok": True,
            "provider": "browser",
            "url": url,
            "query": q,
            "message": f"Searching for {q}.",
            "results": [],
        }


class GoogleSearchProvider:
    """Use the Google Custom Search API when configured and never redirect the user to a browser."""

    def search(self, query: str) -> dict:
        q = query.strip()
        if not q:
            return {"ok": False, "provider": "google", "query": q, "results": [], "message": "No query provided."}

        results = fetch_web_results(q, max_results=settings.web_search_max_results)
        if not results:
            return {
                "ok": False,
                "provider": "google_no_results",
                "query": q,
                "message": "I couldn't retrieve reliable web results for this question right now.",
                "results": [],
                "context": "",
            }

        context = format_web_context(results)
        titles = "; ".join(r.get("title", "")[:60] for r in results[:3])
        return {
            "ok": True,
            "provider": "google",
            "query": q,
            "message": f"Found Google web results for {q}. {titles}",
            "results": results,
            "context": context,
        }


class FetchSearchProvider:
    """Retrieve snippets without redirecting the user to a browser."""

    def search(self, query: str) -> dict:
        q = query.strip()
        results = fetch_web_results(q, max_results=settings.web_search_max_results)
        if not results:
            return {
                "ok": False,
                "provider": "fetch_no_results",
                "query": q,
                "message": "I couldn't retrieve reliable web results for this question right now.",
                "results": [],
                "context": "",
            }
        context = format_web_context(results)
        titles = "; ".join(r.get("title", "")[:60] for r in results[:3])
        return {
            "ok": True,
            "provider": "fetch",
            "query": q,
            "message": f"Found web results for {q}. {titles}",
            "results": results,
            "context": context,
        }


def get_search_provider() -> SearchProvider:
    if settings.web_search_mode == "browser":
        return BrowserSearchProvider()
    if settings.google_search_api_key and settings.google_search_cse_id:
        return GoogleSearchProvider()
    return FetchSearchProvider()
