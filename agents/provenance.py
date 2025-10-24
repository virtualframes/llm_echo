import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
import subprocess

PROV_DIR = Path(".github/PROVENANCE")
PROV_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = PROV_DIR / "audit_trace.jsonl"

def current_git_short_sha():
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
        return out
    except Exception:
        return None

def emit(event_type: str, payload: dict, agent: str = "jules-v0.1"):
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "agent": agent,
        "event_type": event_type,
        "payload": payload,
        "git_commit": current_git_short_sha()
    }
    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry

def input_sha256_text(s: str):
    import hashlib
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()
