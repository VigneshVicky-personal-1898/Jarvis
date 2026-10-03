# AI-ASSISTED: Cursor
# PROMPT: Legacy ActionExecutor delegating to tool registry
# ACCEPTED-BY: vignesh

from __future__ import annotations

from typing import Any

from engine import CommandEngine, MatchResult
from tools.setup import build_registry


def _load_apps() -> dict[str, dict[str, str]]:
    from tools.applications import load_apps

    return load_apps()


class ActionExecutor:
    """Backward-compatible wrapper around the tool registry."""

    def __init__(self, engine: CommandEngine) -> None:
        self.engine = engine
        self.registry = build_registry(engine)
        self.apps = _load_apps()

    def execute(self, match: MatchResult) -> dict[str, Any]:
        if match.action == "none":
            return {"ok": True, "speak": match.response or "Done.", "data": {}}
        params = dict(match.params)
        if match.action == "sleep" and match.response:
            params["message"] = match.response
        return self.registry.execute(match.action, params)
