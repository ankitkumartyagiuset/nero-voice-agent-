"""
Speech-to-Text (STT) Engine using faster-whisper.
Maintains a singleton model loaded in memory for low-latency interactive transcription.
"""
import time
import io
import numpy as np
from typing import Optional, Tuple
from config.settings import STTConfig
from config.loader import get_settings
from utils.logger import get_logger

logger = get_logger("stt_engine")


class SpeechToTextEngine:
    """Singleton faster-whisper transcription engine."""

    def __init__(self, config: Optional[STTConfig] = None):
        self.config = config or get_settings().voice.stt
        self._model = None
        self._is_loaded = False
        self._device = "cpu"
        self._compute_type = "int8"

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def load_model(self) -> bool:
        """Load the faster-whisper model into memory once."""
        if self._is_loaded and self._model is not None:
            return True

        start_time = time.perf_counter()
        model_name = self.config.model

        # Auto-detect CUDA capability
        device = self.config.device
        if device == "auto":
            try:
                import ctranslate2
                if ctranslate2.get_cuda_device_count() > 0:
                    device = "cuda"
                    compute_type = "float16" if self.config.compute_type == "auto" else self.config.compute_type
                else:
                    device = "cpu"
                    compute_type = "int8" if self.config.compute_type == "auto" else self.config.compute_type
            except Exception:
                device = "cpu"
                compute_type = "int8"
        else:
            compute_type = self.config.compute_type if self.config.compute_type != "auto" else "default"

        self._device = device
        self._compute_type = compute_type

        logger.info(f"Loading faster-whisper model '{model_name}' on {device} ({compute_type})...")

        try:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(
                model_name,
                device=device,
                compute_type=compute_type,
                cpu_threads=4,
            )
            self._is_loaded = True
            elapsed = (time.perf_counter() - start_time) * 1000.0
            logger.info(f"faster-whisper model loaded in {elapsed:.1f}ms.")
            return True

        except Exception as e:
            logger.warning(f"Failed to load faster-whisper on {device}: {e}. Retrying CPU fallback...")
            try:
                from faster_whisper import WhisperModel
                self._model = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=4)
                self._device = "cpu"
                self._compute_type = "int8"
                self._is_loaded = True
                logger.info("faster-whisper model loaded successfully on CPU fallback.")
                return True
            except Exception as e2:
                logger.error(f"Failed to initialize faster-whisper: {e2}")
                self._is_loaded = False
                return False

    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Tuple[str, float, float]:
        """
        Transcribe numpy audio array.
        Returns: (transcribed_text, confidence, latency_ms)
        """
        if not self._is_loaded or self._model is None:
            if not self.load_model():
                return "", 0.0, 0.0

        start_time = time.perf_counter()

        try:
            # Ensure float32 normalized [-1.0, 1.0]
            if audio_data.dtype != np.float32:
                audio_float = audio_data.astype(np.float32) / 32768.0
            else:
                audio_float = audio_data

            # Run greedy inference
            segments, info = self._model.transcribe(
                audio_float,
                beam_size=self.config.beam_size,
                language=self.config.language if self.config.language != "auto" else None,
                vad_filter=False, # We already performed precise local VAD
            )

            text_segments = []
            for s in segments:
                text_segments.append(s.text.strip())

            full_text = " ".join(text_segments).strip()
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            logger.info(f"STT transcribed: '{full_text}' ({elapsed_ms:.1f}ms)")
            return full_text, 1.0, round(elapsed_ms, 2)

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Transcription error: {e}")
            return "", 0.0, round(elapsed_ms, 2)


_GLOBAL_STT_ENGINE: Optional[SpeechToTextEngine] = None


def get_stt_engine() -> SpeechToTextEngine:
    global _GLOBAL_STT_ENGINE
    if _GLOBAL_STT_ENGINE is None:
        _GLOBAL_STT_ENGINE = SpeechToTextEngine()
    return _GLOBAL_STT_ENGINE
