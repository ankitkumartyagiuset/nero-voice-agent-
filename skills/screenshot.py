"""
Screenshot Capture Skill.
Captures the primary desktop screen and stores it with timestamp in screenshots directory.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from .base import BaseSkill, SkillResult
from utils.logger import get_logger

logger = get_logger("screenshot_skill")


class ScreenshotSkill(BaseSkill):
    name = "screenshot"
    description = "Capture a high-resolution screenshot of the desktop"
    supported_actions = ["take_screenshot"]

    def __init__(self, output_dir: str = "screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def execute(self, action: str, parameters: Dict[str, Any]) -> SkillResult:
        try:
            from PIL import ImageGrab
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            file_path = self.output_dir / filename

            # Capture desktop screen
            screenshot = ImageGrab.grab(all_screens=True)
            screenshot.save(str(file_path), "PNG")

            logger.info(f"Saved screenshot to {file_path}")
            return SkillResult(
                success=True,
                output_message=f"Screenshot saved to {filename}",
                spoken_message="Screenshot captured.",
                data={"path": str(file_path), "filename": filename}
            )
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return SkillResult(
                success=False,
                output_message=f"Failed to capture screenshot: {e}",
                spoken_message="I couldn't take a screenshot."
            )
