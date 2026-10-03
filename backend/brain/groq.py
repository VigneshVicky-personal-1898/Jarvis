from __future__ import annotations

import time
from typing import Any

import httpx

from config import settings


class GroqAPIError(RuntimeError):
    pass


class GroqClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = (base_url or settings.groq_base_url).rstrip("/")
        self.model = model or settings.groq_model
        self.api_key = settings.groq_api_key if api_key is None else api_key
        self.timeout = timeout
        self._availability_checked_at = 0.0
        self._availability_cache = False

    def available(self) -> bool:
        if not self.api_key.strip():
            return False
        now = time.monotonic()
        if now - self._availability_checked_at < 15:
            return self._availability_cache
        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
            self._availability_cache = response.status_code == 200
        except httpx.HTTPError:
            self._availability_cache = False
        self._availability_checked_at = now
        return self._availability_cache

    def chat(self, system: str, user: str, json_mode: bool = False) -> str:
        if not self.api_key.strip():
            raise GroqAPIError("GROQ_API_KEY is not configured.")
        payload: dict[str, Any] = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status == 401 or status == 403:
                message = "Groq authentication failed. Check GROQ_API_KEY and account access."
            elif status == 404:
                message = "Groq model or endpoint was not found. Check GROQ_MODEL and GROQ_BASE_URL."
            elif status == 429:
                retry_after = exc.response.headers.get("retry-after")
                message = "Groq rate limit reached. Check your model limits and try again."
                if retry_after:
                    message += f" Retry after {retry_after} seconds."
            elif status >= 500:
                message = "Groq is temporarily unavailable. Try again later."
            else:
                message = f"Groq returned HTTP {status}."
            raise GroqAPIError(message) from exc
        except httpx.TimeoutException as exc:
            raise GroqAPIError("The Groq request timed out.") from exc
        except httpx.RequestError as exc:
            raise GroqAPIError("Could not connect to Groq. Check your internet connection.") from exc

        choices = response.json().get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        return str(message.get("content") or "").strip()