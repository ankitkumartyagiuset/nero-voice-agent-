"""
Browser & Web Navigation Skill.
Opens URLs, YouTube search, and general queries in default browser.
"""
import urllib.parse
import webbrowser
from typing import Dict, Any
from .base import BaseSkill, SkillResult
from utils.logger import get_logger

logger = get_logger("browser_skill")


class BrowserSkill(BaseSkill):
    name = "browser"
    description = "Open web pages, search Google, or search YouTube"
    supported_actions = ["open_url", "search_web", "search_youtube"]

    async def execute(self, action: str, parameters: Dict[str, Any]) -> SkillResult:
        if action == "open_url":
            url = parameters.get("url", "").strip()
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"
            webbrowser.open(url)
            return SkillResult(
                success=True,
                output_message=f"Opened URL: {url}",
                spoken_message=f"Opening website."
            )

        elif action == "search_web":
            query = parameters.get("query", "").strip()
            if not query:
                return SkillResult(success=False, output_message="No search query provided.", spoken_message="What should I search for?")
            encoded = urllib.parse.quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded}"
            webbrowser.open(search_url)
            return SkillResult(
                success=True,
                output_message=f"Searching web for: {query}",
                spoken_message=f"Searching for {query}."
            )

        elif action == "search_youtube":
            query = parameters.get("query", "").strip()
            if not query:
                return SkillResult(success=False, output_message="No YouTube query provided.", spoken_message="What should I look for on YouTube?")
            encoded = urllib.parse.quote_plus(query)
            yt_url = f"https://www.youtube.com/results?search_query={encoded}"
            webbrowser.open(yt_url)
            return SkillResult(
                success=True,
                output_message=f"Searching YouTube for: {query}",
                spoken_message=f"Searching YouTube for {query}."
            )

        return SkillResult(success=False, output_message=f"Unknown browser action: {action}")
