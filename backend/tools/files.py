# AI-ASSISTED: Cursor
# PROMPT: File search and safe folder creation under user home
# ACCEPTED-BY: vignesh

from __future__ import annotations

from pathlib import Path
from typing import Any


def tool_search_files(params: dict[str, Any]) -> dict[str, Any]:
    query = str(params.get("query", "")).strip().lower()
    root = Path(str(params.get("root", Path.home()))).expanduser().resolve()
    limit = int(params.get("limit", 15))
    if not query:
        return {"ok": False, "speak": "Tell me what to search for in your files.", "data": {}}
    if not root.is_dir():
        return {"ok": False, "speak": "That folder does not exist.", "data": {}}

    matches: list[str] = []
    skip = {".git", "node_modules", ".venv", "__pycache__"}
    for path in root.rglob("*"):
        if any(part in skip for part in path.parts):
            continue
        if query in path.name.lower():
            matches.append(str(path))
            if len(matches) >= limit:
                break

    if not matches:
        speak = f"No files matching {query} under {root}."
    else:
        speak = f"Found {len(matches)} matches. Top result: {matches[0]}."
    return {"ok": True, "speak": speak, "data": {"matches": matches, "root": str(root)}}


def _safe_folder_path(name: str, parent: Path) -> Path | None:
    clean = name.strip().replace("/", "").replace("\\", "")
    if not clean or clean in (".", ".."):
        return None
    base = parent.expanduser().resolve()
    home = Path.home().resolve()
    target = (base / clean).resolve()
    if not str(target).startswith(str(home)):
        return None
    return target


def tool_create_folder(params: dict[str, Any]) -> dict[str, Any]:
    name = str(params.get("name") or params.get("folder") or "").strip()
    parent = Path(str(params.get("parent", Path.home())))
    if not name:
        return {"ok": False, "speak": "What should I name the folder?", "data": {}}
    target = _safe_folder_path(name, parent)
    if not target:
        return {
            "ok": False,
            "speak": "I can only create folders inside your home directory.",
            "data": {},
        }
    if target.exists():
        return {
            "ok": True,
            "speak": f"Folder {name} already exists at {target}.",
            "data": {"path": str(target), "created": False},
        }
    target.mkdir(parents=True, exist_ok=False)
    return {
        "ok": True,
        "speak": f"Created folder {name}.",
        "data": {"path": str(target), "created": True},
    }
