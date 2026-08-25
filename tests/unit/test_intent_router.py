"""
Unit tests for Fast Path Intent Router matching rules.
"""
from brain.intent_router import FastIntentRouter


def test_fast_router_app_control():
    router = FastIntentRouter()

    match = router.route("open vscode")
    assert match.is_matched
    assert match.action == "open_application"
    assert match.parameters["application"] == "vscode"

    match = router.route("launch visual studio code")
    assert match.is_matched
    assert match.action == "open_application"
    assert match.parameters["application"] == "vscode"

    match = router.route("close chrome")
    assert match.is_matched
    assert match.action == "close_application"
    assert match.parameters["application"] == "chrome"


def test_fast_router_volume_and_screenshot():
    router = FastIntentRouter()

    match = router.route("take a screenshot")
    assert match.is_matched
    assert match.action == "take_screenshot"

    match = router.route("set volume to 75")
    assert match.is_matched
    assert match.action == "set_volume"
    assert match.parameters["value"] == 75

    match = router.route("mute audio")
    assert match.is_matched
    assert match.action == "mute_volume"


def test_fast_router_time_and_workflows():
    router = FastIntentRouter()

    match = router.route("what time is it")
    assert match.is_matched
    assert match.action == "get_time"

    match = router.route("coding mode on")
    assert match.is_matched
    assert match.action == "run_workflow"
    assert match.parameters["workflow"] == "coding_mode"

    match = router.route("stop coding mode")
    assert match.is_matched
    assert match.action == "cancel_workflow"


def test_ai_path_routing():
    router = FastIntentRouter()

    match = router.route("explain how Python decorators work")
    assert not match.is_matched
    assert match.execution_path == "ai"

    match = router.route("write a binary search function")
    assert not match.is_matched
    assert match.execution_path == "ai"
