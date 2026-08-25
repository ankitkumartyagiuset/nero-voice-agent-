"""Voice subsystem for NERO including streaming capture, wake word, VAD, STT, and TTS."""
from .audio_stream import AudioStream, get_audio_stream
from .wake_word import WakeWordDetector
from .vad import VoiceActivityDetector
from .speech_to_text import SpeechToTextEngine, get_stt_engine
from .text_to_speech import TextToSpeechEngine, get_tts_engine
from .audio_session import AudioSessionManager

__all__ = [
    "AudioStream", "get_audio_stream",
    "WakeWordDetector",
    "VoiceActivityDetector",
    "SpeechToTextEngine", "get_stt_engine",
    "TextToSpeechEngine", "get_tts_engine",
    "AudioSessionManager",
]
