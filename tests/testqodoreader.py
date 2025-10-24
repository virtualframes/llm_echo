import pytest
from agents.jules.qodo_reader import parse_qodo_comment_body


def test_parse_simple_qodo():
    body = (
        "Qodo summary: This PR is risky.\n\n- Risk: uses unpinned actions\n- Recommend: pin actions"
    )
    parsed = parse_qodo_comment_body(body)
    assert "This PR is risky." in parsed["summary"]
    assert any("Risk" in r for r in parsed["risks"])
    assert any("Recommend" in r for r in parsed["recommendations"])


def test_parse_malformed_qodo():
    body = "This is not a Qodo comment."
    parsed = parse_qodo_comment_body(body)
    assert parsed["summary"] == "This is not a Qodo comment."
    assert not parsed["risks"]
    assert not parsed["recommendations"]
