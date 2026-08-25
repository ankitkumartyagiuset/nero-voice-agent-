"""
Data models and state schemas for the NERO Workflow Automation Engine.
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class StepType(Enum):
    ACTION = "action"
    DELAY = "delay"
    TTS = "tts"


class WorkflowStatus(Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class WorkflowStep:
    name: str
    step_type: StepType = StepType.ACTION
    action: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    delay_seconds: float = 0.0
    message: str = ""
    is_parallel: bool = False


@dataclass
class WorkflowDefinition:
    id: str
    name: str
    description: str
    steps: List[WorkflowStep] = field(default_factory=list)
    tts_announcement: Optional[str] = None
