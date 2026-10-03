# AI-ASSISTED: Cursor
# PROMPT: Fetch web snippets locally for Jarvis answers with sources
# ACCEPTED-BY: vignesh

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import httpx

from config import settings


def _strip_html(text: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text, flags=re.I | re.S)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _enrich_search_results(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if not rows:
        return rows

    def fetch_page(url: str) -> str:
        try:
            response = httpx.get(url, timeout=8.0, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            return _strip_html(response.text)[:500]
        except Exception:
            return ""

    candidates = rows[: min(len(rows), 3)]
    urls = [row.get("url", "") for row in candidates if row.get("url")]
    if not urls:
        return rows

    with ThreadPoolExecutor(max_workers=min(len(urls), 3)) as pool:
        page_texts = list(pool.map(fetch_page, urls))

    enriched: list[dict[str, str]] = []
    for row, page_text in zip(candidates, page_texts):
        snippet = str(row.get("snippet", "") or "").strip()
        if not snippet and page_text:
            snippet = page_text
        elif page_text and len(snippet) < 180:
            snippet = (snippet + " " + page_text).strip()
        compact = {**row, "snippet": snippet[:700]}
        enriched.append(compact)

    for row in rows[min(len(rows), 3) :]:
        enriched.append(row)
    return enriched


def _google_custom_search(query: str, *, max_results: int) -> list[dict[str, str]] | None:
    api_key = settings.google_search_api_key.strip()
    cse_id = settings.google_search_cse_id.strip()
    if not api_key or not cse_id:
        return None

    try:
        response = httpx.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": api_key,
                "cx": cse_id,
                "q": query,
                "num": max(1, min(max_results, 10)),
            },
            timeout=12.0,
        )
        response.raise_for_status()
        payload = response.json() or {}
        items = payload.get("items") or []
        rows: list[dict[str, str]] = []
        for item in items:
            rows.append(
                {
                    "title": str(item.get("title", "")),
                    "snippet": str(item.get("snippet", "")),
                    "url": str(item.get("link", "")),
                },
            )
        return _enrich_search_results(rows)
    except Exception:
        return None


def fetch_web_results(query: str, *, max_results: int | None = None) -> list[dict[str, str]]:
    q = query.strip()
    if not q:
        return []
    limit = max(1, min(max_results or int(settings.web_search_max_results), 5))

    google_results = _google_custom_search(q, max_results=limit)
    if google_results:
        return google_results

    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return []
    rows: list[dict[str, str]] = []
    try:
        with DDGS() as ddgs:
            for item in ddgs.text(q, max_results=limit):
                rows.append(
                    {
                        "title": str(item.get("title", "")),
                        "snippet": str(item.get("body", "")),
                        "url": str(item.get("href", "")),
                    },
                )
    except Exception:
        return []
    return _enrich_search_results(rows)


def format_web_context(results: list[dict[str, str]], max_chars: int = 8000) -> str:
    if not results:
        return ""
    parts: list[str] = []
    used = 0
    for i, row in enumerate(results, start=1):
        block = (
            f"[web-{i}] {row.get('title', 'result')}\n"
            f"{row.get('snippet', '')}\n"
            f"Source: {row.get('url', '')}\n"
        )
        if used + len(block) > max_chars:
            break
        parts.append(block)
        used += len(block)
    return "\n".join(parts).strip()
