# AI-ASSISTED: Cursor
# PROMPT: Bridge MCP tools into Jarvis tool registry
# ACCEPTED-BY: vignesh

from __future__ import annotations

from typing import Any

from mcp.client import McpClient
from tools.qe_engine import tool_qe_agent_command, tool_qe_regression
from tools.registry import PermissionLevel, ToolRegistry, ToolSpec


def register_mcp_tools(registry: ToolRegistry, client: McpClient | None = None) -> None:
    mcp = client or McpClient()

    def _qe_via_mcp(params: dict[str, Any]) -> dict[str, Any]:
        if mcp.enabled():
            try:
                body = mcp.call_tool("qe_regression", params)
            except Exception as e:
                return {"ok": False, "speak": f"MCP call failed: {e}", "data": {}}
            speak = body.get("speak") or body.get("message") or "MCP tool finished."
            return {"ok": body.get("ok", True), "speak": speak, "data": body}
        return tool_qe_regression(params)

    def _qe_agent_via_mcp(params: dict[str, Any]) -> dict[str, Any]:
        if mcp.enabled():
            try:
                body = mcp.call_tool("qe_agent_command", params)
            except Exception as e:
                return {"ok": False, "speak": f"MCP call failed: {e}", "data": {}}
            speak = body.get("speak") or body.get("message") or "MCP agent finished."
            return {"ok": body.get("ok", True), "speak": speak, "data": body}
        return tool_qe_agent_command(params)

    registry.register(
        ToolSpec(
            "mcp_qe_regression",
            "Run regression via MCP or QE Engine HTTP API.",
            _qe_via_mcp,
            permission=PermissionLevel.CONFIRMATION,
            category="qe_engine",
        ),
    )
    registry.register(
        ToolSpec(
            "mcp_qe_agent",
            "Run QE MCP agent via MCP proxy or ProactiveAutomation API.",
            _qe_agent_via_mcp,
            permission=PermissionLevel.CONFIRMATION,
            category="qe_engine",
        ),
    )
