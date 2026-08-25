"""
Media Controls Skill.
Emulates media keys for Play, Pause, Next Track, and Previous Track.
"""
from typing import Dict, Any
from .base import BaseSkill, SkillResult
from platforms import get_platform_controller


class MediaSkill(BaseSkill):
    name = "media"
    description = "Control media playback (play, pause, next, previous)"
    supported_actions = ["media_control", "media_play_pause", "media_next", "media_previous"]

    def __init__(self):
        self.controller = get_platform_controller()

    async def execute(self, action: str, parameters: Dict[str, Any]) -> SkillResult:
        sub_action = parameters.get("command") or action

        if sub_action in ("play", "pause", "play_pause", "media_play_pause", "media_control"):
            self.controller.media_play_pause()
            return SkillResult(success=True, output_message="Media playback toggled.", spoken_message="Toggled media.")

        elif sub_action in ("next", "next_track", "media_next"):
            self.controller.media_next()
            return SkillResult(success=True, output_message="Skipped to next track.", spoken_message="Next track.")

        elif sub_action in ("previous", "prev", "media_previous"):
            self.controller.media_previous()
            return SkillResult(success=True, output_message="Returning to previous track.", spoken_message="Previous track.")

        return SkillResult(success=False, output_message=f"Unknown media action: {sub_action}")
