# AI-ASSISTED: Cursor
# PROMPT: Orchestrate RAG, web fetch, and chat via route planner
# ACCEPTED-BY: vignesh

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent.chat_brain import ChatBrain
from agent.orchestrator import InformationRoute, RoutePlan, plan_information_route
from agent.confirmation import (
    clear_active,
    consume,
    get_active,
    is_affirmative,
    is_negative,
)
from agent.intent_schema import (
    ACTION_TO_INTENT,
    IntentCategory,
    StructuredIntent,
    normalize_tool_name,
)
from agent.structured_intent import StructuredIntentDetector
from ai.provider import AIProvider, get_ai_provider
from config import settings
from i18n.locale import current_language, localize_speak, normalize_language
from rag.service import get_rag
from search.internet import fetch_web_results, format_web_context
from engine import CommandEngine, MatchResult
from memory.short_term import ShortTermMemory
from observability import ExecutionRecord, RequestTimer, log_execution
from time import time as unix_time
from tools.registry import ToolRegistry


@dataclass
class PipelineResult:
    ok: bool
    speak: str
    command_id: str | None
    action: str | None
    confidence: float
    data: dict[str, Any]
    unmatched: bool
    source: str
    ui_state: str
    intent: str


class CommandPipeline:
    def __init__(
        self,
        engine: CommandEngine,
        registry: ToolRegistry,
        provider: AIProvider | None = None,
        memory: ShortTermMemory | None = None,
    ) -> None:
        self.engine = engine
        self.registry = registry
        self.provider = provider or get_ai_provider()
        self.memory = memory or ShortTermMemory()
        self.detector = StructuredIntentDetector(self.provider, registry)
        self.chat_brain = ChatBrain(self.provider, self.memory)  # type: ignore[arg-type]

    def process(self, text: str, *, language: str = "en") -> PipelineResult:
        lang = normalize_language(language)
        lang_token = current_language.set(lang)
        timer = RequestTimer()
        utterance = text.strip()
        try:
            return self._process_inner(utterance, timer, lang)
        finally:
            current_language.reset(lang_token)

    def _process_inner(
        self,
        utterance: str,
        timer: RequestTimer,
        lang: str,
    ) -> PipelineResult:

        pending = get_active()
        if pending:
            if is_affirmative(utterance):
                confirmed = consume(pending.id, True)
                if confirmed:
                    return self._execute_tool(
                        confirmed.tool,
                        confirmed.arguments,
                        utterance,
                        IntentCategory.UNKNOWN,
                        "confirmation",
                        timer,
                        confirmed=True,
                        ui_state="EXECUTING",
                    )
            if is_negative(utterance):
                clear_active()
                return self._finish(
                    ok=True,
                    speak="Cancelled.",
                    command_id="cancel",
                    action=None,
                    confidence=1.0,
                    data={"cancelled": True},
                    unmatched=False,
                    source="confirmation",
                    ui_state="IDLE",
                    intent="CANCEL",
                    utterance=utterance,
                    timer=timer,
                )

        normalized, wake_reply = self.engine.normalize_for_command(utterance)
        if wake_reply:
            return self._finish(
                ok=True,
                speak=wake_reply,
                command_id="wake_ack",
                action="none",
                confidence=1.0,
                data={"wake_only": True},
                unmatched=False,
                source="wake",
                ui_state="LISTENING",
                intent=IntentCategory.CONVERSATION.value,
                utterance=utterance,
                timer=timer,
            )

        match = self.engine.match(normalized)
        if match:
            return self._from_rule_match(match, normalized, timer)

        if settings.agent_enabled and self.provider.available():
            try:
                structured = self.detector.detect(normalized)
            except Exception as e:
                return self._finish(
                    ok=False,
                    speak=f"The language model request failed: {e}",
                    command_id=None,
                    action=None,
                    confidence=0.0,
                    data={"input": normalized, "llm_provider": settings.llm_provider},
                    unmatched=True,
                    source="llm",
                    ui_state="ERROR",
                    intent=IntentCategory.UNKNOWN.value,
                    utterance=normalized,
                    timer=timer,
                )
            if structured and structured.tool and structured.intent not in (
                IntentCategory.GENERAL_QUESTION,
                IntentCategory.CONVERSATION,
                IntentCategory.UNKNOWN,
            ):
                tool = normalize_tool_name(structured.tool)
                if tool and self.registry.get(tool or ""):
                    return self._execute_tool(
                        tool or "",
                        structured.arguments,
                        normalized,
                        structured.intent,
                        "ai",
                        timer,
                        confirmed=False,
                        ui_state="EXECUTING",
                        extra={"structured_intent": structured.model_dump()},
                    )
            if structured and structured.intent == IntentCategory.GENERAL_QUESTION:
                return self._knowledge_response(normalized, structured, timer, lang)
            if structured and structured.intent in (
                IntentCategory.SEARCH_WEB,
            ) and not structured.tool:
                return self._knowledge_response(
                    normalized,
                    structured,
                    timer,
                    lang,
                    force_web=True,
                )

            plan_tool = structured.tool if structured else None
            if plan_tool and plan_tool != "none":
                return self._execute_tool(
                    plan_tool,
                    structured.arguments if structured else {},
                    normalized,
                    structured.intent if structured else IntentCategory.UNKNOWN,
                    "ai",
                    timer,
                    ui_state="EXECUTING",
                )
            return self._knowledge_response(normalized, structured, timer, lang)

        plan = plan_information_route(normalized)
        if plan.route != InformationRoute.CHAT or settings.rag_enabled:
            if self.provider.available():
                return self._knowledge_response(normalized, None, timer, lang)
            return self._knowledge_offline(normalized, plan, timer)

        return self._unknown(normalized, timer)

    def _from_rule_match(
        self,
        match: MatchResult,
        utterance: str,
        timer: RequestTimer,
    ) -> PipelineResult:
        intent = ACTION_TO_INTENT.get(match.action, IntentCategory.UNKNOWN)
        if match.action == "none":
            return self._finish(
                ok=True,
                speak=match.response or "Done.",
                command_id=match.command_id,
                action=match.action,
                confidence=match.confidence,
                data={},
                unmatched=False,
                source="rules",
                ui_state="SPEAKING",
                intent=intent.value,
                utterance=utterance,
                timer=timer,
            )
        return self._execute_tool(
            match.action,
            dict(match.params),
            utterance,
            intent,
            "rules",
            timer,
            command_id=match.command_id,
            confidence=match.confidence,
            ui_state="EXECUTING",
        )

    def _execute_tool(
        self,
        tool: str,
        arguments: dict[str, Any],
        utterance: str,
        intent: IntentCategory,
        source: str,
        timer: RequestTimer,
        *,
        confirmed: bool = False,
        command_id: str | None = None,
        confidence: float = 0.95,
        ui_state: str = "EXECUTING",
        extra: dict[str, Any] | None = None,
    ) -> PipelineResult:
        params = dict(arguments)
        if tool == "sleep" and "message" not in params:
            params.setdefault("message", "Going to sleep.")
        if tool == "qe_agent_command" and not (
            params.get("command") or params.get("message") or params.get("query")
        ):
            params["command"] = utterance
        if tool == "qe_execution_result" and not params.get("execution_id"):
            from tools.qe_engine import _EXEC_ID

            found = _EXEC_ID.search(utterance)
            if found:
                params["execution_id"] = found.group(0).upper()
        result = self.registry.execute(tool, params, confirmed=confirmed)
        data = {**(result.get("data") or {}), **(extra or {})}
        if data.get("requires_confirmation"):
            return self._finish(
                ok=True,
                speak=result.get("speak", ""),
                command_id=tool,
                action=tool,
                confidence=confidence,
                data=data,
                unmatched=False,
                source=source,
                ui_state="WAITING_CONFIRMATION",
                intent=intent.value,
                utterance=utterance,
                timer=timer,
            )
        self.memory.add(utterance, tool, result.get("speak", ""))
        return self._finish(
            ok=result.get("ok", True),
            speak=result.get("speak", ""),
            command_id=command_id or tool,
            action=tool,
            confidence=confidence,
            data=data,
            unmatched=False,
            source=source,
            ui_state="SPEAKING" if result.get("speak") else "IDLE",
            intent=intent.value,
            utterance=utterance,
            timer=timer,
            tool=tool,
            args=arguments,
        )

    def _knowledge_response(
        self,
        utterance: str,
        structured: StructuredIntent | None,
        timer: RequestTimer,
        lang: str,
        *,
        force_web: bool = False,
    ) -> PipelineResult:
        plan = plan_information_route(utterance, force_web=force_web)
        rag_context = ""
        chunks: list[dict[str, Any]] = []
        web_results: list[dict[str, str]] = []
        web_context = ""

        if plan.use_rag:
            rag_context, chunks = get_rag().retrieve_context(utterance)
        if plan.use_web:
            web_results = fetch_web_results(
                utterance,
                max_results=settings.web_search_max_results,
            )
            web_context = format_web_context(web_results)

        intent = (
            IntentCategory.SEARCH_WEB.value
            if plan.route in (InformationRoute.WEB, InformationRoute.RAG_AND_WEB)
            else IntentCategory.GENERAL_QUESTION.value
        )
        source = plan.route.value

        if not self.provider.available():
            return self._knowledge_offline(utterance, plan, timer)

        try:
            reply = self.chat_brain.answer(
                utterance,
                language=lang,
                use_rag=plan.use_rag,
                use_web=plan.use_web,
                rag_context=rag_context,
                web_context=web_context,
            )
        except Exception as e:
            return self._finish(
                ok=False,
                speak=f"I could not reach the language model: {e}",
                command_id=None,
                action=None,
                confidence=0.0,
                data={"input": utterance, "route": source},
                unmatched=True,
                source=source,
                ui_state="ERROR",
                intent=intent,
                utterance=utterance,
                timer=timer,
            )
        self.memory.add(utterance, source, reply)
        return self._finish(
            ok=True,
            speak=reply,
            command_id="chat",
            action="chat",
            confidence=structured.confidence if structured else 0.85,
            data={
                "agent": {"intent": "chat"},
                "route": source,
                "route_reason": plan.reason,
                "rag_chunks": len(chunks),
                "web_sources": [
                    {"title": r.get("title", ""), "url": r.get("url", "")}
                    for r in web_results
                ],
            },
            unmatched=False,
            source=source,
            ui_state="SPEAKING",
            intent=intent,
            utterance=utterance,
            timer=timer,
        )

    def _knowledge_offline(
        self,
        utterance: str,
        plan: RoutePlan,
        timer: RequestTimer,
    ) -> PipelineResult:
        rag_context, chunks = "", []
        web_results: list[dict[str, str]] = []
        if plan.use_rag:
            _, chunks = get_rag().retrieve_context(utterance)
        if plan.use_web:
            web_results = fetch_web_results(
                utterance,
                max_results=settings.web_search_max_results,
            )

        parts: list[str] = []
        if chunks:
            preview = str(chunks[0].get("text", ""))[:400]
            meta = chunks[0].get("metadata") or {}
            parts.append(
                f"From your files ({meta.get('file_name', 'document')}): {preview}",
            )
        if web_results:
            for row in web_results[:2]:
                parts.append(
                    f"{row.get('title', 'Web')}: {row.get('snippet', '')[:200]} "
                    f"Source {row.get('url', '')}",
                )
        if parts:
            speak = (
                "The configured language model is unavailable, so here is what I found locally. "
                + " ".join(parts)
            )
        else:
            speak = (
                "I did not recognize that command, and the configured language model is unavailable. "
                "Check the provider configuration, or try help or qe engine status."
            )
        return self._finish(
            ok=True,
            speak=speak,
            command_id=None,
            action=None,
            confidence=0.5,
            data={
                "route": plan.route.value,
                "rag_chunks": len(chunks),
                "web_sources": web_results,
                "llm_available": False,
            },
            unmatched=not parts,
            source=plan.route.value,
            ui_state="OFFLINE",
            intent="GENERAL_QUESTION",
            utterance=utterance,
            timer=timer,
        )

    def _unknown(self, utterance: str, timer: RequestTimer) -> PipelineResult:
        caps = self.registry.capability_summary()
        speak = (
            "I'm not sure what you want me to do. You can ask me to: "
            + "; ".join(caps[:6])
            + ". Or say help for more."
        )
        llm_available = self.provider.available()
        if not llm_available:
            speak = (
                "I did not recognize that command, and the configured language model is unavailable. "
                "Without it, try: help, "
                "latest results, qe engine status, or open chrome."
            )
        return self._finish(
            ok=True,
            speak=speak,
            command_id=None,
            action=None,
            confidence=0.0,
            data={"input": utterance, "llm_available": llm_available},
            unmatched=True,
            source="rules",
            ui_state="ERROR" if not llm_available else "IDLE",
            intent=IntentCategory.UNKNOWN.value,
            utterance=utterance,
            timer=timer,
        )

    def _finish(
        self,
        *,
        ok: bool,
        speak: str,
        command_id: str | None,
        action: str | None,
        confidence: float,
        data: dict[str, Any],
        unmatched: bool,
        source: str,
        ui_state: str,
        intent: str,
        utterance: str,
        timer: RequestTimer,
        tool: str | None = None,
        args: dict[str, Any] | None = None,
    ) -> PipelineResult:
        exec_meta = {
            "intent": intent,
            "ui_state": ui_state,
            "source": source,
            "duration_ms": round(timer.elapsed_ms, 2),
        }
        if settings.debug_mode:
            exec_meta["debug"] = {
                "tool": tool,
                "arguments": args or {},
                "confidence": confidence,
            }
        merged = {**data, "execution": exec_meta, "language": current_language.get()}
        speak_out = localize_speak(speak, current_language.get(), self.provider)
        log_execution(
            ExecutionRecord(
                timestamp=unix_time(),
                user_input=utterance,
                intent=intent,
                tool=tool or action,
                arguments=args or {},
                source=source,
                success=ok,
                duration_ms=timer.elapsed_ms,
                response_preview=(speak_out or "")[:120],
            ),
        )
        return PipelineResult(
            ok=ok,
            speak=speak_out,
            command_id=command_id,
            action=action,
            confidence=confidence,
            data=merged,
            unmatched=unmatched,
            source=source,
            ui_state=ui_state,
            intent=intent,
        )
