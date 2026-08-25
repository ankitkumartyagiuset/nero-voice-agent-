"""
Reminders Skill for NERO.
Saves, queries, and completes persistent reminders in SQLite.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import re
from .base import BaseSkill, SkillResult
from storage.repositories import ReminderRepository
from utils.logger import get_logger

logger = get_logger("reminders_skill")


class RemindersSkill(BaseSkill):
    name = "reminders"
    description = "Create, list, and complete persistent reminders"
    supported_actions = ["create_reminder", "list_reminders", "complete_reminder"]

    def __init__(self, repo: Optional[ReminderRepository] = None):
        self.repo = repo or ReminderRepository()

    async def execute(self, action: str, parameters: Dict[str, Any]) -> SkillResult:
        if action == "create_reminder":
            message = parameters.get("message", "Reminder")
            time_str = parameters.get("time")
            minutes_ahead = parameters.get("minutes_ahead")

            scheduled_at = datetime.now() + timedelta(minutes=10)
            if minutes_ahead is not None:
                scheduled_at = datetime.now() + timedelta(minutes=int(minutes_ahead))
            elif time_str:
                # Attempt to parse HH:MM or natural time
                try:
                    now = datetime.now()
                    # e.g., "18:00" or "6:00 PM"
                    parsed = self._parse_time(time_str)
                    if parsed:
                        scheduled_at = parsed
                except Exception as e:
                    logger.warning(f"Failed to parse time '{time_str}': {e}")

            model = self.repo.create(message=message, scheduled_at=scheduled_at)
            time_fmt = scheduled_at.strftime("%I:%M %p")
            return SkillResult(
                success=True,
                output_message=f"Reminder set for {time_fmt}: '{message}'",
                spoken_message=f"I've set a reminder for {time_fmt} to {message}.",
                data={"id": model.id, "scheduled_at": scheduled_at.isoformat()}
            )

        elif action == "list_reminders":
            active = self.repo.get_all_active()
            if not active:
                return SkillResult(
                    success=True,
                    output_message="No active reminders.",
                    spoken_message="You have no upcoming reminders."
                )

            summary = [f"• {r.scheduled_at.strftime('%I:%M %p')}: {r.message}" for r in active]
            return SkillResult(
                success=True,
                output_message="Upcoming Reminders:\n" + "\n".join(summary),
                spoken_message=f"You have {len(active)} upcoming reminder{'s' if len(active)>1 else ''}. The next one is: {active[0].message}.",
                data={"reminders": [r.message for r in active]}
            )

        return SkillResult(success=False, output_message=f"Unknown reminder action: {action}")

    def _parse_time(self, time_str: str) -> Optional[datetime]:
        now = datetime.now()
        # Check "in X minutes/hours"
        match_min = re.search(r"(\d+)\s*(?:minute|min)", time_str, re.IGNORECASE)
        if match_min:
            return now + timedelta(minutes=int(match_min.group(1)))

        match_hr = re.search(r"(\d+)\s*(?:hour|hr)", time_str, re.IGNORECASE)
        if match_hr:
            return now + timedelta(hours=int(match_hr.group(1)))

        # Check "6 PM", "6:30 PM", "18:00"
        match_clock = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", time_str, re.IGNORECASE)
        if match_clock:
            hour = int(match_clock.group(1))
            minute = int(match_clock.group(2)) if match_clock.group(2) else 0
            meridiem = match_clock.group(3)
            if meridiem:
                if meridiem.lower() == "pm" and hour < 12:
                    hour += 12
                elif meridiem.lower() == "am" and hour == 12:
                    hour = 0
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target <= now:
                target += timedelta(days=1)
            return target

        return None
