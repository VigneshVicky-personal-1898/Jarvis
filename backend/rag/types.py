# AI-ASSISTED: Cursor
# PROMPT: RAG chunk and document metadata types
# ACCEPTED-BY: vignesh

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    text: str
    file_name: str
    doc_type: str
    source_path: str
    version: str
    indexed_at: str
