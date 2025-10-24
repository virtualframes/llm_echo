import pytest
from agents.stancedetector import detectstance

def test_detectstance():
    replytext = "This is a reply."
    claim_id = "claim-1"
    stance = detectstance(replytext, claim_id)
    assert stance["stance"] == "support"
    assert stance["score"] == 0.9
