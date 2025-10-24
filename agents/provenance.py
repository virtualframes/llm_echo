import json
import uuid
from datetime import datetime, timezone
from agents.jules.schema_validator import validate_event_or_raise
from agents.jules.io_utils import sha256_hex_of_obj, ensure_dir, atomic_write_json

PROV_DIR = ".github/PROVENANCE"


def emitevent(module: str, payload: dict, commitsha: str = None, inputhash: str = None):
    output_hash = sha256_hex_of_obj(payload)
    provenance_token = str(uuid.uuid4())
    event = {
        "module": module,
        "eventtype": "evidence_emitted",
        "timestampiso": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "commitsha": commitsha or "",
        "inputhash": inputhash or "",
        "outputhash": output_hash,
        "provenancetoken": provenance_token,
    }
    # Validate schema
    validate_event_or_raise(event)
    # Write atomically
    ensure_dir(PROV_DIR)
    bundle_path = f"{PROV_DIR}/{provenance_token}-bundle.json"
    atomic_write_json(bundle_path, event)
    return event
