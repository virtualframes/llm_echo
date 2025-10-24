import json
import jsonschema
from agents.provenance import emitevent


def test_emitevent_schema():
    """
    Tests that the emitevent function produces a schema-compliant event.
    """
    with open(".github/PROVENANCE_SCHEMA.json") as f:
        schema = json.load(f)

    provenance_bundle = []
    emitevent(
        "test_module",
        "test_event",
        {"test": "payload"},
        provenance_bundle,
    )

    assert len(provenance_bundle) == 1
    jsonschema.validate(instance=provenance_bundle[0], schema=schema)
