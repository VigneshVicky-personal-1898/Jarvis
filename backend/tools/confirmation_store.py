# AI-ASSISTED: Cursor
# PROMPT: Pending tool confirmation store (no agent imports)
# ACCEPTED-BY: vignesh

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class PendingAction:
    id: str
    tool: str
    arguments: dict[str, Any]
    prompt: str


_store: dict[str, PendingAction] = {}
_active_id: str | None = None

AFFIRMATIVE = {"yes", "yeah", "yep", "confirm", "do it", "go ahead", "proceed", "ok", "okay"}
NEGATIVE = {"no", "nope", "cancel", "stop", "don't", "do not"}


def create_pending(tool: str, arguments: dict[str, Any], prompt: str) -> PendingAction:
    global _active_id
    action_id = str(uuid.uuid4())
    pending = PendingAction(id=action_id, tool=tool, arguments=arguments, prompt=prompt)
    _store[action_id] = pending
    _active_id = action_id
    return pending


def get_active() -> PendingAction | None:
    if not _active_id:
        return None
    return _store.get(_active_id)


def consume(action_id: str, approved: bool) -> PendingAction | None:
    global _active_id
    pending = _store.pop(action_id, None)
    if _active_id == action_id:
        _active_id = None
    if not pending or not approved:
        return None
    return pending


def is_affirmative(text: str) -> bool:
    t = text.lower().strip().strip(".!")
    return t in AFFIRMATIVE or t.startswith("yes ")


def is_negative(text: str) -> bool:
    t = text.lower().strip().strip(".!")
    return t in NEGATIVE or t.startswith("no ")


def clear_active() -> None:
    global _active_id
    if _active_id:
        _store.pop(_active_id, None)
    _active_id = None
