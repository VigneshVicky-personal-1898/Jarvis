# AI-ASSISTED: Cursor
# PROMPT: Session memory with context block for LLM chat
# ACCEPTED-BY: vignesh

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass
class Turn:
    user: str
    tool: str
    response: str


class ShortTermMemory:
    def __init__(self, max_turns: int = 20) -> None:
        self._turns: deque[Turn] = deque(maxlen=max_turns)

    def add(self, user: str, tool: str, response: str) -> None:
        self._turns.append(Turn(user=user, tool=tool, response=response))

    def recent(self, limit: int = 5) -> list[Turn]:
        return list(self._turns)[-limit:]

    def context_block(self, limit: int = 5) -> str:
        lines: list[str] = []
        for turn in self.recent(limit):
            lines.append(f"User: {turn.user}")
            if turn.response:
                lines.append(f"RAYA: {turn.response[:400]}")
        return "\n".join(lines)
