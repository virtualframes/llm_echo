import pytest
from agents.nliadapter import nli_status

def test_nli_status():
    premise = "This is a premise."
    hypothesis = "This is a hypothesis."
    status = nli_status(premise, hypothesis)
    assert status["label"] == "entailment"
    assert status["score"] == 0.9
