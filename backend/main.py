# AI-ASSISTED: Cursor
# PROMPT: POST /api/tts ElevenLabs audio for RAYA voice
# ACCEPTED-BY: vignesh

from __future__ import annotations

import hmac
import time
from collections import deque
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent.agent import RayaAgent
from tools.confirmation_store import clear_active, consume
from config import settings
from security import SESSION_COOKIE, create_session_token, valid_session_token
from integrations.qe_engine.health import integration_snapshot
from engine import CommandEngine
from mcp.tools import register_mcp_tools
from observability import recent_executions
from tools.registry import ToolRegistry
from tools.setup import build_registry
from rag.service import get_rag
from voice import tts as voice_tts

if settings.cloud_mode:
    if not settings.auth_enabled:
        raise RuntimeError("RAYA_AUTH_ENABLED must be true when RAYA_CLOUD_MODE is enabled.")
    if not settings.access_password or len(settings.session_secret) < 32:
        raise RuntimeError(
            "Cloud mode requires RAYA_ACCESS_PASSWORD and a RAYA_SESSION_SECRET of at least 32 characters.",
        )

app = FastAPI(
    title="RAYA",
    version="3.0.0",
    docs_url=None if settings.cloud_mode else "/docs",
    redoc_url=None if settings.cloud_mode else "/redoc",
    openapi_url=None if settings.cloud_mode else "/openapi.json",
)


@app.on_event("startup")
def _startup_rag_sync() -> None:
    if not settings.rag_enabled:
        return
    try:
        get_rag().sync()
    except Exception:
        pass

if not settings.cloud_mode:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def require_cloud_login(request: Request, call_next):
    public_auth_paths = {
        "/api/auth/session",
        "/api/auth/login",
        "/api/auth/logout",
    }
    if (
        settings.auth_enabled
        and request.url.path.startswith("/api/")
        and request.url.path not in public_auth_paths
        and not valid_session_token(request.cookies.get(SESSION_COOKIE))
    ):
        return JSONResponse({"detail": "Authentication required."}, status_code=401)
    return await call_next(request)

engine = CommandEngine()
registry: ToolRegistry = build_registry(engine)
register_mcp_tools(registry)
agent = RayaAgent(engine, registry)
_LOGIN_ATTEMPTS: dict[str, deque[float]] = {}
_LOGIN_ATTEMPTS_LOCK = Lock()

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


class ProcessRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    require_wake_word: bool = False
    language: str = Field(default="en", max_length=12)


class ConfirmRequest(BaseModel):
    confirmation_id: str
    approved: bool = True


class TtsRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    language: str = Field(default="en", max_length=12)


class LoginRequest(BaseModel):
    password: str = Field(..., min_length=1, max_length=256)


class ProcessResponse(BaseModel):
    ok: bool
    speak: str
    command_id: str | None = None
    action: str | None = None
    confidence: float = 0.0
    data: dict = Field(default_factory=dict)
    unmatched: bool = False
    ui_state: str = "IDLE"
    intent: str = "UNKNOWN"


def _to_response(result) -> ProcessResponse:
    data = dict(result.data)
    data["source"] = result.source
    if not settings.debug_mode and "debug" in data.get("execution", {}):
        data["execution"] = {
            k: v for k, v in data["execution"].items() if k != "debug"
        }
    return ProcessResponse(
        ok=result.ok,
        speak=result.speak,
        command_id=result.command_id,
        action=result.action,
        confidence=result.confidence,
        data=data,
        unmatched=result.unmatched,
        ui_state=result.ui_state,
        intent=result.intent,
    )


@app.get("/api/health")
def health() -> dict:
    online = agent.brain.available()
    return {
        "status": "ok",
        "service": "raya",
        "llm_available": online,
        "llm_provider": settings.llm_provider,
        "ollama_available": online and settings.llm_provider == "ollama",
        "agent_enabled": settings.agent_enabled,
        "mcp_enabled": settings.mcp_enabled,
        "rag": get_rag().status(),
        "connectivity": "online" if online else "offline",
        "debug_mode": settings.debug_mode,
        "tts_provider": settings.tts_provider,
        "tts_available": voice_tts.tts_available(),
    }


