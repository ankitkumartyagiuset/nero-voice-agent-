"""
Security policy evaluation and application allowlist validation.
"""
from typing import Dict, Any, List, Optional
from config.settings import SecurityConfig
from utils.logger import get_logger

logger = get_logger("security_policy")


class SecurityPolicy:
    """Security policy guard ensuring zero arbitrary shell execution and valid targets."""

    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self._allowed_protocols = {"http", "https"}

    def is_url_safe(self, url: str) -> bool:
        """Validate if a URL starts with standard web protocols."""
        if not url:
            return False
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.scheme in self._allowed_protocols

    def is_application_safe(self, app_id: str, configured_apps: List[str]) -> bool:
        """Ensure only registered applications in config are permitted."""
        clean_id = app_id.lower().strip()
        return clean_id in [a.lower() for a in configured_apps]

    def contains_injection_patterns(self, text: str) -> bool:
        """Check for dangerous shell characters or blocked command keywords."""
        if not text:
            return False
        lower_text = text.lower()
        for blocked in self.config.blocked_commands:
            if blocked in lower_text:
                logger.warning(f"Blocked dangerous pattern detected in input: '{blocked}'")
                return True
        return False
