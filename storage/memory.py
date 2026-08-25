"""
In-memory cache and session state for fast runtime access.
"""
from typing import Dict, Any, Optional
import time


class SessionMemory:
    """Thread-safe fast cache for ephemeral state (confirmation tokens, temp context)."""

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._expirations: Dict[str, float] = {}

    def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        self._cache[key] = value
        if ttl_seconds is not None:
            self._expirations[key] = time.time() + ttl_seconds
        elif key in self._expirations:
            del self._expirations[key]

    def get(self, key: str, default: Any = None) -> Any:
        if key in self._expirations and time.time() > self._expirations[key]:
            self.delete(key)
            return default
        return self._cache.get(key, default)

    def delete(self, key: str) -> None:
        self._cache.pop(key, None)
        self._expirations.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()
        self._expirations.clear()
