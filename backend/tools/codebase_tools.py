# AI-ASSISTED: Cursor
# PROMPT: Safe project tree scan and code search for connected repos
# ACCEPTED-BY: vignesh

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from config import ROOT, settings
from integrations.qe_engine.projects import QE_PROJECTS

_SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".cursor",
}


def _registered_roots() -> dict[str, Path]:
    roots: dict[str, Path] = {"raya": ROOT}
    for proj in QE_PROJECTS:
        roots[proj.id] = proj.path
    return roots


def _tree_summary(root: Path, *, max_depth: int = 2, max_entries: int = 40) -> list[str]:
    lines: list[str] = []
    if not root.is_dir():
        return [f"{root}: not found"]

    def walk(path: Path, depth: int) -> None:
        if len(lines) >= max_entries or depth > max_depth:
            return
        try:
            children = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except OSError:
            lines.append(f"{'  ' * depth}[access denied] {path.name}")
            return
        for child in children[:25]:
            if child.name in _SKIP_DIRS:
                continue
            rel = child.relative_to(root)
            tag = "/" if child.is_dir() else ""
            lines.append(f"{'  ' * depth}{rel}{tag}")
            if child.is_dir() and depth < max_depth:
                walk(child, depth + 1)
            if len(lines) >= max_entries:
                break

    walk(root, 0)
    return lines


def tool_analyze_project(params: dict[str, Any]) -> dict[str, Any]:
    project_id = str(params.get("project") or params.get("project_id") or "raya").strip().lower()
    roots = _registered_roots()
    if project_id == "jarvis":
        project_id = "raya"
    if project_id not in roots:
        ids = ", ".join(sorted(roots.keys()))
        return {
            "ok": False,
            "speak": f"Unknown project {project_id}. Known projects: {ids}.",
            "data": {"projects": list(roots.keys())},
        }
    root = roots[project_id]
    tree = _tree_summary(root)
    readme = root / "README.md"
    readme_hint = ""
    if readme.is_file():
        readme_hint = readme.read_text(encoding="utf-8", errors="replace")[:600].strip()
    speak = (
        f"Project {project_id} at {root}. "
        f"Top structure: {'; '.join(tree[:8])}."
    )
    if readme_hint:
        speak += " README excerpt loaded for the activity panel."
    return {
        "ok": True,
        "speak": speak,
        "data": {
            "project_id": project_id,
            "path": str(root),
            "tree": tree,
            "readme_excerpt": readme_hint,
        },
    }


def tool_search_project_code(params: dict[str, Any]) -> dict[str, Any]:
    query = str(params.get("query") or params.get("pattern") or "").strip()
    if not query:
        return {"ok": False, "speak": "What should I search for in the codebase?", "data": {}}
    project_id = str(params.get("project") or params.get("project_id") or "raya").strip().lower()
    if project_id == "jarvis":
        project_id = "raya"
    roots = _registered_roots()
    root = roots.get(project_id, ROOT)
    if not root.is_dir():
        return {"ok": False, "speak": f"Project path missing for {project_id}.", "data": {}}
    try:
        proc = subprocess.run(
            [
                "rg",
                "--line-number",
                "--max-count",
                "15",
                "--glob",
                "!.git/*",
                "--glob",
                "!node_modules/*",
                query,
                str(root),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        return {
            "ok": False,
            "speak": "Code search needs ripgrep installed on this machine.",
            "data": {},
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "speak": "Code search timed out.", "data": {}}
    hits = proc.stdout.strip().splitlines()
    if not hits:
        return {
            "ok": True,
            "speak": f"No matches for {query} in {project_id}.",
            "data": {"matches": []},
        }
    preview = "; ".join(hits[:5])
    return {
        "ok": True,
        "speak": f"Found {len(hits)} matches in {project_id}. {preview}",
        "data": {"matches": hits, "project_id": project_id, "query": query},
    }


def tool_list_connected_projects(_params: dict[str, Any]) -> dict[str, Any]:
    roots = _registered_roots()
    parts = []
    for pid, path in roots.items():
        parts.append(f"{pid}: {'ready' if path.is_dir() else 'missing'}")
    speak = "Connected codebases. " + "; ".join(parts) + "."
    return {"ok": True, "speak": speak, "data": {"projects": {k: str(v) for k, v in roots.items()}}}
