"""
System Control Skill.
Manages Volume, Mute, System Lock, and confirmation-gated Shutdown / Restart.
"""
from typing import Dict, Any
from .base import BaseSkill, SkillResult
from platforms import get_platform_controller
from security.secrets import generate_confirmation_token
from utils.logger import get_logger

logger = get_logger("system_skill")


class SystemSkill(BaseSkill):
    name = "system"
    description = "Control volume, lock computer, or safely shut down / restart system"
    supported_actions = [
        "set_volume", "mute_volume", "unmute_volume",
        "lock_system", "shutdown_system", "restart_system", "get_system_stats"
    ]

    def __init__(self):
        self.controller = get_platform_controller()

    async def execute(self, action: str, parameters: Dict[str, Any]) -> SkillResult:
        # Check if confirmed flag is passed (post-confirmation)
        is_confirmed = parameters.get("confirmed", False)

        if action == "set_volume":
            val = parameters.get("value", 50)
            try:
                level = int(val)
                self.controller.set_volume(level)
                return SkillResult(
                    success=True,
                    output_message=f"Volume set to {level}%.",
                    spoken_message=f"Volume set to {level} percent."
                )
            except Exception as e:
                return SkillResult(success=False, output_message=f"Failed to set volume: {e}")

        elif action == "mute_volume":
            self.controller.mute()
            return SkillResult(success=True, output_message="System audio muted.", spoken_message="Muted.")

        elif action == "unmute_volume":
            self.controller.unmute()
            return SkillResult(success=True, output_message="System audio unmuted.", spoken_message="Unmuted.")

        elif action == "lock_system":
            self.controller.lock_workstation()
            return SkillResult(success=True, output_message="Workstation locked.", spoken_message="Locking system.")

        elif action == "shutdown_system":
            if not is_confirmed:
                token = generate_confirmation_token("shutdown_system", parameters)
                return SkillResult(
                    success=False,
                    output_message="System shutdown requires explicit confirmation.",
                    spoken_message="Shutdown requires confirmation. Continue?",
                    requires_confirmation=True,
                    confirmation_token=token,
                )
            self.controller.shutdown()
            return SkillResult(success=True, output_message="Initiating system shutdown.", spoken_message="Shutting down.")

        elif action == "restart_system":
            if not is_confirmed:
                token = generate_confirmation_token("restart_system", parameters)
                return SkillResult(
                    success=False,
                    output_message="System restart requires explicit confirmation.",
                    spoken_message="Restart requires confirmation. Continue?",
                    requires_confirmation=True,
                    confirmation_token=token,
                )
            self.controller.restart()
            return SkillResult(success=True, output_message="Initiating system restart.", spoken_message="Restarting.")

        elif action == "get_system_stats":
            stats = self.controller.get_system_stats()
            cpu = stats.get("cpu_percent", 0)
            ram = stats.get("ram_percent", 0)
            return SkillResult(
                success=True,
                output_message=f"CPU: {cpu}% | RAM: {ram}%",
                spoken_message=f"CPU usage is at {cpu} percent, memory is at {ram} percent.",
                data=stats
            )

        return SkillResult(success=False, output_message=f"Unknown system action: {action}")
