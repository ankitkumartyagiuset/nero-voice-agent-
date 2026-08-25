"""
Structured Tool Call Schemas for LLM integration.
Enforces typed parameter schemas (no raw shell execution).
"""
from typing import List, Dict, Any

NERO_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Launch a registered desktop application such as VS Code, Chrome, Spotify, or Notepad.",
            "parameters": {
                "type": "object",
                "properties": {
                    "application": {
                        "type": "string",
                        "description": "Name or ID of the application (e.g. 'vscode', 'chrome', 'spotify', 'notepad')."
                    }
                },
                "required": ["application"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web on Google for technical information or queries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search term or question to look up."
                    }
                },
                "required": ["query"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_youtube",
            "description": "Search for videos and tutorials on YouTube.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The video search keywords."
                    }
                },
                "required": ["query"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Capture a screenshot of the user's desktop display.",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Set the system master volume level.",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "integer",
                        "description": "Volume percentage from 0 to 100."
                    }
                },
                "required": ["value"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_workflow",
            "description": "Execute a pre-configured automation workflow such as 'coding_mode' or 'focus_mode'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow": {
                        "type": "string",
                        "description": "Workflow identifier (e.g., 'coding_mode', 'focus_mode')."
                    }
                },
                "required": ["workflow"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_reminder",
            "description": "Set a persistent scheduled reminder for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "What to remind the user about."
                    },
                    "time": {
                        "type": "string",
                        "description": "Time expression (e.g., '6:00 PM', 'in 15 minutes')."
                    }
                },
                "required": ["message"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather condition and temperature for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g., 'New Delhi', 'London', 'San Francisco')."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Fetch top technology and global news headlines.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "shutdown_system",
            "description": "Request computer system shutdown (triggers safety confirmation).",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]
