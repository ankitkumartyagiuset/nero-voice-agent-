"""Core orchestrator, state machine, and event system for NERO."""
from .state import AssistantState, StateMachine
from .events import (
    Event,
    StateChangedEvent,
    WakeWordDetectedEvent,
    SpeechStartedEvent,
    SpeechEndedEvent,
    AudioChunkEvent,
    TranscriptionCompletedEvent,
    IntentRoutedEvent,
    SkillExecutionStartedEvent,
    SkillExecutionCompletedEvent,
    LLMResponseChunkEvent,
    TTSStartedEvent,
    TTSFinishedEvent,
    ErrorEvent,
)
from .event_bus import EventBus, get_event_bus
from .exceptions import NeroError, VoiceError, SkillError, SecurityError, AIError

__all__ = [
    "AssistantState",
    "StateMachine",
    "Event",
    "StateChangedEvent",
    "WakeWordDetectedEvent",
    "SpeechStartedEvent",
    "SpeechEndedEvent",
    "AudioChunkEvent",
    "TranscriptionCompletedEvent",
    "IntentRoutedEvent",
    "SkillExecutionStartedEvent",
    "SkillExecutionCompletedEvent",
    "LLMResponseChunkEvent",
    "TTSStartedEvent",
    "TTSFinishedEvent",
    "ErrorEvent",
    "EventBus",
    "get_event_bus",
    "NeroError",
    "VoiceError",
    "SkillError",
    "SecurityError",
    "AIError",
]
