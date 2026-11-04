"""Persistent Chat Archive and Session Store for StemClaw."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from stemclaw.config import get_settings


class ChatStore:
    """Manages persistent SQLite storage of all conversation turns across sessions."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        if db_path:
            self.db_path = db_path
        else:
            settings = get_settings()
            self.db_path = settings.stemclaw_dir / "cache.db"

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    turn_count INTEGER DEFAULT 0,
                    started_at TEXT NOT NULL,
                    last_active_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    turn_index INTEGER NOT NULL,
                    user_query TEXT NOT NULL,
                    assistant_response TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_turns_session ON chat_turns (session_id)")

    def record_turn(
        self,
        session_id: str,
        category: str,
        turn_index: int,
        user_query: str,
        assistant_response: str,
    ) -> None:
        """Record or update a user-assistant conversation turn in SQLite."""
        now_iso = datetime.now(timezone.utc).isoformat()
        clean_query = user_query.strip()
        first_title = clean_query[:75] if clean_query else "Research Session"

        with self._get_connection() as conn:
            # Upsert session metadata
            conn.execute(
                """
                INSERT INTO chat_sessions (session_id, category, title, turn_count, started_at, last_active_at)
                VALUES (?, ?, ?, 1, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    turn_count = chat_sessions.turn_count + 1,
                    last_active_at = excluded.last_active_at
                """,
                (session_id, category, first_title, now_iso, now_iso),
            )
            # Insert turn
            conn.execute(
                """
                INSERT INTO chat_turns (session_id, turn_index, user_query, assistant_response, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, turn_index, clean_query, assistant_response, now_iso),
            )
            conn.commit()

    def list_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List past conversation sessions."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT session_id, category, title, turn_count, started_at, last_active_at
                FROM chat_sessions
                ORDER BY last_active_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_session_turns(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve all turns for a specific session."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT turn_index, user_query, assistant_response, created_at
                FROM chat_turns
                WHERE session_id = ?
                ORDER BY turn_index ASC
                """,
                (session_id.strip(),),
            )
            return [dict(row) for row in cursor.fetchall()]

    # Snapshot helpers for hot /reload preservation
    @staticmethod
    def save_last_snapshot(
        session_id: str,
        category: str,
        messages: List[Dict[str, Any]],
    ) -> None:
        """Save active in-flight conversation to .stemclaw/last_session.json for /reload."""
        settings = get_settings()
        target = settings.stemclaw_dir / "last_session.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "session_id": session_id,
            "category": category,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "messages": messages,
        }
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @staticmethod
    def load_last_snapshot() -> Optional[Dict[str, Any]]:
        """Load last saved conversation snapshot if present."""
        settings = get_settings()
        target = settings.stemclaw_dir / "last_session.json"
        if not target.exists():
            return None
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            return None

    @staticmethod
    def clear_last_snapshot() -> None:
        settings = get_settings()
        target = settings.stemclaw_dir / "last_session.json"
        if target.exists():
            try:
                target.unlink()
            except Exception:
                pass


_GLOBAL_CHAT_STORE: Optional[ChatStore] = None


def get_chat_store() -> ChatStore:
    global _GLOBAL_CHAT_STORE
    if _GLOBAL_CHAT_STORE is None:
        _GLOBAL_CHAT_STORE = ChatStore()
    return _GLOBAL_CHAT_STORE

