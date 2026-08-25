"""
Typed Event definitions for asynchronous pub/sub messaging across NERO subsystems.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from .state import AssistantState


@dataclass
class Event:
    """Base event class."""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class StateChangedEvent(Event):
    old_state: AssistantState = AssistantState.STARTING
    new_state: AssistantState = AssistantState.IDLE
    reason: str = ""


@dataclass
class AudioChunkEvent(Event):
    """Raw microphone PCM audio data and amplitude for waveform visualization."""
    chunk: bytes = b""
    amplitude: float = 0.0
    is_speech: bool = False


@dataclass
class WakeWordDetectedEvent(Event):
    keyword: str = "nero"
    confidence: float = 1.0


@dataclass
class SpeechStartedEvent(Event):
    session_id: str = ""


@dataclass
class SpeechEndedEvent(Event):
    session_id: str = ""
    audio_data: bytes = b""
    duration_ms: float = 0.0


@dataclass
class TranscriptionCompletedEvent(Event):
    session_id: str = ""
    text: str = ""
    confidence: float = 1.0
    latency_ms: float = 0.0


@dataclass
class IntentRoutedEvent(Event):
    session_id: str = ""
    intent_type: str = ""
    action: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    execution_path: str = "fast"  # "fast" or "ai"
    latency_ms: float = 0.0


@dataclass
class SkillExecutionStartedEvent(Event):
    session_id: str = ""
    skill_name: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillExecutionCompletedEvent(Event):
    session_id: str = ""
    skill_name: str = ""
    success: bool = True
    output_message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0


@dataclass
class LLMResponseChunkEvent(Event):
    session_id: str = ""
    delta: str = ""
    is_finished: bool = False


@dataclass
class TTSStartedEvent(Event):
    text: str = ""


@dataclass
class TTSFinishedEvent(Event):
    text: str = ""
    duration_ms: float = 0.0


@dataclass
class ConfirmationRequestedEvent(Event):
    session_id: str = ""
    action: str = ""
    target: str = ""
    prompt: str = ""
    token: str = ""


@dataclass
class WorkflowStatusEvent(Event):
    workflow_id: str = ""
    status: str = ""  # "running", "completed", "cancelled", "failed"
    step_description: str = ""


@dataclass
class ErrorEvent(Event):
    subsystem: str = "core"
    message: str = ""
    exception: Optional[Exception] = None
