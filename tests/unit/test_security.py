"""
Security and permission enforcement tests.
Verifies shell injection rejection, confirmation requirements, and secret masking.
"""
from security.permissions import PermissionManager, PermissionLevel
from security.command_validator import CommandValidator
from security.policy import SecurityPolicy
from utils.logger import mask_sensitive_data


def test_permission_tiers():
    pm = PermissionManager()
    assert pm.is_safe("open_application")
    assert pm.is_safe("take_screenshot")
    assert pm.requires_confirmation("shutdown_system")
    assert pm.requires_confirmation("restart_system")
    assert pm.is_blocked("execute_shell")
    assert pm.is_blocked("execute_raw_command")


def test_command_validator_blocks_shell_injection():
    validator = CommandValidator()
    allowed_apps = ["vscode", "chrome"]

    # Blocked shell command attempt
    is_valid, reason = validator.validate_action("execute_shell", {"cmd": "rm -rf /"}, allowed_apps)
    assert not is_valid

    # Disallowed unconfigured application
    is_valid, reason = validator.validate_action("open_application", {"application": "malware.exe"}, allowed_apps)
    assert not is_valid

    # Valid application
    is_valid, reason = validator.validate_action("open_application", {"application": "vscode"}, allowed_apps)
    assert is_valid


def test_secret_masking_in_logs():
    raw_log = "Error connecting with api_key=sk-1234567890abcdef1234567890"
    masked = mask_sensitive_data(raw_log)
    assert "sk-1234567890abcdef1234567890" not in masked
    assert "****" in masked or "..." in masked
