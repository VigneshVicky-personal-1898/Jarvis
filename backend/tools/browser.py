# AI-ASSISTED: Cursor
# PROMPT: Web search tool with fetch snippets and browser fallback
# ACCEPTED-BY: vignesh

from __future__ import annotations

import webbrowser
from typing import Any

from search.provider import get_search_provider


def tool_web_search(params: dict[str, Any]) -> dict[str, Any]:
    query = str(params.get("query", "")).strip()
    if not query:
        return {"ok": False, "speak": "What should I search for?", "data": {}}
    body = get_search_provider().search(query)
    results = body.get("results") or []
    if not results:
        return {
            "ok": False,
            "speak": "I couldn't find reliable information for that right now. Try a slightly different wording.",
            "data": body,
        }

    top = results[0]
    title = str(top.get("title", "Recent result")).strip()
    snippet = str(top.get("snippet", "")).strip()
    source = str(top.get("url", "")).strip()
    if not snippet:
        snippet = "This looks like a relevant recent update."
    summary = snippet[:220]
    speak = (
        f"Sure! I checked the latest information for '{query}'. "
        f"The key update is: {title}. {summary}"
    )
    if source:
        speak += f" Source: {source}."
    return {
        "ok": True,
        "speak": speak,
        "data": body,
    }


def tool_open_url(params: dict[str, Any]) -> dict[str, Any]:
    url = str(params.get("url", "")).strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return {"ok": True, "speak": f"Opening {url}.", "data": {"url": url}}
