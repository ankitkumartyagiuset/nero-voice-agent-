"""
Unit tests for the Core State Machine transitions.
"""
from core.state import StateMachine, AssistantState


def test_valid_transitions():
    sm = StateMachine(initial_state=AssistantState.IDLE)
    assert sm.current_state == AssistantState.IDLE

    # IDLE -> WAKE_DETECTED
    assert sm.transition_to(AssistantState.WAKE_DETECTED)
    assert sm.current_state == AssistantState.WAKE_DETECTED

    # WAKE_DETECTED -> LISTENING
    assert sm.transition_to(AssistantState.LISTENING)
    assert sm.current_state == AssistantState.LISTENING

    # LISTENING -> TRANSCRIBING
    assert sm.transition_to(AssistantState.TRANSCRIBING)
    assert sm.current_state == AssistantState.TRANSCRIBING

    # TRANSCRIBING -> EXECUTING
    assert sm.transition_to(AssistantState.EXECUTING)
    assert sm.current_state == AssistantState.EXECUTING

    # EXECUTING -> SPEAKING
    assert sm.transition_to(AssistantState.SPEAKING)
    assert sm.current_state == AssistantState.SPEAKING

    # SPEAKING -> IDLE
    assert sm.transition_to(AssistantState.IDLE)
    assert sm.current_state == AssistantState.IDLE


def test_state_change_observer():
    sm = StateMachine(initial_state=AssistantState.IDLE)
    observed = []

    def _listener(old, new):
        observed.append((old, new))

    sm.add_listener(_listener)
    sm.transition_to(AssistantState.WAKE_DETECTED)

    assert len(observed) == 1
    assert observed[0] == (AssistantState.IDLE, AssistantState.WAKE_DETECTED)
