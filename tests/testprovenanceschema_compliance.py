import tempfile
import os
import json
import pytest
from agents.provenance import emitevent
from agents.jules.io_utils import sha256_hex_of_obj, ensure_dir


@pytest.fixture
def setup_prov_schema(tmp_path):
    schema_dir = tmp_path / ".github"
    ensure_dir(schema_dir)
    schema_path = schema_dir / "PROVENANCE_SCHEMA.json"
    with open(schema_path, "w") as f:
        json.dump(
            {
                "type": "object",
                "properties": {
                    "module": {"type": "string"},
                    "eventtype": {"type": "string"},
                    "timestampiso": {"type": "string"},
                    "payload": {"type": "object"},
                    "commitsha": {"type": "string"},
                    "inputhash": {"type": "string"},
                    "outputhash": {"type": "string"},
                    "provenancetoken": {"type": "string"},
                },
                "required": [
                    "module",
                    "eventtype",
                    "timestampiso",
                    "payload",
                    "commitsha",
                    "inputhash",
                    "outputhash",
                    "provenancetoken",
                ],
            },
            f,
        )


def test_emitevent_writes_bundle(tmp_path, monkeypatch, setup_prov_schema):
    d = tmp_path / ".github" / "PROVENANCE"
    monkeypatch.chdir(tmp_path)
    payload = {"foo": "bar"}
    event = emitevent("test_module", payload, commitsha="deadbeef", inputhash="abc123")
    # ensure outputhash is correct
    assert "outputhash" in event
    assert event["payload"] == payload
    # bundle exists
    token = event["provenancetoken"]
    bundle_path = tmp_path / ".github" / "PROVENANCE" / f"{token}-bundle.json"
    assert bundle_path.exists()
    # load and validate basic shape
    b = json.loads(bundle_path.read_text())
    assert b["module"] == "test_module"
