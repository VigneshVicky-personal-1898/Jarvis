# AI-ASSISTED: Cursor
# PROMPT: Registered QE Engine project paths for Jarvis
# ACCEPTED-BY: vignesh

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config import settings


@dataclass(frozen=True)
class QeProject:
    id: str
    name: str
    path: Path
    role: str


def _p(env_path: str, default: str) -> Path:
    raw = env_path.strip() if env_path else default
    return Path(raw).expanduser().resolve()


QE_PROJECTS: tuple[QeProject, ...] = (
    QeProject(
        id="mcp_automation",
        name="MCP Automation",
        path=_p(settings.qe_mcp_automation_dir, "/data/QE_Engine/QE_Engine/mcp_automation"),
        role="MCP proxy, WF360 tool runner, Cursor bridge",
    ),
    QeProject(
        id="proactive_automation",
        name="Proactive Automation",
        path=_p(settings.qe_proactive_dir, "/data/QE_Engine/QE_Engine/ProactiveAutomation"),
        role="QE Engine API (Java), MCP agent, test execution",
    ),
    QeProject(
        id="qe_engine_ui",
        name="QE Engine UI",
        path=_p(settings.qe_ui_dir, "/data/QE_Engine/QE_Engine/qe_engine_ui"),
        role="React dashboard for tests, MCP agent, regression",
    ),
)


def project_status() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for proj in QE_PROJECTS:
        exists = proj.path.is_dir()
        rows.append(
            {
                "id": proj.id,
                "name": proj.name,
                "path": str(proj.path),
                "role": proj.role,
                "present": exists,
            },
        )
    return rows
