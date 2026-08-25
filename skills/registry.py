"""
Skill Registry managing discovery, registration, and dispatch of skills.
"""
from typing import Dict, Optional, List
from .base import BaseSkill, SkillResult
from utils.logger import get_logger

logger = get_logger("skill_registry")


class SkillRegistry:
    """Registry maintaining active skills mapped to supported actions."""

    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self._action_map: Dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> None:
        """Register a skill instance."""
        self._skills[skill.name] = skill
        for action in skill.supported_actions:
            self._action_map[action] = skill
        logger.info(f"Registered skill: {skill.name} for actions: {skill.supported_actions}")

    def get_skill_for_action(self, action: str) -> Optional[BaseSkill]:
        """Find the registered skill capable of handling the action."""
        return self._action_map.get(action)

    def list_actions(self) -> List[str]:
        return list(self._action_map.keys())

    async def dispatch(self, action: str, parameters: Dict) -> SkillResult:
        """Dispatch action to matching skill."""
        skill = self.get_skill_for_action(action)
        if not skill:
            return SkillResult(
                success=False,
                output_message=f"No skill registered to handle action '{action}'.",
                spoken_message=f"I don't know how to handle the action '{action}'."
            )
        try:
            return await skill.execute(action, parameters)
        except Exception as e:
            logger.error(f"Error executing skill '{skill.name}' for action '{action}': {e}", exc_info=True)
            return SkillResult(
                success=False,
                output_message=f"Error executing {action}: {str(e)}",
                spoken_message=f"An error occurred while executing {action}."
            )


_GLOBAL_SKILL_REGISTRY: Optional[SkillRegistry] = None


def get_skill_registry() -> SkillRegistry:
    global _GLOBAL_SKILL_REGISTRY
    if _GLOBAL_SKILL_REGISTRY is None:
        _GLOBAL_SKILL_REGISTRY = SkillRegistry()
    return _GLOBAL_SKILL_REGISTRY
