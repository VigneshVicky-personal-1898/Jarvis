# AI-ASSISTED: Cursor
# PROMPT: Semantic retrieval from local Chroma vector store
# ACCEPTED-BY: vignesh

from __future__ import annotations

from typing import Any

from config import settings
from rag.embeddings import embed_query
from rag import vector_store


def retrieve(query: str, top_k: int | None = None) -> list[dict[str, Any]]:
    if not settings.rag_enabled:
        return []
    k = top_k or settings.rag_top_k
    if not query.strip():
        return []
    try:
        emb = embed_query(query.strip())
        rows = vector_store.query(emb, top_k=k)
    except Exception:
        return []
    min_score = settings.rag_min_score
    return [r for r in rows if float(r.get("score", 0)) >= min_score]


def format_context(chunks: list[dict[str, Any]], max_chars: int = 6000) -> str:
    if not chunks:
        return ""
    parts: list[str] = []
    used = 0
    for i, row in enumerate(chunks, start=1):
        meta = row.get("metadata") or {}
        header = (
            f"[{i}] {meta.get('file_name', 'doc')} "
            f"({meta.get('doc_type', '?')}) "
            f"score={row.get('score', 0):.2f}"
        )
        body = str(row.get("text", "")).strip()
        block = f"{header}\n{body}\n"
        if used + len(block) > max_chars:
            break
        parts.append(block)
        used += len(block)
    return "\n".join(parts).strip()
