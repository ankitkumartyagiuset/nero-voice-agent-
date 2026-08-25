"""
Central Assistant Orchestrator for NERO.
Coordinates Voice, Fast Path Intent Routing, AI Brain, Skills, Security, and State Transitions.
"""
import asyncio
import time
import uuid
from typing import Optional, Dict, Any

from config.loader import get_settings
from config.settings import NeroSettings
from .state import StateMachine, AssistantState
from .event_bus import get_event_bus
from .events import (
    StateChangedEvent,
    WakeWordDetectedEvent,
    IntentRoutedEvent,
    SkillExecutionStartedEvent,
    SkillExecutionCompletedEvent,
    ConfirmationRequestedEvent,
    ErrorEvent,
)
from voice.audio_stream import get_audio_stream
from voice.wake_word import WakeWordDetector
from voice.vad import VoiceActivityDetector
from voice.speech_to_text import get_stt_engine
from voice.text_to_speech import get_tts_engine
from voice.audio_session import AudioSessionManager
from brain.intent_router import FastIntentRouter, IntentMatch
from brain.llm_provider import get_llm_provider, BaseLLMProvider
from brain.tool_schema import NERO_TOOLS
from brain.conversation import ConversationManager
from brain.response_generator import ResponseGenerator
from skills.registry import get_skill_registry
from skills.app_control import AppControlSkill
from skills.browser import BrowserSkill
from skills.system import SystemSkill
from skills.media import MediaSkill
from skills.screenshot import ScreenshotSkill
from skills.weather import WeatherSkill
from skills.news import NewsSkill
from skills.reminders import RemindersSkill
from skills.time_date import TimeDateSkill
from skills.search import SearchSkill
from security.permissions import PermissionManager, PermissionLevel
from security.policy import SecurityPolicy
from security.command_validator import CommandValidator
from security.secrets import get_confirmation_manager
from automation.workflow_engine import get_workflow_engine
from automation.workflow_registry import get_workflow_registry
from automation.scheduler import get_scheduler
from services.health_service import get_health_service
from utils.metrics import LatencyTracker, MetricsCollector
from utils.logger import get_logger

logger = get_logger("assistant")


