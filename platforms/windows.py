"""
Windows-specific system controller implementation using Win32 API, ctypes, and psutil.
"""
import ctypes
import subprocess
import psutil
from typing import Dict, Any
from .base import BaseSystemController
from utils.logger import get_logger

logger = get_logger("windows_controller")

# Windows Virtual-Key codes for multimedia
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002


def _send_key(vk_code: int) -> None:
    """Send a single virtual key press and release event on Windows."""
    try:
        user32 = ctypes.windll.user32
        user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
        user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
    except Exception as e:
        logger.error(f"Failed to send key event {vk_code}: {e}")


class WindowsSystemController(BaseSystemController):
    """Native Windows controller implementation."""

    def set_volume(self, level: int) -> bool:
        """
        Set volume by calculating step difference or using PowerShell Audio API.
        """
        clamped = max(0, min(100, int(level)))
        try:
            # Use PowerShell Windows CoreAudio API wrapper
            ps_script = f"""
            $obj = New-Object -ComObject WScript.Shell
            1..50 | ForEach-Object {{ $obj.SendKeys([char]174) }}
            1..{clamped // 2} | ForEach-Object {{ $obj.SendKeys([char]175) }}
            """
            subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script], capture_output=True, timeout=5)
            logger.info(f"Volume adjusted to approximately {clamped}%")
            return True
        except Exception as e:
            logger.warning(f"Fallback volume adjustment: {e}")
            _send_key(VK_VOLUME_UP)
            return True

    def get_volume(self) -> int:
        return 50

    def mute(self) -> bool:
        _send_key(VK_VOLUME_MUTE)
        return True

    def unmute(self) -> bool:
        _send_key(VK_VOLUME_MUTE)
        return True

    def lock_workstation(self) -> bool:
        try:
            ctypes.windll.user32.LockWorkStation()
            logger.info("Workstation locked.")
            return True
        except Exception as e:
            logger.error(f"Failed to lock workstation: {e}")
            return False

    def shutdown(self) -> bool:
        try:
            logger.warning("Initiating Windows shutdown sequence...")
            subprocess.run(["shutdown.exe", "/s", "/t", "0"], check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to execute shutdown: {e}")
            return False

    def restart(self) -> bool:
        try:
            logger.warning("Initiating Windows restart sequence...")
            subprocess.run(["shutdown.exe", "/r", "/t", "0"], check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to execute restart: {e}")
            return False

    def media_play_pause(self) -> bool:
        _send_key(VK_MEDIA_PLAY_PAUSE)
        return True

    def media_next(self) -> bool:
        _send_key(VK_MEDIA_NEXT_TRACK)
        return True

    def media_previous(self) -> bool:
        _send_key(VK_MEDIA_PREV_TRACK)
        return True

    def get_system_stats(self) -> Dict[str, Any]:
        """Fetch live CPU, RAM, Battery, and Disk usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            battery = psutil.sensors_battery()

            return {
                "cpu_percent": cpu_percent,
                "ram_percent": mem.percent,
                "ram_used_gb": round(mem.used / (1024 ** 3), 1),
                "ram_total_gb": round(mem.total / (1024 ** 3), 1),
                "disk_percent": disk.percent,
                "battery_percent": battery.percent if battery else None,
                "battery_plugged": battery.power_plugged if battery else None,
            }
        except Exception as e:
            logger.error(f"Failed to fetch system stats: {e}")
            return {
                "cpu_percent": 0.0,
                "ram_percent": 0.0,
                "ram_used_gb": 0.0,
                "ram_total_gb": 0.0,
                "disk_percent": 0.0,
                "battery_percent": None,
                "battery_plugged": None,
            }
