# RAYA voice activation and response

<!-- AI-ASSISTED: Cursor -->
<!-- PROMPT: Wake word, clap, ElevenLabs TTS, and UI animation states -->
<!-- ACCEPTED-BY: vignesh -->

## Flow

```text
Idle → (wake “Raya” or clap) → Activated → Listening → command
  → Processing / Executing → ElevenLabs (or browser) speak → Idle
```

## Wake word

- Enable **Wake word mode** in the header (on by default).
- With wake mode on, the mic stays on in the background (Chrome/Edge Web Speech API).
- Say **“Raya”** or **“hey Raya”** — RAYA activates, listens for your command, then processes it.
- Wake phrases come from `backend/config/commands.yaml` (`wake_words`).

## Clap activation

- Enable **Clap activation** (requires wake word mode).
- A clap triggers the same **Activated → Listening** path as the wake word.
- Clap uses a lightweight Web Audio detector; if the mic is already in use, clap may be unavailable on some systems.

## ElevenLabs voice

Set in `.env`:

```env
RAYA_TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=your_key
ELEVENLABS_VOICE_ID=your_voice_id
```

Restart the API. The UI shows **ElevenLabs voice** in the header when `/api/health` reports `tts_available: true`.

Audio is synthesized at `POST /api/tts` (API key stays on the server). If ElevenLabs fails, the UI falls back to browser speech.

## UI animation phases

The orb reflects: **idle**, **activated**, **listening**, **thinking**, **executing**, **speaking** (see `frontend/src/voice/rayaVoicePhase.ts`).

## Manual mic

The header **mic icon** still toggles listening when wake mode is off or for manual control.
