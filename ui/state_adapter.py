"""
State Adapter bridging Python EventBus events to Qt Signals for thread-safe UI updates.
"""
from typing import Optional
from PySide6.QtCore import QObject, Signal
from core.event_bus import get_event_bus
from core.events import (
    StateChangedEvent,
    AudioChunkEvent,
    WakeWordDetectedEvent,
    TranscriptionCompletedEvent,
    SkillExecutionCompletedEvent,
    WorkflowStatusEvent,
    ErrorEvent,
)


class UIStateAdapter(QObject):
    """Qt Signal bridge receiving core events and safely triggering UI updates."""

    # Qt Signals
    state_changed = Signal(str, str)             # (old_state_str, new_state_str)
    audio_amplitude_updated = Signal(float)       # amplitude (0.0 to 1.0)
    wake_word_triggered = Signal(str)            # keyword
    transcription_received = Signal(str, float)  # (text, latency_ms)
    ai_response_received = Signal(str, str, float) # (role, content, latency_ms)
    skill_executed = Signal(str, bool, str)      # (skill_name, success, message)
    workflow_updated = Signal(str, str, str)     # (workflow_id, status, step_desc)
    status_indicator_updated = Signal(str, str)  # (subsystem, status)

    def __init__(self):
        super().__init__()
        self.event_bus = get_event_bus()
        self._subscribe_events()

    def _subscribe_events(self) -> None:
        self.event_bus.subscribe(StateChangedEvent, self._on_state_changed)
        self.event_bus.subscribe(AudioChunkEvent, self._on_audio_chunk)
        self.event_bus.subscribe(WakeWordDetectedEvent, self._on_wake_detected)
        self.event_bus.subscribe(TranscriptionCompletedEvent, self._on_transcription)
        self.event_bus.subscribe(SkillExecutionCompletedEvent, self._on_skill_completed)
        self.event_bus.subscribe(WorkflowStatusEvent, self._on_workflow_status)

    def _on_state_changed(self, event: StateChangedEvent) -> None:
        self.state_changed.emit(event.old_state.value, event.new_state.value)

    def _on_audio_chunk(self, event: AudioChunkEvent) -> None:
        self.audio_amplitude_updated.emit(event.amplitude)

    def _on_wake_detected(self, event: WakeWordDetectedEvent) -> None:
        self.wake_word_triggered.emit(event.keyword)

    def _on_transcription(self, event: TranscriptionCompletedEvent) -> None:
        self.transcription_received.emit(event.text, event.latency_ms)

    def _on_skill_completed(self, event: SkillExecutionCompletedEvent) -> None:
        self.skill_executed.emit(event.skill_name, event.success, event.output_message)

    def _on_workflow_status(self, event: WorkflowStatusEvent) -> None:
        self.workflow_updated.emit(event.workflow_id, event.status, event.step_description)


_GLOBAL_UI_ADAPTER: Optional[UIStateAdapter] = None


def get_ui_adapter() -> UIStateAdapter:
    global _GLOBAL_UI_ADAPTER
    if _GLOBAL_UI_ADAPTER is None:
        _GLOBAL_UI_ADAPTER = UIStateAdapter()
    return _GLOBAL_UI_ADAPTER
