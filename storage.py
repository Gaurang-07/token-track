"""
storage.py - Reads and writes chat logs to logs.json
"""

import json
import os
from pathlib import Path
from datetime import datetime

LOGS_FILE = Path(__file__).parent / "logs.json"


def _load_raw():
    if not LOGS_FILE.exists():
        return []
    try:
        with open(LOGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_raw(data):
    with open(LOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def save_entry(provider, model, prompt, response, input_tokens, output_tokens, total_tokens):
    """Save a single chat interaction to logs.json"""
    logs = _load_raw()
    entry = {
        "id": f"{provider}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "provider": provider,
        "model": model,
        "prompt": prompt,
        "response": response,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
    }
    logs.append(entry)
    _save_raw(logs)
    return entry


def load_all_logs():
    """Load all saved chat logs."""
    return _load_raw()


def clear_logs():
    """Clear all logs."""
    _save_raw([])
