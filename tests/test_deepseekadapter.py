import pytest
import os
from search.deepseekadapter import deepseekquery

from search.deepseekadapter import normalize_response

def test_deepseekquery_mock():
    os.environ["DEEPSEEKMOCKURL"] = "http://localhost:8000/v1/chat/completions"
    query_obj = {"model": "deepseek-chat", "messages": [{"role": "user", "content": "test"}]}
    provenance_bundle = []
    response = deepseekquery(query_obj, provenance_bundle)
    assert response[0]["snippet"] == "This is the first mock snippet."
    assert len(provenance_bundle) == 1

def test_normalize_response():
    """
    Tests the normalize_response function.
    """
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": "[{\"id\": \"1\", \"url\": \"https://example.com/1\", \"snippet\": \"This is the first mock snippet.\", \"title\": \"Mock Title 1\", \"score\": 0.9}, {\"id\": \"2\", \"url\": \"https://example.com/2\", \"snippet\": \"This is the second mock snippet.\", \"title\": \"Mock Title 2\", \"score\": 0.8}]"
                }
            }
        ]
    }
    normalized_response = normalize_response(mock_response)
    assert len(normalized_response) == 2
    assert normalized_response[0]["snippet"] == "This is the first mock snippet."
    assert normalized_response[1]["score"] == 0.8
