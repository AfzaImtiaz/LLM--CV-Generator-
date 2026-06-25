"""
Minimal JSON-file-backed history store.
"""
import json
import os
import time
from threading import Lock
from typing import Any

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "history.json")
_lock = Lock()


def _load_history() -> list[dict[str, Any]]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_entry(entry: dict[str, Any]) -> None:
    entry = {**entry, "timestamp": time.time()}
    with _lock:
        history = _load_history()
        history.append(entry)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)


def get_history(limit: int = 50) -> list[dict[str, Any]]:
    history = _load_history()
    return list(reversed(history))[:limit]