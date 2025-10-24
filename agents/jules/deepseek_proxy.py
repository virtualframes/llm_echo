import requests
from typing import Dict, Any, List


def redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: redact(v) for k, v in obj.items() if k != "api_key"}
    if isinstance(obj, list):
        return [redact(i) for i in obj]
    return obj


# Minimal proxy that sends HTML (or rendered result) to DeepSeek API
# This function expects caller to handle secrets and to redact before emitting.

DEEPSEEK_URL = "https://api.deepseek.example/v1/chat/completions"


def querydeepseekviaapi(
    html: str,
    instructions: str,
    schema: Dict[str, Any],
    provenance_bundle: Dict[str, Any],
    session: requests.Session = None,
) -> Dict[str, Any]:
    s = session or requests.Session()
    payload = {
        "html": html,
        "instructions": instructions,
        "schema": schema,
        "metadata": provenance_bundle,
    }
    # call DeepSeek (the runtime must inject API key via headers/env)
    resp = s.post(DEEPSEEK_URL, json=payload, timeout=60)
    resp.raise_for_status()
    result = resp.json()
    # Normalize: ensure evidence key exists and redact obvious secrets if present
    evidence = result.get("evidence") or result.get("results") or result
    return {"evidence": redact(evidence)}
