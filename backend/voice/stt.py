# AI-ASSISTED: Cursor
# PROMPT: Server-side STT placeholder (Whisper/Vosk later)
# ACCEPTED-BY: vignesh

from __future__ import annotations


def transcribe(_audio_bytes: bytes) -> str:
    raise NotImplementedError("Use browser Web Speech API or add Whisper in voice/stt.py.")
