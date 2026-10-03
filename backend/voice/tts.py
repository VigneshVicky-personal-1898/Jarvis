# AI-ASSISTED: Cursor
# PROMPT: TTS router — ElevenLabs or not configured
# ACCEPTED-BY: vignesh

from __future__ import annotations

from voice import elevenlabs


def tts_available() -> bool:
    if settings_provider() == "elevenlabs":
        return elevenlabs.configured()
    return False


def settings_provider() -> str:
    from config import settings

    return settings.tts_provider.strip().lower()


def synthesize(text: str, *, language: str = "en") -> bytes:
    provider = settings_provider()
    if provider == "elevenlabs":
        return elevenlabs.synthesize_speech(text, language=language)
    raise NotImplementedError(
        "Set RAYA_TTS_PROVIDER=elevenlabs and ElevenLabs keys in .env",
    )
