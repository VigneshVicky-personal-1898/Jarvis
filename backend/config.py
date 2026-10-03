# AI-ASSISTED: Cursor
# PROMPT: ElevenLabs TTS env and RAYA_TTS_PROVIDER
# ACCEPTED-BY: vignesh

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
RAG_DIR = DATA_DIR / "rag"
CHROMA_DIR = RAG_DIR / "chroma"
MEMORY_DB = DATA_DIR / "memory.db"


def _load_dotenv_file(path: Path, *, override: bool) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        if override or key not in os.environ:
            os.environ[key] = value


def _load_dotenv() -> None:
    # Process environment wins, followed by `.env` and then example defaults.
    _load_dotenv_file(ROOT / ".env", override=False)
    _load_dotenv_file(ROOT / ".env.example", override=False)


def _normalize_qe_engine_url(raw: str) -> str:
    url = raw.strip().rstrip("/")
    if not url:
        return url
    for suffix in (
        "/qe_engine/login",
        "/qe_engine",
        "/login",
    ):
        if url.lower().endswith(suffix):
            url = url[: -len(suffix)].rstrip("/")
    return url


_load_dotenv()


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _env_bool_legacy(raya_key: str, legacy_key: str, default: bool) -> bool:
    if os.getenv(raya_key) is not None:
        return _env_bool(raya_key, default)
    return _env_bool(legacy_key, default)


def _env_str(raya_key: str, legacy_key: str, default: str) -> str:
    val = os.getenv(raya_key)
    if val is not None and val.strip() != "":
        return val
    legacy = os.getenv(legacy_key)
    if legacy is not None and legacy.strip() != "":
        return legacy
    return default


@dataclass(frozen=True)
class Settings:
    cloud_mode: bool = _env_bool("RAYA_CLOUD_MODE", False)
    auth_enabled: bool = _env_bool("RAYA_AUTH_ENABLED", False)
    access_password: str = os.getenv("RAYA_ACCESS_PASSWORD", "")
    session_secret: str = os.getenv("RAYA_SESSION_SECRET", "")
    session_max_age: int = int(os.getenv("RAYA_SESSION_MAX_AGE", "604800"))
    llm_provider: str = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_base_url: str = os.getenv(
        "GROQ_BASE_URL",
        "https://api.groq.com/openai/v1",
    )
    groq_model: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    agent_enabled: bool = _env_bool_legacy("RAYA_AGENT_ENABLED", "JARVIS_AGENT_ENABLED", True)
    mcp_enabled: bool = _env_bool_legacy("RAYA_MCP_ENABLED", "JARVIS_MCP_ENABLED", False)
    mcp_server_url: str = _env_str("RAYA_MCP_URL", "JARVIS_MCP_URL", "")
    qe_engine_url: str = _normalize_qe_engine_url(
        os.getenv("QE_ENGINE_URL", "http://127.0.0.1:8888"),
    )
    qe_engine_username: str = os.getenv("QE_ENGINE_USERNAME", "")
    qe_engine_password: str = os.getenv("QE_ENGINE_PASSWORD", "")
    qe_engine_project: str = os.getenv("QE_ENGINE_PROJECT_NAME", "")
    qe_engine_token: str = os.getenv("QE_ENGINE_TOKEN", "")
    qe_mcp_proxy_url: str = os.getenv("QE_MCP_PROXY_URL", "http://127.0.0.1:3100/mcp")
    qe_ui_url: str = os.getenv("QE_ENGINE_UI_URL", "http://127.0.0.1:3000")
    qe_mcp_automation_dir: str = os.getenv(
        "QE_MCP_AUTOMATION_DIR",
        "/data/QE_Engine/QE_Engine/mcp_automation",
    )
    qe_proactive_dir: str = os.getenv(
        "QE_PROACTIVE_DIR",
        "/data/QE_Engine/QE_Engine/ProactiveAutomation",
    )
    qe_ui_dir: str = os.getenv(
        "QE_ENGINE_UI_DIR",
        "/data/QE_Engine/QE_Engine/qe_engine_ui",
    )
    memory_enabled: bool = _env_bool_legacy("RAYA_MEMORY_ENABLED", "JARVIS_MEMORY_ENABLED", True)
    rag_enabled: bool = _env_bool_legacy("RAYA_RAG_ENABLED", "JARVIS_RAG_ENABLED", False)
    rag_embed_model: str = _env_str(
        "RAYA_RAG_EMBED_MODEL",
        "JARVIS_RAG_EMBED_MODEL",
        "all-MiniLM-L6-v2",
    )
    rag_chunk_size: int = int(_env_str("RAYA_RAG_CHUNK_SIZE", "JARVIS_RAG_CHUNK_SIZE", "800"))
    rag_chunk_overlap: int = int(
        _env_str("RAYA_RAG_CHUNK_OVERLAP", "JARVIS_RAG_CHUNK_OVERLAP", "120"),
    )
    rag_top_k: int = int(_env_str("RAYA_RAG_TOP_K", "JARVIS_RAG_TOP_K", "5"))
    rag_min_score: float = float(_env_str("RAYA_RAG_MIN_SCORE", "JARVIS_RAG_MIN_SCORE", "0.25"))
    rag_extra_paths: str = _env_str("RAYA_RAG_EXTRA_PATHS", "JARVIS_RAG_EXTRA_PATHS", "")
    web_search_mode: str = _env_str(
        "RAYA_WEB_SEARCH_MODE",
        "JARVIS_WEB_SEARCH_MODE",
        "fetch",
    ).strip().lower()
    web_search_max_results: int = int(
        _env_str("RAYA_WEB_SEARCH_MAX_RESULTS", "JARVIS_WEB_SEARCH_MAX_RESULTS", "3"),
    )
    google_search_api_key: str = _env_str(
        "RAYA_GOOGLE_API_KEY",
        "JARVIS_GOOGLE_API_KEY",
        "",
    )
    google_search_cse_id: str = _env_str(
        "RAYA_GOOGLE_CSE_ID",
        "JARVIS_GOOGLE_CSE_ID",
        "",
    )
    debug_mode: bool = _env_bool_legacy("RAYA_DEBUG", "JARVIS_DEBUG", False)
    tts_provider: str = _env_str("RAYA_TTS_PROVIDER", "JARVIS_TTS_PROVIDER", "browser")
    elevenlabs_api_key: str = _env_str("ELEVENLABS_API_KEY", "JARVIS_ELEVENLABS_API_KEY", "")
    elevenlabs_voice_id: str = _env_str(
        "ELEVENLABS_VOICE_ID",
        "JARVIS_ELEVENLABS_VOICE_ID",
        "",
    )
    elevenlabs_model: str = _env_str(
        "ELEVENLABS_MODEL",
        "JARVIS_ELEVENLABS_MODEL",
        "eleven_multilingual_v2",
    )
    elevenlabs_stability: float = float(
        _env_str("ELEVENLABS_STABILITY", "JARVIS_ELEVENLABS_STABILITY", "0.45"),
    )
    elevenlabs_similarity: float = float(
        _env_str("ELEVENLABS_SIMILARITY", "JARVIS_ELEVENLABS_SIMILARITY", "0.75"),
    )


settings = Settings()
