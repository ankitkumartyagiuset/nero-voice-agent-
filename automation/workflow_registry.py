"""
Workflow Registry holding built-in and user-configured automation workflows.
"""
from typing import Dict, Optional, List
from .workflow_models import WorkflowDefinition, WorkflowStep, StepType
from config.loader import get_settings
from utils.logger import get_logger

logger = get_logger("workflow_registry")


class WorkflowRegistry:
    """Registry maintaining active workflow definitions."""

    def __init__(self):
        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._init_defaults()

    def _init_defaults(self) -> None:
        settings = get_settings()

        # 1. Coding Mode Workflow
        coding_steps = [
            WorkflowStep(name="Open VS Code", step_type=StepType.ACTION, action="open_application", parameters={"application": "vscode"}),
            WorkflowStep(name="Open Google Chrome", step_type=StepType.ACTION, action="open_application", parameters={"application": "chrome"}, delay_seconds=0.5),
            WorkflowStep(name="Open GitHub", step_type=StepType.ACTION, action="open_url", parameters={"url": "https://github.com"}),
        ]
        self.register(WorkflowDefinition(
            id="coding_mode",
            name="Coding Mode",
            description="Launch development IDE, browser, and GitHub repository",
            steps=coding_steps,
            tts_announcement="Coding mode activated. Opening development environment."
        ))

        # 2. Focus Mode Workflow
        focus_steps = [
            WorkflowStep(name="Mute Audio", step_type=StepType.ACTION, action="mute_volume"),
        ]
        self.register(WorkflowDefinition(
            id="focus_mode",
            name="Focus Mode",
            description="Mute system volume and minimize interruptions",
            steps=focus_steps,
            tts_announcement="Focus mode engaged."
        ))

    def register(self, workflow: WorkflowDefinition) -> None:
        self._workflows[workflow.id] = workflow
        logger.info(f"Registered workflow: {workflow.id} ({workflow.name})")

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        return self._workflows.get(workflow_id)

    def list_workflows(self) -> List[WorkflowDefinition]:
        return list(self._workflows.values())


_GLOBAL_WORKFLOW_REGISTRY: Optional[WorkflowRegistry] = None


def get_workflow_registry() -> WorkflowRegistry:
    global _GLOBAL_WORKFLOW_REGISTRY
    if _GLOBAL_WORKFLOW_REGISTRY is None:
        _GLOBAL_WORKFLOW_REGISTRY = WorkflowRegistry()
    return _GLOBAL_WORKFLOW_REGISTRY
