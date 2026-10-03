# AI-ASSISTED: Cursor
# PROMPT: Ollama HTTP client for local Llama reasoning
# ACCEPTED-BY: vignesh

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from config import settings


class OllamaClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = (base_url or settings.ollama_host).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout

    def available(self) -> bool:
        try:
            with httpx.Client(timeout=3.0) as client:
                r = client.get(f"{self.base_url}/api/tags")
                return r.status_code == 200
        except httpx.HTTPError:
            return False

    def chat(self, system: str, user: str, json_mode: bool = False) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if json_mode:
            payload["format"] = "json"
        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(f"{self.base_url}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
        return (data.get("message") or {}).get("content", "").strip()

    @staticmethod
    def parse_json_object(text: str) -> dict[str, Any] | None:
        text = text.strip()
        if not text:
            return None
        try:
            obj = json.loads(text)
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            pass
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return None
        try:
            obj = json.loads(match.group(0))
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            return None
