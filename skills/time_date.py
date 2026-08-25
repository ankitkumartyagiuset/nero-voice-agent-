"""
Time & Date Skill for NERO.
Provides precise local system time and calendar date.
"""
from typing import Dict, Any
from .base import BaseSkill, SkillResult
from utils.helpers import get_current_time_str, get_current_date_str


class TimeDateSkill(BaseSkill):
    name = "time_date"
    description = "Report current system time and date"
    supported_actions = ["get_time", "get_date"]

    async def execute(self, action: str, parameters: Dict[str, Any]) -> SkillResult:
        if action == "get_time":
            time_str = get_current_time_str()
            return SkillResult(
                success=True,
                output_message=f"Current Time: {time_str}",
                spoken_message=f"It is {time_str}."
            )
        elif action == "get_date":
            date_str = get_current_date_str()
            return SkillResult(
                success=True,
                output_message=f"Current Date: {date_str}",
                spoken_message=f"Today is {date_str}."
            )
        return SkillResult(success=False, output_message=f"Unknown action {action}")
