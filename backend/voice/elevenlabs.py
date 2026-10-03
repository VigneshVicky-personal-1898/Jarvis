# AI-ASSISTED: Cursor
# PROMPT: ElevenLabs TTS synthesis for RAYA voice responses
# ACCEPTED-BY: vignesh

from __future__ import annotations

import httpx

from config import settings


def configured() -> bool:
    return bool(settings.elevenlabs_api_key.strip() and settings.elevenlabs_voice_id.strip())


def synthesize_speech(text: str, *, language: str = "en") -> bytes:
    if not configured():
        raise RuntimeError("ElevenLabs is not configured")
    _ = language
    body = {
        "text": text.strip(),
        "model_id": settings.elevenlabs_model,
        "voice_settings": {
            "stability": settings.elevenlabs_stability,
            "similarity_boost": settings.elevenlabs_similarity,
        },
    }
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}"
    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(url, json=body, headers=headers)
        resp.raise_for_status()
        return resp.content
