import json
import hashlib
from datetime import datetime, timezone
import subprocess

def emitevent(eventtype, payload, provenance_bundle):
    """
    emits a provenance event and adds it to the bundle.
    """

    provenance_token = {
        "eventtype": eventtype,
        "timestampiso": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "commitsha": get_commit_sha(),
        "inputhash": get_input_hash(payload),
        "outputhash": None,
    }

    provenance_bundle.append(provenance_token)

def get_commit_sha():
    """
    returns the current commit sha.
    """
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()
    except Exception:
        return "unknown"

def get_input_hash(data):
    """
    returns the sha256 hash of the input data.
    """
    return hashlib.sha256(json.dumps(data).encode()).hexdigest()
