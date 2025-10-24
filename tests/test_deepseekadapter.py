import pytest
import os
from search.deepseekadapter import deepseekquery

def test_deepseekquery_mock():
    os.environ["USEREALDEEPSEEK"] = "false"
    query_obj = {"model": "deepseek-chat", "messages": [{"role": "user", "content": "test"}]}
    provenance_bundle = []
    response = deepseekquery(query_obj, provenance_bundle)
    assert response[0]["snippet"] == "This is a mock response from the DeepSeek API."
    assert len(provenance_bundle) == 1
