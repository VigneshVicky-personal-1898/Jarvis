# AI-ASSISTED: Cursor
# PROMPT: ChromaDB persistent vector store with chunk metadata
# ACCEPTED-BY: vignesh

from __future__ import annotations

from functools import lru_cache
from typing import Any

from config import CHROMA_DIR
from rag.types import DocumentChunk

_COLLECTION = "raya_knowledge"


@lru_cache
def _client():
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def get_collection():
    return _client().get_or_create_collection(
        name=_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def upsert_chunks(chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
    if not chunks:
        return
    col = get_collection()
    col.upsert(
        ids=[c.chunk_id for c in chunks],
        embeddings=embeddings,
        documents=[c.text for c in chunks],
        metadatas=[
            {
                "file_name": c.file_name,
                "doc_type": c.doc_type,
                "source_path": c.source_path,
                "version": c.version,
                "indexed_at": c.indexed_at,
                "chunk_id": c.chunk_id,
            }
            for c in chunks
        ],
    )


def delete_by_source(source_path: str) -> None:
    col = get_collection()
    col.delete(where={"source_path": source_path})


def delete_by_source_version(source_path: str, version: str) -> None:
    col = get_collection()
    col.delete(where={"$and": [{"source_path": source_path}, {"version": version}]})


def query(
    embedding: list[float],
    *,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    col = get_collection()
    if col.count() == 0:
        return []
    result = col.query(
        query_embeddings=[embedding],
        n_results=min(top_k, col.count()),
        include=["documents", "metadatas", "distances"],
    )
    rows: list[dict[str, Any]] = []
    docs = (result.get("documents") or [[]])[0]
    metas = (result.get("metadatas") or [[]])[0]
    dists = (result.get("distances") or [[]])[0]
    for doc, meta, dist in zip(docs, metas, dists, strict=False):
        rows.append(
            {
                "text": doc,
                "metadata": meta or {},
                "score": 1.0 - float(dist) if dist is not None else 0.0,
            },
        )
    return rows


def stats() -> dict[str, Any]:
    col = get_collection()
    return {"chunk_count": col.count(), "collection": _COLLECTION}
