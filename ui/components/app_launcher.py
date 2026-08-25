"""
Quick Application Launcher Dock Widget.
"""
from typing import Callable, Optional
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt


class AppLauncherDock(QWidget):
    """Quick launcher bar for registered desktop applications."""

    def __init__(self, on_launch_callback: Optional[Callable[[str], None]] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._callback = on_launch_callback

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        apps = [
            ("VS Code", "vscode"),
            ("Chrome", "chrome"),
            ("Spotify", "spotify"),
            ("YouTube", "youtube"),
            ("GitHub", "github"),
            ("Terminal", "terminal"),
        ]

        for name, app_id in apps:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked=False, aid=app_id: self._on_clicked(aid))
            layout.addWidget(btn)

    def _on_clicked(self, app_id: str) -> None:
        if self._callback:
            self._callback(app_id)
