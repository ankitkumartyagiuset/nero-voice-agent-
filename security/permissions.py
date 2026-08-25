"""
Permission Level classification and enforcement for NERO commands.
"""
from enum import Enum, auto
from typing import Dict, Optional
from utils.logger import get_logger

logger = get_logger("permissions")


class PermissionLevel(Enum):
    SAFE = "SAFE"                 # Instant local execution without user confirmation
    CONFIRMATION = "CONFIRMATION" # Requires explicit user confirmation ("yes" / "confirm")
    BLOCKED = "BLOCKED"           # Strictly prohibited under all circumstances


# Map actions to default permission tiers
ACTION_PERMISSION_MAP: Dict[str, PermissionLevel] = {
    # Safe Actions
    "open_application": PermissionLevel.SAFE,
    "close_application": PermissionLevel.SAFE,
    "open_url": PermissionLevel.SAFE,
    "search_web": PermissionLevel.SAFE,
    "search_youtube": PermissionLevel.SAFE,
    "get_time": PermissionLevel.SAFE,
    "get_date": PermissionLevel.SAFE,
    "get_weather": PermissionLevel.SAFE,
    "get_news": PermissionLevel.SAFE,
    "take_screenshot": PermissionLevel.SAFE,
    "set_volume": PermissionLevel.SAFE,
    "mute_volume": PermissionLevel.SAFE,
    "unmute_volume": PermissionLevel.SAFE,
    "media_control": PermissionLevel.SAFE,
    "create_reminder": PermissionLevel.SAFE,
    "list_reminders": PermissionLevel.SAFE,
    "run_workflow": PermissionLevel.SAFE,
    "lock_system": PermissionLevel.SAFE,

    # Confirmation Required Actions
    "shutdown_system": PermissionLevel.CONFIRMATION,
    "restart_system": PermissionLevel.CONFIRMATION,
    "delete_file": PermissionLevel.CONFIRMATION,
    "install_software": PermissionLevel.CONFIRMATION,
    "send_external_message": PermissionLevel.CONFIRMATION,

    # Blocked Actions
    "execute_shell": PermissionLevel.BLOCKED,
    "execute_raw_command": PermissionLevel.BLOCKED,
    "format_drive": PermissionLevel.BLOCKED,
    "extract_credentials": PermissionLevel.BLOCKED,
}


class PermissionManager:
    """Evaluates and enforces permission rules before executing any action."""

    def __init__(self, custom_overrides: Optional[Dict[str, PermissionLevel]] = None):
        self._rules = ACTION_PERMISSION_MAP.copy()
        if custom_overrides:
            self._rules.update(custom_overrides)

    def get_permission(self, action: str) -> PermissionLevel:
        """Return the permission tier for a given action name."""
        return self._rules.get(action, PermissionLevel.BLOCKED)

    def is_safe(self, action: str) -> bool:
        return self.get_permission(action) == PermissionLevel.SAFE

    def requires_confirmation(self, action: str) -> bool:
        return self.get_permission(action) == PermissionLevel.CONFIRMATION

    def is_blocked(self, action: str) -> bool:
        return self.get_permission(action) == PermissionLevel.BLOCKED
