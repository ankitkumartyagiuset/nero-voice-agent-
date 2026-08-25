"""
Configuration loader for NERO assistant.
Reads YAML configuration and environment variables.
"""
import os
import yaml
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from .settings import NeroSettings

_GLOBAL_SETTINGS: Optional[NeroSettings] = None


def load_settings(config_path: Optional[str] = None) -> NeroSettings:
    """
    Load settings from YAML file with environment variable overrides.
    """
    global _GLOBAL_SETTINGS

    # Load environment variables from .env if present
    env_path = Path(".env")
    if not env_path.exists():
        env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)

    # Determine YAML configuration path
    if config_path:
        target_path = Path(config_path)
    else:
        # Check standard locations
        candidates = [
            Path("config.yaml"),
            Path("config/config.yaml"),
            Path(__file__).parent / "config.yaml",
            Path(__file__).parent / "config.example.yaml",
        ]
        target_path = None
        for cand in candidates:
            if cand.exists():
                target_path = cand
                break

    data = {}
    if target_path and target_path.exists():
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[WARN] Failed to read configuration from {target_path}: {e}")

    # Build Pydantic model
    settings = NeroSettings(**data)

    # Override secrets from environment variables
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        settings.ai.openai.api_key = openai_key

    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        settings.ai.gemini.api_key = gemini_key

    local_url = os.getenv("LOCAL_LLM_URL")
    if local_url:
        settings.ai.local.base_url = local_url

    env_name = os.getenv("NERO_ENV")
    if env_name:
        settings.app.env = env_name

    _GLOBAL_SETTINGS = settings
    return settings


def get_settings() -> NeroSettings:
    """Return cached settings or load defaults."""
    global _GLOBAL_SETTINGS
    if _GLOBAL_SETTINGS is None:
        return load_settings()
    return _GLOBAL_SETTINGS
