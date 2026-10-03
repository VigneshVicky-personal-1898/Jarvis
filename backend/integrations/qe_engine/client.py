# AI-ASSISTED: Cursor
# PROMPT: Test plan execution APIs (TPX/RTP ids and latest summaries)
# ACCEPTED-BY: vignesh

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import httpx

from config import settings


class QeEngineClient:
    def __init__(self) -> None:
        self.base_url = settings.qe_engine_url.rstrip("/")
        self.username = settings.qe_engine_username.strip()
        self.project_name = settings.qe_engine_project.strip()
        self._token = settings.qe_engine_token.strip()

    def configured(self) -> bool:
        return bool(self.base_url and self.username and self.project_name)

    def _ensure_token(self) -> str | None:
        if self._token:
            return self._token
        if not settings.qe_engine_password:
            return None
        url = f"{self.base_url}/api/rest/auth/login"
        with httpx.Client(timeout=30.0) as client:
            r = client.post(
                url,
                json={
                    "username": self.username,
                    "password": settings.qe_engine_password,
                },
            )
            r.raise_for_status()
            token = r.headers.get("qeAuth") or r.headers.get("QEAuth")
            if not token:
                body = r.json()
                token = body.get("token") or body.get("qeAuth")
            if token:
                self._token = token
            return self._token

    def _headers(self) -> dict[str, str]:
        token = self._ensure_token()
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            headers["qeAuth"] = token
        return headers

    def _params(self) -> dict[str, str]:
        return {"username": self.username, "projectName": self.project_name}

    def backend_reachable(self) -> bool:
        if not self.base_url:
            return False
        try:
            with httpx.Client(timeout=3.0) as client:
                r = client.get(f"{self.base_url}/api/rest/auth/login")
                return r.status_code in (200, 405, 401, 403, 404)
        except httpx.HTTPError:
            return False

    def agent_chat(
        self,
        message: str,
        *,
        config_name: str | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if not self.configured():
            return {
                "ok": False,
                "message": "QE Engine is not configured in RAYA .env",
            }
        body: dict[str, Any] = {
            "message": message,
            "history": history or [],
        }
        if config_name:
            body["configName"] = config_name
        url = f"{self.base_url}/api/rest/mcp/agent/chat"
        with httpx.Client(timeout=600.0) as client:
            r = client.post(url, params=self._params(), json=body, headers=self._headers())
            if r.status_code >= 400:
                return {
                    "ok": False,
                    "status_code": r.status_code,
                    "message": r.text[:500],
                }
            data = r.json()
        status = data.get("status", "success")
        answer = (
            data.get("answer")
            or data.get("message")
            or data.get("finalAnswer")
            or ""
        )
        return {
            "ok": status == "success",
            "message": str(answer) if answer else str(data.get("message", "")),
            "data": data,
        }

    def _get_json(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        timeout: float = 60.0,
    ) -> dict[str, Any]:
        query = {"username": self.username, **(params or {})}
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=timeout) as client:
            r = client.get(url, params=query, headers=self._headers())
            if r.status_code >= 400:
                return {"ok": False, "status_code": r.status_code, "message": r.text[:800]}
            data = r.json()
            if isinstance(data, str):
                data = json.loads(data)
            return {"ok": True, "data": data}

    def get_test_plan_execution(self, execution_id: str) -> dict[str, Any]:
        if not self.configured():
            return {"ok": False, "message": "QE Engine not configured"}
        eid = execution_id.strip().upper()
        if eid.startswith("RTP-") or eid.startswith("REX-"):
            path = (
                f"/api/rest/testplan/regressionTestPlanResults/"
                f"{self.project_name}/{eid}"
            )
        else:
            path = f"/api/rest/testplan/testplanResults/{self.project_name}/{eid}"
        out = self._get_json(path)
        if not out.get("ok"):
            return out
        body = out.get("data") or {}
        doc = body.get("result")
        if doc is None and body.get("status") == "Error":
            return {"ok": False, "message": body.get("message", "Not found"), "data": body}
        if doc is None:
            return {"ok": False, "message": f"No result for execution id {eid}", "data": body}
        return {"ok": True, "data": body, "result": doc}

    def latest_test_plan_results(self, *, limit: int = 5) -> dict[str, Any]:
        if not self.configured():
            return {"ok": False, "message": "QE Engine not configured"}
        limit = max(1, min(limit, 20))
        recent = self._get_json(
            f"/api/rest/testplan/testplanResults/{self.project_name}",
            params={"page": 1, "limit": limit},
        )
        internal = self._get_json(
            f"/api/rest/testplan/latestExecutionSummary/{self.project_name}",
        )
        regression = self._get_json(
            f"/api/rest/testplan/regressionTestPlan/latestExecutionSummary/{self.project_name}",
        )
        recent_rows: list[Any] = []
        if recent.get("ok"):
            recent_rows = (recent.get("data") or {}).get("results") or []
        return {
            "ok": True,
            "recent": recent_rows,
            "internal_summary": (internal.get("data") or {}).get("results") or [],
            "regression_summary": (regression.get("data") or {}).get("results") or [],
            "total_count": (recent.get("data") or {}).get("count") if recent.get("ok") else None,
        }

    def list_mcp_tools(self, config_name: str | None = None) -> dict[str, Any]:
        if not self.configured():
            return {"ok": False, "message": "QE Engine not configured"}
        params = dict(self._params())
        if config_name:
            params["configName"] = config_name
        url = f"{self.base_url}/api/rest/mcp/tools"
        with httpx.Client(timeout=120.0) as client:
            r = client.get(url, params=params, headers=self._headers())
            r.raise_for_status()
            return {"ok": True, "data": r.json()}

    def latest_execution_results(self, *, limit: int = 5) -> dict[str, Any]:
        if not self.configured():
            return {"ok": False, "message": "QE Engine not configured"}
        url = f"{self.base_url}/api/rest/testcases/activemq/results"
        params = {
            "projectName": self.project_name,
            "page": 1,
            "limit": max(1, min(limit, 20)),
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                r = client.get(url, params=params, headers=self._headers())
                if r.status_code >= 400:
                    return {"ok": False, "message": r.text[:500], "status_code": r.status_code}
                data = r.json()
        except Exception as e:
            return {"ok": False, "message": str(e)}
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return {"ok": False, "message": data[:500]}
        items = data.get("items") if isinstance(data, dict) else None
        if items is None:
            return {"ok": False, "message": "Unexpected results format from QE Engine"}
        return {"ok": True, "data": data, "items": items}

    def run_regression_suite(self, suite_path: str | None = None) -> dict[str, Any]:
        if not self.configured():
            return {"ok": False, "message": "QE Engine not configured"}
        body: dict[str, Any] = {}
        if suite_path:
            body["suitePath"] = suite_path
        url = f"{self.base_url}/api/rest/mcp/run-suite"
        with httpx.Client(timeout=900.0) as client:
            r = client.post(url, params=self._params(), json=body, headers=self._headers())
            if r.status_code >= 400:
                return {"ok": False, "message": r.text[:500]}
            return {"ok": True, "data": r.json()}

    def run_local_node_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        automation_dir = Path(settings.qe_mcp_automation_dir)
        script = automation_dir / "src" / "singleCall.js"
        if not script.is_file():
            return {"ok": False, "message": f"Missing {script}"}
        try:
            proc = subprocess.run(
                ["node", str(script)],
                input=json.dumps(payload),
                cwd=str(automation_dir),
                capture_output=True,
                text=True,
                timeout=600,
            )
        except (OSError, subprocess.TimeoutExpired) as e:
            return {"ok": False, "message": str(e)}
        stdout = proc.stdout.strip()
        if not stdout:
            return {"ok": False, "message": proc.stderr[:800] or "No output from MCP runner"}
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            data = {"raw": stdout, "stderr": proc.stderr}
        return {"ok": proc.returncode == 0, "data": data}
