"""
Main Command Line Entry Point for NERO.
Parses CLI options and launches NERO GUI or CLI headless mode.
"""
import sys
import argparse
import os
from typing import Callable

# Ensure package root in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def load_run_app() -> Callable[..., int]:
    from app import run_app
    return run_app


def main():
    parser = argparse.ArgumentParser(
        description="NERO — Production-Grade Voice-First AI Desktop Assistant"
    )
    parser.add_argument(
        "--cli", "--no-ui", action="store_true",
        help="Run NERO in headless terminal / CLI mode without launching the PySide6 HUD"
    )
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to custom config.yaml file"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable detailed debug logging"
    )

    args = parser.parse_args()

    if args.debug:
        os.environ["NERO_LOG_LEVEL"] = "DEBUG"

    run_app = load_run_app()
    sys.exit(run_app(cli=args.cli, config=args.config))


if __name__ == "__main__":
    main()
