import pytest
from agents.factverifier import verifyclaim

def test_verifyclaim():
    claimid = "claim-1"
    claimtext = "This is a claim."
    evidencelist = []
    verification_record = verifyclaim(claimid, claimtext, evidencelist)
    assert verification_record["supporting"] == 0
    assert verification_record["contradicting"] == 0
    assert verification_record["neutral"] == 0
    assert verification_record["verificationscore"] == 0.0
