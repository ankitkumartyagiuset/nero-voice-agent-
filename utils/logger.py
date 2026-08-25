"""
Structured and secure logging system for NERO.
Ensures API keys, tokens, and sensitive personal information are masked in all logs.
"""
import logging
import os
import re
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

# Patterns for sensitive keys that should be masked
SENSITIVE_PATTERNS = [
    re.compile(r'(sk-[A-Za-z0-9-_]{20,})', re.IGNORECASE),
    re.compile(r'(AIzaSy[A-Za-z0-9-_]{33})', re.IGNORECASE),
    re.compile(r'(api[_-]?key[:=]\s*["\']?)([^"\'\s]{8,})', re.IGNORECASE),
    re.compile(r'(authorization[:=]\s*Bearer\s+)([^"\'\s]{8,})', re.IGNORECASE),
    re.compile(r'(password[:=]\s*["\']?)([^"\'\s]+)', re.IGNORECASE),
]


def mask_sensitive_data(message: str) -> str:
    """Mask credentials, API keys, and sensitive tokens in text."""
    if not isinstance(message, str):
        return str(message)
    masked = message
    for pattern in SENSITIVE_PATTERNS:
        def _repl(match):
            if len(match.groups()) == 1:
                val = match.group(1)
                return val[:4] + "*" * (len(val) - 8) + val[-4:] if len(val) > 8 else "****"
            elif len(match.groups()) == 2:
                prefix = match.group(1)
                val = match.group(2)
                return prefix + (val[:3] + "..." + val[-3:] if len(val) > 6 else "****")
            return "[REDACTED]"
        masked = pattern.sub(_repl, masked)
    return masked


class SafeFormatter(logging.Formatter):
    """Custom logging formatter that automatically redacts secrets."""

    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        return mask_sensitive_data(original)


_ROOT_LOGGER: Optional[logging.Logger] = None


def setup_logger(
    name: str = "nero",
    log_file: str = "nero.log",
    level: str = "INFO",
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
) -> logging.Logger:
    """Set up and return the application logger."""
    global _ROOT_LOGGER
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = SafeFormatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.addHandler(console_handler)

    # File Handler
    try:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"[WARN] Failed to initialize file logger: {e}")

    _ROOT_LOGGER = logger
    return logger


def get_logger(name: str = "nero") -> logging.Logger:
    """Get or create logger instance."""
    global _ROOT_LOGGER
    if _ROOT_LOGGER is None:
        return setup_logger(name)
    return logging.getLogger(f"nero.{name}" if name != "nero" else "nero")
