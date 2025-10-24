import pytest
from agents.argumentminer import tag_roles

def test_tag_roles():
    text = "This is a test text."
    roles = tag_roles(text)
    assert len(roles) == 1
    assert roles[0]["role"] == "claim"
