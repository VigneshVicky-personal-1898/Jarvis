# AI-ASSISTED: Cursor
# PROMPT: Load PDF, text, markdown, YAML from knowledge paths for RAG
# ACCEPTED-BY: vignesh

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from config import KNOWLEDGE_DIR, settings

_SUPPORTED = {".md", ".txt", ".pdf", ".yaml", ".yml", ".json", ".rst", ".csv"}


def knowledge_roots() -> list[Path]:
    roots = [KNOWLEDGE_DIR]
    extra = (getattr(settings, "rag_extra_paths", "") or "").strip()
    for part in extra.split(","):
        p = part.strip()
        if p:
            roots.append(Path(p).expanduser().resolve())
    return roots


def discover_files() -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()
    for root in knowledge_roots():
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in _SUPPORTED:
                continue
            key = str(path.resolve())
            if key in seen:
                continue
            seen.add(key)
            found.append(path.resolve())
    return sorted(found)


def file_version(path: Path) -> str:
    st = path.stat()
    digest = hashlib.sha256(
        f"{st.st_mtime_ns}:{st.st_size}:{path}".encode(),
    ).hexdigest()[:16]
    return digest


def file_indexed_at(path: Path) -> str:
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def load_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as e:
            raise RuntimeError("Install pypdf for PDF ingestion") from e
        reader = PdfReader(str(path))
        parts: list[str] = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts)
    return path.read_text(encoding="utf-8", errors="replace")
