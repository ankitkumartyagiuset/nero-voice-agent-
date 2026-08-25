"""
Local LLM Provider (Ollama / vLLM / llama.cpp) implementation.
"""
import time
import requests
from typing import List, Dict, Any, Optional
from .llm_provider import BaseLLMProvider, LLMResponse
from config.settings import LocalLLMConfig
from utils.logger import get_logger

logger = get_logger("local_llm_provider")


class LocalLLMProvider(BaseLLMProvider):
    name = "local"

    def __init__(self, config: LocalLLMConfig):
        self.config = config

    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.4,
        max_tokens: int = 300,
    ) -> LLMResponse:
        start_time = time.perf_counter()

        try:
            url = f"{self.config.base_url.rstrip('/')}/chat/completions"
            payload = {
                "model": self.config.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            resp = requests.post(url, json=payload, timeout=12)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return LLMResponse(content=content, latency_ms=round(elapsed_ms, 2))
            else:
                return LLMResponse(content="Local LLM endpoint offline.", latency_ms=round(elapsed_ms, 2))

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return LLMResponse(content="Local LLM unreachable.", latency_ms=round(elapsed_ms, 2))
