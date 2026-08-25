"""
Weather Skill for NERO.
Fetches and formats current weather conditions and forecasts.
"""
from typing import Dict, Any
from .base import BaseSkill, SkillResult
from services.weather_service import get_weather_service


class WeatherSkill(BaseSkill):
    name = "weather"
    description = "Report current weather and temperature"
    supported_actions = ["get_weather"]

    def __init__(self):
        self.weather_service = get_weather_service()

    async def execute(self, action: str, parameters: Dict[str, Any]) -> SkillResult:
        city = parameters.get("city", "New Delhi")
        data = self.weather_service.get_current_weather(city=city)

        if not data.get("available", False):
            return SkillResult(
                success=False,
                output_message="Weather service is currently unavailable.",
                spoken_message="Weather service is currently unavailable."
            )

        temp = data.get("temperature_c")
        cond = data.get("condition")
        humidity = data.get("humidity")
        wind = data.get("wind_speed_kmh")

        output_msg = f"Weather in {city}: {cond}, {temp}°C, Humidity: {humidity}%, Wind: {wind} km/h"
        spoken_msg = f"In {city}, it is currently {temp} degrees Celsius with {cond.lower()}."

        return SkillResult(
            success=True,
            output_message=output_msg,
            spoken_message=spoken_msg,
            data=data
        )
