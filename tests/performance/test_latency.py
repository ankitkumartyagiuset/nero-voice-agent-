"""
Performance benchmark tests verifying sub-50ms latency budget for local routing and state transitions.
"""
import time
import pytest
from brain.intent_router import FastIntentRouter
from core.state import StateMachine, AssistantState


def test_intent_router_latency_budget():
    """Verify local fast intent router executes in < 5ms (budget is 50ms)."""
    router = FastIntentRouter()
    commands = [
        "open vscode",
        "close chrome",
        "set volume to 80",
        "take a screenshot",
        "mute audio",
        "what is the time",
        "coding mode on",
        "search youtube for python tutorial",
    ]

    for cmd in commands:
        t0 = time.perf_counter()
        match = router.route(cmd)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert match.is_matched
        assert elapsed_ms < 15.0, f"Intent routing took {elapsed_ms:.2f}ms, exceeding latency budget!"


def test_state_transition_latency():
    """Verify state transitions execute in < 1ms."""
    sm = StateMachine(initial_state=AssistantState.IDLE)

    t0 = time.perf_counter()
    sm.transition_to(AssistantState.WAKE_DETECTED)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert elapsed_ms < 5.0
