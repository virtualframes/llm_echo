import os
import requests
import time
import json
import hashlib
from agents import provenance
from typing import List, Dict, Any

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
RETRY_ATTEMPTS = 5
RETRY_DELAY = 0.5

def deepseekquery(query_obj: Dict[str, Any], provenance_bundle: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Queries the DeepSeek API with the given query object.
    """
    if os.environ.get("USEREALDEEPSEEK") == "true":
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        url = DEEPSEEK_API_URL
    else:
        headers = {"Content-Type": "application/json"}
        url = os.environ.get("DEEPSEEKMOCKURL", "http://localhost:8000/v1/chat/completions")

    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.post(url, headers=headers, json=query_obj, timeout=8)
            response.raise_for_status()
            data = response.json()

            normalized_response = normalize_response(data)

            provenance.emitevent(
                "deepseekquery",
                {
                    "query": query_obj,
                    "response": normalized_response,
                    "mode": "real" if os.environ.get("USEREALDEEPSEEK") == "true" else "mock",
                },
                provenance_bundle
            )
            return normalized_response
        except requests.exceptions.RequestException as e:
            if attempt < RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY * (2**attempt))
            else:
                raise e

def normalize_response(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normalizes the DeepSeek API response.
    """

    normalized_evidence = []
    for choice in data.get("choices", []):
        content = choice.get("message", {}).get("content", "")
        # This is a dummy normalization, a real implementation would parse the content
        # and extract evidence, url, title, etc.
        normalized_evidence.append({
            "evidenceid": data.get("id"),
            "url": "https://example.com",
            "snippet": content,
            "title": "Example Title",
            "score": 0.9,
            "provenanceid": data.get("id"),
            "snippet_hash": get_snippet_hash(content, "https://example.com")
        })

    return normalized_evidence

def get_snippet_hash(snippet: str, url: str) -> str:
    """
    Returns the sha256 hash of the snippet and url.
    """
    return hashlib.sha256((snippet + url).encode()).hexdigest()
