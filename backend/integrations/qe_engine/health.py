# AI-ASSISTED: Cursor
# PROMPT: Harden QE status checks so endpoint never 500s on missing certifi/httpx
# ACCEPTED-BY: vignesh

from __future__ import annotations

from config import settings
from integrations.qe_engine.projects import project_status


def _url_up(url: str, timeout: float = 2.5) -> bool:
    if not url.strip():
        return False
    try:
        import httpx
    except ImportError:
        return False
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.get(url.rstrip("/"))
            return r.status_code < 500
    except Exception:
        return False


def _backend_online() -> bool:
    try:
        from integrations.qe_engine.client import QeEngineClient

        client = QeEngineClient()
        if not client.configured():
            return False
        return client.backend_reachable()
    except Exception:
        return False


def _client_configured() -> bool:
    try:
        from integrations.qe_engine.client import QeEngineClient

        return QeEngineClient().configured()
    except Exception:
        return False


def integration_snapshot() -> dict[str, object]:
    return {
        "configured": _client_configured(),
        "backend_url": settings.qe_engine_url,
        "backend_online": _backend_online(),
        "mcp_proxy_url": settings.qe_mcp_proxy_url,
        "mcp_proxy_online": _url_up(settings.qe_mcp_proxy_url),
        "qe_ui_url": settings.qe_ui_url,
        "qe_ui_online": _url_up(settings.qe_ui_url),
        "project_name": settings.qe_engine_project,
        "username": settings.qe_engine_username,
        "projects": project_status(),
    }
