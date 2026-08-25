"""
Continuous Subsystem Health Monitoring Service for NERO.
Tracks state of Microphone, STT engine, AI Cloud/Local providers, TTS, and Storage.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from utils.logger import get_logger

logger = get_logger("health_service")


@dataclass
class SubsystemStatus:
    name: str
    status: str  # "READY", "DEGRADED", "FAILED", "OFFLINE"
    message: str = ""


class HealthService:
    """Monitors and reports the health of all subsystems for the HUD status bar."""

    def __init__(self):
        self._statuses: Dict[str, SubsystemStatus] = {
            "mic": SubsystemStatus(name="MIC", status="READY", message="Microphone active"),
            "stt": SubsystemStatus(name="STT", status="READY", message="Speech recognition engine loaded"),
            "ai": SubsystemStatus(name="AI", status="CONNECTED", message="AI Brain online"),
            "tts": SubsystemStatus(name="TTS", status="READY", message="Text to speech ready"),
            "storage": SubsystemStatus(name="DB", status="READY", message="SQLite database connected"),
        }

    def set_status(self, subsystem: str, status: str, message: str = "") -> None:
        if subsystem in self._statuses:
            self._statuses[subsystem].status = status
            self._statuses[subsystem].message = message
            logger.info(f"Health update [{subsystem.upper()}]: {status} - {message}")

    def get_all_statuses(self) -> Dict[str, Dict[str, str]]:
        return {
            k: {"name": v.name, "status": v.status, "message": v.message}
            for k, v in self._statuses.items()
        }


_HEALTH_SERVICE: Optional[HealthService] = None


def get_health_service() -> HealthService:
    global _HEALTH_SERVICE
    if _HEALTH_SERVICE is None:
        _HEALTH_SERVICE = HealthService()
    return _HEALTH_SERVICE
