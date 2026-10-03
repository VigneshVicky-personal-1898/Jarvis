# AI-ASSISTED: Cursor
# PROMPT: Voice tools to sync and query local RAG knowledge base
# ACCEPTED-BY: vignesh

from __future__ import annotations

from typing import Any

from config import settings
from rag.service import get_rag


def tool_rag_sync(_params: dict[str, Any]) -> dict[str, Any]:
    if not settings.rag_enabled:
        return {
            "ok": False,
            "speak": "RAG is disabled. Set RAYA_RAG_ENABLED=true in .env.",
            "data": {},
        }
    result = get_rag().sync()
    if not result.get("ok"):
        return {"ok": False, "speak": str(result.get("message", "Sync failed")), "data": result}
    speak = (
        f"Knowledge base synced. {result.get('files_tracked', 0)} files tracked, "
        f"{result.get('files_ingested', 0)} updated, "
        f"{result.get('chunk_count', 0)} chunks in the index."
    )
    return {"ok": True, "speak": speak, "data": result}


def tool_rag_status(_params: dict[str, Any]) -> dict[str, Any]:
    st = get_rag().status()
    if not st.get("enabled"):
        return {"ok": True, "speak": "Local RAG is turned off in configuration.", "data": st}
    if not st.get("available"):
        return {
            "ok": False,
            "speak": "RAG is enabled but the vector store is not ready. Check dependencies.",
            "data": st,
        }
    speak = f"Local knowledge index has {st.get('chunk_count', 0)} chunks."
    return {"ok": True, "speak": speak, "data": st}
