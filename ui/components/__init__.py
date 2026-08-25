"""UI Components for NERO Desktop Assistant."""
from .glass_panel import GlassPanel
from .nero_core import NeroCoreWidget
from .waveform import WaveformWidget
from .system_control import SystemControlPanel
from .daily_info import DailyInfoPanel
from .automation_panel import AutomationPanel
from .ai_brain import AIBrainPanel
from .status_bar import StatusBarWidget
from .app_launcher import AppLauncherDock

__all__ = [
    "GlassPanel",
    "NeroCoreWidget",
    "WaveformWidget",
    "SystemControlPanel",
    "DailyInfoPanel",
    "AutomationPanel",
    "AIBrainPanel",
    "StatusBarWidget",
    "AppLauncherDock",
]
