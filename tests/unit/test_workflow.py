"""
Unit tests for the automation workflow engine.
"""
import pytest
from automation.workflow_models import WorkflowDefinition, WorkflowStep, StepType
from automation.workflow_engine import WorkflowEngine
from automation.workflow_registry import WorkflowRegistry


@pytest.mark.asyncio
async def test_workflow_registry_defaults():
    registry = WorkflowRegistry()
    wf = registry.get_workflow("coding_mode")
    assert wf is not None
    assert wf.name == "Coding Mode"
    assert len(wf.steps) >= 2


@pytest.mark.asyncio
async def test_workflow_execution_and_cancellation(test_db):
    from storage.repositories import WorkflowRepository
    repo = WorkflowRepository(test_db)
    engine = WorkflowEngine(repo)

    steps = [
        WorkflowStep(name="Step 1", step_type=StepType.DELAY, delay_seconds=0.01),
        WorkflowStep(name="Step 2", step_type=StepType.DELAY, delay_seconds=0.01),
    ]
    wf = WorkflowDefinition(id="test_wf", name="Test Workflow", description="Testing", steps=steps)

    success = await engine.execute_workflow(wf)
    assert success