class NeroAssistant:
    """Master controller managing the complete NERO AI Desktop Assistant lifecycle."""

    def __init__(self, settings: Optional[NeroSettings] = None):
        self.settings = settings or get_settings()
        self.event_bus = get_event_bus()
        self.state_machine = StateMachine(initial_state=AssistantState.STARTING)

        # Register state listener for event bus
        self.state_machine.add_listener(self._on_state_change)

        # Core components
        self.health_service = get_health_service()
        self.metrics_collector = MetricsCollector()
        self.permission_mgr = PermissionManager()
        self.security_policy = SecurityPolicy(self.settings.security)
        self.validator = CommandValidator(self.permission_mgr, self.security_policy)
        self.confirmation_mgr = get_confirmation_manager()

        # Storage & Conversation
        self.conversation_mgr = ConversationManager()
        self.response_generator = ResponseGenerator()

        # Skills & Workflows
        self.skill_registry = get_skill_registry()
        self.workflow_engine = get_workflow_engine()
        self.workflow_registry = get_workflow_registry()
        self.scheduler = get_scheduler()

        # Voice Components
        self.audio_stream = get_audio_stream()
        self.wake_detector = WakeWordDetector(
            keyword=self.settings.voice.wake_word.keyword,
            sensitivity=self.settings.voice.wake_word.sensitivity,
        )
        self.vad = VoiceActivityDetector(
            silence_duration_ms=self.settings.voice.vad.silence_duration_ms,
            min_speech_duration_ms=self.settings.voice.vad.min_speech_duration_ms,
        )
        self.stt_engine = get_stt_engine()
        self.tts_engine = get_tts_engine()

        # Brain & Routing
        self.fast_router = FastIntentRouter()
        self.llm_provider: BaseLLMProvider = get_llm_provider(self.settings.ai.default_provider)

        # Audio Session Coordinator
        self.audio_session = AudioSessionManager(
            state_machine=self.state_machine,
            audio_stream=self.audio_stream,
            wake_detector=self.wake_detector,
            vad=self.vad,
            stt=self.stt_engine,
        )
        self.audio_session.set_transcription_callback(self._on_speech_transcribed)

        # Wire scheduler callback
        self.scheduler.set_alert_callback(self._on_reminder_alert)

        self._init_skills()

    def _on_state_change(self, old_state: AssistantState, new_state: AssistantState) -> None:
        self.event_bus.publish(StateChangedEvent(old_state=old_state, new_state=new_state))

    def _init_skills(self) -> None:
        """Register all built-in laptop skills."""
        self.skill_registry.register(AppControlSkill())
        self.skill_registry.register(BrowserSkill())
        self.skill_registry.register(SystemSkill())
        self.skill_registry.register(MediaSkill())
        self.skill_registry.register(ScreenshotSkill())
        self.skill_registry.register(WeatherSkill())
        self.skill_registry.register(NewsSkill())
        self.skill_registry.register(RemindersSkill())
        self.skill_registry.register(TimeDateSkill())
        self.skill_registry.register(SearchSkill())

    async def initialize(self, enable_voice: bool = True) -> bool:
        """Initialize subsystems, optionally excluding hardware-backed voice services."""
        logger.info("Initializing NERO subsystems...")

        try:
            if enable_voice:
                mic_ok = self.audio_stream.start()
                self.health_service.set_status("mic", "READY" if mic_ok else "DEGRADED")
                asyncio.create_task(self._warmup_stt())
            else:
                logger.info("Voice services disabled for headless startup.")
                self.health_service.set_status("mic", "DISABLED")
                self.health_service.set_status("stt", "DISABLED")

            asyncio.create_task(self.scheduler.start())

            # Ready
            self.state_machine.transition_to(AssistantState.IDLE, reason="Startup completed")
            logger.info("NERO is online and READY.")
            return True

        except Exception as e:
            logger.error(f"Startup error: {e}", exc_info=True)
            self.state_machine.transition_to(AssistantState.ERROR, reason=str(e))
            return False

    async def _warmup_stt(self) -> None:
        """Load STT model asynchronously without blocking startup."""
        try:
            self.stt_engine.load_model()
            self.health_service.set_status("stt", "READY")
        except Exception as e:
            logger.warning(f"STT background warmup: {e}")
            self.health_service.set_status("stt", "DEGRADED")

    def _on_speech_transcribed(self, text: str, stt_latency_ms: float) -> None:
        """Callback from audio session when user voice command is transcribed."""
        asyncio.create_task(self.process_command(text, stt_latency_ms=stt_latency_ms, from_voice=True))

    def _on_reminder_alert(self, message: str) -> None:
        """Triggered when a reminder is due."""
        spoken = f"Reminder alert: {message}"
        self.tts_engine.speak(spoken)

    async def process_command(
        self,
        command_text: str,
        stt_latency_ms: float = 0.0,
        from_voice: bool = False
    ) -> str:
        """
        Master execution pipeline:
        Command -> Fast Intent Router -> Permission Check -> Skill OR LLM -> TTS -> State Recovery
        """
        if not command_text or not command_text.strip():
            self.state_machine.transition_to(AssistantState.IDLE, reason="Empty command")
            return ""

        session_id = str(uuid.uuid4())[:8]
        tracker = LatencyTracker(session_id=session_id)
        tracker.metrics.command_text = command_text
        tracker.metrics.stt_latency_ms = stt_latency_ms

        logger.info(f"Processing command: '{command_text}'")
        self.conversation_mgr.add_user_message(command_text)

        # -------------------------------------------------------------
        # 1. Check Pending Safety Confirmation ("yes" / "confirm")
        # -------------------------------------------------------------
        pending = self.confirmation_mgr.get_latest_pending()
        if pending:
            clean_input = command_text.lower().strip()
            if clean_input in ("yes", "confirm", "proceed", "go ahead", "do it", "sure"):
                token, action, params = pending
                self.confirmation_mgr.consume_latest()
                logger.info(f"User confirmed dangerous action: {action}")
                return await self._execute_confirmed_action(action, params, tracker)
            elif clean_input in ("no", "cancel", "stop", "abort", "don't", "dont"):
                self.confirmation_mgr.consume_latest()
                msg = "Action cancelled."
                self.tts_engine.speak(msg)
                self.state_machine.transition_to(AssistantState.IDLE, reason="Action cancelled by user")
                return msg

        # -------------------------------------------------------------
        # 2. Fast Path Local Intent Routing (<5ms)
        # -------------------------------------------------------------
        tracker.start_stage("intent")
        intent_match: IntentMatch = self.fast_router.route(command_text)
        intent_ms = tracker.end_stage("intent")

        if intent_match.is_matched:
            # -------------------- FAST PATH EXECUTION --------------------
            tracker.metrics.execution_path = "fast"
            self.event_bus.publish(IntentRoutedEvent(
                session_id=session_id,
                intent_type=intent_match.action,
                action=intent_match.action,
                parameters=intent_match.parameters,
                execution_path="fast",
                latency_ms=intent_ms
            ))

            return await self._execute_fast_path(intent_match, tracker)
        else:
            # -------------------- AI PATH EXECUTION ----------------------
            tracker.metrics.execution_path = "ai"
            return await self._execute_ai_path(command_text, tracker)

    async def _execute_fast_path(self, intent: IntentMatch, tracker: LatencyTracker) -> str:
        """Execute deterministic laptop action bypassing LLM."""
        action = intent.action
        params = intent.parameters

        # Handle workflow cancellation special case
        if action == "cancel_workflow":
            wf_id = params.get("workflow", "coding_mode")
            self.workflow_engine.cancel_workflow(wf_id)
            msg = f"Cancelled {wf_id.replace('_', ' ')}."
            self.tts_engine.speak(msg)
            self.state_machine.transition_to(AssistantState.IDLE, reason="Workflow cancelled")
            return msg

        # Handle workflow execution
        if action == "run_workflow":
            wf_id = params.get("workflow", "coding_mode")
            wf_def = self.workflow_registry.get_workflow(wf_id)
            if wf_def:
                if wf_def.tts_announcement:
                    self.tts_engine.speak(wf_def.tts_announcement)
                asyncio.create_task(self.workflow_engine.execute_workflow(wf_def))
                self.state_machine.transition_to(AssistantState.IDLE, reason="Workflow started")
                return f"Running workflow: {wf_def.name}"

        # 1. Security & Permission Validation
        allowed_apps = list(self.settings.applications.keys())
        is_valid, reason = self.validator.validate_action(action, params, allowed_apps)
        if not is_valid:
            self.tts_engine.speak(reason)
            self.state_machine.transition_to(AssistantState.IDLE, reason="Validation failed")
            return reason

        # 2. Skill Execution
        self.state_machine.transition_to(AssistantState.EXECUTING, reason=f"Executing {action}")
        tracker.start_stage("skill")
        self.event_bus.publish(SkillExecutionStartedEvent(skill_name=action, parameters=params))

        result = await self.skill_registry.dispatch(action, params)
        skill_ms = tracker.end_stage("skill")

        self.event_bus.publish(SkillExecutionCompletedEvent(
            skill_name=action,
            success=result.success,
            output_message=result.output_message,
            data=result.data,
            latency_ms=skill_ms
        ))

        # Check if confirmation requested (e.g. shutdown)
        if result.requires_confirmation:
            self.event_bus.publish(ConfirmationRequestedEvent(
                session_id=tracker.session_id,
                action=action,
                prompt=result.speech,
                token=result.confirmation_token or ""
            ))
            self.tts_engine.speak(result.speech)
            self.state_machine.transition_to(AssistantState.IDLE, reason="Waiting for confirmation")
            return result.output_message

        # 3. Text to Speech Response
        if result.speech:
            self.state_machine.transition_to(AssistantState.SPEAKING, reason="Speaking result")
            self.tts_engine.speak(
                result.speech,
                on_finish=lambda: self.state_machine.transition_to(AssistantState.IDLE, reason="Speech finished")
            )
        else:
            self.state_machine.transition_to(AssistantState.IDLE, reason="Execution complete")

        self.conversation_mgr.add_assistant_message(result.output_message, intent=action, latency_ms=skill_ms)
        metrics = tracker.finalize(success=result.success)
        self.metrics_collector.add(metrics)

        return result.output_message

    async def _execute_ai_path(self, user_query: str, tracker: LatencyTracker) -> str:
        """Execute query via LLM reasoning with structured function tools."""
        self.state_machine.transition_to(AssistantState.THINKING, reason="Querying AI Brain")
        tracker.start_stage("llm")

        messages = self.conversation_mgr.get_messages_for_llm()
        response = await self.llm_provider.chat(
            messages=messages,
            tools=NERO_TOOLS,
            temperature=self.settings.ai.temperature,
            max_tokens=self.settings.ai.max_tokens
        )
        llm_ms = tracker.end_stage("llm")
        tracker.metrics.llm_latency_ms = llm_ms

        # 1. Handle structured Tool Calls requested by LLM
        if response.tool_calls:
            tool_results = []
            for tc in response.tool_calls:
                action = tc.name
                params = tc.arguments
                allowed_apps = list(self.settings.applications.keys())

                # Validate
                is_valid, reason = self.validator.validate_action(action, params, allowed_apps)
                if not is_valid:
                    tool_results.append(reason)
                    continue

                self.state_machine.transition_to(AssistantState.EXECUTING, reason=f"Executing tool {action}")
                res = await self.skill_registry.dispatch(action, params)
                tool_results.append(res.output_message)

                if res.speech:
                    self.state_machine.transition_to(AssistantState.SPEAKING, reason="Speaking tool result")
                    self.tts_engine.speak(
                        res.speech,
                        on_finish=lambda: self.state_machine.transition_to(AssistantState.IDLE, reason="Speech finished")
                    )

            combined_output = "\n".join(tool_results)
            self.conversation_mgr.add_assistant_message(combined_output, intent="tool_call", latency_ms=llm_ms)
            metrics = tracker.finalize(success=True)
            self.metrics_collector.add(metrics)
            return combined_output

        # 2. Conversational text response
        content = response.content or "I didn't receive a response from the AI service."
        speech_text = self.response_generator.format_speech(content)

        self.state_machine.transition_to(AssistantState.SPEAKING, reason="Speaking response")
        self.tts_engine.speak(
            speech_text,
            on_finish=lambda: self.state_machine.transition_to(AssistantState.IDLE, reason="Speech finished")
        )

        self.conversation_mgr.add_assistant_message(content, intent="ai_chat", latency_ms=llm_ms)
        metrics = tracker.finalize(success=True)
        self.metrics_collector.add(metrics)
        return content

    async def _execute_confirmed_action(self, action: str, params: Dict, tracker: LatencyTracker) -> str:
        """Execute dangerous action that has received explicit user confirmation."""
        params["confirmed"] = True
        self.state_machine.transition_to(AssistantState.EXECUTING, reason=f"Executing confirmed {action}")
        result = await self.skill_registry.dispatch(action, params)

        if result.speech:
            self.tts_engine.speak(
                result.speech,
                on_finish=lambda: self.state_machine.transition_to(AssistantState.IDLE, reason="Confirmed action finished")
            )
        else:
            self.state_machine.transition_to(AssistantState.IDLE, reason="Confirmed action finished")

        metrics = tracker.finalize(success=result.success)
        self.metrics_collector.add(metrics)
        return result.output_message

    def shutdown(self) -> None:
        """Clean shutdown of all subsystems."""
        self.state_machine.transition_to(AssistantState.STOPPING, reason="Application shutdown")
        self.audio_stream.stop()
        self.tts_engine.stop()
        self.scheduler.stop()
        logger.info("NERO assistant shut down cleanly.")
