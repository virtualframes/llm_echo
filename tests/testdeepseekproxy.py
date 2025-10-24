import unittest
import os
import json
from agents.jules.deepseekproxy import query_deepseek
from search.deepseekadapter import redact_query
import subprocess
import time

class TestDeepSeekProxy(unittest.TestCase):

    def setUp(self):
        # Start the mock DeepSeek server
        self.mock_server_process = subprocess.Popen(["python", "search/mock_deepseek.py"])
        time.sleep(1)  # Give the server a moment to start
        os.environ["DEEPSEEKMOCKURL"] = "http://localhost:8000/v1/chat/completions"

    def tearDown(self):
        # Stop the mock DeepSeek server
        self.mock_server_process.terminate()
        self.mock_server_process.wait()
        del os.environ["DEEPSEEKMOCKURL"]

    def test_deepseek_proxy_redaction(self):
        """Test that the DeepSeek proxy redacts sensitive information."""
        query_obj = {
            "api_key": "sensitive_api_key",
            "messages": [{"role": "user", "content": "test"}]
        }
        redacted = redact_query(query_obj)
        self.assertNotIn("api_key", redacted)
        self.assertNotIn("messages", redacted)
        self.assertIn("messages_hash", redacted)

    def test_deepseek_proxy_normalization(self):
        """Test that the DeepSeek proxy normalizes the response."""
        query_obj = {"model": "deepseek-coder", "messages": [{"role": "user", "content": "test"}]}
        normalized_response = query_deepseek(query_obj)

        self.assertIsInstance(normalized_response, list)
        if normalized_response:
            self.assertIsInstance(normalized_response[0], dict)
            self.assertIn("evidenceid", normalized_response[0])
            self.assertIn("url", normalized_response[0])
            self.assertIn("snippet", normalized_response[0])
            self.assertIn("title", normalized_response[0])
            self.assertIn("score", normalized_response[0])
            self.assertIn("provenanceid", normalized_response[0])
            self.assertIn("snippet_hash", normalized_response[0])


if __name__ == "__main__":
    unittest.main()
