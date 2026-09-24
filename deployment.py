"""
Headless ASGI deployment entrypoint for cloud platforms.
"""
import os
from fastapi import FastAPI

app = FastAPI(title="NERO Deployment API", version="1.0.0")


@app.get("/")
def root() -> dict:
    return {"service": "nero-voice-agent", "status": "ok"}


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "mode": os.getenv("NERO_DEPLOYMENT_MODE", "api"),
    }
