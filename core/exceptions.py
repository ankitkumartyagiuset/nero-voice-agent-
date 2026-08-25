"""
Domain exception hierarchy for NERO assistant.
"""


class NeroError(Exception):
    """Base exception for all NERO domain errors."""
    pass


class ConfigurationError(NeroError):
    """Raised when configuration is missing or invalid."""
    pass


class VoiceError(NeroError):
    """Base exception for audio/voice subsystem errors."""
    pass


class AudioStreamError(VoiceError):
    """Raised when microphone capture fails."""
    pass


class STTError(VoiceError):
    """Raised when speech-to-text inference fails."""
    pass


class TTSError(VoiceError):
    """Raised when text-to-speech generation/playback fails."""
    pass


class SkillError(NeroError):
    """Raised when a skill fails to execute."""
    pass


class SecurityError(NeroError):
    """Raised when a permission check or security validation fails."""
    pass


class ConfirmationRequiredError(SecurityError):
    """Raised when an action requires user confirmation before execution."""
    def __init__(self, action: str, prompt: str, token: str):
        super().__init__(prompt)
        self.action = action
        self.prompt = prompt
        self.token = token


class AIError(NeroError):
    """Base exception for LLM provider errors."""
    pass


class LLMTimeoutError(AIError):
    """Raised when LLM request exceeds configured timeout."""
    pass


class WorkflowError(NeroError):
    """Raised when an automation workflow fails."""
    pass
