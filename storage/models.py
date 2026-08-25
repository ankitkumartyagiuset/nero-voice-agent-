"""
Data models and DTOs for persistent database entities.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ReminderModel:
    id: Optional[int]
    message: str
    scheduled_at: datetime
    status: str = "pending"  # "pending", "completed", "cancelled"
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class MessageModel:
    id: Optional[int]
    session_id: str
    role: str  # "user", "assistant", "system"
    content: str
    intent: Optional[str] = None
    latency_ms: Optional[float] = None
    created_at: Optional[datetime] = None


@dataclass
class WorkflowRunModel:
    id: Optional[int]
    workflow_id: str
    status: str  # "running", "completed", "failed", "cancelled"
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None
