"""
Application bootstrap for NERO Assistant with PySide6 GUI and Asyncio integration.
"""
import sys
import os
import asyncio
from typing import TYPE_CHECKING, Optional

# Ensure package root in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config.loader import load_settings
from core.assistant import NeroAssistant
from core.lifecycle import LifecycleManager
from utils.logger import setup_logger, get_logger

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication
    from ui.main_window import NeroMainWindow

logger = setup_logger("nero")


class NeroApplication:
    """Master application launcher combining Qt event loop with asyncio loop."""

    def __init__(self, cli_mode: bool = False, config_path: Optional[str] = None):
        self.settings = load_settings(config_path)
        self.cli_mode = cli_mode
        self.assistant = NeroAssistant(self.settings)
        self.lifecycle = LifecycleManager(self.assistant)
        self.qt_app: Optional["QApplication"] = None
        self.main_window: Optional["NeroMainWindow"] = None

    def run(self) -> int:
        if self.cli_mode or not self.settings.app.ui_enabled:
            logger.info("Starting NERO in headless CLI mode...")
            self.lifecycle.start_headless()
            return 0

        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import QTimer
            from ui.main_window import NeroMainWindow
        except ImportError as exc:
            logger.error("GUI requires a local graphical environment: %s", exc)
            return 1

        logger.info("Starting NERO Desktop HUD Interface...")
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setApplicationName("NERO Assistant")

        # Set up shared async event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.assistant.event_bus.set_event_loop(loop)

        # Create Main Window
        self.main_window = NeroMainWindow(assistant=self.assistant)
        self.main_window.show()

        # Run background async tasks inside Qt event loop using QTimer tick
        timer = QTimer()
        timer.setInterval(10) # 10ms tick for asyncio processing
        timer.timeout.connect(lambda: self._process_async_events(loop))
        timer.start()

        # Initialize backend subsystems
        loop.run_until_complete(self.assistant.initialize())

        try:
            exit_code = self.qt_app.exec()
        finally:
            self.assistant.shutdown()
            loop.close()

        return exit_code

    def _process_async_events(self, loop: asyncio.AbstractEventLoop) -> None:
        """Process pending asyncio events during Qt event loop iterations."""
        loop.stop()
        loop.run_forever()


def run_app(cli: bool = False, config: Optional[str] = None) -> int:
    app = NeroApplication(cli_mode=cli, config_path=config)
    return app.run()


if __name__ == "__main__":
    cli_flag = "--cli" in sys.argv or "--no-ui" in sys.argv
    sys.exit(run_app(cli=cli_flag))
