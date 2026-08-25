"""
Application Control Skill.
Launches and closes configured desktop applications safely.
"""
import os
import subprocess
import webbrowser
import psutil
from typing import Dict, Any, Optional
from .base import BaseSkill, SkillResult
from config.settings import AppTarget
from config.loader import get_settings
from utils.logger import get_logger

logger = get_logger("app_control_skill")


class AppControlSkill(BaseSkill):
    name = "app_control"
    description = "Launch, switch to, or close desktop applications"
    supported_actions = ["open_application", "close_application"]

    def __init__(self, apps_config: Optional[Dict[str, AppTarget]] = None):
        self.settings = get_settings()
        self.apps = apps_config or self.settings.applications

    async def execute(self, action: str, parameters: Dict[str, Any]) -> SkillResult:
        app_key = parameters.get("application", "").lower().strip()
        app_info = self.apps.get(app_key)

        if not app_info:
            # Fallback search by alias/name
            for k, v in self.apps.items():
                if v.name.lower() == app_key or app_key in v.name.lower():
                    app_info = v
                    app_key = k
                    break

        if not app_info:
            return SkillResult(
                success=False,
                output_message=f"Application '{app_key}' is not configured in NERO settings.",
                spoken_message=f"{app_key.title()} is not installed or configured."
            )

        if action == "open_application":
            return self._open_app(app_key, app_info)
        elif action == "close_application":
            return self._close_app(app_key, app_info)

        return SkillResult(success=False, output_message=f"Unsupported action {action}")

    def _open_app(self, app_key: str, app_info: AppTarget) -> SkillResult:
        # Check if it is a web shortcut (e.g. YouTube, GitHub)
        if app_info.url:
            webbrowser.open(app_info.url)
            return SkillResult(
                success=True,
                output_message=f"Opened {app_info.name} in default browser.",
                spoken_message=f"Opening {app_info.name}."
            )

        # Native OS command execution
        cmd = None
        if os.name == "nt" and app_info.windows:
            cmd = app_info.windows.get("command")
        elif app_info.linux:
            cmd = app_info.linux.get("command")
        elif app_info.macos:
            cmd = app_info.macos.get("command")

        if not cmd:
            return SkillResult(
                success=False,
                output_message=f"No execution command configured for {app_info.name} on this OS.",
                spoken_message=f"I couldn't launch {app_info.name} on this system."
            )

        try:
            # Launch detached process safely
            if os.name == "nt":
                subprocess.Popen(
                    [cmd],
                    shell=False,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                )
            else:
                subprocess.Popen([cmd], start_new_session=True)

            logger.info(f"Launched application: {app_info.name} ({cmd})")
            return SkillResult(
                success=True,
                output_message=f"Successfully launched {app_info.name}.",
                spoken_message=f"Opening {app_info.name}."
            )
        except Exception as e:
            logger.error(f"Failed to launch {app_info.name}: {e}")
            return SkillResult(
                success=False,
                output_message=f"Failed to launch {app_info.name}: {e}",
                spoken_message=f"I couldn't open {app_info.name}."
            )

    def _close_app(self, app_key: str, app_info: AppTarget) -> SkillResult:
        exec_name = None
        if os.name == "nt" and app_info.windows:
            exec_name = app_info.windows.get("executable_name") or app_info.windows.get("command")
        elif app_info.linux:
            exec_name = app_info.linux.get("command")

        if not exec_name:
            exec_name = app_key

        terminated = 0
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    pname = proc.info['name']
                    if pname and (exec_name.lower() in pname.lower() or app_key in pname.lower()):
                        proc.terminate()
                        terminated += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if terminated > 0:
                logger.info(f"Closed {terminated} process(es) matching {app_info.name}")
                return SkillResult(
                    success=True,
                    output_message=f"Closed {app_info.name}.",
                    spoken_message=f"Closing {app_info.name}."
                )
            else:
                return SkillResult(
                    success=True,
                    output_message=f"{app_info.name} is not currently running.",
                    spoken_message=f"{app_info.name} is not running."
                )
        except Exception as e:
            logger.error(f"Failed to close {app_info.name}: {e}")
            return SkillResult(
                success=False,
                output_message=f"Failed to close {app_info.name}: {e}",
                spoken_message=f"I couldn't close {app_info.name}."
            )
