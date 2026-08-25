"""
System Control Panel Component for NERO HUD.
Controls Applications, Master Volume, Screenshots, Screen Lock, and System Shutdown.
"""
from typing import Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QFrame
)
from PySide6.QtCore import Qt
from .glass_panel import GlassPanel
from .app_launcher import AppLauncherDock


class SystemControlPanel(GlassPanel):
    """HUD Card for direct laptop control."""

    def __init__(
        self,
        on_action_callback: Optional[Callable[[str, dict], None]] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(title="SYSTEM CONTROL", parent=parent)
        self._callback = on_action_callback

        # 1. App Launchers Dock
        app_label = QLabel("LAUNCH APPLICATIONS")
        app_label.setObjectName("SubtleLabel")
        self.inner_layout.addWidget(app_label)

        self._dock = AppLauncherDock(on_launch_callback=self._launch_app)
        self.inner_layout.addWidget(self._dock)

        # Separator line
        self.inner_layout.addWidget(self._create_separator())

        # 2. Master Volume Slider
        vol_header = QHBoxLayout()
        vol_title = QLabel("SYSTEM VOLUME")
        vol_title.setObjectName("SubtleLabel")
        self._vol_val_label = QLabel("50%")
        self._vol_val_label.setStyleSheet("color: #00f0ff; font-weight: bold;")
        vol_header.addWidget(vol_title)
        vol_header.addStretch()
        vol_header.addWidget(self._vol_val_label)
        self.inner_layout.addLayout(vol_header)

        self._vol_slider = QSlider(Qt.Horizontal)
        self._vol_slider.setRange(0, 100)
        self._vol_slider.setValue(50)
        self._vol_slider.valueChanged.connect(self._on_volume_changed)
        self.inner_layout.addWidget(self._vol_slider)

        # Mute / Unmute buttons
        vol_btns = QHBoxLayout()
        mute_btn = QPushButton("Mute")
        mute_btn.clicked.connect(lambda: self._trigger_action("mute_volume", {}))
        unmute_btn = QPushButton("Unmute")
        unmute_btn.clicked.connect(lambda: self._trigger_action("unmute_volume", {}))
        vol_btns.addWidget(mute_btn)
        vol_btns.addWidget(unmute_btn)
        self.inner_layout.addLayout(vol_btns)

        # Separator line
        self.inner_layout.addWidget(self._create_separator())

        # 3. Hardware & Screen Action Buttons
        act_header = QLabel("DESKTOP UTILITIES")
        act_header.setObjectName("SubtleLabel")
        self.inner_layout.addWidget(act_header)

        util_layout = QHBoxLayout()
        screenshot_btn = QPushButton("📷 Screenshot")
        screenshot_btn.clicked.connect(lambda: self._trigger_action("take_screenshot", {}))

        lock_btn = QPushButton("🔒 Lock PC")
        lock_btn.clicked.connect(lambda: self._trigger_action("lock_system", {}))

        util_layout.addWidget(screenshot_btn)
        util_layout.addWidget(lock_btn)
        self.inner_layout.addLayout(util_layout)

        # 4. Dangerous Action Buttons
        danger_layout = QHBoxLayout()
        shutdown_btn = QPushButton("⚠️ Shutdown")
        shutdown_btn.setObjectName("DangerButton")
        shutdown_btn.clicked.connect(lambda: self._trigger_action("shutdown_system", {}))

        restart_btn = QPushButton("🔄 Restart")
        restart_btn.setObjectName("DangerButton")
        restart_btn.clicked.connect(lambda: self._trigger_action("restart_system", {}))

        danger_layout.addWidget(shutdown_btn)
        danger_layout.addWidget(restart_btn)
        self.inner_layout.addLayout(danger_layout)

        self.inner_layout.addStretch()

    def _create_separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: rgba(0, 240, 255, 0.15); height: 1px; border: none;")
        return line

    def _launch_app(self, app_id: str) -> None:
        self._trigger_action("open_application", {"application": app_id})

    def _on_volume_changed(self, val: int) -> None:
        self._vol_val_label.setText(f"{val}%")
        self._trigger_action("set_volume", {"value": val})

    def _trigger_action(self, action: str, params: dict) -> None:
        if self._callback:
            self._callback(action, params)
