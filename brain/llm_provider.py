"""
Abstract Base Provider for AI/LLM models.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from config.loader import get_settings


@dataclass
class ToolCall:
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    content: Optional[str] = None
    tool_calls: List[ToolCall] = field(default_factory=list)
    latency_ms: float = 0.0
    finish_reason: str = "stop"


class BaseLLMProvider(ABC):
    """Abstract interface for LLM backends (OpenAI, Gemini, Local)."""

    name: str = "base_llm"

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.4,
        max_tokens: int = 300,
    ) -> LLMResponse:
        """Send chat messages and optional tool definitions to the model."""
        pass


def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    """Factory to instantiate the configured LLM provider."""
    settings = get_settings()
    name = provider_name or settings.ai.default_provider

    if name == "gemini":
        from .gemini_provider import GeminiProvider
        return GeminiProvider(settings.ai.gemini)
    elif name == "local":
        from .local_provider import LocalLLMProvider
        return LocalLLMProvider(settings.ai.local)
    else:
        from .openai_provider import OpenAIProvider
        return OpenAIProvider(settings.ai.openai)
