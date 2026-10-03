# AI-ASSISTED: Cursor
# PROMPT: Application launch tool backed by commands.yaml apps map
# ACCEPTED-BY: vignesh

from __future__ import annotations

import platform
import subprocess
from pathlib import Path
from typing import Any

import yaml

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "commands.yaml"


def _system_key() -> str:
    s = platform.system().lower()
    if s == "darwin":
        return "darwin"
    if s == "windows":
        return "win32"
    return "linux"


def load_apps() -> dict[str, dict[str, str]]:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("apps", {})


def tool_open_app(params: dict[str, Any]) -> dict[str, Any]:
    app_key = str(params.get("app", "")).strip().lower()
    aliases = {"chrome": "chrome", "google chrome": "chrome", "browser": "browser"}
    app_key = aliases.get(app_key, app_key)
    apps = load_apps()
    app_cfg = apps.get(app_key, {})
    cmd = app_cfg.get(_system_key())
    if not cmd:
        return {
            "ok": False,
            "speak": f"I cannot open {app_key} on this system.",
            "data": {},
        }
    try:
        subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {"ok": True, "speak": f"Opening {app_key}.", "data": {"app": app_key}}
    except OSError as e:
        return {"ok": False, "speak": f"Failed to open {app_key}: {e}", "data": {}}
