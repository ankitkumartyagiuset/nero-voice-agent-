"""
General utility helper functions for NERO.
"""
import sys
import platform
from datetime import datetime
from typing import Tuple


def get_current_time_str() -> str:
    """Format current time cleanly for voice and HUD."""
    now = datetime.now()
    return now.strftime("%I:%M %p")


def get_current_date_str() -> str:
    """Format current date cleanly."""
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y")


def is_windows() -> bool:
    return sys.platform.startswith("win") or platform.system() == "Windows"


def is_macos() -> bool:
    return sys.platform.startswith("darwin") or platform.system() == "Darwin"


def is_linux() -> bool:
    return sys.platform.startswith("linux") or platform.system() == "Linux"


def normalize_text(text: str) -> str:
    """Normalize spoken command text for intent routing."""
    if not text:
        return ""
    # Strip whitespace, lowercase, remove trailing punctuation
    cleaned = text.strip().lower()
    cleaned = cleaned.rstrip(".?!,:;")
    # Collapse multiple spaces
    return " ".join(cleaned.split())


def clean_voice_response(text: str) -> str:
    """Strip markdown symbols (code blocks, bold, stars) for spoken output."""
    if not text:
        return ""
    import re
    # Remove markdown bold/italics
    cleaned = re.sub(r'[*_`#~]', '', text)
    # Remove urls
    cleaned = re.sub(r'https?://\S+', 'link', cleaned)
    # Clean whitespace
    return " ".join(cleaned.split())
