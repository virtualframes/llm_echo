import pytest
import os
import subprocess
import time
from unittest.mock import patch
from search.deepseekadapter import deepseekquery, normalize_response


@pytest.fixture(scope="module")
def mock_server():
    """Starts the mock DeepSeek server in a separate process."""
    process = subprocess.Popen(["python", "search/mock_deepseek.py"])
    time.sleep(1)  # Give the server a moment to start
    yield
    process.kill()
    process.wait()


@patch(
    "agents.jules.deepseek_proxy.DEEPSEEK_URL",
    "http://localhost:8000/v1/chat/completions",
)
def test_deepseekquery_with_mock_server(mock_server):
    """
    Tests that deepseekquery correctly interacts with the mock server.
    """
    provenance_bundle = {"test": "data"}
    response = deepseekquery(
        "<html></html>",
        provenance_bundle=provenance_bundle,
        instructions="test",
        schema={},
    )
    assert "provenancebundle" in response
    assert "evidence" in response
    # The mock server returns a JSON string in the 'content' field, which normalize_response doesn't parse.
    # So we expect the evidence to be a list containing a single dictionary.
    assert len(response["evidence"]) == 1


def test_normalize_response():
    """
    Tests the normalize_response function with a mock response.
    """
    mock_response = {
        "evidence": [
            {
                "id": "1",
                "url": "https://example.com/1",
                "snippet": "This is the first mock snippet.",
                "title": "Mock Title 1",
                "score": 0.9,
            },
            {
                "id": "2",
                "url": "https://example.com/2",
                "snippet": "This is the second mock snippet.",
                "title": "Mock Title 2",
                "score": 0.8,
            },
        ]
    }
    normalized_response = normalize_response(mock_response)
    assert "provenancebundle" in normalized_response
    assert "evidence" in normalized_response
    assert len(normalized_response["evidence"]) == 2
    assert normalized_response["evidence"][0]["snippet"] == "This is the first mock snippet."
    assert normalized_response["evidence"][1]["score"] == 0.8
