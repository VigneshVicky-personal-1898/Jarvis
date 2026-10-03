# AI-ASSISTED: Cursor
# PROMPT: Provider-backed intent router — tool actions vs general chat
# ACCEPTED-BY: vignesh

from __future__ import annotations

import re
from typing import Any

from ai.provider import AIProvider
from agent.prompts import planner_system
from tools.registry import ToolRegistry

_CHAT_HINT = re.compile(
    r"\b(what is|what's|who is|explain|tell me about|difference between|compare|why |how does|define )\b",
    re.I,
)


class AgentPlanner:
    def __init__(self, brain: AIProvider, registry: ToolRegistry) -> None:
        self.brain = brain
        self.registry = registry

    def plan(self, user_text: str) -> dict[str, Any]:
        tools = self.registry.catalog()
        system = planner_system(tools)
        raw = self.brain.chat(system, user_text, json_mode=True)
        parsed = self.brain.parse_json(raw) or {}
        tool = str(parsed.get("tool", "none")).strip()
        params = parsed.get("params") or {}
        if not isinstance(params, dict):
            params = {}
        intent = str(parsed.get("intent", "")).strip().lower()
        if intent not in ("tool", "chat"):
            intent = "chat" if tool in ("", "none") and _CHAT_HINT.search(user_text) else "tool"
        if tool in ("", "none") and intent != "chat" and _CHAT_HINT.search(user_text):
            intent = "chat"
        return {
            "intent": intent,
            "tool": tool,
            "params": params,
            "reason": parsed.get("reason", ""),
            "raw": raw,
        }
