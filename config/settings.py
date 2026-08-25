"""
Settings models and schema definitions for NERO assistant.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    name: str = "NERO"
    version: str = "1.0.0"
    env: str = "production"
    debug: bool = False
    ui_enabled: bool = True
    confirmation_timeout_seconds: int = 15


class WakeWordConfig(BaseModel):
    keyword: str = "nero"
    sensitivity: float = 0.65
    sample_rate: int = 16000
    chunk_size: int = 1024
    energy_threshold: float = 400.0
    cooldown_seconds: float = 1.5


class VADConfig(BaseModel):
    enabled: bool = True
    silence_duration_ms: int = 450
    min_speech_duration_ms: int = 120
    max_command_duration_seconds: int = 12
    energy_threshold_multiplier: float = 1.4


class STTConfig(BaseModel):
    provider: str = "faster_whisper"
    model: str = "base"
    device: str = "auto"
    compute_type: str = "auto"
    language: str = "en"
    beam_size: int = 1


class TTSConfig(BaseModel):
    provider: str = "pyttsx3"
    rate: int = 185
    volume: float = 0.95
    voice_index: int = 0
    interruptible: bool = True


class VoiceConfig(BaseModel):
    wake_word: WakeWordConfig = Field(default_factory=WakeWordConfig)
    vad: VADConfig = Field(default_factory=VADConfig)
    stt: STTConfig = Field(default_factory=STTConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)


class OpenAIConfig(BaseModel):
    model: str = "gpt-4o-mini"
    base_url: str = "https://api.openai.com/v1"
    api_key: Optional[str] = None


class GeminiConfig(BaseModel):
    model: str = "gemini-1.5-flash"
    api_key: Optional[str] = None


class LocalLLMConfig(BaseModel):
    model: str = "llama3:latest"
    base_url: str = "http://localhost:11434/v1"


class AIConfig(BaseModel):
    default_provider: str = "openai"
    fallback_enabled: bool = True
    temperature: float = 0.4
    max_tokens: int = 300
    memory_message_limit: int = 10
    auto_summarize: bool = True
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
    local: LocalLLMConfig = Field(default_factory=LocalLLMConfig)


class AppTarget(BaseModel):
    name: str
    windows: Optional[Dict[str, Any]] = None
    linux: Optional[Dict[str, Any]] = None
    macos: Optional[Dict[str, Any]] = None
    url: Optional[str] = None


class WorkflowConfig(BaseModel):
    name: str
    description: str = ""
    applications: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    mute_media: bool = False
    tts_announcement: Optional[str] = None


class SecurityConfig(BaseModel):
    strict_validation: bool = True
    blocked_commands: List[str] = Field(default_factory=lambda: [
        "format", "rmdir", "reg", "powershell -enc", "cmd /c", "del /f /s /q"
    ])
    confirmation_required: List[str] = Field(default_factory=lambda: [
        "shutdown", "restart", "delete_file", "install_software"
    ])


class StorageConfig(BaseModel):
    db_path: str = "nero.db"
    backup_interval_minutes: int = 60


class NeroSettings(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    voice: VoiceConfig = Field(default_factory=VoiceConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    applications: Dict[str, AppTarget] = Field(default_factory=dict)
    workflows: Dict[str, WorkflowConfig] = Field(default_factory=dict)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
