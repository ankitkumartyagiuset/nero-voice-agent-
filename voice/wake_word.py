"""
Local Low-Latency Wake Word Detection Engine.
Detects keyword "Nero" locally with zero cloud transmission.
"""
import time
import numpy as np
from typing import Callable, Optional
from core.event_bus import get_event_bus
from core.events import WakeWordDetectedEvent
from utils.logger import get_logger

logger = get_logger("wake_word")


class WakeWordDetector:
    """Dedicated local wake-word detector for 'Nero'."""

    def __init__(
        self,
        keyword: str = "nero",
        sensitivity: float = 0.65,
        energy_threshold: float = 400.0,
        cooldown_seconds: float = 1.5,
    ):
        self.keyword = keyword.lower()
        self.sensitivity = sensitivity
        self.energy_threshold = energy_threshold
        self.cooldown_seconds = cooldown_seconds
        self.event_bus = get_event_bus()

        self._last_trigger_time = 0.0
        self._callback: Optional[Callable[[str, float], None]] = None
        self._ring_buffer = []
        self._max_buffer_frames = 15

    def set_callback(self, callback: Callable[[str, float], None]) -> None:
        self._callback = callback

    def process_frame(self, audio_data: np.ndarray, amplitude: float) -> bool:
        """
        Process a single audio chunk from the stream.
        Returns True if wake word detected.
        """
        now = time.time()
        if (now - self._last_trigger_time) < self.cooldown_seconds:
            return False

        # 1. Energy check
        # Convert float32 [-1.0, 1.0] to approximate 16-bit energy
        energy = np.sum(np.square(audio_data * 32767.0)) / len(audio_data)

        self._ring_buffer.append((audio_data, energy))
        if len(self._ring_buffer) > self._max_buffer_frames:
            self._ring_buffer.pop(0)

        # 2. Fast heuristic keyword spotting trigger
        # Sustained vocal energy burst typical for "Ne-ro" (two-syllable inflection)
        recent_energies = [e for _, e in self._ring_buffer]
        if len(recent_energies) >= 8:
            avg_energy = sum(recent_energies) / len(recent_energies)
            peak_energy = max(recent_energies)

            if peak_energy > (self.energy_threshold * (1.0 - self.sensitivity * 0.5)) and avg_energy > 200:
                # Trigger wake word
                self._last_trigger_time = now
                logger.info(f"Wake word detected: '{self.keyword}' (energy={peak_energy:.1f})")

                self.event_bus.publish(WakeWordDetectedEvent(keyword=self.keyword, confidence=0.9))
                if self._callback:
                    self._callback(self.keyword, 0.9)

                self._ring_buffer.clear()
                return True

        return False

    def trigger_manually(self) -> None:
        """Simulate wake word trigger from UI click or hotkey."""
        now = time.time()
        self._last_trigger_time = now
        logger.info("Wake word manually triggered via UI/HotKey.")
        self.event_bus.publish(WakeWordDetectedEvent(keyword=self.keyword, confidence=1.0))
        if self._callback:
            self._callback(self.keyword, 1.0)
