import os
import logging
import requests

# pick the first available value from common environment variable names
DEEPSEEK_URL = (
    os.getenv("DEEPSEEK_URL")
    or os.getenv("DEEPSEEK_API_URL")
    or os.getenv("DEEPSEEKMOCKURL")
    or "https://api.deepseek.example"
)

logger = logging.getLogger(__name__)
logger.info("Using DeepSeek endpoint: %s", DEEPSEEK_URL)


def normalize_response(raw_response):
    """
    Normalize a DeepSeek raw response into a payload with keys:
      - provenancebundle: dict
      - evidence: list

    This is intentionally defensive: it accepts None, dicts with different key names,
    and raw lists. Tests that import normalize_response will find a stable API.
    """
    if raw_response is None:
        return {"provenancebundle": {}, "evidence": []}

    # If raw_response is not a dict, but a list of hits, treat it as evidence
    if not isinstance(raw_response, dict):
        return {"provenancebundle": {}, "evidence": list(raw_response)}

    # Prefer explicit keys if present
    provenance = raw_response.get("provenancebundle") or raw_response.get("provenance") or {}
    evidence = raw_response.get("evidence")

    # Fallbacks for common alternative shapes
    if evidence is None:
        evidence = raw_response.get("results") or raw_response.get("hits") or []

    # Ensure evidence is a list
    if evidence is None:
        evidence = []
    elif not isinstance(evidence, list):
        evidence = [evidence]

    return {"provenancebundle": provenance or {}, "evidence": evidence}


def deepseekquery(html, provenance_bundle=None, instructions=None, schema=None):
    # call proxy or DeepSeek client and receive normalized evidence
    from agents.jules.deepseek_proxy import querydeepseekviaapi

    result = querydeepseekviaapi(html, instructions or "", schema or {}, provenance_bundle or {})
    # Use normalize_response so callers and tests get consistent output
    return normalize_response(result)
