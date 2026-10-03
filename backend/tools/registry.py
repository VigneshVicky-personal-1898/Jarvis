# AI-ASSISTED: Cursor
# PROMPT: Tool registry with permissions and confirmation gates
# ACCEPTED-BY: vignesh

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable

ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


class PermissionLevel(StrEnum):
    SAFE = "SAFE"
    CONFIRMATION = "CONFIRMATION"
    HIGH_RISK = "HIGH_RISK"


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    handler: ToolHandler
    allowed: bool = True
    permission: PermissionLevel = PermissionLevel.SAFE
    requires_confirmation: bool = False
    category: str = "general"


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def unregister(self, name: str) -> None:
        self._tools.pop(name, None)

    def names(self) -> list[str]:
        return sorted(self._tools.keys())

    def catalog(self) -> list[dict[str, str]]:
        out: list[dict[str, str]] = []
        for t in self._tools.values():
            if not t.allowed:
                continue
            out.append(
                {
                    "name": t.name,
                    "description": t.description,
                    "permission": t.permission.value,
                    "category": t.category,
                },
            )
        return out

    def capability_summary(self) -> list[str]:
        cats = sorted({t.category for t in self._tools.values() if t.allowed})
        labels = {
            "system": "Report system status, time, and date",
            "applications": "Open applications on your computer",
            "browser": "Search the web and open URLs",
            "files": "Find and create files and folders",
            "memory": "Remember and recall your preferences",
            "developer": "Run developer and QA tasks",
            "qe_engine": "QE Engine: MCP agent, regression, Workflow360, API automation",
            "general": "Other assistant capabilities",
        }
        return [labels.get(c, c) for c in cats]

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    def execute(
        self,
        name: str,
        params: dict[str, Any] | None = None,
        *,
        confirmed: bool = False,
    ) -> dict[str, Any]:
        spec = self._tools.get(name)
        if not spec:
            return {
                "ok": False,
                "speak": f"Tool {name} is not registered.",
                "data": {"error_code": "UNKNOWN_TOOL"},
            }
        if not spec.allowed:
            return {
                "ok": False,
                "speak": f"Tool {name} is not allowed.",
                "data": {"error_code": "TOOL_DENIED"},
            }

        args = dict(params or {})
        needs_confirm = spec.requires_confirmation or spec.permission in (
            PermissionLevel.CONFIRMATION,
            PermissionLevel.HIGH_RISK,
        )
        if needs_confirm and not confirmed and not args.pop("_confirmed", False):
            from tools.confirmation_store import create_pending

            prompt = args.get("_confirm_prompt") or (
                f"I need your confirmation before running {name}. Say yes to continue or no to cancel."
            )
            pending = create_pending(name, args, prompt)
            return {
                "ok": True,
                "speak": prompt,
                "data": {
                    "requires_confirmation": True,
                    "confirmation_id": pending.id,
                    "tool": name,
                    "arguments": args,
                },
            }

        result = spec.handler(args)
        if "data" not in result:
            result["data"] = {}
        result["data"]["permission"] = spec.permission.value
        return result
