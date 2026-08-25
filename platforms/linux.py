"""
Linux system controller implementation.
"""
import subprocess
import psutil
from typing import Dict, Any
from .base import BaseSystemController


class LinuxSystemController(BaseSystemController):
    def set_volume(self, level: int) -> bool:
        try:
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{level}%"], check=True)
            return True
        except Exception:
            return False

    def get_volume(self) -> int:
        return 50

    def mute(self) -> bool:
        try:
            subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"], check=True)
            return True
        except Exception:
            return False

    def unmute(self) -> bool:
        try:
            subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"], check=True)
            return True
        except Exception:
            return False

    def lock_workstation(self) -> bool:
        try:
            subprocess.run(["loginctl", "lock-session"], check=True)
            return True
        except Exception:
            return False

    def shutdown(self) -> bool:
        try:
            subprocess.run(["shutdown", "now"], check=True)
            return True
        except Exception:
            return False

    def restart(self) -> bool:
        try:
            subprocess.run(["reboot"], check=True)
            return True
        except Exception:
            return False

    def media_play_pause(self) -> bool:
        try:
            subprocess.run(["playerctl", "play-pause"], check=True)
            return True
        except Exception:
            return False

    def media_next(self) -> bool:
        try:
            subprocess.run(["playerctl", "next"], check=True)
            return True
        except Exception:
            return False

    def media_previous(self) -> bool:
        try:
            subprocess.run(["playerctl", "previous"], check=True)
            return True
        except Exception:
            return False

    def get_system_stats(self) -> Dict[str, Any]:
        try:
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            battery = psutil.sensors_battery()
            return {
                "cpu_percent": psutil.cpu_percent(),
                "ram_percent": mem.percent,
                "ram_used_gb": round(mem.used / (1024 ** 3), 1),
                "ram_total_gb": round(mem.total / (1024 ** 3), 1),
                "disk_percent": disk.percent,
                "battery_percent": battery.percent if battery else None,
                "battery_plugged": battery.power_plugged if battery else None,
            }
        except Exception:
            return {}
