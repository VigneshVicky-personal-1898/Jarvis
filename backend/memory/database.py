# AI-ASSISTED: Cursor
# PROMPT: SQLite connection helper for Jarvis memory
# ACCEPTED-BY: vignesh

from __future__ import annotations

import sqlite3
from pathlib import Path

from config import DATA_DIR, MEMORY_DB


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    ensure_data_dir()
    path = db_path or MEMORY_DB
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
