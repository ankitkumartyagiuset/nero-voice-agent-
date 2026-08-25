"""
Application Lifecycle Manager for NERO.
Handles graceful startup, background async loop, signal handling, and shutdown.
"""
import asyncio
import signal
import sys
from typing import Optional
from .assistant import NeroAssistant
from utils.logger import get_logger

logger = get_logger("lifecycle")


class LifecycleManager:
    """Manages application startup, async event loop, and clean shutdown."""

    def __init__(self, assistant: Optional[NeroAssistant] = None):
        self.assistant = assistant or NeroAssistant()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._is_running = False

    def start_headless(self) -> None:
        """Start assistant in headless CLI / console mode."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self.assistant.event_bus.set_event_loop(self._loop)

        # Handle OS interrupt signals
        def _signal_handler(sig, frame):
            logger.info("Interrupt signal received. Initiating shutdown...")
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, _signal_handler)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, _signal_handler)

        self._is_running = True

        async def _main_loop():
            await self.assistant.initialize()
            logger.info("Press Ctrl+C to terminate NERO.")
            while self._is_running:
                await asyncio.sleep(0.5)

        try:
            self._loop.run_until_complete(_main_loop())
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop all processes and close event loop."""
        self._is_running = False
        if self.assistant:
            self.assistant.shutdown()
        if self._loop and self._loop.is_running():
            self._loop.stop()
        logger.info("Lifecycle manager stopped.")
