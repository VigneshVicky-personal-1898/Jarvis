# AI-ASSISTED: Cursor
# PROMPT: Persistent memory with categories for JARVIS preferences
# ACCEPTED-BY: vignesh

from __future__ import annotations

from config import settings
from memory.database import connect


class LongTermMemory:
    def __init__(self) -> None:
        self._conn = connect()
        self._init_schema()

    def _init_schema(self) -> None:
        if not settings.memory_enabled:
            return
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (category, key)
            )
            """
        )
        self._conn.commit()

    def set_preference(self, key: str, value: str) -> None:
        if not settings.memory_enabled:
            return
        self._conn.execute(
            """
            INSERT INTO preferences (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
            """,
            (key, value),
        )
        self._conn.commit()

    def get_preference(self, key: str) -> str | None:
        if not settings.memory_enabled:
            return None
        row = self._conn.execute(
            "SELECT value FROM preferences WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else None

    def save(self, category: str, key: str, value: str) -> None:
        if not settings.memory_enabled:
            return
        self._conn.execute(
            """
            INSERT INTO memories (category, key, value) VALUES (?, ?, ?)
            ON CONFLICT(category, key) DO UPDATE SET
              value=excluded.value, updated_at=CURRENT_TIMESTAMP
            """,
            (category, key, value),
        )
        self._conn.commit()
        if key in ("main_project", "default_project"):
            self.set_preference("main_project", value)

    def get(self, category: str, key: str) -> str | None:
        if not settings.memory_enabled:
            return None
        row = self._conn.execute(
            "SELECT value FROM memories WHERE category = ? AND key = ?",
            (category, key),
        ).fetchone()
        return row["value"] if row else None

    def get_any(self, key: str) -> str | None:
        pref = self.get_preference(key)
        if pref:
            return pref
        row = self._conn.execute(
            "SELECT value FROM memories WHERE key = ? ORDER BY updated_at DESC LIMIT 1",
            (key,),
        ).fetchone()
        return row["value"] if row else None
