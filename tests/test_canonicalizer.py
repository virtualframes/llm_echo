import pytest
from agents.claimcanonicalizer import canonicalize

def test_canonicalize():
    claimtext = "This is a claim."
    canonical_form = canonicalize(claimtext)
    assert canonical_form["canonicalid"] == "canonical-1"
    assert canonical_form["canonicaltext"] == "This is a canonical claim."
