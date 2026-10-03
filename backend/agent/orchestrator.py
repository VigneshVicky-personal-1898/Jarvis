# AI-ASSISTED: Cursor
# PROMPT: Modular route planner for RAG, web, tools, and combined answers
# ACCEPTED-BY: vignesh

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from config import settings
from rag.router import should_use_rag


class InformationRoute(StrEnum):
    """How to answer a knowledge-oriented utterance (actions use tools separately)."""

    CHAT = "chat"
    RAG = "rag"
    WEB = "web"
    RAG_AND_WEB = "rag_and_web"


_PERSONAL = re.compile(
    r"\b("
    r"my|mine|our|my project|project location|my notes|my documents|"
    r"knowledge base|according to my|in my files|saved in|personal|"
    r"my workflow|my qe|my team|my password|my config"
    r")\b",
    re.I,
)
_WEB_CURRENT = re.compile(
    r"\b("
    r"weather|forecast|temperature|news|headline|latest|today|tonight|"
    r"current|recent|now|live|price|cost|stock|crypto|score|who won|"
    r"this week|this month|2024|2025|2026|update|released|launch date"
    r")\b",
    re.I,
)
_EXPLICIT_WEB = re.compile(
    r"\b(search the web|google|look up online|on the internet|web search)\b",
    re.I,
)


@dataclass(frozen=True)
class RoutePlan:
    route: InformationRoute
    reason: str
    use_rag: bool
    use_web: bool


def plan_information_route(
    utterance: str,
    *,
    force_web: bool = False,
) -> RoutePlan:
    text = utterance.strip()
    personal = bool(_PERSONAL.search(text))
    web_hint = force_web or bool(_WEB_CURRENT.search(text) or _EXPLICIT_WEB.search(text))
    rag_eligible = settings.rag_enabled and should_use_rag(text, has_tool=False)

    if personal and web_hint:
        return RoutePlan(
            route=InformationRoute.RAG_AND_WEB,
            reason="personal_and_current",
            use_rag=rag_eligible,
            use_web=True,
        )
    if personal or (rag_eligible and not web_hint and _looks_personal_doc_query(text)):
        return RoutePlan(
            route=InformationRoute.RAG,
            reason="personal_knowledge",
            use_rag=rag_eligible,
            use_web=False,
        )
    if web_hint:
        return RoutePlan(
            route=InformationRoute.WEB,
            reason="current_or_external",
            use_rag=False,
            use_web=True,
        )
    if rag_eligible:
        return RoutePlan(
            route=InformationRoute.RAG,
            reason="knowledge_fallback",
            use_rag=True,
            use_web=False,
        )
    return RoutePlan(
        route=InformationRoute.CHAT,
        reason="general_llm",
        use_rag=False,
        use_web=False,
    )


def _looks_personal_doc_query(text: str) -> bool:
    return bool(
        re.search(
            r"\b(documentation|docs|pdf|notes|workflow360|qe engine|project)\b",
            text,
            re.I,
        ),
    )
