import json
import jsonschema
from agents.provenance import emitevent
import pytest
from unittest.mock import patch


def test_emitevent_schema():
    """
    Tests that the emitevent function produces a schema-compliant event.
    """
    with open(".github/PROVENANCE_SCHEMA.json") as f:
        schema = json.load(f)

    provenance_bundle = []

    def mock_atomic_write_json(path, data):
        provenance_bundle.append(data)

    with patch("agents.provenance.atomic_write_json", new=mock_atomic_write_json):
        emitevent(
            "test_module",
            "test_event",
            {"test": "payload"},
        )

    assert len(provenance_bundle) == 1
    jsonschema.validate(instance=provenance_bundle[0], schema=schema)
