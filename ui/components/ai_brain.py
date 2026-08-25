"""
AI Brain Live Conversation & Latency Dashboard Component.
Displays real-time user-assistant dialogues and millisecond pipeline benchmarks.
"""
from typing import Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt
from .glass_panel import GlassPanel


class AIBrainPanel(GlassPanel):
    """HUD Card displaying live conversation history, text query input, and latency stats."""

    def __init__(
        self,
        on_text_query: Optional[Callable[[str], None]] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(title="AI BRAIN", parent=parent)
        self._query_callback = on_text_query

        # 1. Header with latency badge
        header_layout = QHBoxLayout()
        self._ai_status = QLabel("● CONNECTED")
        self._ai_status.setStyleSheet("font-size: 11px; color: #00ff88; font-weight: bold;")
        self._latency_badge = QLabel("Latency: 0ms")
        self._latency_badge.setStyleSheet("font-size: 11px; color: #8fa3bf;")
        header_layout.addWidget(self._ai_status)
        header_layout.addStretch()
        header_layout.addWidget(self._latency_badge)
        self.inner_layout.addLayout(header_layout)

        # 2. Conversation Transcript Area
        self._transcript = QTextEdit()
        self._transcript.setReadOnly(True)
        self._transcript.setMinimumHeight(160)
        self._transcript.setStyleSheet("""
            QTextEdit {
                background-color: rgba(4, 8, 18, 0.85);
                border: 1px solid rgba(0, 240, 255, 0.2);
                border-radius: 8px;
                color: #ffffff;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.4;
                padding: 10px;
            }
        """)
        self.inner_layout.addWidget(self._transcript)

        # Initial welcome message
        self.append_message("NERO", "Systems initialized. Listening for 'Nero' or text command.")

        # 3. Direct Text Input Box (Alternative to Voice)
        input_layout = QHBoxLayout()
        self._input_field = QLineEdit()
        self._input_field.setPlaceholderText("Type a command or ask a question...")
        self._input_field.returnPressed.connect(self._on_send)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self._on_send)

        input_layout.addWidget(self._input_field)
        input_layout.addWidget(send_btn)
        self.inner_layout.addLayout(input_layout)

    def _on_send(self) -> None:
        text = self._input_field.text().strip()
        if not text:
            return
        self._input_field.clear()
        self.append_message("USER", text)
        if self._query_callback:
            self._query_callback(text)

    def append_message(self, speaker: str, text: str, latency_ms: Optional[float] = None) -> None:
        """Add styled message entry to transcript."""
        if speaker.upper() == "USER":
            color = "#ff007f"
            prefix = "USER"
        else:
            color = "#00f0ff"
            prefix = "NERO"

        latency_str = f" <span style='color: #8fa3bf; font-size: 10px;'>({latency_ms:.0f}ms)</span>" if latency_ms else ""
        entry_html = f"<div style='margin-bottom: 8px;'><span style='color: {color}; font-weight: bold;'>{prefix}:</span> <span style='color: #ffffff;'>{text}</span>{latency_str}</div>"

        self._transcript.append(entry_html)
        # Scroll to bottom
        sb = self._transcript.verticalScrollBar()
        sb.setValue(sb.maximum())

    def update_latency(self, total_ms: float) -> None:
        self._latency_badge.setText(f"Latency: {total_ms:.0f}ms")
