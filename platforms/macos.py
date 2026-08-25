"""
macOS system controller implementation.
"""
import subprocess
import psutil
from typing import Dict, Any
from .base import BaseSystemController


class MacOSSystemController(BaseSystemController):
    def set_volume(self, level: int) -> bool:
        try:
            vol_val = max(0, min(100, level))
            subprocess.run(["osascript", "-e", f"set volume output volume {vol_val}"], check=True)
            return True
        except Exception:
            return False

    def get_volume(self) -> int:
        return 50

    def mute(self) -> bool:
        try:
            subprocess.run(["osascript", "-e", "set volume with output muted"], check=True)
            return True
        except Exception:
            return False

    def unmute(self) -> bool:
        try:
            subprocess.run(["osascript", "-e", "set volume without output muted"], check=True)
            return True
        except Exception:
            return False

    def lock_workstation(self) -> bool:
        try:
            subprocess.run(["pmset", "displaysleepnow"], check=True)
            return True
        except Exception:
            return False

    def shutdown(self) -> bool:
        try:
            subprocess.run(["osascript", "-e", 'tell app "System Events" to shut down'], check=True)
            return True
        except Exception:
            return False

    def restart(self) -> bool:
        try:
            subprocess.run(["osascript", "-e", 'tell app "System Events" to restart'], check=True)
            return True
        except Exception:
            return False

    def media_play_pause(self) -> bool:
        try:
            subprocess.run(["osascript", "-e", 'tell application "Music" to playpause'], check=True)
            return True
        except Exception:
            return False

    def media_next(self) -> bool:
        try:
            subprocess.run(["osascript", "-e", 'tell application "Music" to next track'], check=True)
            return True
        except Exception:
            return False

    def media_previous(self) -> bool:
        try:
            subprocess.run(["osascript", "-e", 'tell application "Music" to previous track'], check=True)
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
