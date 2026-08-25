"""
Audio Session Coordinator.
Bridges AudioStream, WakeWordDetector, VAD, and STT into an event-driven pipeline.
"""
import time
import numpy as np
from typing import Optional, Callable
from .audio_stream import AudioStream, get_audio_stream
from .wake_word import WakeWordDetector
from .vad import VoiceActivityDetector
from .speech_to_text import SpeechToTextEngine, get_stt_engine
from core.state import AssistantState, StateMachine
from core.event_bus import get_event_bus
from core.events import (
    WakeWordDetectedEvent,
    SpeechStartedEvent,
    SpeechEndedEvent,
    TranscriptionCompletedEvent
)
from utils.logger import get_logger

logger = get_logger("audio_session")


class AudioSessionManager:
    """Manages audio pipeline states: Wake Detection -> Speech Capture -> Fast STT."""

    def __init__(
        self,
        state_machine: StateMachine,
        audio_stream: Optional[AudioStream] = None,
        wake_detector: Optional[WakeWordDetector] = None,
        vad: Optional[VoiceActivityDetector] = None,
        stt: Optional[SpeechToTextEngine] = None,
    ):
        self.state_machine = state_machine
        self.audio_stream = audio_stream or get_audio_stream()
        self.wake_detector = wake_detector or WakeWordDetector()
        self.vad = vad or VoiceActivityDetector()
        self.stt = stt or get_stt_engine()
        self.event_bus = get_event_bus()

        self._on_transcription_ready: Optional[Callable[[str, float], None]] = None

        # Wire audio stream callback
        self.audio_stream.add_listener(self._handle_audio_frame)

    def set_transcription_callback(self, callback: Callable[[str, float], None]) -> None:
        self._on_transcription_ready = callback

    def _handle_audio_frame(self, audio_chunk: np.ndarray, amplitude: float) -> None:
        """Process incoming microphone audio frame based on current assistant state."""
        current_state = self.state_machine.current_state

        if current_state == AssistantState.IDLE:
            # Check for Wake Word
            if self.wake_detector.process_frame(audio_chunk, amplitude):
                self.state_machine.transition_to(AssistantState.WAKE_DETECTED, reason="Wake word recognized")
                self.start_listening_session()

        elif current_state == AssistantState.LISTENING:
            # Process VAD
            is_finished, captured_audio = self.vad.process_frame(audio_chunk, amplitude)
            if is_finished:
                if captured_audio is not None and len(captured_audio) > 0:
                    self.state_machine.transition_to(AssistantState.TRANSCRIBING, reason="Speech capture finished")
                    self._process_transcription(captured_audio)
                else:
                    logger.info("No speech captured in command window; returning to IDLE.")
                    self.state_machine.transition_to(AssistantState.IDLE, reason="Silence timeout")

    def start_listening_session(self) -> None:
        """Triggered on wake detection or manual UI click."""
        self.state_machine.transition_to(AssistantState.LISTENING, reason="Starting command capture")
        self.vad.start_listening()
        self.event_bus.publish(SpeechStartedEvent(session_id="voice_turn"))

    def _process_transcription(self, audio_data: np.ndarray) -> None:
        """Run STT inference in background/async worker."""
        text, conf, latency_ms = self.stt.transcribe(audio_data)

        self.event_bus.publish(TranscriptionCompletedEvent(
            session_id="voice_turn",
            text=text,
            confidence=conf,
            latency_ms=latency_ms
        ))

        if self._on_transcription_ready and text:
            self._on_transcription_ready(text, latency_ms)
        elif not text:
            self.state_machine.transition_to(AssistantState.IDLE, reason="Empty transcription")
