"""
Core State Machine for NERO Assistant.
Enforces valid state transitions and notifies observers.
"""
from enum import Enum, auto
from typing import Callable, List, Optional
from utils.logger import get_logger

logger = get_logger("state_machine")


class AssistantState(Enum):
    STARTING = "STARTING"
    IDLE = "IDLE"
    WAKE_DETECTED = "WAKE_DETECTED"
    LISTENING = "LISTENING"
    TRANSCRIBING = "TRANSCRIBING"
    THINKING = "THINKING"
    EXECUTING = "EXECUTING"
    SPEAKING = "SPEAKING"
    ERROR = "ERROR"
    STOPPING = "STOPPING"


# Allowed state transitions graph
VALID_TRANSITIONS = {
    AssistantState.STARTING: [AssistantState.IDLE, AssistantState.ERROR, AssistantState.STOPPING],
    AssistantState.IDLE: [AssistantState.WAKE_DETECTED, AssistantState.LISTENING, AssistantState.THINKING, AssistantState.STOPPING, AssistantState.ERROR],
    AssistantState.WAKE_DETECTED: [AssistantState.LISTENING, AssistantState.IDLE, AssistantState.SPEAKING, AssistantState.ERROR],
    AssistantState.LISTENING: [AssistantState.TRANSCRIBING, AssistantState.IDLE, AssistantState.ERROR, AssistantState.WAKE_DETECTED],
    AssistantState.TRANSCRIBING: [AssistantState.THINKING, AssistantState.EXECUTING, AssistantState.SPEAKING, AssistantState.IDLE, AssistantState.ERROR],
    AssistantState.THINKING: [AssistantState.EXECUTING, AssistantState.SPEAKING, AssistantState.IDLE, AssistantState.ERROR],
    AssistantState.EXECUTING: [AssistantState.SPEAKING, AssistantState.IDLE, AssistantState.ERROR],
    AssistantState.SPEAKING: [AssistantState.IDLE, AssistantState.LISTENING, AssistantState.WAKE_DETECTED, AssistantState.ERROR],
    AssistantState.ERROR: [AssistantState.IDLE, AssistantState.STOPPING],
    AssistantState.STOPPING: [],
}


class StateMachine:
    """Thread-safe state manager for NERO's runtime state."""

    def __init__(self, initial_state: AssistantState = AssistantState.STARTING):
        self._current_state = initial_state
        self._listeners: List[Callable[[AssistantState, AssistantState], None]] = []

    @property
    def current_state(self) -> AssistantState:
        return self._current_state

    def add_listener(self, listener: Callable[[AssistantState, AssistantState], None]) -> None:
        """Register a callback for state changes: fn(old_state, new_state)."""
        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[AssistantState, AssistantState], None]) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def transition_to(self, new_state: AssistantState, reason: str = "") -> bool:
        """
        Attempt transition to new state.
        Returns True if transition succeeded, False if invalid.
        """
        old_state = self._current_state
        if old_state == new_state:
            return True

        valid_targets = VALID_TRANSITIONS.get(old_state, [])
        if new_state not in valid_targets:
            logger.warning(
                f"Illegal state transition attempted: {old_state.value} -> {new_state.value} (Reason: {reason})"
            )
            # Force transition if recovering from or to ERROR/IDLE
            if new_state in (AssistantState.ERROR, AssistantState.IDLE, AssistantState.STOPPING):
                logger.info(f"Forced recovery transition: {old_state.value} -> {new_state.value}")
            else:
                return False

        self._current_state = new_state
        logger.info(f"State transition: {old_state.value} -> {new_state.value} ({reason})")

        # Notify observers
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception as e:
                logger.error(f"Error in state change listener: {e}")

        return True
