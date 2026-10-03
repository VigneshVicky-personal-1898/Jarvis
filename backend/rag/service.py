# AI-ASSISTED: Cursor
# PROMPT: RAG service facade for ingest, status, and availability checks
# ACCEPTED-BY: vignesh

from __future__ import annotations

from config import settings
from rag import indexer, retriever, vector_store


class RAGService:
    def enabled(self) -> bool:
        return settings.rag_enabled

    def available(self) -> bool:
        if not settings.rag_enabled:
            return False
        try:
            vector_store.stats()
            return True
        except Exception:
            return False

    def sync(self) -> dict[str, object]:
        return indexer.sync_knowledge_base()

    def status(self) -> dict[str, object]:
        if not settings.rag_enabled:
            return {"enabled": False, "available": False}
        try:
            st = vector_store.stats()
            return {"enabled": True, "available": True, **st}
        except Exception as e:
            return {"enabled": True, "available": False, "error": str(e)}

    def retrieve_context(self, query: str) -> tuple[str, list[dict]]:
        chunks = retriever.retrieve(query)
        ctx = retriever.format_context(chunks)
        return ctx, chunks


_rag: RAGService | None = None


def get_rag() -> RAGService:
    global _rag
    if _rag is None:
        _rag = RAGService()
    return _rag
