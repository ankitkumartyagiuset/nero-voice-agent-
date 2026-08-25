"""
Secret token utilities and two-phase confirmation helpers.
"""
import uuid
import time
from typing import Dict, Optional, Tuple


class ConfirmationTokenManager:
    """Manages ephemeral single-use confirmation tokens for dangerous operations."""

    def __init__(self, timeout_seconds: int = 15):
        self.timeout_seconds = timeout_seconds
        self._tokens: Dict[str, Tuple[str, Dict, float]] = {}  # token -> (action, params, expires_at)

    def generate_token(self, action: str, params: Optional[Dict] = None) -> str:
        token = str(uuid.uuid4())[:8]
        expires_at = time.time() + self.timeout_seconds
        self._tokens[token] = (action, params or {}, expires_at)
        return token

    def verify_and_consume(self, token: str) -> Optional[Tuple[str, Dict]]:
        """Verify token and return (action, params) if valid and not expired."""
        if token not in self._tokens:
            return None
        action, params, expires_at = self._tokens.pop(token)
        if time.time() > expires_at:
            return None
        return action, params

    def get_latest_pending(self) -> Optional[Tuple[str, str, Dict]]:
        """Return the newest unexpired pending confirmation token and action."""
        now = time.time()
        # Clean expired
        expired = [k for k, v in self._tokens.items() if now > v[2]]
        for k in expired:
            self._tokens.pop(k, None)

        if not self._tokens:
            return None
        # Return newest
        latest_token = list(self._tokens.keys())[-1]
        action, params, _ = self._tokens[latest_token]
        return latest_token, action, params

    def consume_latest(self) -> Optional[Tuple[str, Dict]]:
        pending = self.get_latest_pending()
        if not pending:
            return None
        token, _, _ = pending
        return self.verify_and_consume(token)


_GLOBAL_CONFIRMATION_MGR: Optional[ConfirmationTokenManager] = None


def generate_confirmation_token(action: str, params: Optional[Dict] = None) -> str:
    global _GLOBAL_CONFIRMATION_MGR
    if _GLOBAL_CONFIRMATION_MGR is None:
        _GLOBAL_CONFIRMATION_MGR = ConfirmationTokenManager()
    return _GLOBAL_CONFIRMATION_MGR.generate_token(action, params)


def get_confirmation_manager() -> ConfirmationTokenManager:
    global _GLOBAL_CONFIRMATION_MGR
    if _GLOBAL_CONFIRMATION_MGR is None:
        _GLOBAL_CONFIRMATION_MGR = ConfirmationTokenManager()
    return _GLOBAL_CONFIRMATION_MGR
