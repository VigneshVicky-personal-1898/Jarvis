# AI-ASSISTED: Cursor
# PROMPT: Validates and executes only registered tools
# ACCEPTED-BY: vignesh

from __future__ import annotations

from typing import Any

from tools.registry import ToolRegistry


class ToolRouter:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def run(
        self,
        tool: str,
        params: dict[str, Any] | None = None,
        *,
        confirmed: bool = False,
    ) -> dict[str, Any]:
        name = (tool or "").strip()
        if not name or name == "none":
            return {
                "ok": True,
                "speak": "",
                "data": {"skipped": True},
            }
        return self.registry.execute(name, params or {}, confirmed=confirmed)
