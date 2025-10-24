import unittest
import json
import os
from agents.provenance import emitevent
from agents.jules.schemavalidator import validateeventor_raise, SchemaValidationError
from agents.jules.ioutils import sha256hexof

class TestProvenanceSchemaCompliance(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for provenance bundles
        self.prov_dir = ".github/PROVENANCE_TEST"
        os.makedirs(self.prov_dir, exist_ok=True)
        # Monkey patch the PROV_DIR
        import agents.provenance
        self.original_prov_dir = agents.provenance.PROV_DIR
        agents.provenance.PROV_DIR = self.prov_dir

    def tearDown(self):
        # Clean up the temporary directory
        for f in os.listdir(self.prov_dir):
            os.remove(os.path.join(self.prov_dir, f))
        os.rmdir(self.prov_dir)
        # Restore the original PROV_DIR
        import agents.provenance
        agents.provenance.PROV_DIR = self.original_prov_dir

    def test_emitevent_produces_valid_event(self):
        """Test that emitevent produces a schema-valid event."""
        payload = {"test": "data"}
        event = emitevent("test_module", "test_event", payload)

        self.assertIn("module", event)
        self.assertIn("eventtype", event)
        self.assertIn("timestampiso", event)
        self.assertIn("payload", event)
        self.assertIn("commitsha", event)
        self.assertIn("inputhash", event)
        self.assertIn("outputhash", event)
        self.assertIn("provenancetoken", event)

        # test output hash correctness
        payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        expected_output_hash = sha256hexof(payload_json)
        self.assertEqual(event["outputhash"], expected_output_hash)

        # test that the event is valid against the schema
        try:
            validateeventor_raise(event)
        except SchemaValidationError as e:
            self.fail(f"Event did not validate against schema: {e}")

    def test_schema_validator_rejects_missing_fields(self):
        """Test that the schema validator rejects events with missing required fields."""
        invalid_event = {"module": "test"}
        with self.assertRaises(SchemaValidationError):
            validateeventor_raise(invalid_event)

if __name__ == "__main__":
    unittest.main()
