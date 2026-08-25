"""
Real Weather Service using Open-Meteo REST API (free, reliable, no API key required).
"""
import requests
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger("weather_service")

# WMO Weather interpretation codes
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


class WeatherService:
    """Fetches real current weather and forecasts via Open-Meteo."""

    def __init__(self):
        self._cached_weather: Optional[Dict[str, Any]] = None
        self._last_fetch_time: float = 0.0

    def get_current_weather(self, city: str = "New Delhi", lat: float = 28.6139, lon: float = 77.2090) -> Dict[str, Any]:
        """Fetch current weather data from Open-Meteo."""
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&timezone=auto"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                temp = current.get("temperature_2m", 0)
                humidity = current.get("relative_humidity_2m", 0)
                wind = current.get("wind_speed_10m", 0)
                wcode = current.get("weather_code", 0)
                condition = WMO_CODES.get(wcode, "Clear")

                result = {
                    "available": True,
                    "city": city,
                    "temperature_c": round(temp, 1),
                    "humidity": humidity,
                    "wind_speed_kmh": round(wind, 1),
                    "condition": condition,
                    "weather_code": wcode,
                }
                self._cached_weather = result
                return result
            else:
                logger.warning(f"Open-Meteo returned status code {resp.status_code}")
        except Exception as e:
            logger.error(f"Failed to fetch weather: {e}")

        # Fallback to cache or graceful degraded response
        if self._cached_weather:
            return self._cached_weather

        return {
            "available": False,
            "city": city,
            "temperature_c": None,
            "condition": "Unavailable",
            "error": "Weather service is currently unavailable."
        }


_WEATHER_SERVICE: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    global _WEATHER_SERVICE
    if _WEATHER_SERVICE is None:
        _WEATHER_SERVICE = WeatherService()
    return _WEATHER_SERVICE
