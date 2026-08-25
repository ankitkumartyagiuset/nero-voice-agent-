"""Skill modules and registry for laptop control and assistant capabilities."""
from .base import BaseSkill, SkillResult
from .registry import SkillRegistry, get_skill_registry

__all__ = ["BaseSkill", "SkillResult", "SkillRegistry", "get_skill_registry"]
