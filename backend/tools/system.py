# AI-ASSISTED: Cursor
# PROMPT: System tools (time, status, volume) for tool registry
# ACCEPTED-BY: vignesh

from __future__ import annotations

import platform
import shutil
import subprocess
from datetime import datetime
from typing import Any

import psutil


def _system_key() -> str:
    s = platform.system().lower()
    if s == "darwin":
        return "darwin"
    if s == "windows":
        return "win32"
    return "linux"


def _run_shell(command: str) -> tuple[bool, str]:
    try:
        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True, f"Executed: {command}"
    except OSError as e:
        return False, str(e)


def tool_time(_params: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now().strftime("%I:%M %p")
    return {"ok": True, "speak": f"The time is {now}.", "data": {"time": now}}


def tool_date(_params: dict[str, Any]) -> dict[str, Any]:
    today = datetime.now().strftime("%A, %B %d, %Y")
    return {"ok": True, "speak": f"Today is {today}.", "data": {"date": today}}


def tool_system_status(_params: dict[str, Any]) -> dict[str, Any]:
    cpu = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    speak = (
        f"CPU usage is {cpu:.0f} percent. "
        f"Memory is {mem.percent:.0f} percent used. "
        f"Disk is {disk.percent:.0f} percent full."
    )
    return {
        "ok": True,
        "speak": speak,
        "data": {
            "cpu_percent": cpu,
            "memory_percent": mem.percent,
            "disk_percent": disk.percent,
        },
    }


def tool_volume(params: dict[str, Any]) -> dict[str, Any]:
    direction = params.get("direction", "up")
    if _system_key() != "linux":
        return {
            "ok": False,
            "speak": "Volume control is configured for Linux in tools/system.py.",
            "data": {},
        }
    tool = shutil.which("pactl") or shutil.which("amixer")
    if not tool:
        return {
            "ok": False,
            "speak": "No volume tool found. Install pulseaudio or alsa-utils.",
            "data": {},
        }
    if "pactl" in tool:
        if direction == "mute":
            cmd = "pactl set-sink-mute @DEFAULT_SINK@ 1"
        elif direction == "up":
            cmd = "pactl set-sink-volume @DEFAULT_SINK@ +5%"
        else:
            cmd = "pactl set-sink-volume @DEFAULT_SINK@ -5%"
    else:
        if direction == "mute":
            cmd = "amixer -D pulse sset Master mute"
        elif direction == "up":
            cmd = "amixer -D pulse sset Master 5%+"
        else:
            cmd = "amixer -D pulse sset Master 5%-"
    ok, _ = _run_shell(cmd)
    label = {"up": "Louder.", "down": "Quieter.", "mute": "Muted."}.get(direction, "Done.")
    return {"ok": ok, "speak": label if ok else "Could not change volume.", "data": {}}


def tool_sleep(params: dict[str, Any]) -> dict[str, Any]:
    msg = params.get("message") or "Going to sleep."
    return {"ok": True, "speak": msg, "data": {"sleep": True}}
