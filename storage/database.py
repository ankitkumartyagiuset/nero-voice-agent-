"""
SQLite Database manager with schema migration and thread-safe connection pooling.
"""
import sqlite3
import threading
from pathlib import Path
from typing import Optional
from utils.logger import get_logger

logger = get_logger("database")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    scheduled_at DATETIME NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'completed', 'cancelled'
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

CREATE TABLE IF NOT EXISTS conversation_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    intent TEXT,
    latency_ms REAL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversation_summaries (
    session_id TEXT PRIMARY KEY,
    summary TEXT NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT NOT NULL,
    status TEXT NOT NULL, -- 'running', 'completed', 'failed', 'cancelled'
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS key_value_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reminders_status_sched ON reminders(status, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_conv_session ON conversation_messages(session_id, created_at);
"""


class DatabaseManager:
    """Manages SQLite database connections and transactions safely."""

    def __init__(self, db_path: str = "nero.db"):
        self.db_path = Path(db_path)
        self._local = threading.local()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=20.0,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            self._local.conn = conn
        return self._local.conn

    def _init_db(self) -> None:
        """Create tables and indexes if they do not exist."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.executescript(SCHEMA_SQL)
                conn.commit()
            logger.info(f"Database initialized successfully at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def execute_query(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        """Execute a SELECT query and return rows."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def execute_write(self, statement: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE statement and return lastrowid or rowcount."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(statement, params)
        conn.commit()
        return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    def close(self) -> None:
        """Close connection for current thread."""
        if hasattr(self._local, "conn") and self._local.conn is not None:
            try:
                self._local.conn.close()
            except Exception:
                pass
            self._local.conn = None


_DB_INSTANCE: Optional[DatabaseManager] = None


def get_db(db_path: str = "nero.db") -> DatabaseManager:
    global _DB_INSTANCE
    if _DB_INSTANCE is None:
        _DB_INSTANCE = DatabaseManager(db_path)
    return _DB_INSTANCE
