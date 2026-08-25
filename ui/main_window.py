"""
Master HUD Main Window for NERO AI Desktop Assistant.
Assembles the futuristic cyberpunk control console with glassmorphism layout.
"""
import asyncio
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

from .theme import MAIN_STYLESHEET
from .state_adapter import get_ui_adapter
from .components.glass_panel import GlassPanel
from .components.nero_core import NeroCoreWidget
from .components.waveform import WaveformWidget
from .components.system_control import SystemControlPanel
from .components.daily_info import DailyInfoPanel
from .components.automation_panel import AutomationPanel
from .components.ai_brain import AIBrainPanel
from .components.status_bar import StatusBarWidget
from core.assistant import NeroAssistant
from utils.logger import get_logger

logger = get_logger("main_window")


class NeroMainWindow(QMainWindow):
    """Main Futuristic PySide6 HUD Window for NERO Assistant."""

    def __init__(self, assistant: Optional[NeroAssistant] = None):
        super().__init__()
        self.assistant = assistant
        self.ui_adapter = get_ui_adapter()

        self.setWindowTitle("NERO — Production AI Desktop Console")
        self.setMinimumSize(1200, 720)
        self.resize(1366, 800)
        self.setStyleSheet(MAIN_STYLESHEET)

        self._init_ui()
        self._wire_signals()

    def _init_ui(self) -> None:
        """Construct the HUD layout."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(16, 16, 16, 8)
        root_layout.setSpacing(12)

        # -------------------------------------------------------------
        # Top Header Bar
        # -------------------------------------------------------------
        header_layout = QHBoxLayout()
        header_title = QLabel("N E R O   C O N S O L E")
        header_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00f0ff; letter-spacing: 3px;")

        self._status_badge = QLabel("STATUS: READY")
        self._status_badge.setStyleSheet("font-size: 11px; color: #00ff88; font-weight: bold; letter-spacing: 1px;")

        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addWidget(self._status_badge)
        root_layout.addLayout(header_layout)

        # -------------------------------------------------------------
        # Main Grid Layout (Left Panel, Center Core, Right Panel)
        # -------------------------------------------------------------
        grid_layout = QGridLayout()
        grid_layout.setSpacing(14)

        # 1. Left Column: System Control (Top) & Daily Info (Bottom)
        self.system_control = SystemControlPanel(on_action_callback=self._handle_system_action)
        self.daily_info = DailyInfoPanel()
        grid_layout.addWidget(self.system_control, 0, 0)
        grid_layout.addWidget(self.daily_info, 1, 0)

        # 2. Center Column: Central NERO Core + Real Waveform + Voice Trigger
        center_panel = GlassPanel(title="NERO CORE")
        center_panel.inner_layout.setAlignment(Qt.AlignCenter)

        self.nero_core = NeroCoreWidget()
        center_panel.inner_layout.addWidget(self.nero_core, alignment=Qt.AlignCenter)

        self.waveform = WaveformWidget()
        center_panel.inner_layout.addWidget(self.waveform)

        # Manual Listen / Wake Button
        self.mic_btn = QPushButton("🎤 Click to Speak")
        self.mic_btn.clicked.connect(self._manual_wake_trigger)
        center_panel.inner_layout.addWidget(self.mic_btn, alignment=Qt.AlignCenter)

        grid_layout.addWidget(center_panel, 0, 1, 2, 1)

        # 3. Right Column: Automation Panel (Top) & AI Brain (Bottom)
        self.automation_panel = AutomationPanel(on_toggle_coding_mode=self._handle_coding_mode_toggle)
        self.ai_brain = AIBrainPanel(on_text_query=self._handle_text_query)
        grid_layout.addWidget(self.automation_panel, 0, 2)
        grid_layout.addWidget(self.ai_brain, 1, 2)

        # Set column stretch factors for responsive scaling
        grid_layout.setColumnStretch(0, 3)
        grid_layout.setColumnStretch(1, 4)
        grid_layout.setColumnStretch(2, 4)
        grid_layout.setRowStretch(0, 5)
        grid_layout.setRowStretch(1, 4)

        root_layout.addLayout(grid_layout)

        # -------------------------------------------------------------
        # Bottom Status Bar
        # -------------------------------------------------------------
        self.status_bar = StatusBarWidget()
        root_layout.addWidget(self.status_bar)

    def _wire_signals(self) -> None:
        """Connect UIStateAdapter Qt Signals to update widget visuals."""
        self.ui_adapter.state_changed.connect(self._on_state_changed)
        self.ui_adapter.audio_amplitude_updated.connect(self._on_amplitude_updated)
        self.ui_adapter.transcription_received.connect(self._on_transcription_received)
        self.ui_adapter.workflow_updated.connect(self.automation_panel.update_workflow_progress)

    def _on_state_changed(self, old_state: str, new_state: str) -> None:
        self.nero_core.set_state(new_state)
        self._status_badge.setText(f"STATUS: {new_state}")

        # Color status badge
        if new_state in ("WAKE_DETECTED", "LISTENING"):
            self._status_badge.setStyleSheet("font-size: 11px; color: #ff007f; font-weight: bold; letter-spacing: 1px;")
        elif new_state in ("THINKING", "TRANSCRIBING"):
            self._status_badge.setStyleSheet("font-size: 11px; color: #9d00ff; font-weight: bold; letter-spacing: 1px;")
        elif new_state == "ERROR":
            self._status_badge.setStyleSheet("font-size: 11px; color: #ff3344; font-weight: bold; letter-spacing: 1px;")
        else:
            self._status_badge.setStyleSheet("font-size: 11px; color: #00ff88; font-weight: bold; letter-spacing: 1px;")

    def _on_amplitude_updated(self, amplitude: float) -> None:
        self.waveform.set_amplitude(amplitude)
        self.nero_core.set_amplitude(amplitude)

    def _on_transcription_received(self, text: str, latency_ms: float) -> None:
        self.ai_brain.append_message("USER", text)

    def _manual_wake_trigger(self) -> None:
        if self.assistant:
            self.assistant.wake_detector.trigger_manually()

    def _handle_system_action(self, action: str, params: dict) -> None:
        """Trigger action from UI buttons."""
        if self.assistant:
            asyncio.create_task(self.assistant.process_command(f"{action}"))

    def _handle_text_query(self, query: str) -> None:
        """Trigger command from UI text box."""
        if self.assistant:
            async def _run():
                result = await self.assistant.process_command(query)
                self.ai_brain.append_message("NERO", result)
            asyncio.create_task(_run())

    def _handle_coding_mode_toggle(self, active: bool) -> None:
        if self.assistant:
            cmd = "coding mode on" if active else "stop coding mode"
            asyncio.create_task(self.assistant.process_command(cmd))
