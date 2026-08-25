"""
Search Skill for NERO.
Delegates to web or local queries.
"""
from typing import Dict, Any
from .base import BaseSkill, SkillResult
from .browser import BrowserSkill


class SearchSkill(BaseSkill):
    name = "search"
    description = "Search the web or specific sites"
    supported_actions = ["general_search"]

    def __init__(self):
        self.browser_skill = BrowserSkill()

    async def execute(self, action: str, parameters: Dict[str, Any]) -> SkillResult:
        query = parameters.get("query", "")
        return await self.browser_skill.execute("search_web", {"query": query})
