"""
Input command validation and strict schema enforcement.
Guarantees zero arbitrary shell execution from LLM or untrusted inputs.
"""
from typing import Any, Dict, Optional, Tuple
from .permissions import PermissionManager, PermissionLevel
from .policy import SecurityPolicy
from core.exceptions import SecurityError
from utils.logger import get_logger

logger = get_logger("command_validator")


class CommandValidator:
    """Validates structured tool/action calls before execution."""

    def __init__(self, permission_mgr: Optional[PermissionManager] = None, policy: Optional[SecurityPolicy] = None):
        self.permission_mgr = permission_mgr or PermissionManager()
        self.policy = policy or SecurityPolicy()

    def validate_action(self, action: str, params: Dict[str, Any], allowed_apps: list[str]) -> Tuple[bool, str]:
        """
        Validate whether the given action and parameters meet security criteria.
        Returns: (is_valid, error_reason)
        """
        # 1. Check if action is blocked
        perm = self.permission_mgr.get_permission(action)
        if perm == PermissionLevel.BLOCKED:
            msg = f"Action '{action}' is blocked by security policy."
            logger.error(msg)
            return False, msg

        # 2. Check for shell injection strings in parameters
        for k, v in params.items():
            if isinstance(v, str):
                if self.policy.contains_injection_patterns(v):
                    msg = f"Security violation: Parameter '{k}' contains prohibited pattern."
                    logger.error(msg)
                    return False, msg

        # 3. Action-specific validation
        if action == "open_application" or action == "close_application":
            app_name = params.get("application", "")
            if not self.policy.is_application_safe(app_name, allowed_apps):
                msg = f"Application '{app_name}' is not in the configured application allowlist."
                logger.warning(msg)
                return False, msg

        elif action in ("open_url", "search_web", "search_youtube"):
            url = params.get("url", "")
            if url and not self.policy.is_url_safe(url):
                msg = f"URL '{url}' is invalid or uses an insecure protocol."
                logger.warning(msg)
                return False, msg

        elif action == "set_volume":
            vol = params.get("value")
            if vol is None or not (0 <= float(vol) <= 100):
                return False, "Volume level must be an integer between 0 and 100."

        return True, ""
