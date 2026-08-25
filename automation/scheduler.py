"""
Background Reminder and Recurring Task Scheduler for NERO.
Survives application restarts by checking SQLite database periodically.
"""
import asyncio
import threading
import time
from datetime import datetime
from typing import Optional, Callable
from storage.repositories import ReminderRepository
from core.event_bus import get_event_bus
from core.events import Event
from utils.logger import get_logger

logger = get_logger("scheduler")


class ReminderScheduler:
    """Monitors scheduled reminders in background thread/task."""

    def __init__(self, repo: Optional[ReminderRepository] = None, check_interval_seconds: float = 5.0):
        self.repo = repo or ReminderRepository()
        self.check_interval = check_interval_seconds
        self.event_bus = get_event_bus()
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._callback: Optional[Callable[[str], None]] = None

    def set_alert_callback(self, callback: Callable[[str], None]) -> None:
        """Register a callback when a reminder is triggered (e.g. speak message)."""
        self._callback = callback

    async def start(self) -> None:
        """Start the background monitoring loop."""
        self._running = True
        logger.info("Reminder scheduler started.")
        while self._running:
            try:
                now = datetime.now()
                pending = self.repo.get_pending(now)
                for reminder in pending:
                    logger.info(f"Triggering scheduled reminder: {reminder.message}")
                    # Mark completed in DB
                    self.repo.mark_completed(reminder.id)

                    # Trigger alert callback
                    if self._callback:
                        self._callback(reminder.message)

            except Exception as e:
                logger.error(f"Error checking scheduled reminders: {e}")

            await asyncio.sleep(self.check_interval)

    def stop(self) -> None:
        self._running = False
        logger.info("Reminder scheduler stopped.")


_GLOBAL_SCHEDULER: Optional[ReminderScheduler] = None


def get_scheduler() -> ReminderScheduler:
    global _GLOBAL_SCHEDULER
    if _GLOBAL_SCHEDULER is None:
        _GLOBAL_SCHEDULER = ReminderScheduler()
    return _GLOBAL_SCHEDULER
