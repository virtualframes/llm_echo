import json
import hashlib
from datetime import datetime, timezone
import subprocess
import uuid

def get_output_hash(token):
    """
    Calculates the SHA256 hash of a provenance token, excluding the outputhash field.
    """
    token_copy = token.copy()
    token_copy.pop("outputhash", None)
    return get_input_hash(token_copy)

def emitevent(module, eventtype, payload, provenance_bundle):
    """
    emits a provenance event and adds it to the bundle.
    """

    provenance_token = {
        "module": module,
        "eventtype": eventtype,
        "timestampiso": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "commitsha": get_commit_sha(),
        "inputhash": get_input_hash(payload),
        "outputhash": None,
        "provenancetoken": str(uuid.uuid4()),
    }
    provenance_token["outputhash"] = get_output_hash(provenance_token)

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
