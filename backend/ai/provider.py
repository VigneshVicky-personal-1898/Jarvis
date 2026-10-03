# AI-ASSISTED: Cursor
# PROMPT: Pluggable AI providers (Groq default, Ollama optional)
# ACCEPTED-BY: vignesh

from __future__ import annotations

import json
import re
from typing import Any, Protocol

from brain.ollama import OllamaClient
from brain.groq import GroqClient
from config import settings


class AIProvider(Protocol):
    def available(self) -> bool: ...

    def chat(self, system: str, user: str, json_mode: bool = False) -> str: ...

    def parse_json(self, text: str) -> dict[str, Any] | None: ...


class OllamaProvider:
    def __init__(self, client: OllamaClient | None = None) -> None:
        self._client = client or OllamaClient()

    def available(self) -> bool:
        return self._client.available()

    def chat(self, system: str, user: str, json_mode: bool = False) -> str:
        return self._client.chat(system, user, json_mode=json_mode)

    def parse_json(self, text: str) -> dict[str, Any] | None:
        return parse_json_object(text)


class GroqProvider:
    def __init__(self, client: GroqClient | None = None) -> None:
        self._client = client or GroqClient()

    def available(self) -> bool:
        return self._client.available()

    def chat(self, system: str, user: str, json_mode: bool = False) -> str:
        return self._client.chat(system, user, json_mode=json_mode)

    def parse_json(self, text: str) -> dict[str, Any] | None:
        return parse_json_object(text)


def parse_json_object(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return None
        try:
            obj = json.loads(match.group(0))
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            return None


def get_ai_provider() -> AIProvider:
    if settings.llm_provider == "groq":
        return GroqProvider()
    if settings.llm_provider == "ollama":
        return OllamaProvider()
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
