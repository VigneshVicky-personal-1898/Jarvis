# AI-ASSISTED: Cursor
# PROMPT: RAYA tool registry including raya_recent_activity
# ACCEPTED-BY: vignesh

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from tools.applications import tool_open_app
from tools.rag_tools import tool_rag_status, tool_rag_sync
from tools.codebase_tools import (
    tool_analyze_project,
    tool_list_connected_projects,
    tool_search_project_code,
)
from tools.browser import tool_open_url, tool_web_search
from tools.files import tool_create_folder, tool_search_files
from tools.memory_tools import tool_memory_retrieve, tool_memory_save
from tools.qe_engine import (
    tool_raya_recent_activity,
    tool_qe_agent_command,
    tool_qe_execution_result,
    tool_qe_latest_results,
    tool_qe_list_mcp_tools,
    tool_qe_projects_status,
    tool_qe_regression,
)
from tools.registry import PermissionLevel, ToolRegistry, ToolSpec
from config import settings
from tools.system import (
    tool_date,
    tool_sleep,
    tool_system_status,
    tool_time,
    tool_volume,
)

if TYPE_CHECKING:
    from engine import CommandEngine


def build_registry(engine: CommandEngine | None = None) -> ToolRegistry:
    reg = ToolRegistry()

    reg.register(
        ToolSpec(
            "time",
            "Tell the current local time.",
            tool_time,
            permission=PermissionLevel.SAFE,
            category="system",
        ),
    )
    reg.register(
        ToolSpec(
            "date",
            "Tell today's date.",
            tool_date,
            permission=PermissionLevel.SAFE,
            category="system",
        ),
    )
    reg.register(
        ToolSpec(
            "system_status",
            "Return CPU, memory, and disk usage.",
            tool_system_status,
            permission=PermissionLevel.SAFE,
            category="system",
        ),
    )
    reg.register(
        ToolSpec(
            "open_app",
            "Open a configured application (chrome, browser, terminal, vscode).",
            tool_open_app,
            permission=PermissionLevel.SAFE,
            category="applications",
        ),
    )
    reg.register(
        ToolSpec(
            "web_search",
            "Search the internet for current information.",
            tool_web_search,
            permission=PermissionLevel.SAFE,
            category="browser",
        ),
    )
    reg.register(
        ToolSpec(
            "google_search",
            "Search Google for current information and summarize the top result.",
            tool_web_search,
            permission=PermissionLevel.SAFE,
            category="browser",
        ),
    )
    reg.register(
        ToolSpec(
            "open_url",
            "Open a URL in the default browser.",
            tool_open_url,
            permission=PermissionLevel.SAFE,
            category="browser",
        ),
    )
    reg.register(
        ToolSpec(
            "volume",
            "Change volume: direction up, down, or mute.",
            tool_volume,
            permission=PermissionLevel.SAFE,
            category="system",
        ),
    )
    reg.register(
        ToolSpec(
            "sleep",
            "Stop listening / go to sleep.",
            tool_sleep,
            permission=PermissionLevel.SAFE,
            category="general",
        ),
    )
    reg.register(
        ToolSpec(
            "search_files",
            "Search filenames under a directory (default: home).",
            tool_search_files,
            permission=PermissionLevel.SAFE,
            category="files",
        ),
    )
    reg.register(
        ToolSpec(
            "create_folder",
            "Create a folder under the user home directory.",
            tool_create_folder,
            permission=PermissionLevel.CONFIRMATION,
            requires_confirmation=True,
            category="files",
        ),
    )
    reg.register(
        ToolSpec(
            "memory_save",
            "Save user information to local memory.",
            tool_memory_save,
            permission=PermissionLevel.SAFE,
            category="memory",
        ),
    )
    reg.register(
        ToolSpec(
            "memory_retrieve",
            "Retrieve stored user information from local memory.",
            tool_memory_retrieve,
            permission=PermissionLevel.SAFE,
            category="memory",
        ),
    )
    reg.register(
        ToolSpec(
            "rag_sync",
            "Re-index documents from data/knowledge into local vector store.",
            tool_rag_sync,
            permission=PermissionLevel.SAFE,
            category="memory",
        ),
    )
    reg.register(
        ToolSpec(
            "rag_status",
            "Report local RAG index chunk count and availability.",
            tool_rag_status,
            permission=PermissionLevel.SAFE,
            category="memory",
        ),
    )
    reg.register(
        ToolSpec(
            "list_connected_projects",
            "List RAYA and QE codebases available for analysis.",
            tool_list_connected_projects,
            permission=PermissionLevel.SAFE,
            category="developer",
        ),
    )
    reg.register(
        ToolSpec(
            "analyze_project",
            "Summarize a connected project folder structure (raya, qe paths).",
            tool_analyze_project,
            permission=PermissionLevel.SAFE,
            category="developer",
        ),
    )
    reg.register(
        ToolSpec(
            "search_project_code",
            "Search code in a connected project with ripgrep.",
            tool_search_project_code,
            permission=PermissionLevel.SAFE,
            category="developer",
        ),
    )
    reg.register(
        ToolSpec(
            "raya_recent_activity",
            "Summarize recent RAYA commands and responses (works without an LLM).",
            tool_raya_recent_activity,
            permission=PermissionLevel.SAFE,
            category="general",
        ),
    )
    reg.register(
        ToolSpec(
            "qe_execution_result",
            "Fetch QE test plan results for an execution id (TPX-22, RTP-, REX-).",
            tool_qe_execution_result,
            permission=PermissionLevel.SAFE,
            category="qe_engine",
        ),
    )
    reg.register(
        ToolSpec(
            "qe_latest_results",
            "Fetch latest QE test plan execution results for the configured project.",
            tool_qe_latest_results,
            permission=PermissionLevel.SAFE,
            category="qe_engine",
        ),
    )
    reg.register(
        ToolSpec(
            "qe_projects_status",
            "Report QE Engine project folders and API connectivity.",
            tool_qe_projects_status,
            permission=PermissionLevel.SAFE,
            category="qe_engine",
        ),
    )
    reg.register(
        ToolSpec(
            "qe_agent_command",
            "Send a natural-language task to QE Engine MCP agent (APIs, workflows, tools).",
            tool_qe_agent_command,
            permission=PermissionLevel.CONFIRMATION,
            category="qe_engine",
        ),
    )
    reg.register(
        ToolSpec(
            "qe_list_mcp_tools",
            "List MCP tools exposed by QE Engine for the configured project.",
            tool_qe_list_mcp_tools,
            permission=PermissionLevel.SAFE,
            category="qe_engine",
        ),
    )
    reg.register(
        ToolSpec(
            "qe_regression",
            "Run QE Engine / Workflow360 regression suite.",
            tool_qe_regression,
            permission=PermissionLevel.CONFIRMATION,
            category="qe_engine",
        ),
    )

    if engine is not None:

        def _list_commands(_params: dict[str, Any]) -> dict[str, Any]:
            caps = reg.capability_summary()
            speak = "I can currently: " + "; ".join(caps) + "."
            return {
                "ok": True,
                "speak": speak,
                "data": {"capabilities": caps, "commands": engine.list_command_summaries()},
            }

        reg.register(
            ToolSpec(
                "list_commands",
                "List what RAYA can do from registered tools and commands.",
                _list_commands,
                permission=PermissionLevel.SAFE,
                category="general",
            ),
        )

    if settings.cloud_mode:
        for name in (
            "system_status",
            "open_app",
            "open_url",
            "volume",
            "search_files",
            "create_folder",
            "list_connected_projects",
            "analyze_project",
            "search_project_code",
        ):
            reg.unregister(name)

    return reg
