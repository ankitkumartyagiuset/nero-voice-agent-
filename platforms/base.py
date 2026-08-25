"""
Abstract Base System Controller.
Defines required interface for laptop hardware and OS functions.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseSystemController(ABC):
    """Abstract interface for native desktop OS operations."""

    @abstractmethod
    def set_volume(self, level: int) -> bool:
        """Set master volume (0 to 100)."""
        pass

    @abstractmethod
    def get_volume(self) -> int:
        """Get current master volume level (0 to 100)."""
        pass

    @abstractmethod
    def mute(self) -> bool:
        """Mute system audio."""
        pass

    @abstractmethod
    def unmute(self) -> bool:
        """Unmute system audio."""
        pass

    @abstractmethod
    def lock_workstation(self) -> bool:
        """Lock the computer screen."""
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """Initiate system shutdown."""
        pass

    @abstractmethod
    def restart(self) -> bool:
        """Initiate system restart."""
        pass

    @abstractmethod
    def media_play_pause(self) -> bool:
        """Send play/pause media key."""
        pass

    @abstractmethod
    def media_next(self) -> bool:
        """Send next track media key."""
        pass

    @abstractmethod
    def media_previous(self) -> bool:
        """Send previous track media key."""
        pass

    @abstractmethod
    def get_system_stats(self) -> Dict[str, Any]:
        """Return CPU, RAM, Battery, and Disk usage stats."""
        pass
