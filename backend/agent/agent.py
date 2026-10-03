# AI-ASSISTED: Cursor
# PROMPT: RayaAgent facade over CommandPipeline
# ACCEPTED-BY: vignesh

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent.pipeline import CommandPipeline, PipelineResult
from ai.provider import get_ai_provider
from engine import CommandEngine
from memory.short_term import ShortTermMemory
from tools.registry import ToolRegistry


@dataclass
class AgentResult:
    ok: bool
    speak: str
    command_id: str | None
    action: str | None
    confidence: float
    data: dict[str, Any]
    unmatched: bool
    source: str
    ui_state: str = "IDLE"
    intent: str = "UNKNOWN"


class RayaAgent:
    def __init__(
        self,
        engine: CommandEngine,
        registry: ToolRegistry,
        memory: ShortTermMemory | None = None,
    ) -> None:
        self.engine = engine
        self.registry = registry
        self.memory = memory or ShortTermMemory()
        self.provider = get_ai_provider()
        self.pipeline = CommandPipeline(engine, registry, self.provider, self.memory)

    @property
    def brain(self):
        return self.provider

    def process(self, text: str, *, language: str = "en") -> AgentResult:
        result = self.pipeline.process(text, language=language)
        return _to_agent_result(result)


def _to_agent_result(r: PipelineResult) -> AgentResult:
    return AgentResult(
        ok=r.ok,
        speak=r.speak,
        command_id=r.command_id,
        action=r.action,
        confidence=r.confidence,
        data=r.data,
        unmatched=r.unmatched,
        source=r.source,
        ui_state=r.ui_state,
        intent=r.intent,
    )
