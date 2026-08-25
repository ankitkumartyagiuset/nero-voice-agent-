"""
OpenAI LLM Provider implementation using OpenAI Python SDK or async HTTP.
"""
import time
import json
from typing import List, Dict, Any, Optional
from .llm_provider import BaseLLMProvider, LLMResponse, ToolCall
from config.settings import OpenAIConfig
from utils.logger import get_logger

logger = get_logger("openai_provider")


class OpenAIProvider(BaseLLMProvider):
    name = "openai"

    def __init__(self, config: OpenAIConfig):
        self.config = config
        self._client = None
        self._init_client()

    def _init_client(self) -> None:
        if self.config.api_key:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.4,
        max_tokens: int = 300,
    ) -> LLMResponse:
        start_time = time.perf_counter()

        if not self._client:
            # Fallback when no API key configured
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return LLMResponse(
                content="OpenAI API key is not configured in .env. Deterministic fast path commands remain fully operational.",
                latency_ms=round(elapsed, 2)
            )

        try:
            kwargs: Dict[str, Any] = {
                "model": self.config.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = await self._client.chat.completions.create(**kwargs)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            choice = response.choices[0]
            msg = choice.message
            content = msg.content
            tool_calls = []

            if msg.tool_calls:
                for tc in msg.tool_calls:
                    try:
                        args = json.loads(tc.function.arguments)
                        tool_calls.append(ToolCall(name=tc.function.name, arguments=args))
                    except Exception as e:
                        logger.error(f"Failed to parse tool arguments: {e}")

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                latency_ms=round(elapsed_ms, 2),
                finish_reason=choice.finish_reason or "stop"
            )

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"OpenAI chat completion error: {e}")
            return LLMResponse(
                content=f"AI service encountered an issue: {str(e)}",
                latency_ms=round(elapsed_ms, 2),
                finish_reason="error"
            )
