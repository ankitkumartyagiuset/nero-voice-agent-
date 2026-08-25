"""
Animation helpers and math utilities for UI visual effects.
"""
import math
from PySide6.QtCore import QObject, QTimer, Signal


class AnimationDriver(QObject):
    """Timer-driven animation ticker maintaining 60 FPS tick events."""

    tick = Signal(float)  # current time or phase

    def __init__(self, fps: int = 60, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(int(1000 / fps))
        self._timer.timeout.connect(self._on_timeout)
        self._phase = 0.0

    def start(self) -> None:
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def _on_timeout(self) -> None:
        self._phase += 0.05
        if self._phase > 2 * math.pi * 100:
            self._phase = 0.0
        self.tick.emit(self._phase)
