import os

import pytest
from fastapi import FastAPI

import deployment
import main


def test_deployment_exposes_asgi_app():
    assert isinstance(deployment.app, FastAPI)


def test_deployment_health_reports_default_mode(monkeypatch):
    monkeypatch.delenv("NERO_DEPLOYMENT_MODE", raising=False)
    response = deployment.health()
    assert response["status"] == "ok"
    assert response["mode"] == "api"


def test_main_cli_flag_still_routes_to_run_app(monkeypatch):
    calls = {}

    def fake_run_app(*, cli=False, config=None):
        calls["cli"] = cli
        calls["config"] = config
        return 0

    monkeypatch.setattr(main, "load_run_app", lambda: fake_run_app)
    monkeypatch.setattr(main.sys, "argv", ["main.py", "--cli"])
    monkeypatch.delenv("NERO_LOG_LEVEL", raising=False)

    with pytest.raises(SystemExit) as exc:
        main.main()

    assert exc.value.code == 0
    assert calls == {"cli": True, "config": None}
