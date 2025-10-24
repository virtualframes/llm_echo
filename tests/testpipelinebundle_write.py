import unittest
import os
import json
import subprocess
import time
from unittest.mock import patch
from agents.jules.schema_validator import (
    validate_event_or_raise,
    SchemaValidationError,
)


class TestPipelineBundleWrite(unittest.TestCase):
    def setUp(self):
        # Start the mock DeepSeek server
        self.mock_server_process = subprocess.Popen(
            ["python", "search/mock_deepseek.py"]
        )
        time.sleep(1)  # Give the server a moment to start

        # Create a temporary directory for provenance bundles
        self.prov_dir = ".github/PROVENANCE_TEST"
        os.makedirs(self.prov_dir, exist_ok=True)
        # Monkey patch the PROV_DIR
        import agents.provenance

        self.original_prov_dir = agents.provenance.PROV_DIR
        agents.provenance.PROV_DIR = self.prov_dir

    def tearDown(self):
        # Stop the mock DeepSeek server
        self.mock_server_process.terminate()
        self.mock_server_process.wait()

        # Clean up the temporary directory
        for f in os.listdir(self.prov_dir):
            os.remove(os.path.join(self.prov_dir, f))
        os.rmdir(self.prov_dir)
        # Restore the original PROV_DIR
        import agents.provenance

        agents.provenance.PROV_DIR = self.original_prov_dir

    @patch(
        "agents.jules.deepseek_proxy.DEEPSEEK_URL",
        "http://localhost:8000/v1/chat/completions",
    )
    def test_pipeline_writes_valid_bundle(self):
        """Test that the pipeline writes a schema-valid bundle."""
        # Run the pipeline
        from workflows.pipeline import run_pipeline

        class MockArgs:
            sample = None
            mock_deepseek = True
            limit = 1
            outdir = "out/test"

        run_pipeline(MockArgs())

        # Check that a bundle file was written
        bundle_files = os.listdir(self.prov_dir)
        self.assertEqual(len(bundle_files), 2)

        # Validate each bundle file
        for bundle_file in bundle_files:
            with open(os.path.join(self.prov_dir, bundle_file), "r") as f:
                bundle = json.load(f)
                try:
                    validate_event_or_raise(bundle)
                except SchemaValidationError as e:
                    self.fail(
                        f"Bundle {bundle_file} did not validate against schema: {e}"
                    )


if __name__ == "__main__":
    unittest.main()
