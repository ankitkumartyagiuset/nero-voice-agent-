"""
Pytest configuration and shared test fixtures for NERO.
Ensures zero real hardware shutdowns, file deletions, or real OS destructions during testing.
"""
import sys
import os
from pathlib import Path
import pytest
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import NeroSettings, AppTarget
from config.loader import load_settings
from storage.database import DatabaseManager


@pytest.fixture
def mock_settings(tmp_path):
    """Create test settings with a temporary SQLite database."""
    db_file = tmp_path / "test_nero.db"
    settings = NeroSettings()
    settings.storage.db_path = str(db_file)
    settings.applications = {
        "vscode": AppTarget(name="Visual Studio Code", windows={"command": "code"}),
        "chrome": AppTarget(name="Google Chrome", windows={"command": "chrome"}),
        "spotify": AppTarget(name="Spotify", windows={"command": "spotify"}),
    }
    return settings


@pytest.fixture
def test_db(tmp_path):
    """Provide a clean temporary SQLite database manager."""
    db_file = tmp_path / "test_nero.db"
    return DatabaseManager(str(db_file))


@pytest.fixture
def sample_audio_chunk():
    """Generate 1024 frames of 16kHz float32 audio."""
    return np.zeros(1024, dtype=np.float32)
