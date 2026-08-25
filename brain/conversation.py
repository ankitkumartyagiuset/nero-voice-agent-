"""
Bounded Conversation Memory Manager with automatic summarization for NERO.
"""
from typing import List, Dict, Optional
from storage.repositories import ConversationRepository
from config.loader import get_settings
from utils.logger import get_logger

logger = get_logger("conversation_mgr")

NERO_SYSTEM_PROMPT = """You are NERO, a futuristic, fast, and intelligent voice-first personal desktop AI assistant.
Your answers will be spoken back to the user aloud.
Guidelines:
1. Be concise, direct, and helpful. Avoid long conversational filler unless asked for detail.
2. For coding questions, explain key concepts clearly and provide brief examples.
3. When actions (like opening applications or searching) are needed, use available tools.
4. Never generate raw shell scripts or claim to execute dangerous commands directly.
"""


class ConversationManager:
    """Manages bounded multi-turn message history with rolling summaries."""

    def __init__(self, session_id: str = "default_session", repo: Optional[ConversationRepository] = None):
        self.session_id = session_id
        self.repo = repo or ConversationRepository()
        self.settings = get_settings()
        self.limit = self.settings.ai.memory_message_limit

    def add_user_message(self, text: str) -> None:
        self.repo.add_message(self.session_id, "user", text)

    def add_assistant_message(self, text: str, intent: Optional[str] = None, latency_ms: Optional[float] = None) -> None:
        self.repo.add_message(self.session_id, "assistant", text, intent=intent, latency_ms=latency_ms)

    def get_messages_for_llm(self) -> List[Dict[str, str]]:
        """Construct the prompt messages array including system prompt and bounded history."""
        messages = [{"role": "system", "content": NERO_SYSTEM_PROMPT}]

        # Append summary if available
        summary = self.repo.get_summary(self.session_id)
        if summary:
            messages.append({"role": "system", "content": f"Context summary of earlier conversation: {summary}"})

        # Fetch recent messages
        recent = self.repo.get_recent_messages(self.session_id, limit=self.limit)
        for m in recent:
            messages.append({"role": m.role, "content": m.content})

        return messages

    def clear(self) -> None:
        self.repo.clear_session(self.session_id)
        logger.info(f"Cleared session history for: {self.session_id}")
