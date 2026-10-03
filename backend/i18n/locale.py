# AI-ASSISTED: Cursor
# PROMPT: Request language context and Tamil localization for spoken replies
# ACCEPTED-BY: vignesh

from __future__ import annotations

from contextvars import ContextVar

from ai.provider import AIProvider

current_language: ContextVar[str] = ContextVar("raya_language", default="en")


def normalize_language(raw: str | None) -> str:
    if not raw:
        return "en"
    key = raw.strip().lower()
    if key.startswith("ta") or key in ("tamil", "தமிழ்"):
        return "ta"
    return "en"


def localize_speak(text: str, language: str, provider: AIProvider | None) -> str:
    if not text or language != "ta":
        return text
    if provider is None or not provider.available():
        return text
    try:
        translated = provider.chat(
            (
                "You translate assistant voice lines into natural spoken Tamil. "
                "Keep numbers, IDs (like TPX-22), and product names unchanged. "
                "Output Tamil text only, no quotes."
            ),
            text,
            json_mode=False,
        )
        return translated.strip() or text
    except Exception:
        return text
