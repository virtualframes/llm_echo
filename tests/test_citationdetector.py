import pytest
from agents.citationdetector import detectcitations

def test_detectcitations():
    text = "This is a test text with a citation (Smith, 2023)."
    citations = detectcitations(text)
    assert len(citations) == 1
    assert citations[0]["text"] == "This is a citation."
