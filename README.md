# NERO — Production-Grade Voice-First AI Desktop Assistant

NERO is a real, modular, responsive, and secure desktop AI assistant for Windows and cross-platform laptops. Designed with a futuristic Cyberpunk/Sci-Fi HUD interface powered by **PySide6**, NERO pairs ultra-low-latency local deterministic execution with advanced AI reasoning.

---

## Architecture Overview

```
                               ┌─────────────────────────────────────┐
                               │              NERO UI                │
                               │      Futuristic PySide6 HUD         │
                               └─────────────────┬───────────────────┘
                                                 │ (Qt Signals / Events)
                               ┌─────────────────▼───────────────────┐
                               │          NERO ORCHESTRATOR          │
                               │       State + Events + Routing      │
                               └─────────────────┬───────────────────┘
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
             ┌─────────────────────┐                           ┌─────────────────────┐
             │   FAST LOCAL PATH   │                           │       AI PATH       │
             │   Intent Router     │                           │  OpenAI / Gemini    │
             │   Latency: < 5ms    │                           │  Tool Calling & LLM │
             └──────────┬──────────┘                           └──────────┬──────────┘
                        │                                                 │
                        └────────────────────────┬────────────────────────┘
                                                 ▼
                               ┌─────────────────────────────────────┐
                               │          PERMISSION LAYER           │
                               │     SAFE | CONFIRMATION | BLOCKED   │
                               └─────────────────┬───────────────────┘
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
             ┌─────────────────────┐                           ┌─────────────────────┐
             │    LAPTOP SKILLS    │                           │   WORKFLOW ENGINE   │
             │ Apps, Media, Vol,   │                           │ Coding Mode, Focus, │
             │ Screen, Weather...  │                           │ Background Sched.   │
             └─────────────────────┘                           └─────────────────────┘
```

---

## Key Features

1. **Dual Execution Paths**:
   - **Fast Path (<50ms)**: Bypasses LLMs entirely for deterministic commands (e.g. *"open vscode"*, *"mute"*, *"set volume to 60"*, *"take screenshot"*, *"coding mode on"*, *"what's the time"*).
   - **AI Path**: Routes open-ended questions, complex reasoning, coding queries, and multi-step tool calls to OpenAI GPT-4o / Google Gemini / Local models.
2. **Low-Latency Voice Pipeline**:
   - Persistent microphone streaming with circular audio buffering.
   - Dedicated local wake-word engine tuned for keyword **"Nero"**.
   - Voice Activity Detection (VAD) with 450ms silence endpointing to prevent awkward conversational pauses.
   - Singleton `faster-whisper` STT model with greedy beam decoding.
   - Non-blocking, interruptible `pyttsx3` & ElevenLabs Text-to-Speech playback.
3. **Futuristic HUD Console (PySide6)**:
   - Animated Central AI Core widget (`NeroCoreWidget`) with rotating orbital rings and dynamic state-colored glow.
   - Real-time microphone audio amplitude waveform (`WaveformWidget`).
   - System control dock, live volume slider, and screenshot capture.
   - Real system clock, calendar date, live Open-Meteo weather, and live RSS tech news headlines.
   - Active automation status and persistent reminder scheduler.
4. **Security & Zero Arbitrary Shell Execution**:
   - Strict architectural prohibition of arbitrary shell execution (`os.system` / `shell=True` from LLMs).
   - Non-bypassable two-phase confirmation tokens for dangerous operations (*shutdown*, *restart*).
   - Secret masking in all log files (`nero.log`).

---

## Directory Structure

```
nero/
├── app.py                      # Main PySide6 application lifecycle runner
├── main.py                     # CLI entrypoint (--cli, --debug, --config)
├── config/                     # Configuration loader & Pydantic schema
│   ├── settings.py
│   ├── loader.py
│   └── config.yaml
├── core/                       # Core state machine, event bus, and orchestrator
│   ├── assistant.py
│   ├── lifecycle.py
│   ├── state.py
│   ├── events.py
│   ├── event_bus.py
│   └── exceptions.py
├── voice/                      # Audio capture, wake word, VAD, STT, and TTS
│   ├── audio_stream.py
│   ├── wake_word.py
│   ├── vad.py
│   ├── speech_to_text.py
│   ├── audio_session.py
│   └── text_to_speech.py
├── brain/                      # Intent routing, LLM providers, and conversation
│   ├── intent_router.py
│   ├── intent_parser.py
│   ├── llm_provider.py
│   ├── openai_provider.py
│   ├── gemini_provider.py
│   ├── local_provider.py
│   ├── tool_schema.py
│   └── conversation.py
├── skills/                     # Modular laptop control capabilities
│   ├── base.py
│   ├── registry.py
│   ├── app_control.py
│   ├── browser.py
│   ├── system.py
│   ├── media.py
│   ├── screenshot.py
│   ├── weather.py
│   ├── news.py
│   ├── reminders.py
│   └── time_date.py
├── automation/                 # Automation workflows & reminder scheduler
│   ├── workflow_engine.py
│   ├── workflow_registry.py
│   ├── workflow_models.py
│   └── scheduler.py
├── security/                   # Permission manager & command validator
│   ├── permissions.py
│   ├── policy.py
│   ├── command_validator.py
│   └── secrets.py
├── storage/                    # SQLite database & repositories
│   ├── database.py
│   ├── models.py
│   └── repositories.py
├── platform/                   # OS platform controllers (Windows, Linux, macOS)
│   ├── base.py
│   └── windows.py
├── ui/                         # PySide6 HUD Theme & Components
│   ├── main_window.py
│   ├── theme.py
│   ├── state_adapter.py
│   └── components/
├── services/                   # Live Open-Meteo & RSS News services
│   ├── weather_service.py
│   ├── news_service.py
│   └── health_service.py
├── utils/                      # Safe logger and millisecond metrics tracker
│   ├── logger.py
│   └── metrics.py
└── tests/                      # Pytest unit, integration, and latency tests
```

---

## Installation & Setup

### 1. Requirements
- **OS**: Windows 10/11 (or Linux/macOS)
- **Python**: 3.11+
- **Hardware**: Working microphone and speakers / headphones. GPU optional (CUDA supported).

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Secrets
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your API keys (optional if only using local fast path):
```ini
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
```

---

## Running NERO

### Launch Futuristic HUD Interface:
```bash
python main.py
```

### Launch Headless CLI Mode:
```bash
python main.py --cli
```

---

## Voice Commands Reference

| Command | Action / Path |
| :--- | :--- |
| **"Nero"** | Wakes up the assistant |
| **"Open VS Code"** | Launches Visual Studio Code (Fast Path) |
| **"Open Chrome"** | Launches Google Chrome (Fast Path) |
| **"Set volume to 50"** | Adjusts master volume to 50% (Fast Path) |
| **"Take a screenshot"** | Captures display to `screenshots/` (Fast Path) |
| **"What time is it?"** | Spoken system time (Fast Path) |
| **"What's today's weather?"** | Live Open-Meteo weather report (Fast Path) |
| **"Give me tech news"** | Live headlines feed (Fast Path) |
| **"Coding mode on"** | Launches IDE, Chrome, GitHub (Workflow Engine) |
| **"Stop coding mode"** | Cancels running workflow |
| **"Remind me in 10 minutes to review code"** | Sets persistent SQLite reminder |
| **"Shut down"** | Prompts confirmation *"Shutdown requires confirmation. Continue?"* |
| **"Explain binary search in Python"** | Streams response from AI Brain |

---

## Running Tests

Run the full test suite with pytest:
```bash
python -m pytest tests/ -v
```
