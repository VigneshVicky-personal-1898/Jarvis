# AI-ASSISTED: Cursor
# PROMPT: LLM structured intent extraction with JSON validation
# ACCEPTED-BY: vignesh

from __future__ import annotations

import json
import re
from typing import Any

from agent.intent_schema import IntentCategory, StructuredIntent, normalize_tool_name
from ai.provider import AIProvider
from tools.registry import ToolRegistry

CURRENT_INFO_HINT = re.compile(
    r"\b(latest|today|current|recent|now|this week|news|weather|price)\b",
    re.I,
)


def _intent_system(tools: list[dict[str, str]]) -> str:
    catalog = json.dumps(tools, indent=2)
    intents = [i.value for i in IntentCategory]
    return f"""You are RAYA intent classifier. Return JSON only.

Intents: {intents}

Tools (use exact name in tool field):
{catalog}

Schema:
{{
  "intent": "OPEN_APPLICATION | SEARCH_WEB | GENERAL_QUESTION | ...",
  "confidence": 0.0-1.0,
  "tool": "registry tool name or null",
  "arguments": {{ }},
  "requires_confirmation": false,
  "response": "short voice line if acting, else empty"
}}

Rules:
- Map browser/chrome requests to open_app with {{"app": "chrome"}}.
- Map search requests to web_search with {{"query": "..."}}.
- Map remember/save to memory_save.
- Map "what is my project" to memory_retrieve.
- Use GENERAL_QUESTION for explanations (Selenium, Docker) without web search.
- Use SEARCH_WEB intent when user needs current/live information (latest, today, news).
- Never invent shell commands.
- Pure knowledge / documentation questions → GENERAL_QUESTION (RAG + chat), not a tool.
- Actions (run, open, create, trigger, regression) → pick the matching tool, not chat.
- QE Engine / Workflow360 / MCP / "create API" / "run regression" / test automation:
  use qe_agent_command with {{"command": "<full user request>"}} unless user only asks
  for QE status (qe_projects_status) or tool list (qe_list_mcp_tools) or explicit
  regression (qe_regression). Execution ids like TPX-22 → qe_execution_result.
  Latest test plan results → qe_latest_results (not ActiveMQ).
"""


class StructuredIntentDetector:
    def __init__(self, provider: AIProvider, registry: ToolRegistry) -> None:
        self.provider = provider
        self.registry = registry

    def detect(self, utterance: str) -> StructuredIntent | None:
        if not self.provider.available():
            return None
        raw = self.provider.chat(_intent_system(self.registry.catalog()), utterance, json_mode=True)
        parsed = self.provider.parse_json(raw) or {}
        try:
            intent = IntentCategory(str(parsed.get("intent", "UNKNOWN")))
        except ValueError:
            intent = IntentCategory.UNKNOWN
        tool = normalize_tool_name(parsed.get("tool"))
        if tool == "none":
            tool = None
        args = parsed.get("arguments") or parsed.get("params") or {}
        if not isinstance(args, dict):
            args = {}
        if intent == IntentCategory.OPEN_APPLICATION and "app" not in args:
            if "application" in args:
                args["app"] = args.pop("application")
            elif "browser" in utterance.lower():
                args["app"] = "chrome"
        if intent == IntentCategory.SEARCH_WEB and "query" not in args:
            if "query" in args:
                pass
            else:
                args["query"] = utterance
        if intent == IntentCategory.GENERAL_QUESTION and CURRENT_INFO_HINT.search(utterance):
            intent = IntentCategory.SEARCH_WEB
            tool = "web_search"
            args.setdefault("query", utterance)
        return StructuredIntent(
            intent=intent,
            confidence=float(parsed.get("confidence", 0.7)),
            tool=tool,
            arguments=args,
            requires_confirmation=bool(parsed.get("requires_confirmation", False)),
            response=str(parsed.get("response", "")),
            route="ai",
        )
