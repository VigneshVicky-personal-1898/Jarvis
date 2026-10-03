# AI-ASSISTED: Cursor
# PROMPT: Sync filesystem knowledge into ChromaDB when files change
# ACCEPTED-BY: vignesh

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from config import RAG_DIR, settings
from rag.chunking import chunk_text
from rag.document_loader import (
    discover_files,
    file_indexed_at,
    file_version,
    load_text,
)
from rag.embeddings import embed_texts
from rag.types import DocumentChunk
from rag import vector_store

_MANIFEST = RAG_DIR / "manifest.json"


def _load_manifest() -> dict[str, str]:
    if not _MANIFEST.is_file():
        return {}
    try:
        return json.loads(_MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_manifest(data: dict[str, str]) -> None:
    RAG_DIR.mkdir(parents=True, exist_ok=True)
    _MANIFEST.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _chunk_id(source: str, version: str, index: int) -> str:
    safe = source.replace("/", "_").replace(" ", "_")[-120:]
    return f"{safe}:{version}:{index}"


def sync_knowledge_base() -> dict[str, object]:
    if not settings.rag_enabled:
        return {"ok": False, "message": "RAG disabled in config"}

    manifest = _load_manifest()
    files = discover_files()
    current: dict[str, str] = {}
    ingested = 0
    removed = 0
    errors: list[str] = []

    for path in files:
        src = str(path)
        version = file_version(path)
        current[src] = version
        if manifest.get(src) == version:
            continue
        if src in manifest:
            vector_store.delete_by_source(src)
        try:
            raw = load_text(path)
            pieces = chunk_text(
                raw,
                chunk_size=settings.rag_chunk_size,
                overlap=settings.rag_chunk_overlap,
            )
            if not pieces:
                continue
            indexed_at = datetime.now(tz=timezone.utc).isoformat()
            chunks: list[DocumentChunk] = []
            for i, piece in enumerate(pieces):
                chunks.append(
                    DocumentChunk(
                        chunk_id=_chunk_id(src, version, i),
                        text=piece,
                        file_name=path.name,
                        doc_type=path.suffix.lower().lstrip(".") or "unknown",
                        source_path=src,
                        version=version,
                        indexed_at=indexed_at,
                    ),
                )
            vectors = embed_texts([c.text for c in chunks])
            vector_store.upsert_chunks(chunks, vectors)
            ingested += 1
        except Exception as e:
            errors.append(f"{path.name}: {e}")

    for old_path in set(manifest.keys()) - set(current.keys()):
        vector_store.delete_by_source(old_path)
        removed += 1

    _save_manifest(current)
    st = vector_store.stats()
    return {
        "ok": True,
        "files_tracked": len(current),
        "files_ingested": ingested,
        "files_removed": removed,
        "errors": errors,
        **st,
    }
