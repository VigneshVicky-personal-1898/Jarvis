# AI-ASSISTED: Cursor
# PROMPT: RAYA wake words for voice pipeline
# ACCEPTED-BY: vignesh

from __future__ import annotations

DEFAULT_WAKE_WORDS = ("hey raya", "raya", "hey raya da", "raya da")


def normalize_wake_words(words: list[str] | None = None) -> tuple[str, ...]:
    src = words or list(DEFAULT_WAKE_WORDS)
    return tuple(w.strip().lower() for w in src if w.strip())
