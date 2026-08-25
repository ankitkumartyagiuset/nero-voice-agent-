"""
Workflow Engine for executing sequential and parallel automation steps.
Supports live progress reporting, cancellation, and event bus integration.
"""
import asyncio
from typing import Dict, Optional, List
from .workflow_models import WorkflowDefinition, WorkflowStep, WorkflowStatus, StepType
from skills.registry import get_skill_registry
from core.event_bus import get_event_bus
from core.events import WorkflowStatusEvent
from storage.repositories import WorkflowRepository
from utils.logger import get_logger

logger = get_logger("workflow_engine")


class WorkflowEngine:
    """Async workflow execution coordinator."""

    def __init__(self, repo: Optional[WorkflowRepository] = None):
        self.repo = repo or WorkflowRepository()
        self.skill_registry = get_skill_registry()
        self.event_bus = get_event_bus()
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._statuses: Dict[str, WorkflowStatus] = {}

    def get_status(self, workflow_id: str) -> WorkflowStatus:
        return self._statuses.get(workflow_id, WorkflowStatus.IDLE)

    def is_running(self, workflow_id: str) -> bool:
        return self.get_status(workflow_id) == WorkflowStatus.RUNNING

    async def execute_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Run workflow definition asynchronously."""
        workflow_id = workflow.id

        if self.is_running(workflow_id):
            logger.warning(f"Workflow '{workflow_id}' is already running.")
            return False

        self._statuses[workflow_id] = WorkflowStatus.RUNNING
        self.event_bus.publish(WorkflowStatusEvent(workflow_id=workflow_id, status="running", step_description="Starting workflow"))

        run_id = self.repo.record_start(workflow_id)

        try:
            for i, step in enumerate(workflow.steps):
                # Check for cancellation before each step
                if self._statuses.get(workflow_id) == WorkflowStatus.CANCELLING:
                    self._statuses[workflow_id] = WorkflowStatus.CANCELLED
                    self.event_bus.publish(WorkflowStatusEvent(workflow_id=workflow_id, status="cancelled", step_description="Cancelled by user"))
                    self.repo.record_finish(run_id, "cancelled")
                    logger.info(f"Workflow '{workflow_id}' cancelled by user.")
                    return False

                step_desc = f"Step {i+1}/{len(workflow.steps)}: {step.name}"
                logger.info(f"Executing workflow '{workflow_id}' -> {step_desc}")
                self.event_bus.publish(WorkflowStatusEvent(workflow_id=workflow_id, status="running", step_description=step_desc))

                # Handle Step types
                if step.step_type == StepType.ACTION:
                    result = await self.skill_registry.dispatch(step.action, step.parameters)
                    if not result.success:
                        logger.warning(f"Workflow step failed: {step.name} -> {result.output_message}")

                elif step.step_type == StepType.DELAY:
                    await asyncio.sleep(step.delay_seconds)

                # Optional delay between actions
                if step.delay_seconds > 0:
                    await asyncio.sleep(step.delay_seconds)

            self._statuses[workflow_id] = WorkflowStatus.COMPLETED
            self.event_bus.publish(WorkflowStatusEvent(workflow_id=workflow_id, status="completed", step_description="Completed successfully"))
            self.repo.record_finish(run_id, "completed")
            logger.info(f"Workflow '{workflow_id}' completed successfully.")
            return True

        except asyncio.CancelledError:
            self._statuses[workflow_id] = WorkflowStatus.CANCELLED
            self.event_bus.publish(WorkflowStatusEvent(workflow_id=workflow_id, status="cancelled", step_description="Workflow cancelled"))
            self.repo.record_finish(run_id, "cancelled")
            return False

        except Exception as e:
            self._statuses[workflow_id] = WorkflowStatus.FAILED
            self.event_bus.publish(WorkflowStatusEvent(workflow_id=workflow_id, status="failed", step_description=f"Error: {e}"))
            self.repo.record_finish(run_id, "failed", str(e))
            logger.error(f"Workflow '{workflow_id}' encountered an error: {e}", exc_info=True)
            return False

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        if not self.is_running(workflow_id):
            return False

        self._statuses[workflow_id] = WorkflowStatus.CANCELLING
        if workflow_id in self._active_tasks:
            self._active_tasks[workflow_id].cancel()
        logger.info(f"Cancellation requested for workflow '{workflow_id}'")
        return True


_GLOBAL_WORKFLOW_ENGINE: Optional[WorkflowEngine] = None


def get_workflow_engine() -> WorkflowEngine:
    global _GLOBAL_WORKFLOW_ENGINE
    if _GLOBAL_WORKFLOW_ENGINE is None:
        _GLOBAL_WORKFLOW_ENGINE = WorkflowEngine()
    return _GLOBAL_WORKFLOW_ENGINE
