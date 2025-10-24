import pytest
from unittest.mock import patch
from search.verify import (
    wikisearch,
    arxiv_search,
    crossref_lookup,
    verify_evidence,
)

@patch("search.verify._http_get")
def test_wikisearch(mock_http_get):
    """Tests the wikisearch function."""
    mock_http_get.return_value.json.return_value = {
        "query": {
            "search": [
                {"title": "Test Title", "snippet": "Test snippet."},
            ]
        }
    }
    mock_http_get.return_value.content = b"mock content"

    results = wikisearch("test query")
    assert len(results) == 1
    assert results[0]["title"] == "Test Title"

@patch("search.verify._http_get")
def test_arxiv_search(mock_http_get):
    """Tests the arxiv_search function."""
    mock_http_get.return_value.content = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>test-id</id><title>test-title</title><summary>test-summary</summary></entry></feed>'
    results = arxiv_search("test query")
    assert len(results) > 0

@patch("search.verify._http_get")
def test_crossref_lookup(mock_http_get):
    """Tests the crossref_lookup function."""
    mock_http_get.return_value.json.return_value = {"message": {"items": []}}
    mock_http_get.return_value.content = b"mock content"

    result = crossref_lookup("test query")
    assert "metadata" in result

def test_verify_evidence():
    """Tests the verify_evidence function."""
    candidate = {
        "title": "The quick brown fox",
        "snippet": "jumps over the lazy dog.",
        "http_sha256": "sha256-hash",
    }
    claim_tokens = {"quick", "brown", "fox"}

    result = verify_evidence(candidate, claim_tokens)
    assert result["verification_status"] == "verified"
    assert result["match_score"] == 1.0
