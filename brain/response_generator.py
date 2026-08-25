"""
Response Generator for synthesizing spoken and text outputs.
"""
from utils.helpers import clean_voice_response


class ResponseGenerator:
    """Formats raw LLM responses or skill outputs into clean, voice-friendly text."""

    @staticmethod
    def format_speech(raw_text: str) -> str:
        """Create a clean, spoken output without markdown code fences or markdown bold syntax."""
        return clean_voice_response(raw_text)
