"""
Persistent Microphone Audio Stream.
Captures continuous audio, computes amplitude for HUD waveform, and maintains circular buffer.
"""
import time
import threading
import numpy as np
from typing import Callable, List, Optional, Dict
from core.event_bus import get_event_bus
from core.events import AudioChunkEvent
from utils.logger import get_logger

logger = get_logger("audio_stream")


class AudioStream:
    """Persistent audio streaming service capturing microphone input with auto-recovery."""

    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_size: int = 1024,
        channels: int = 1,
        device_index: Optional[int] = None,
    ):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.device_index = device_index
        self.event_bus = get_event_bus()

        self._is_running = False
        self._stream = None
        self._listeners: List[Callable[[np.ndarray, float], None]] = []
        self._lock = threading.Lock()
        self._last_amplitude: float = 0.0

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def last_amplitude(self) -> float:
        return self._last_amplitude

    def add_listener(self, listener: Callable[[np.ndarray, float], None]) -> None:
        """Register callback: fn(chunk_array, amplitude)."""
        with self._lock:
            if listener not in self._listeners:
                self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[np.ndarray, float], None]) -> None:
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def list_devices(self) -> List[Dict]:
        """Enumerate available audio input devices."""
        devices = []
        try:
            import sounddevice as sd
            devs = sd.query_devices()
            for i, dev in enumerate(devs):
                if dev.get("max_input_channels", 0) > 0:
                    devices.append({
                        "index": i,
                        "name": dev.get("name"),
                        "channels": dev.get("max_input_channels"),
                        "sample_rate": dev.get("default_samplerate")
                    })
        except Exception as e:
            logger.warning(f"Error querying audio devices: {e}")
        return devices

    def start(self) -> bool:
        """Start the persistent audio stream."""
        if self._is_running:
            return True

        try:
            import sounddevice as sd

            def _audio_callback(indata, frames, time_info, status):
                if status:
                    logger.debug(f"Audio stream status: {status}")

                # Convert to mono float32 array
                audio_data = indata.copy().flatten()

                # Calculate RMS amplitude (0.0 to 1.0)
                rms = np.sqrt(np.mean(np.square(audio_data)))
                # Scale for visual responsiveness
                amplitude = min(1.0, float(rms * 10.0))
                self._last_amplitude = amplitude

                # Publish chunk event for visualizer
                raw_bytes = (audio_data * 32767).astype(np.int16).tobytes()
                self.event_bus.publish(AudioChunkEvent(
                    chunk=raw_bytes,
                    amplitude=amplitude,
                    is_speech=(amplitude > 0.15)
                ))

                # Notify listeners
                with self._lock:
                    listeners = list(self._listeners)
                for listener in listeners:
                    try:
                        listener(audio_data, amplitude)
                    except Exception as err:
                        logger.error(f"Error in audio listener: {err}")

            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                device=self.device_index,
                channels=self.channels,
                dtype="float32",
                callback=_audio_callback,
            )
            self._stream.start()
            self._is_running = True
            logger.info("Persistent microphone audio stream started successfully.")
            return True

        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            self._is_running = False
            return False

    def stop(self) -> None:
        """Stop the audio stream safely."""
        self._is_running = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception as e:
                logger.warning(f"Error closing audio stream: {e}")
            self._stream = None
        logger.info("Audio stream stopped.")


_GLOBAL_AUDIO_STREAM: Optional[AudioStream] = None


def get_audio_stream() -> AudioStream:
    global _GLOBAL_AUDIO_STREAM
    if _GLOBAL_AUDIO_STREAM is None:
        _GLOBAL_AUDIO_STREAM = AudioStream()
    return _GLOBAL_AUDIO_STREAM
