# AI-ASSISTED: Cursor
# PROMPT: Memory save and retrieve tools backed by SQLite
# ACCEPTED-BY: vignesh

from __future__ import annotations

import re
from typing import Any

from memory.long_term import LongTermMemory

_memory = LongTermMemory()


def _parse_remember(text: str) -> tuple[str, str]:
    patterns = [
        r"remember(?:\s+that)?\s+(?:my\s+)?(.+?)\s+is\s+(.+)",
        r"remember\s+(.+)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            if len(m.groups()) == 2:
                return m.group(1).strip().replace(" ", "_"), m.group(2).strip()
            return "note", m.group(1).strip()
    return "note", text.strip()


def tool_memory_save(params: dict[str, Any]) -> dict[str, Any]:
    raw = str(params.get("information") or params.get("value") or params.get("text") or "")
    category = str(params.get("category") or "IMPORTANT_NOTE")
    key = str(params.get("key") or "").strip()
    value = str(params.get("value") or "").strip()
    if not key and raw:
        key, value = _parse_remember(raw)
    if not value and raw:
        value = raw
    if not key or not value:
        return {
            "ok": False,
            "speak": "What should I remember?",
            "data": {"error_code": "MISSING_MEMORY_FIELDS"},
        }
    _memory.save(category, key, value)
    return {
        "ok": True,
        "speak": f"Noted. I'll remember that {key.replace('_', ' ')} is {value}.",
        "data": {"category": category, "key": key, "value": value},
    }


def tool_memory_retrieve(params: dict[str, Any]) -> dict[str, Any]:
    key = str(params.get("key") or "main_project").strip()
    category = params.get("category")
    if category:
        val = _memory.get(str(category), key)
    else:
        val = _memory.get_any(key)
    if not val:
        return {
            "ok": True,
            "speak": f"I don't have anything stored for {key.replace('_', ' ')} yet.",
            "data": {"found": False},
        }
    return {
        "ok": True,
        "speak": f"{key.replace('_', ' ')}: {val}.",
        "data": {"found": True, "key": key, "value": val},
    }
