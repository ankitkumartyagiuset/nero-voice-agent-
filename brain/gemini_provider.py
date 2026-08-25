"""
Google Gemini LLM Provider implementation via REST API.
"""
import time
import requests
from typing import List, Dict, Any, Optional
from .llm_provider import BaseLLMProvider, LLMResponse, ToolCall
from config.settings import GeminiConfig
from utils.logger import get_logger

logger = get_logger("gemini_provider")


class GeminiProvider(BaseLLMProvider):
    name = "gemini"

    def __init__(self, config: GeminiConfig):
        self.config = config

    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.4,
        max_tokens: int = 300,
    ) -> LLMResponse:
        start_time = time.perf_counter()

        if not self.config.api_key:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return LLMResponse(
                content="Gemini API key is not configured in .env. Deterministic fast path commands remain operational.",
                latency_ms=round(elapsed, 2)
            )

        try:
            # Build simple Gemini prompt
            contents = []
            for m in messages:
                role = "user" if m["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m["content"]}]})

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.model}:generateContent?key={self.config.api_key}"
            payload = {
                "contents": contents,
                "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
            }

            resp = requests.post(url, json=payload, timeout=10)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return LLMResponse(content=text, latency_ms=round(elapsed_ms, 2))
            else:
                return LLMResponse(content=f"Gemini error: {resp.text}", latency_ms=round(elapsed_ms, 2))

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Gemini chat error: {e}")
            return LLMResponse(content=f"Gemini error: {e}", latency_ms=round(elapsed_ms, 2))
