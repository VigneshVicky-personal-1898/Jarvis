# AI-ASSISTED: Cursor
# PROMPT: Per-request execution metadata for debug and UI timeline
# ACCEPTED-BY: vignesh

from __future__ import annotations

import time
from collections import deque
from time import time as unix_time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionRecord:
    timestamp: float
    user_input: str
    intent: str
    tool: str | None
    arguments: dict[str, Any]
    source: str
    success: bool
    duration_ms: float
    error_code: str | None = None
    response_preview: str = ""


_history: deque[ExecutionRecord] = deque(maxlen=200)


def log_execution(record: ExecutionRecord) -> None:
    _history.appendleft(record)


def recent_executions(limit: int = 30) -> list[dict[str, Any]]:
    return [
        {
            "timestamp": r.timestamp,
            "user_input": r.user_input,
            "intent": r.intent,
            "tool": r.tool,
            "arguments": r.arguments,
            "source": r.source,
            "success": r.success,
            "duration_ms": r.duration_ms,
            "error_code": r.error_code,
            "response_preview": r.response_preview,
        }
        for r in list(_history)[:limit]
    ]


class RequestTimer:
    def __init__(self) -> None:
        self._start = time.perf_counter()

    @property
    def elapsed_ms(self) -> float:
        return (time.perf_counter() - self._start) * 1000
