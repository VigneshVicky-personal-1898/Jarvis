# RAYA

<!-- AI-ASSISTED: Cursor -->
<!-- PROMPT: Link docs/VOICE.md for wake, clap, ElevenLabs -->
<!-- ACCEPTED-BY: vignesh -->

**RAYA** is a voice-controlled personal assistant with a Groq Cloud LLM by default, a **tool router** for safe local actions, a **local RAG index** over your documents (Chroma + Sentence Transformers), optional MCP/QE Engine integration, and a React UI. Prompts and retrieved context are sent to the configured LLM provider. See [docs/RAG.md](docs/RAG.md).

**Advanced spec tracking:** see [docs/JARVIS_SPEC_STATUS.md](docs/JARVIS_SPEC_STATUS.md) (product spec vs this codebase).

**Cloud deployment:** see [docs/CLOUD_DEPLOYMENT.md](docs/CLOUD_DEPLOYMENT.md) for the authenticated, always-on container setup.

## Architecture

```text
Personal Jarvis/   (repo folder name; assistant brand: RAYA)
├── backend/
│   ├── main.py              # FastAPI
│   ├── config.py            # .env settings (RAYA_*; JARVIS_* legacy)
│   ├── engine.py            # YAML command fallback
│   ├── agent/               # Orchestrator → RAG / web / tools
│   ├── tools/               # system, browser, files, apps, QE
│   ├── memory/              # SQLite + session buffer
│   └── rag/                 # Local knowledge index
├── frontend/src/
├── data/knowledge/          # drop docs for RAG
└── tests/
```

Wake words: **hey RAYA**, **raya**, **hey raya da**, **raya da** (speech saying “jarvis” is normalized to “raya” before matching).

**Voice (wake word, clap, ElevenLabs):** see [docs/VOICE.md](docs/VOICE.md).

## Requirements

- Python 3.10+
- Node.js 18+
- A Groq API key and a model enabled for your Groq account
- Chromium-based browser for Web Speech API

## Quick start

```bash
cd /home/vignesh/Personal/Jarvis
cp .env.example .env
# Set GROQ_API_KEY in .env. Change GROQ_MODEL if your account uses another model.

chmod +x run.sh
./run.sh
```

Open **http://127.0.0.1:5173**. Optional emblem: **`frontend/public/assets/raya-logo.jpg`**.

### Manual start

**API**

```bash
cd /home/vignesh/Personal/Jarvis
python3 -m pip install -r requirements.txt
python3 -m uvicorn main:app --host 127.0.0.1 --port 8765 --app-dir backend
```

**UI**

```bash
cd frontend && npm install && npm run dev
```

## Environment (`.env`)

| Variable | Purpose |
|----------|---------|
| `LLM_PROVIDER` | LLM provider (`groq` by default; `ollama` remains optional) |
| `GROQ_API_KEY` | Backend-only Groq API key; keep it out of frontend code |
| `GROQ_BASE_URL` | Groq OpenAI-compatible API base URL |
| `GROQ_MODEL` | Model ID enabled for your Groq account |
| `RAYA_AGENT_ENABLED` | Use the configured LLM when available (`JARVIS_*` still read as fallback) |
| `RAYA_RAG_ENABLED` | Local knowledge RAG |
| `QE_ENGINE_URL` | HTTP base for QE Engine |
| `RAYA_MCP_ENABLED` / `RAYA_MCP_URL` | MCP tool server |

## Customize YAML commands

Edit `backend/config/commands.yaml`, then:

```bash
curl -X POST http://127.0.0.1:8765/api/reload
```

## Tests

```bash
cd backend && PYTHONPATH=. python3 -m pytest ../tests -q
```

## Logo

Add **`frontend/public/assets/raya-logo.jpg`** for the header and orb emblem, then refresh the dev server.
