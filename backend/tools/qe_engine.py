# AI-ASSISTED: Cursor
# PROMPT: Test plan latest results and TPX execution id lookup for QE Engine
# ACCEPTED-BY: vignesh

from __future__ import annotations

from typing import Any

import re

from integrations.qe_engine.client import QeEngineClient
from integrations.qe_engine.projects import project_status
from integrations.qe_engine.results_format import format_execution_document, format_latest_list
from observability import recent_executions

_EXEC_ID = re.compile(r"\b(tpx|rtp|rex)-[\w-]+\b", re.IGNORECASE)


def _client() -> QeEngineClient:
    return QeEngineClient()


def tool_qe_projects_status(_params: dict[str, Any]) -> dict[str, Any]:
    client = _client()
    projects = project_status()
    backend = client.backend_reachable() if client.configured() else False
    speak_parts = []
    for p in projects:
        mark = "ok" if p["present"] else "missing"
        speak_parts.append(f"{p['name']}: {mark}")
    speak = "QE projects — " + "; ".join(speak_parts)
    if client.configured():
        speak += f". Backend API: {'online' if backend else 'offline'}."
    else:
        speak += ". Set QE_ENGINE_URL and credentials in RAYA .env."
    return {
        "ok": True,
        "speak": speak,
        "data": {"projects": projects, "backend_online": backend, "configured": client.configured()},
    }


def tool_qe_agent_command(params: dict[str, Any]) -> dict[str, Any]:
    command = str(params.get("command") or params.get("message") or params.get("query") or "").strip()
    if not command:
        return {"ok": False, "speak": "What should I run in QE Engine?", "data": {}}
    config_name = params.get("configName") or params.get("config_name")
    client = _client()
    if not client.configured():
        return {
            "ok": False,
            "speak": (
                "QE Engine is not linked yet. Copy .env.example to .env and set "
                "QE_ENGINE_URL (API host, not the login page), username, password, "
                "and project name, then restart the RAYA API."
            ),
            "data": {"configured": False},
        }
    if not client.backend_reachable():
        return {
            "ok": False,
            "speak": (
                "QE Engine backend is not reachable. Start ProactiveAutomation on port 8888 "
                "and ensure MCP proxy is running if needed."
            ),
            "data": {},
        }
    result = client.agent_chat(command, config_name=str(config_name) if config_name else None)
    speak = result.get("message") or "QE Engine finished."
    if len(speak) > 1200:
        speak = speak[:1197] + "..."
    return {
        "ok": result.get("ok", False),
        "speak": speak,
        "data": result.get("data", {}),
    }


def tool_qe_regression(params: dict[str, Any]) -> dict[str, Any]:
    suite = str(params.get("suite", "workflow360")).strip()
    suite_path = params.get("suite_path") or params.get("suitePath")
    client = _client()
    if not client.configured():
        return {
            "ok": False,
            "speak": "Configure QE_ENGINE_URL and credentials in .env to run regression.",
            "data": {"suite": suite},
        }
    result = client.run_regression_suite(str(suite_path) if suite_path else None)
    if not result.get("ok"):
        return {
            "ok": False,
            "speak": result.get("message", "Regression run failed."),
            "data": result,
        }
    body = result.get("data") or {}
    summary = body.get("summary") or body.get("message") or f"{suite} regression completed."
    return {"ok": True, "speak": str(summary), "data": body}


def tool_raya_recent_activity(params: dict[str, Any]) -> dict[str, Any]:
    limit = int(params.get("limit") or 5)
    rows = recent_executions(limit)
    if not rows:
        return {
            "ok": True,
            "speak": "No recent RAYA activity yet. Run a command first.",
            "data": {"items": []},
        }
    parts: list[str] = []
    for row in rows[:limit]:
        inp = str(row.get("user_input", ""))[:50]
        preview = str(row.get("response_preview", ""))[:80]
        tool = row.get("tool") or row.get("intent") or "—"
        parts.append(f"{inp}: {tool}. {preview}")
    speak = "Recent RAYA activity. " + " Next, ".join(parts[:3])
    if len(speak) > 1200:
        speak = speak[:1197] + "..."
    return {"ok": True, "speak": speak, "data": {"items": rows}}


def _summarize_qe_result(item: dict[str, Any]) -> str:
    name = item.get("testCaseName") or item.get("name") or item.get("testCaseId") or "run"
    status = item.get("status") or item.get("executionStatus") or "unknown"
    when = item.get("endTime") or item.get("createdAt") or item.get("startTime") or ""
    bit = f"{name} {status}"
    if when:
        bit += f" at {when}"
    return bit


def tool_qe_execution_result(params: dict[str, Any]) -> dict[str, Any]:
    eid = str(
        params.get("execution_id")
        or params.get("testExecutionId")
        or params.get("id")
        or "",
    ).strip()
    if not eid:
        return {"ok": False, "speak": "Which execution id? For example TPX-22.", "data": {}}
    client = _client()
    if not client.configured():
        return {"ok": False, "speak": "QE Engine is not configured in .env.", "data": {}}
    result = client.get_test_plan_execution(eid)
    if not result.get("ok"):
        return {
            "ok": False,
            "speak": str(result.get("message", "Could not load that execution.")),
            "data": result,
        }
    doc = result.get("result") or {}
    speak = "Test plan execution. " + format_execution_document(doc)
    return {"ok": True, "speak": speak, "data": {"result": doc, **result.get("data", {})}}


def tool_qe_latest_results(params: dict[str, Any]) -> dict[str, Any]:
    limit = int(params.get("limit") or 5)
    client = _client()
    if not client.configured():
        fallback = tool_raya_recent_activity({"limit": limit})
        fallback["speak"] = (
            "QE Engine is not configured. Use a .env file with QE_ENGINE_* vars and restart the API. "
            + fallback["speak"]
        )
        return fallback
    if not client.backend_reachable():
        fallback = tool_raya_recent_activity({"limit": limit})
        fallback["speak"] = (
            "QE Engine API is offline. Showing recent RAYA activity instead. "
            + fallback["speak"]
        )
        return fallback
    result = client.latest_test_plan_results(limit=limit)
    if not result.get("ok"):
        msg = result.get("message", "Could not load results.")
        return {"ok": False, "speak": msg, "data": result}
    recent = result.get("recent") or []
    if not recent:
        return {
            "ok": True,
            "speak": f"No test plan results yet for project {client.project_name}.",
            "data": result,
        }
    total = result.get("total_count")
    head = f"{client.project_name} has {total} test plan runs on record. " if total else ""
    speak = head + format_latest_list(recent, label="runs", limit=limit)
    if len(speak) > 1200:
        speak = speak[:1197] + "..."
    return {"ok": True, "speak": speak, "data": result}


def tool_qe_list_mcp_tools(params: dict[str, Any]) -> dict[str, Any]:
    config_name = params.get("configName") or params.get("config_name")
    client = _client()
    if not client.configured():
        return {"ok": False, "speak": "QE Engine not configured.", "data": {}}
    try:
        result = client.list_mcp_tools(str(config_name) if config_name else None)
    except Exception as e:
        return {"ok": False, "speak": f"Could not list MCP tools: {e}", "data": {}}
    tools = result.get("data") or {}
    count = len(tools.get("tools", [])) if isinstance(tools, dict) else 0
    return {
        "ok": True,
        "speak": f"QE Engine reports {count} MCP tools available.",
        "data": tools,
    }

