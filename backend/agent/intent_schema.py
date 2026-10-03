# AI-ASSISTED: Cursor
# PROMPT: Structured JARVIS intent schema for validated tool routing
# ACCEPTED-BY: vignesh

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class IntentCategory(StrEnum):
    GREETING = "GREETING"
    TIME = "TIME"
    DATE = "DATE"
    SYSTEM_STATUS = "SYSTEM_STATUS"
    OPEN_APPLICATION = "OPEN_APPLICATION"
    OPEN_URL = "OPEN_URL"
    SEARCH_WEB = "SEARCH_WEB"
    CREATE_FOLDER = "CREATE_FOLDER"
    FIND_FILE = "FIND_FILE"
    VOLUME_CONTROL = "VOLUME_CONTROL"
    MEMORY_SAVE = "MEMORY_SAVE"
    MEMORY_RETRIEVE = "MEMORY_RETRIEVE"
    GENERAL_QUESTION = "GENERAL_QUESTION"
    CONVERSATION = "CONVERSATION"
    LIST_CAPABILITIES = "LIST_CAPABILITIES"
    SLEEP = "SLEEP"
    DEVELOPER_ACTION = "DEVELOPER_ACTION"
    UNKNOWN = "UNKNOWN"


class StructuredIntent(BaseModel):
    intent: IntentCategory = IntentCategory.UNKNOWN
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    tool: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    requires_confirmation: bool = False
    response: str = ""
    route: str = Field(default="ai", description="rules | ai | chat")


ACTION_TO_INTENT: dict[str, IntentCategory] = {
    "none": IntentCategory.GREETING,
    "time": IntentCategory.TIME,
    "date": IntentCategory.DATE,
    "system_status": IntentCategory.SYSTEM_STATUS,
    "open_app": IntentCategory.OPEN_APPLICATION,
    "web_search": IntentCategory.SEARCH_WEB,
    "google_search": IntentCategory.SEARCH_WEB,
    "open_url": IntentCategory.OPEN_URL,
    "list_commands": IntentCategory.LIST_CAPABILITIES,
    "sleep": IntentCategory.SLEEP,
    "volume": IntentCategory.VOLUME_CONTROL,
    "search_files": IntentCategory.FIND_FILE,
    "create_folder": IntentCategory.CREATE_FOLDER,
    "qe_regression": IntentCategory.DEVELOPER_ACTION,
    "qe_agent_command": IntentCategory.DEVELOPER_ACTION,
    "qe_projects_status": IntentCategory.DEVELOPER_ACTION,
    "qe_list_mcp_tools": IntentCategory.DEVELOPER_ACTION,
    "qe_latest_results": IntentCategory.DEVELOPER_ACTION,
    "qe_execution_result": IntentCategory.DEVELOPER_ACTION,
    "raya_recent_activity": IntentCategory.LIST_CAPABILITIES,
    "memory_save": IntentCategory.MEMORY_SAVE,
    "memory_retrieve": IntentCategory.MEMORY_RETRIEVE,
}

TOOL_ALIASES: dict[str, str] = {
    "open_application": "open_app",
    "search_web": "web_search",
    "google_search": "web_search",
    "google": "web_search",
    "system_status": "system_status",
    "get_time": "time",
    "get_date": "date",
    "volume_control": "volume",
    "file_search": "search_files",
    "save_memory": "memory_save",
    "retrieve_memory": "memory_retrieve",
    "qe_engine": "qe_agent_command",
    "run_qe_agent": "qe_agent_command",
    "create_api": "qe_agent_command",
}


def normalize_tool_name(name: str | None) -> str | None:
    if not name:
        return None
    key = name.strip().lower()
    return TOOL_ALIASES.get(key, key)
