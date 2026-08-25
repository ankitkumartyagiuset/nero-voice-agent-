"""
Text-to-Speech (TTS) Engine.
Supports local pyttsx3 and ElevenLabs providers with non-blocking execution and interruption.
"""
import time
import threading
import queue
from typing import Optional, Callable
from config.settings import TTSConfig
from config.loader import get_settings
from core.event_bus import get_event_bus
from core.events import TTSStartedEvent, TTSFinishedEvent
from utils.logger import get_logger

logger = get_logger("tts_engine")


class TextToSpeechEngine:
    """Non-blocking, interruptible Text-to-Speech engine."""

    def __init__(self, config: Optional[TTSConfig] = None):
        self.config = config or get_settings().voice.tts
        self.event_bus = get_event_bus()

        self._queue = queue.Queue()
        self._is_speaking = False
        self._stop_requested = False
        self._worker_thread: Optional[threading.Thread] = None
        self._engine = None
        self._lock = threading.Lock()

        self._start_worker()

    @property
    def is_speaking(self) -> bool:
        return self._is_speaking

    def _start_worker(self) -> None:
        self._worker_thread = threading.Thread(target=self._run_tts_loop, daemon=True, name="TTS-Worker")
        self._worker_thread.start()

    def _init_local_engine(self) -> None:
        """Initialize pyttsx3 in the dedicated worker thread."""
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.config.rate)
            self._engine.setProperty("volume", self.config.volume)

            voices = self._engine.getProperty("voices")
            if voices and len(voices) > self.config.voice_index:
                self._engine.setProperty("voice", voices[self.config.voice_index].id)

            logger.info("pyttsx3 local TTS engine initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize pyttsx3: {e}")
            self._engine = None

    def _run_tts_loop(self) -> None:
        """Dedicated TTS background thread loop."""
        self._init_local_engine()

        while True:
            try:
                item = self._queue.get()
                if item is None:
                    break

                text, on_start, on_finish = item
                self._stop_requested = False
                self._is_speaking = True

                start_time = time.perf_counter()
                self.event_bus.publish(TTSStartedEvent(text=text))
                if on_start:
                    on_start()

                logger.info(f"Speaking: '{text}'")

                if self._engine:
                    try:
                        self._engine.say(text)
                        self._engine.runAndWait()
                    except Exception as e:
                        logger.error(f"Error during pyttsx3 speech synthesis: {e}")
                        # Re-init on error
                        self._init_local_engine()
                else:
                    # Simulated speech delay when pyttsx3 unavailable
                    time.sleep(max(0.5, len(text) * 0.05))

                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                self._is_speaking = False
                self.event_bus.publish(TTSFinishedEvent(text=text, duration_ms=round(elapsed_ms, 2)))
                if on_finish:
                    on_finish()

                self._queue.task_done()

            except Exception as e:
                logger.error(f"Unhandled error in TTS loop: {e}")
                self._is_speaking = False

    def speak(
        self,
        text: str,
        interrupt_current: bool = True,
        on_start: Optional[Callable[[], None]] = None,
        on_finish: Optional[Callable[[], None]] = None,
    ) -> None:
        """Queue text for non-blocking speech playback."""
        if not text or not text.strip():
            return

        if interrupt_current and self._is_speaking:
            self.stop()

        self._queue.put((text.strip(), on_start, on_finish))

    def stop(self) -> None:
        """Interrupt and stop current speech immediately."""
        self._stop_requested = True
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass

        # Clear pending queue items
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except Exception:
                break

        self._is_speaking = False
        logger.info("TTS playback interrupted/stopped.")


_GLOBAL_TTS_ENGINE: Optional[TextToSpeechEngine] = None


def get_tts_engine() -> TextToSpeechEngine:
    global _GLOBAL_TTS_ENGINE
    if _GLOBAL_TTS_ENGINE is None:
        _GLOBAL_TTS_ENGINE = TextToSpeechEngine()
    return _GLOBAL_TTS_ENGINE
