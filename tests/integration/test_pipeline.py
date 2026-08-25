"""
Integration tests verifying full command pipeline execution.
"""
import pytest
from core.assistant import NeroAssistant


@pytest.mark.asyncio
async def test_fast_path_pipeline_time_command(mock_settings):
    assistant = NeroAssistant(mock_settings)

    # Execute deterministic time command
    output = await assistant.process_command("what time is it")
    assert "Current Time:" in output


@pytest.mark.asyncio
async def test_fast_path_pipeline_screenshot_command(mock_settings):
    assistant = NeroAssistant(mock_settings)

    output = await assistant.process_command("take a screenshot")
    assert "Screenshot saved" in output or "screenshot" in output.lower()


@pytest.mark.asyncio
async def test_dangerous_command_triggers_confirmation(mock_settings):
    assistant = NeroAssistant(mock_settings)

    # First attempt at shutdown
    output = await assistant.process_command("shut down")
    assert "confirmation" in output.lower()

    # User confirms with "yes"
    output_confirmed = await assistant.process_command("yes")
    assert "shutdown" in output_confirmed.lower() or "shutting down" in output_confirmed.lower()
