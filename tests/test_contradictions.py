import pytest
import json
from pathlib import Path
from unittest.mock import patch
from agents.contradiction_detector import (
    discover_candidates,
    fetch_and_verify,
    score_contradictions,
    attach_to_audit,
)

@pytest.fixture
def mock_audit_files(tmp_path):
    """Creates mock audit files for testing."""
    audits_dir = tmp_path / "audits"
    audits_dir.mkdir()

    audit_data = [
        {
            "thread_id": "t1",
            "title": "Claim about quantum physics",
            "flags": ["GPT_style"],
            "subreddit": "r/science",
        },
        {
            "thread_id": "t2",
            "title": "Another claim",
            "flags": ["NoFlag"],
            "subreddit": "r/science",
        },
    ]

    with open(audits_dir / "audits.json", "w") as f:
        json.dump(audit_data, f)

    return [str(audits_dir / "audits.json")]

def test_discover_candidates(mock_audit_files):
    """Tests the discover_candidates function."""
    candidates = discover_candidates(mock_audit_files)
    assert len(candidates) == 1
    assert candidates[0]["thread_id"] == "t1"

@patch("agents.contradiction_detector.wikisearch")
@patch("agents.contradiction_detector.arxiv_search")
@patch("agents.contradiction_detector.crossref_lookup")
def test_fetch_and_verify(mock_crossref, mock_arxiv, mock_wiki):
    """Tests the fetch_and_verify function."""
    mock_wiki.return_value = [{"title": "Quantum physics", "snippet": "A theory."}]
    mock_arxiv.return_value = []
    mock_crossref.return_value = {}
    candidates = [{"scoreable_text": "quantum physics"}]

    evidence = fetch_and_verify(candidates)
    assert len(evidence) == 1
    assert evidence[0]["verification_status"] == "verified"

def test_score_contradictions():
    """Tests the score_contradictions function."""
    evidence_list = [
        {"verification_status": "verified", "match_score": 0.8},
        {"verification_status": "unverified"},
        {"verification_status": "verified", "match_score": 0.9},
    ]
    score = score_contradictions(evidence_list)
    assert score == (0.8 + 0.9) / 2 - 0.2

def test_attach_to_audit():
    """Tests the attach_to_audit function."""
    audit_record = {"thread_id": "t1"}
    hits = [{"verification_status": "verified"}]
    score = 0.5

    updated_audit = attach_to_audit(audit_record, hits, score)
    assert "contradiction_hits" in updated_audit
    assert updated_audit["contradiction_score"] == 0.5
