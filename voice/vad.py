"""
Voice Activity Detection (VAD) Service.
Detects speech onset, captures command audio, and endpoints speech on silence.
"""
import time
import numpy as np
from typing import Optional, List, Tuple
from utils.logger import get_logger

logger = get_logger("vad")


class VoiceActivityDetector:
    """Detects speech start and silence endpoint with sub-500ms latency."""

    def __init__(
        self,
        silence_duration_ms: int = 450,
        min_speech_duration_ms: int = 120,
        max_command_duration_seconds: float = 12.0,
        sample_rate: int = 16000,
        frame_size: int = 1024,
    ):
        self.silence_duration_ms = silence_duration_ms
        self.min_speech_duration_ms = min_speech_duration_ms
        self.max_command_duration_seconds = max_command_duration_seconds
        self.sample_rate = sample_rate
        self.frame_size = frame_size

        self._is_recording = False
        self._speech_detected = False
        self._speech_start_time = 0.0
        self._last_speech_time = 0.0
        self._start_capture_time = 0.0
        self._audio_frames: List[np.ndarray] = []

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def start_listening(self) -> None:
        """Begin speech capture window after wake word detection."""
        self._is_recording = True
        self._speech_detected = False
        self._speech_start_time = 0.0
        self._last_speech_time = 0.0
        self._start_capture_time = time.perf_counter()
        self._audio_frames.clear()
        logger.debug("VAD started listening for speech.")

    def stop_listening(self) -> Optional[np.ndarray]:
        """Stop listening and return recorded audio."""
        self._is_recording = False
        if not self._audio_frames:
            return None
        return np.concatenate(self._audio_frames)

    def process_frame(self, audio_data: np.ndarray, amplitude: float) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Process a single audio frame during LISTENING state.
        Returns: (is_finished, completed_audio_array)
        """
        if not self._is_recording:
            return False, None

        now = time.perf_counter()
        self._audio_frames.append(audio_data)

        # 1. Check max command duration timeout
        if (now - self._start_capture_time) > self.max_command_duration_seconds:
            logger.info("VAD max command duration reached; finalizing audio.")
            audio = self.stop_listening()
            return True, audio

        # 2. Vocal energy threshold
        is_voice = amplitude > 0.08

        if is_voice:
            if not self._speech_detected:
                if self._speech_start_time == 0.0:
                    self._speech_start_time = now
                elif (now - self._speech_start_time) * 1000.0 >= self.min_speech_duration_ms:
                    self._speech_detected = True
                    logger.debug("VAD detected speech onset.")
            self._last_speech_time = now

        else:
            # Silence detected
            if self._speech_detected:
                silence_elapsed_ms = (now - self._last_speech_time) * 1000.0
                if silence_elapsed_ms >= self.silence_duration_ms:
                    # Endpoint reached!
                    logger.info(f"VAD silence endpoint reached after {silence_elapsed_ms:.1f}ms silence.")
                    audio = self.stop_listening()
                    return True, audio

            elif (now - self._start_capture_time) > 4.0:
                # 4 seconds without any speech start after wake word
                logger.info("VAD timed out waiting for speech start.")
                self.stop_listening()
                return True, None

        return False, None
