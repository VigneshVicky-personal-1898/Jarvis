# AI-ASSISTED: Cursor
# PROMPT: MCP HTTP client stub for external tool servers
# ACCEPTED-BY: vignesh

from __future__ import annotations

from typing import Any

import httpx

from config import settings


class McpClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.mcp_server_url).rstrip("/")

    def enabled(self) -> bool:
        return settings.mcp_enabled and bool(self.base_url)

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.enabled():
            return {"ok": False, "error": "mcp_disabled"}
        url = f"{self.base_url}/tools/{name}"
        with httpx.Client(timeout=120.0) as client:
            r = client.post(url, json={"arguments": arguments or {}})
            r.raise_for_status()
            return r.json()
