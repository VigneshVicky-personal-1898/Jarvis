# AI-ASSISTED: Cursor
# PROMPT: Route knowledge questions to RAG vs action requests to tools
# ACCEPTED-BY: vignesh

from __future__ import annotations

import re

_ACTION = re.compile(
    r"\b("
    r"run|open|launch|create|trigger|execute|start|stop|mute|volume|"
    r"regression|kaatu|kattu|pannu|paaru|status|analyze|search files|"
    r"confirm|yes|no|sleep|chrome|terminal|workflow360|tpx|rtp|rex"
    r")\b",
    re.I,
)
_KNOWLEDGE = re.compile(
    r"\b("
    r"what|how|why|when|where|explain|describe|documentation|docs|"
    r"mean|difference|compare|summarize|summary|tell me about|"
    r"according to|in my documents|knowledge base|workflow360|qe engine"
    r")\b",
    re.I,
)


def should_use_rag(utterance: str, *, has_tool: bool) -> bool:
    if has_tool:
        return False
    text = utterance.strip()
    if not text:
        return False
    if _ACTION.search(text) and not _KNOWLEDGE.search(text):
        return False
    if _KNOWLEDGE.search(text):
        return True
    if "?" in text:
        return True
    return len(text.split()) >= 8
