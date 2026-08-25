"""
News Skill for NERO.
Fetches and reads out top technology and global news headlines.
"""
from typing import Dict, Any
from .base import BaseSkill, SkillResult
from services.news_service import get_news_service


class NewsSkill(BaseSkill):
    name = "news"
    description = "Fetch top news and technology headlines"
    supported_actions = ["get_news"]

    def __init__(self):
        self.news_service = get_news_service()

    async def execute(self, action: str, parameters: Dict[str, Any]) -> SkillResult:
        articles = self.news_service.get_latest_headlines(limit=3)
        if not articles:
            return SkillResult(
                success=False,
                output_message="News service is currently unavailable.",
                spoken_message="I couldn't fetch the news right now."
            )

        titles = [a["title"] for a in articles]
        output_msg = "Top Headlines:\n" + "\n".join(f"• {t}" for t in titles)
        spoken_msg = f"Here are the top headlines. First: {titles[0]}."
        if len(titles) > 1:
            spoken_msg += f" Second: {titles[1]}."

        return SkillResult(
            success=True,
            output_message=output_msg,
            spoken_message=spoken_msg,
            data={"articles": articles}
        )
