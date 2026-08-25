"""
Repository classes encapsulating database operations for Reminders, Conversations, and Workflows.
"""
from datetime import datetime
from typing import List, Optional
from .database import DatabaseManager, get_db
from .models import ReminderModel, MessageModel, WorkflowRunModel


class ReminderRepository:
    """Repository for managing reminder records."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or get_db()

    def create(self, message: str, scheduled_at: datetime) -> ReminderModel:
        query = "INSERT INTO reminders (message, scheduled_at, status) VALUES (?, ?, 'pending')"
        row_id = self.db.execute_write(query, (message, scheduled_at.isoformat()))
        return ReminderModel(id=row_id, message=message, scheduled_at=scheduled_at, status="pending")

    def get_pending(self, now: Optional[datetime] = None) -> List[ReminderModel]:
        target = now or datetime.now()
        query = "SELECT * FROM reminders WHERE status = 'pending' AND scheduled_at <= ? ORDER BY scheduled_at ASC"
        rows = self.db.execute_query(query, (target.isoformat(),))
        result = []
        for r in rows:
            result.append(
                ReminderModel(
                    id=r["id"],
                    message=r["message"],
                    scheduled_at=datetime.fromisoformat(r["scheduled_at"]),
                    status=r["status"],
                    created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else None,
                )
            )
        return result

    def get_all_active(self) -> List[ReminderModel]:
        query = "SELECT * FROM reminders WHERE status = 'pending' ORDER BY scheduled_at ASC"
        rows = self.db.execute_query(query)
        result = []
        for r in rows:
            result.append(
                ReminderModel(
                    id=r["id"],
                    message=r["message"],
                    scheduled_at=datetime.fromisoformat(r["scheduled_at"]),
                    status=r["status"],
                    created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else None,
                )
            )
        return result

    def mark_completed(self, reminder_id: int) -> bool:
        query = "UPDATE reminders SET status = 'completed', completed_at = ? WHERE id = ?"
        res = self.db.execute_write(query, (datetime.now().isoformat(), reminder_id))
        return res > 0

    def cancel(self, reminder_id: int) -> bool:
        query = "UPDATE reminders SET status = 'cancelled' WHERE id = ?"
        res = self.db.execute_write(query, (reminder_id,))
        return res > 0


class ConversationRepository:
    """Repository for managing multi-turn chat history and summaries."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or get_db()

    def add_message(
        self, session_id: str, role: str, content: str, intent: Optional[str] = None, latency_ms: Optional[float] = None
    ) -> MessageModel:
        query = "INSERT INTO conversation_messages (session_id, role, content, intent, latency_ms) VALUES (?, ?, ?, ?, ?)"
        row_id = self.db.execute_write(query, (session_id, role, content, intent, latency_ms))
        return MessageModel(
            id=row_id,
            session_id=session_id,
            role=role,
            content=content,
            intent=intent,
            latency_ms=latency_ms,
            created_at=datetime.now(),
        )

    def get_recent_messages(self, session_id: str, limit: int = 10) -> List[MessageModel]:
        query = "SELECT * FROM conversation_messages WHERE session_id = ? ORDER BY id DESC LIMIT ?"
        rows = self.db.execute_query(query, (session_id, limit))
        results = []
        for r in reversed(rows):
            results.append(
                MessageModel(
                    id=r["id"],
                    session_id=r["session_id"],
                    role=r["role"],
                    content=r["content"],
                    intent=r["intent"],
                    latency_ms=r["latency_ms"],
                    created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else None,
                )
            )
        return results

    def get_summary(self, session_id: str) -> Optional[str]:
        query = "SELECT summary FROM conversation_summaries WHERE session_id = ?"
        rows = self.db.execute_query(query, (session_id,))
        return rows[0]["summary"] if rows else None

    def save_summary(self, session_id: str, summary: str) -> None:
        query = "INSERT OR REPLACE INTO conversation_summaries (session_id, summary, updated_at) VALUES (?, ?, ?)"
        self.db.execute_write(query, (session_id, summary, datetime.now().isoformat()))

    def clear_session(self, session_id: str) -> None:
        self.db.execute_write("DELETE FROM conversation_messages WHERE session_id = ?", (session_id,))
        self.db.execute_write("DELETE FROM conversation_summaries WHERE session_id = ?", (session_id,))


class WorkflowRepository:
    """Repository for logging workflow execution history."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or get_db()

    def record_start(self, workflow_id: str) -> int:
        query = "INSERT INTO workflow_runs (workflow_id, status, started_at) VALUES (?, 'running', ?)"
        return self.db.execute_write(query, (workflow_id, datetime.now().isoformat()))

    def record_finish(self, run_id: int, status: str, error_message: Optional[str] = None) -> None:
        query = "UPDATE workflow_runs SET status = ?, finished_at = ?, error_message = ? WHERE id = ?"
        self.db.execute_write(query, (status, datetime.now().isoformat(), error_message, run_id))


class SettingsRepository:
    """Repository for dynamic key-value preferences."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or get_db()

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        rows = self.db.execute_query("SELECT value FROM key_value_settings WHERE key = ?", (key,))
        return rows[0]["value"] if rows else default

    def set(self, key: str, value: str) -> None:
        self.db.execute_write(
            "INSERT OR REPLACE INTO key_value_settings (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, datetime.now().isoformat()),
        )
