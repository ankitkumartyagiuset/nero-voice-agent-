"""Platform-specific system controllers."""
import sys
from .base import BaseSystemController
from .windows import WindowsSystemController

def get_platform_controller() -> BaseSystemController:
    """Return platform controller matching the host OS."""
    if sys.platform.startswith("win"):
        return WindowsSystemController()
    elif sys.platform.startswith("darwin"):
        from .macos import MacOSSystemController
        return MacOSSystemController()
    else:
        from .linux import LinuxSystemController
        return LinuxSystemController()

__all__ = ["BaseSystemController", "WindowsSystemController", "get_platform_controller"]
