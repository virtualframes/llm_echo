import json
import uuid
from datetime import datetime
import subprocess
from agents.jules.schemavalidator import validateeventor_raise
from agents.jules.ioutils import sha256hexof, ensure_dir, atomicwritejson

PROV_DIR = ".github/PROVENANCE"

def emitevent(module, eventtype, payload, commitsha=None, inputhash=None):
    """
    Emits a provenance event, validates it, and writes it to a file.
    """
    if commitsha is None:
        commitsha = get_commit_sha()

    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    outputhash = sha256hexof(payload_json)
    provenancetoken = str(uuid.uuid4())

    event = {
        "module": module,
        "eventtype": eventtype,
        "timestampiso": datetime.utcnow().isoformat() + "Z",
        "payload": payload,
        "commitsha": commitsha,
        "inputhash": inputhash or "",
        "outputhash": outputhash,
        "provenancetoken": provenancetoken
    }

    validateeventor_raise(event)

    ensure_dir(PROV_DIR)
    bundle_path = f"{PROV_DIR}/{provenancetoken}-bundle.json"
    atomicwritejson(bundle_path, event)

    return event

def get_commit_sha():
    """
    Returns the current commit sha.
    """
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()
    except Exception:
        return "unknown"
