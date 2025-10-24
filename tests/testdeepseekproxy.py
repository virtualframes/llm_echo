import pytest
from agents.jules.deepseek_proxy import querydeepseekviaapi
from requests import Session
from requests.models import Response


class DummyResp:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class DummySession(Session):
    def __init__(self, payload):
        super().__init__()
        self.payload = payload

    def post(self, url, json=None, timeout=None):
        return DummyResp(self.payload)


def test_proxy_normalizes():
    sess = DummySession({"evidence": [{"snippet": "x"}]})
    out = querydeepseekviaapi(
        "<html/>", "instr", {}, {"claimid": "1"}, session=sess
    )
    assert "evidence" in out
    assert isinstance(out["evidence"], list)
