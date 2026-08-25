"""
Status Bar Component for NERO HUD.
Displays live health indicators for Microphone, STT, AI Brain, TTS, and Storage.
"""
from typing import Optional, Dict
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt


class StatusBarWidget(QFrame):
    """Bottom HUD bar showing real-time subsystem connectivity and health."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedHeight(34)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(6, 11, 24, 0.9);
                border-top: 1px solid rgba(0, 240, 255, 0.2);
                padding: 2px 16px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(20)

        self._labels: Dict[str, QLabel] = {}
        subsystems = [
            ("MIC", "mic", "READY"),
            ("STT", "stt", "READY"),
            ("AI", "ai", "CONNECTED"),
            ("TTS", "tts", "READY"),
            ("DB", "storage", "READY"),
        ]

        for title, key, default_status in subsystems:
            lbl = QLabel(f"{title} ● {default_status}")
            lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #00ff88; letter-spacing: 0.5px;")
            layout.addWidget(lbl)
            self._labels[key] = lbl

        layout.addStretch()

        # System Architecture Tag
        arch_tag = QLabel("NERO ARCHITECTURE • DUAL PATH (FAST + AI)")
        arch_tag.setStyleSheet("font-size: 10px; color: #4f637e; letter-spacing: 1px;")
        layout.addWidget(arch_tag)

    def set_subsystem_status(self, key: str, status: str) -> None:
        if key in self._labels:
            color = "#00ff88" if status in ("READY", "CONNECTED") else ("#ff9900" if status == "DEGRADED" else "#ff3344")
            title = key.upper()
            self._labels[key].setText(f"{title} ● {status}")
            self._labels[key].setStyleSheet(f"font-size: 11px; font-weight: 600; color: {color}; letter-spacing: 0.5px;")
