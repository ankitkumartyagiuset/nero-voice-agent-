"""
Central Animated NERO AI Reactor Core Widget.
Custom QPainter visualization with rotating energy rings, pulsing core, and dynamic state colors.
"""
import math
from typing import Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QColor, QRadialGradient, QPen, QBrush, QFont, QPainterPath
)


class NeroCoreWidget(QWidget):
    """Central animated futuristic HUD core widget reacting to assistant states and voice amplitude."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMinimumSize(280, 280)

        self._state = "IDLE"
        self._phase = 0.0
        self._amplitude = 0.0
        self._target_amplitude = 0.0

        # State text mappings
        self._state_subtitles = {
            "STARTING": "INITIALIZING...",
            "IDLE": "READY • SAY \"NERO\"",
            "WAKE_DETECTED": "WAKE DETECTED",
            "LISTENING": "LISTENING...",
            "TRANSCRIBING": "TRANSCRIBING...",
            "THINKING": "PROCESSING...",
            "EXECUTING": "EXECUTING...",
            "SPEAKING": "SPEAKING...",
            "ERROR": "SYSTEM ERROR",
            "STOPPING": "SHUTTING DOWN...",
        }

        # 60 FPS animation timer
        self._timer = QTimer(self)
        self._timer.setInterval(16)  # ~60 FPS
        self._timer.timeout.connect(self._animate_step)
        self._timer.start()

    def set_state(self, state_str: str) -> None:
        self._state = state_str
        self.update()

    def set_amplitude(self, amp: float) -> None:
        self._target_amplitude = max(0.0, min(1.0, amp))

    def _animate_step(self) -> None:
        self._phase += 0.04
        if self._phase > 2 * math.pi * 100:
            self._phase = 0.0

        # Smooth amplitude lerp
        self._amplitude += (self._target_amplitude - self._amplitude) * 0.25
        self.update()

    def _get_state_colors(self) -> tuple[QColor, QColor, QColor]:
        """Return (primary_color, secondary_color, core_color) based on state."""
        if self._state in ("WAKE_DETECTED", "LISTENING"):
            return QColor("#ff007f"), QColor("#00f0ff"), QColor(255, 0, 127, 180)
        elif self._state in ("TRANSCRIBING", "THINKING"):
            return QColor("#9d00ff"), QColor("#00f0ff"), QColor(157, 0, 255, 180)
        elif self._state == "EXECUTING":
            return QColor("#ff9900"), QColor("#00f0ff"), QColor(255, 153, 0, 180)
        elif self._state == "SPEAKING":
            return QColor("#00f0ff"), QColor("#00ff88"), QColor(0, 240, 255, 200)
        elif self._state == "ERROR":
            return QColor("#ff3344"), QColor("#ff007f"), QColor(255, 51, 68, 200)
        else: # IDLE / STARTING
            return QColor("#00f0ff"), QColor("#0070f3"), QColor(0, 240, 255, 120)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        cx = width / 2.0
        cy = height / 2.0
        radius = min(cx, cy) - 20.0

        primary, secondary, core_color = self._get_state_colors()
        amp_scale = 1.0 + (self._amplitude * 0.35)

        # 1. Background glow
        glow_grad = QRadialGradient(cx, cy, radius * 1.2 * amp_scale)
        glow_col = QColor(primary)
        glow_col.setAlpha(int(35 + self._amplitude * 80))
        glow_grad.setColorAt(0.0, glow_col)
        glow_grad.setColorAt(0.7, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(glow_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy), radius * 1.2, radius * 1.2)

        # 2. Outer Rotating Orbital Ring
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self._phase * 40.0)

        outer_pen = QPen(primary, 2.0, Qt.DashLine)
        outer_pen.setDashPattern([6, 12, 18, 12])
        painter.setPen(outer_pen)
        painter.setBrush(Qt.NoBrush)
        r_outer = radius * 0.95 * amp_scale
        painter.drawEllipse(QPointF(0, 0), r_outer, r_outer)

        # Orbital node markers
        for i in range(4):
            angle = i * (math.pi / 2)
            nx = math.cos(angle) * r_outer
            ny = math.sin(angle) * r_outer
            painter.setBrush(QBrush(secondary))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(nx, ny), 3.5, 3.5)
        painter.restore()

        # 3. Middle Counter-Rotating Segmented Ring
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-self._phase * 60.0)

        mid_pen = QPen(secondary, 1.5, Qt.CustomDashLine)
        mid_pen.setDashPattern([14, 8, 4, 8])
        painter.setPen(mid_pen)
        r_mid = radius * 0.78 * amp_scale
        painter.drawEllipse(QPointF(0, 0), r_mid, r_mid)
        painter.restore()

        # 4. Pulsing Inner Reactor Core
        pulse_scale = 1.0 + 0.08 * math.sin(self._phase * 3.0) + (self._amplitude * 0.25)
        r_core = radius * 0.58 * pulse_scale

        core_grad = QRadialGradient(cx, cy, r_core)
        core_grad.setColorAt(0.0, QColor(255, 255, 255, 220))
        core_grad.setColorAt(0.4, core_color)
        core_grad.setColorAt(0.85, QColor(primary.red(), primary.green(), primary.blue(), 60))
        core_grad.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setBrush(QBrush(core_grad))
        painter.setPen(QPen(primary, 2.0))
        painter.drawEllipse(QPointF(cx, cy), r_core, r_core)

        # 5. Core Branding & State Typography
        painter.setPen(QColor("#ffffff"))

        # Brand "NERO"
        brand_font = QFont("Arial", 18, QFont.Bold)
        brand_font.setLetterSpacing(QFont.AbsoluteSpacing, 4)
        painter.setFont(brand_font)
        brand_rect = QRectF(cx - 100, cy - 26, 200, 30)
        painter.drawText(brand_rect, Qt.AlignCenter, "NERO")

        # Dynamic State Subtitle
        sub_text = self._state_subtitles.get(self._state, self._state)
        sub_font = QFont("Segoe UI", 9, QFont.DemiBold)
        sub_font.setLetterSpacing(QFont.AbsoluteSpacing, 1.5)
        painter.setFont(sub_font)
        painter.setPen(primary)
        sub_rect = QRectF(cx - 130, cy + 6, 260, 24)
        painter.drawText(sub_rect, Qt.AlignCenter, sub_text)
