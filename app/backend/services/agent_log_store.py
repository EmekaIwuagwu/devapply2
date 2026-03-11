"""
Agent Log Store — file-backed persistent log store shared across all processes.
Reads and writes always hit the JSON file so FastAPI, Celery, and Streamlit
all see the same data regardless of which process writes the logs.
"""
import json
import threading
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

LOG_FILE = Path("./logs/agent_activity.json")
STATE_FILE = Path("./logs/agent_state.json")
MAX_LOGS = 500

_lock = threading.Lock()


def _ensure_dirs():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


# ── Low-level file I/O ──────────────────────────────────────────────────────

def _read_logs() -> List[Dict]:
    _ensure_dirs()
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _write_logs(logs: List[Dict]):
    _ensure_dirs()
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs[-MAX_LOGS:], f, default=str, ensure_ascii=False)
    except Exception:
        pass


def _read_state() -> Dict:
    _ensure_dirs()
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"is_running": False, "task_id": None, "last_run_status": "idle", "log_count": 0}


def _write_state(state: Dict):
    _ensure_dirs()
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, default=str)
    except Exception:
        pass


# ── Public API ──────────────────────────────────────────────────────────────

def add_log(level: str, message: str, task_id: Optional[str] = None):
    """Append a log entry to the file. Thread-safe."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level.upper(),
        "message": message,
        "task_id": task_id,
    }
    with _lock:
        logs = _read_logs()
        logs.append(entry)
        _write_logs(logs)
    return entry


def get_logs(last_n: int = 100) -> List[Dict]:
    """Read last N log entries from file. Always fresh."""
    with _lock:
        logs = _read_logs()
    return logs[-last_n:]


def clear_logs():
    """Delete all logs."""
    with _lock:
        _write_logs([])


def set_running(task_id: str, status: str = "running"):
    state = _read_state()
    state.update({"is_running": True, "task_id": task_id, "last_run_status": status})
    _write_state(state)


def set_idle(status: str = "completed"):
    state = _read_state()
    state.update({"is_running": False, "last_run_status": status})
    _write_state(state)


def get_status() -> Dict:
    return _read_state()
