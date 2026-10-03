# AI-ASSISTED: Cursor
# PROMPT: Normalize legacy jarvis token to raya before YAML match
# ACCEPTED-BY: vignesh

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from i18n.thanglish import expand_tamil_and_thanglish


@dataclass
class MatchResult:
    command_id: str
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    response: str | None = None
    confidence: float = 1.0
    raw_trigger: str = ""


_EXEC_ID = re.compile(r"\b(tpx|rtp|rex)-[\w-]+\b", re.IGNORECASE)


def _keyword_action(norm: str) -> tuple[str, str, dict[str, Any]] | None:
    """Fast-path intents when YAML triggers miss phrasing (STT variants)."""
    exec_match = _EXEC_ID.search(norm)
    if exec_match and (
        "result" in norm
        or "execution" in norm
        or "show" in norm
        or "kaatu" in norm
        or "mudivu" in norm
        or "tpx" in norm
    ):
        eid = exec_match.group(0).upper()
        return (
            "qe_execution",
            "qe_execution_result",
            {"execution_id": eid},
        )

    has_qe = (
        "qe" in norm
        or "workflow360" in norm
        or "workflow 360" in norm
        or "queue engine" in norm
    )
    test_plan = "test plan" in norm or "testplan" in norm
    show_word = "show" in norm or "kaatu" in norm or "kattu" in norm
    wants_results = (
        "latest" in norm or "recent" in norm or "last" in norm or "samipa" in norm
    ) and (
        "result" in norm
        or "results" in norm
        or "run" in norm
        or "execution" in norm
        or "mudivu" in norm
    )
    if show_word and ("result" in norm or "results" in norm or "mudivu" in norm):
        wants_results = True
    if (wants_results or test_plan) and (has_qe or "engine" in norm or test_plan):
        return ("latest_results", "qe_latest_results", {})
    if wants_results:
        return ("latest_results", "qe_latest_results", {})
    if has_qe and ("status" in norm or "online" in norm or "health" in norm):
        return ("qe_status", "qe_projects_status", {})
    if "analyze" in norm and ("project" in norm or "codebase" in norm or "repo" in norm):
        project = "raya"
        for key in ("qe", "workflow", "mcp", "proactive", "raya"):
            if key in norm:
                project = {
                    "qe": "proactive_automation",
                    "workflow": "proactive_automation",
                    "mcp": "mcp_automation",
                    "proactive": "proactive_automation",
                    "raya": "raya",
                }.get(key, project)
        return ("analyze_project", "analyze_project", {"project": project})
    return None


_SPEECH_TYPOS: dict[str, str] = {
    "laest": "latest",
    "latset": "latest",
    "lates": "latest",
    "resutls": "results",
    "resuls": "results",
}


def _normalize(text: str) -> str:
    t = expand_tamil_and_thanglish(text)
    t = t.lower().strip()
    t = re.sub(r"\bjarvis\b", "raya", t)
    t = re.sub(r"[^\w\s\.\-:/]", " ", t, flags=re.UNICODE)
    t = re.sub(r"\s+", " ", t)
    for wrong, right in _SPEECH_TYPOS.items():
        t = re.sub(rf"\b{re.escape(wrong)}\b", right, t)
    return t


def _trigger_to_pattern(trigger: str) -> re.Pattern[str]:
    parts: list[str] = []
    for token in trigger.split():
        if token.startswith("{") and token.endswith("}"):
            name = token[1:-1]
            parts.append(f"(?P<{name}>.+)")
        else:
            parts.append(re.escape(token))
    pattern = r"^\s*" + r"\s+".join(parts) + r"\s*$"
    return re.compile(pattern, re.IGNORECASE)


@dataclass
class CompiledCommand:
    command_id: str
    action: str
    params: dict[str, Any]
    response: str | None
    patterns: list[tuple[str, re.Pattern[str]]]


class CommandEngine:
    def __init__(self, config_path: Path | None = None) -> None:
        base = Path(__file__).resolve().parent
        self.config_path = config_path or base / "config" / "commands.yaml"
        self.wake_words: list[str] = []
        self.commands: list[CompiledCommand] = []
        self.reload()

    def reload(self) -> None:
        with open(self.config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.wake_words = [_normalize(w) for w in data.get("wake_words", [])]
        self.commands = []
        for cmd in data.get("commands", []):
            patterns: list[tuple[str, re.Pattern[str]]] = []
            for trigger in cmd.get("triggers", []):
                patterns.append((trigger, _trigger_to_pattern(trigger)))
            self.commands.append(
                CompiledCommand(
                    command_id=cmd["id"],
                    action=cmd.get("action", "none"),
                    params=dict(cmd.get("params") or {}),
                    response=cmd.get("response"),
                    patterns=patterns,
                )
            )

    def contains_wake_word(self, text: str) -> bool:
        norm = _normalize(text)
        return any(w in norm for w in self.wake_words)

    def strip_wake_word(self, text: str) -> str:
        norm = _normalize(text)
        for w in self.wake_words:
            norm = norm.replace(w, " ").strip()
        return re.sub(r"\s+", " ", norm).strip()

    def normalize_for_command(self, text: str) -> tuple[str, str | None]:
        """Strip wake words; return immediate reply if the utterance was wake-only."""
        utterance = text.strip()
        if not self.contains_wake_word(utterance):
            return utterance, None
        stripped = self.strip_wake_word(utterance)
        if stripped:
            return stripped, None
        return utterance, "Yes? How can I help?"

    def match(self, text: str) -> MatchResult | None:
        norm = _normalize(text)
        if not norm:
            return None

        for cmd in self.commands:
            for raw_trigger, pattern in cmd.patterns:
                m = pattern.match(norm)
                if m:
                    slots = {k: v.strip() for k, v in m.groupdict().items()}
                    params = {**cmd.params, **slots}
                    return MatchResult(
                        command_id=cmd.command_id,
                        action=cmd.action,
                        params=params,
                        response=cmd.response,
                        raw_trigger=raw_trigger,
                    )

        keyword = _keyword_action(norm)
        if keyword:
            command_id, action, params = keyword
            return MatchResult(
                command_id=command_id,
                action=action,
                params=dict(params),
                response=None,
                raw_trigger="keyword",
                confidence=0.82,
            )

        for cmd in self.commands:
            for raw_trigger, _ in cmd.patterns:
                if "{" in raw_trigger:
                    continue
                trigger_norm = _normalize(raw_trigger)
                if trigger_norm and trigger_norm in norm:
                    return MatchResult(
                        command_id=cmd.command_id,
                        action=cmd.action,
                        params=dict(cmd.params),
                        response=cmd.response,
                        raw_trigger=raw_trigger,
                        confidence=0.85,
                    )
        return None

    def list_command_summaries(self) -> list[dict[str, str]]:
        out: list[dict[str, str]] = []
        for cmd in self.commands:
            triggers = [t for t, _ in cmd.patterns if "{" not in t][:3]
            out.append(
                {
                    "id": cmd.command_id,
                    "action": cmd.action,
                    "examples": ", ".join(triggers) if triggers else cmd.command_id,
                }
            )
        return out