@app.get("/api/auth/session")
def auth_session(request: Request) -> dict:
    authenticated = valid_session_token(request.cookies.get(SESSION_COOKIE))
    return {
        "auth_required": settings.auth_enabled,
        "authenticated": authenticated or not settings.auth_enabled,
    }


@app.post("/api/auth/login")
def auth_login(req: LoginRequest, request: Request, response: Response) -> dict:
    if not settings.auth_enabled:
        return {"authenticated": True}
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    with _LOGIN_ATTEMPTS_LOCK:
        failures = _LOGIN_ATTEMPTS.setdefault(client_ip, deque())
        while failures and now - failures[0] > 900:
            failures.popleft()
        if len(failures) >= 5:
            retry_after = max(1, int(900 - (now - failures[0])))
            raise HTTPException(
                status_code=429,
                detail="Too many failed sign-in attempts. Try again later.",
                headers={"Retry-After": str(retry_after)},
            )
    if not hmac.compare_digest(req.password, settings.access_password):
        with _LOGIN_ATTEMPTS_LOCK:
            _LOGIN_ATTEMPTS.setdefault(client_ip, deque()).append(now)
        raise HTTPException(status_code=401, detail="Invalid password.")
    with _LOGIN_ATTEMPTS_LOCK:
        _LOGIN_ATTEMPTS.pop(client_ip, None)
    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(),
        max_age=settings.session_max_age,
        httponly=True,
        secure=settings.cloud_mode,
        samesite="strict",
        path="/",
    )
    return {"authenticated": True}


@app.post("/api/auth/logout")
def auth_logout(response: Response) -> dict:
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"authenticated": False}


@app.post("/api/tts")
def text_to_speech(req: TtsRequest) -> Response:
    if not voice_tts.tts_available():
        raise HTTPException(
            status_code=503,
            detail="TTS not configured. Set RAYA_TTS_PROVIDER=elevenlabs and ELEVENLABS_* in .env",
        )
    try:
        audio = voice_tts.synthesize(req.text, language=req.language)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return Response(content=audio, media_type="audio/mpeg")


@app.get("/api/rag/status")
def rag_status() -> dict:
    return get_rag().status()


@app.post("/api/rag/sync")
def rag_sync() -> dict:
    return get_rag().sync()


@app.get("/api/qe/status")
def qe_status() -> dict:
    return integration_snapshot()


@app.get("/api/commands")
def list_commands() -> dict:
    return {
        "wake_words": engine.wake_words,
        "commands": engine.list_command_summaries(),
        "tools": registry.catalog(),
        "capabilities": registry.capability_summary(),
    }


@app.get("/api/observability")
def observability() -> dict:
    if not settings.debug_mode:
        return {"enabled": False, "records": []}
    return {"enabled": True, "records": recent_executions()}


@app.post("/api/reload")
def reload_config() -> dict[str, str]:
    engine.reload()
    return {"status": "reloaded"}


@app.post("/api/confirm", response_model=ProcessResponse)
def confirm_action(req: ConfirmRequest) -> ProcessResponse:
    pending = consume(req.confirmation_id, req.approved)
    if not pending:
        clear_active()
        result = agent.process("no")
        return _to_response(result)
    result = registry.execute(pending.tool, pending.arguments, confirmed=True)
    from agent.agent import AgentResult

    agent_result = AgentResult(
        ok=result.get("ok", True),
        speak=result.get("speak", ""),
        command_id=pending.tool,
        action=pending.tool,
        confidence=1.0,
        data=result.get("data", {}),
        unmatched=False,
        source="confirmation",
        ui_state="SPEAKING",
        intent="CONFIRMED",
    )
    return _to_response(agent_result)


@app.post("/api/process", response_model=ProcessResponse)
def process(req: ProcessRequest) -> ProcessResponse:
    text = req.text.strip()
    if req.require_wake_word:
        if not engine.contains_wake_word(text):
            return ProcessResponse(
                ok=True,
                speak="",
                unmatched=True,
                data={"reason": "no_wake_word"},
                ui_state="SLEEPING",
            )
        text = engine.strip_wake_word(text)

    return _to_response(agent.process(text, language=req.language))


if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")
