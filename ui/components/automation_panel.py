"""
Automation Panel Component for NERO HUD.
Controls Coding Mode, monitors active workflows, and tracks scheduled reminders.
"""
from typing import Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from .glass_panel import GlassPanel
from automation.workflow_engine import get_workflow_engine
from storage.repositories import ReminderRepository


class AutomationPanel(GlassPanel):
    """HUD Card managing workflows and reminder triggers."""

    def __init__(
        self,
        on_toggle_coding_mode: Optional[Callable[[bool], None]] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(title="AUTOMATION MODE", parent=parent)
        self._toggle_callback = on_toggle_coding_mode
        self.workflow_engine = get_workflow_engine()
        self.reminder_repo = ReminderRepository()

        self._coding_mode_active = False

        # 1. Coding Mode Card
        coding_header = QHBoxLayout()
        coding_title = QLabel("CODING MODE")
        coding_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #ffffff;")
        self._coding_status_badge = QLabel("OFF")
        self._coding_status_badge.setStyleSheet("color: #ff3344; font-weight: bold;")
        coding_header.addWidget(coding_title)
        coding_header.addStretch()
        coding_header.addWidget(self._coding_status_badge)
        self.inner_layout.addLayout(coding_header)

        coding_desc = QLabel("VS Code • Chrome • GitHub")
        coding_desc.setObjectName("SubtleLabel")
        self.inner_layout.addWidget(coding_desc)

        self._coding_btn = QPushButton("Activate Coding Mode")
        self._coding_btn.clicked.connect(self._toggle_coding_mode)
        self.inner_layout.addWidget(self._coding_btn)

        # Separator
        self.inner_layout.addWidget(self._create_separator())

        # 2. Active Automations Stream
        auto_title = QLabel("ACTIVE AUTOMATIONS")
        auto_title.setObjectName("SubtleLabel")
        self.inner_layout.addWidget(auto_title)

        self._workflow_status_label = QLabel("No active background workflows.")
        self._workflow_status_label.setStyleSheet("font-size: 12px; color: #8fa3bf;")
        self.inner_layout.addWidget(self._workflow_status_label)

        # Separator
        self.inner_layout.addWidget(self._create_separator())

        # 3. Upcoming Reminders
        rem_title = QLabel("SCHEDULED REMINDERS")
        rem_title.setObjectName("SubtleLabel")
        self.inner_layout.addWidget(rem_title)

        self._reminders_label = QLabel("No pending reminders.")
        self._reminders_label.setStyleSheet("font-size: 12px; color: #8fa3bf;")
        self.inner_layout.addWidget(self._reminders_label)

        self.inner_layout.addStretch()
        self.refresh_reminders()

    def _create_separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: rgba(0, 240, 255, 0.15); height: 1px; border: none;")
        return line

    def _toggle_coding_mode(self) -> None:
        self._coding_mode_active = not self._coding_mode_active
        self.set_coding_mode_state(self._coding_mode_active)
        if self._toggle_callback:
            self._toggle_callback(self._coding_mode_active)

    def set_coding_mode_state(self, active: bool) -> None:
        self._coding_mode_active = active
        if active:
            self._coding_status_badge.setText("ON")
            self._coding_status_badge.setStyleSheet("color: #00ff88; font-weight: bold;")
            self._coding_btn.setText("Stop Coding Mode")
            self._coding_btn.setObjectName("DangerButton")
        else:
            self._coding_status_badge.setText("OFF")
            self._coding_status_badge.setStyleSheet("color: #ff3344; font-weight: bold;")
            self._coding_btn.setText("Activate Coding Mode")
            self._coding_btn.setObjectName("")
        self._coding_btn.style().unpolish(self._coding_btn)
        self._coding_btn.style().polish(self._coding_btn)

    def update_workflow_progress(self, wf_id: str, status: str, step_desc: str) -> None:
        if status == "running":
            self._workflow_status_label.setText(f"⚙️ {wf_id}: {step_desc}")
            self._workflow_status_label.setStyleSheet("color: #00f0ff; font-size: 12px;")
        elif status == "completed":
            self._workflow_status_label.setText(f"✓ {wf_id} completed.")
            self._workflow_status_label.setStyleSheet("color: #00ff88; font-size: 12px;")
        elif status == "cancelled":
            self._workflow_status_label.setText(f"⏹ {wf_id} cancelled.")
            self._workflow_status_label.setStyleSheet("color: #8fa3bf; font-size: 12px;")
        elif status == "failed":
            self._workflow_status_label.setText(f"✗ {wf_id} failed: {step_desc}")
            self._workflow_status_label.setStyleSheet("color: #ff3344; font-size: 12px;")

    def refresh_reminders(self) -> None:
        try:
            active = self.reminder_repo.get_all_active()
            if active:
                texts = [f"⏰ {r.scheduled_at.strftime('%I:%M %p')}: {r.message}" for r in active[:2]]
                self._reminders_label.setText("\n".join(texts))
            else:
                self._reminders_label.setText("No pending reminders.")
        except Exception:
            self._reminders_label.setText("Reminders service ready.")
