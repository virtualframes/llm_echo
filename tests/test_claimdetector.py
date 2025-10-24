import pytest
from agents.claimdetector import detectclaims


def test_detectclaims():
    threadtext = "This is a test thread. I think that this is a claim. What do you think?"
    claims = detectclaims(threadtext)
    assert len(claims) == 1
    assert claims[0]["text"] == "This is a claim."
