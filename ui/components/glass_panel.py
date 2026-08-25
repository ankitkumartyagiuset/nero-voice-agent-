"""
Glassmorphic Panel Container Card with translucent background and neon borders.
"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt


class GlassPanel(QFrame):
    """Translucent frosted glass card container for HUD panels."""

    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("GlassPanel")

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 14, 16, 16)
        self._layout.setSpacing(12)

        if title:
            self._title_label = QLabel(title)
            self._title_label.setObjectName("PanelTitle")
            self._layout.addWidget(self._title_label)

    @property
    def inner_layout(self) -> QVBoxLayout:
        return self._layout
