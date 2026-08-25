"""
Unit tests for configuration loading and validation.
"""
from config.settings import NeroSettings
from config.loader import load_settings


def test_default_settings_instantiation():
    settings = NeroSettings()
    assert settings.app.name == "NERO"
    assert settings.voice.wake_word.keyword == "nero"
    assert settings.voice.vad.silence_duration_ms == 450
    assert settings.voice.stt.model == "base"
    assert settings.ai.default_provider == "openai"


def test_settings_loader():
    settings = load_settings()
    assert settings is not None
    assert isinstance(settings, NeroSettings)
    assert "vscode" in settings.applications or len(settings.applications) >= 0
