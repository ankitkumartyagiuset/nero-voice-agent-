"""
Abstract Base Skill interface for NERO.
Every skill implements a standardized execution protocol.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class SkillResult:
    """Standardized response from skill execution."""
    success: bool
    output_message: str
    spoken_message: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False
    confirmation_token: Optional[str] = None

    @property
    def speech(self) -> str:
        return self.spoken_message or self.output_message


class BaseSkill(ABC):
    """Abstract Base Class for all assistant capabilities."""

    name: str = "base_skill"
    description: str = "Base skill description"
    supported_actions: list[str] = []

    def can_handle(self, action: str) -> bool:
        return action in self.supported_actions

    @abstractmethod
    async def execute(self, action: str, parameters: Dict[str, Any]) -> SkillResult:
        """Execute the skill with provided structured parameters."""
        pass
