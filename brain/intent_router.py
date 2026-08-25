"""
Fast Local Intent Router for NERO.
Bypasses LLM for deterministic laptop controls, running in sub-5ms.
"""
import re
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from utils.logger import get_logger

logger = get_logger("intent_router")


@dataclass
class IntentMatch:
    is_matched: bool
    action: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    execution_path: str = "fast"  # "fast" or "ai"


class FastIntentRouter:
    """Pattern-based local intent router for rapid deterministic command execution."""

    def __init__(self):
        # Application name synonyms
        self.app_synonyms = {
            "vscode": "vscode",
            "vs code": "vscode",
            "visual studio code": "vscode",
            "editor": "vscode",
            "my editor": "vscode",
            "chrome": "chrome",
            "google chrome": "chrome",
            "browser": "chrome",
            "web browser": "chrome",
            "spotify": "spotify",
            "music player": "spotify",
            "notepad": "notepad",
            "text editor": "notepad",
            "terminal": "terminal",
            "command prompt": "terminal",
            "powershell": "terminal",
            "youtube": "youtube",
            "github": "github",
        }

    def route(self, text: str) -> IntentMatch:
        """Route input text to a structured action or mark for AI path."""
        if not text:
            return IntentMatch(is_matched=False, execution_path="ai")

        clean = text.lower().strip().rstrip(".?!")

        # 0. User Confirmation keywords
        if clean in ("yes", "confirm", "proceed", "go ahead", "do it", "sure", "yes please"):
            return IntentMatch(is_matched=True, action="confirm_action", parameters={}, confidence=1.0)

        if clean in ("no", "cancel", "stop", "abort", "don't", "dont"):
            return IntentMatch(is_matched=True, action="cancel_action", parameters={}, confidence=1.0)

        # 1. Coding Mode & Workflow Automation
        if re.search(r"\b(?:coding mode on|activate coding mode|start coding mode|get me ready for coding|turn on coding mode)\b", clean):
            return IntentMatch(is_matched=True, action="run_workflow", parameters={"workflow": "coding_mode"})

        if re.search(r"\b(?:stop coding mode|cancel coding mode|turn off coding mode|disable coding mode)\b", clean):
            return IntentMatch(is_matched=True, action="cancel_workflow", parameters={"workflow": "coding_mode"})

        if re.search(r"\b(?:focus mode on|activate focus mode|start focus mode)\b", clean):
            return IntentMatch(is_matched=True, action="run_workflow", parameters={"workflow": "focus_mode"})

        # 2. Screenshot
        if re.search(r"\b(?:take (?:a )?screenshot|screenshot|capture screen|screen capture)\b", clean):
            return IntentMatch(is_matched=True, action="take_screenshot", parameters={})

        # 3. Time & Date
        if re.search(r"\b(?:what(?:'s| is) (?:the )?time|tell me the time|current time|what time is it)\b", clean):
            return IntentMatch(is_matched=True, action="get_time", parameters={})

        if re.search(r"\b(?:what(?:'s| is) (?:today(?:'s)? )?date|tell me the date|today(?:'s)? date)\b", clean):
            return IntentMatch(is_matched=True, action="get_date", parameters={})

        # 4. Weather
        weather_match = re.search(r"\b(?:weather(?: in ([a-zA-Z\s]+))?|what(?:'s| is) the weather(?: in ([a-zA-Z\s]+))?|temperature(?: in ([a-zA-Z\s]+))?)\b", clean)
        if weather_match:
            city = weather_match.group(1) or weather_match.group(2) or weather_match.group(3) or "New Delhi"
            return IntentMatch(is_matched=True, action="get_weather", parameters={"city": city.strip()})

        # 5. News
        if re.search(r"\b(?:news|tech news|headlines|give me (?:the )?news|what(?:'s| is) the news)\b", clean):
            return IntentMatch(is_matched=True, action="get_news", parameters={})

        # 6. YouTube Search
        yt_match = re.search(r"\b(?:search youtube for|on youtube search for|look up on youtube|search on youtube) (.+)", clean)
        if yt_match:
            return IntentMatch(is_matched=True, action="search_youtube", parameters={"query": yt_match.group(1).strip()})

        # 7. Web / Google Search
        search_match = re.search(r"\b(?:search (?:the )?web for|google|search for) (.+)", clean)
        if search_match:
            return IntentMatch(is_matched=True, action="search_web", parameters={"query": search_match.group(1).strip()})

        # 8. Volume Controls
        vol_set_match = re.search(r"\b(?:set (?:system )?volume to|volume to|set volume) (\d{1,3})(?: percent|%)?\b", clean)
        if vol_set_match:
            val = int(vol_set_match.group(1))
            return IntentMatch(is_matched=True, action="set_volume", parameters={"value": val})

        if re.search(r"\b(?:mute|mute volume|mute audio|silence)\b", clean):
            return IntentMatch(is_matched=True, action="mute_volume", parameters={})

        if re.search(r"\b(?:unmute|unmute volume|unmute audio)\b", clean):
            return IntentMatch(is_matched=True, action="unmute_volume", parameters={})

        # 9. Media Playback Controls
        if re.search(r"\b(?:pause music|play music|play pause|toggle music|pause playback|resume playback)\b", clean):
            return IntentMatch(is_matched=True, action="media_control", parameters={"command": "play_pause"})

        if re.search(r"\b(?:next song|next track|skip song|skip track)\b", clean):
            return IntentMatch(is_matched=True, action="media_control", parameters={"command": "next"})

        if re.search(r"\b(?:previous song|previous track|prev song)\b", clean):
            return IntentMatch(is_matched=True, action="media_control", parameters={"command": "previous"})

        # 10. Application Launching / Closing
        open_app_match = re.search(r"\b(?:open|launch|start|run) ([a-zA-Z0-9\s]+)", clean)
        if open_app_match:
            raw_target = open_app_match.group(1).strip()
            # Resolve synonym
            app_id = self.app_synonyms.get(raw_target, raw_target)
            return IntentMatch(is_matched=True, action="open_application", parameters={"application": app_id})

        close_app_match = re.search(r"\b(?:close|quit|kill|exit|stop) ([a-zA-Z0-9\s]+)", clean)
        if close_app_match:
            raw_target = close_app_match.group(1).strip()
            if raw_target not in ("coding mode", "focus mode"):
                app_id = self.app_synonyms.get(raw_target, raw_target)
                return IntentMatch(is_matched=True, action="close_application", parameters={"application": app_id})

        # 11. Reminders
        remind_match = re.search(r"\bremind me (?:at|in|to) (.+)", clean)
        if remind_match:
            rest = remind_match.group(1).strip()
            # e.g., "at 6 PM to study" or "in 10 minutes to submit homework"
            time_part = None
            msg_part = rest
            if " to " in rest:
                parts = rest.split(" to ", 1)
                time_part = parts[0]
                msg_part = parts[1]
            return IntentMatch(
                is_matched=True,
                action="create_reminder",
                parameters={"message": msg_part, "time": time_part}
            )

        if re.search(r"\b(?:show (?:my )?reminders|list reminders|what are my reminders)\b", clean):
            return IntentMatch(is_matched=True, action="list_reminders", parameters={})

        # 12. System Functions
        if re.search(r"\b(?:lock (?:the )?(?:pc|computer|system|screen))\b", clean):
            return IntentMatch(is_matched=True, action="lock_system", parameters={})

        if re.search(r"\b(?:shut down|shutdown|turn off (?:the )?(?:pc|computer))\b", clean):
            return IntentMatch(is_matched=True, action="shutdown_system", parameters={})

        if re.search(r"\b(?:restart (?:the )?(?:pc|computer)|reboot)\b", clean):
            return IntentMatch(is_matched=True, action="restart_system", parameters={})

        # Unmatched -> AI Path
        return IntentMatch(is_matched=False, execution_path="ai")
