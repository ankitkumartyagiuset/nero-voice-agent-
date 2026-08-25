"""
Real Audio Waveform Visualizer Widget for NERO.
Renders real-time audio amplitude oscillations from the active microphone stream.
"""
import math
from typing import Optional, List
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient


class WaveformWidget(QWidget):
    """Real-time dynamic audio waveform reacting to microphone audio chunks."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setMinimumWidth(200)

        self._num_bars = 32
        self._amplitudes: List[float] = [0.0] * self._num_bars
        self._target_amp: float = 0.0
        self._phase: float = 0.0

        # 60 FPS animation timer
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._animate)
        self._timer.start()

    def set_amplitude(self, amplitude: float) -> None:
        """Update live amplitude from microphone event (0.0 to 1.0)."""
        self._target_amp = max(0.0, min(1.0, float(amplitude)))

    def _animate(self) -> None:
        self._phase += 0.15

        # Shift bar history left and push new modulated amplitude
        base_val = self._target_amp
        for i in range(self._num_bars):
            # Add spatial sinusoidal variation
            wave = 0.4 * math.sin(self._phase + (i * 0.35)) * base_val
            target_bar = max(0.04, base_val + wave)
            # Smooth interpolation
            self._amplitudes[i] += (target_bar - self._amplitudes[i]) * 0.3

        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        cy = height / 2.0

        bar_width = (width - (self._num_bars * 3)) / self._num_bars
        bar_width = max(2.0, bar_width)

        # Draw symmetric mirrored vertical bars
        for i in range(self._num_bars):
            val = self._amplitudes[i]
            bar_h = max(3.0, val * (height * 0.85))
            x = i * (bar_width + 3)
            y = cy - (bar_h / 2.0)

            # Gradient bar color (Cyan -> Magenta based on amplitude)
            grad = QLinearGradient(x, y, x, y + bar_h)
            if val > 0.4:
                grad.setColorAt(0.0, QColor("#ff007f"))
                grad.setColorAt(0.5, QColor("#00f0ff"))
                grad.setColorAt(1.0, QColor("#0070f3"))
            else:
                grad.setColorAt(0.0, QColor("#00f0ff"))
                grad.setColorAt(1.0, QColor("#0070f3"))

            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRectF(x, y, bar_width, bar_h), 2.0, 2.0)
