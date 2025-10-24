import os
import requests
import time
import json
import hashlib
import uuid
from agents import provenance
from typing import List, Dict, Any

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
RETRY_ATTEMPTS = 5
RETRY_DELAY = 0.5

def deepseekquery(query_obj: Dict[str, Any], provenance_bundle: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Queries the DeepSeek API with the given query object.
    """
    mock_url = os.environ.get("DEEPSEEKMOCKURL")
    if mock_url:
        headers = {"Content-Type": "application/json"}
        url = mock_url
    else:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        url = DEEPSEEK_API_URL

    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.post(url, headers=headers, json=query_obj, timeout=8)
            response.raise_for_status()
            data = response.json()

            normalized_response = normalize_response(data)

            provenance.emitevent(
                "deepseekadapter",
                "deepseekquery",
                redact_provenance_payload(query_obj, normalized_response),
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
        content_str = choice.get("message", {}).get("content", "")
        try:
            content = json.loads(content_str)
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        normalized_evidence.append({
                            "evidenceid": item.get("id", str(uuid.uuid4())),
                            "url": item.get("url", ""),
                            "snippet": item.get("snippet", ""),
                            "title": item.get("title", ""),
                            "score": item.get("score", 0.0),
                            "provenanceid": item.get("id", str(uuid.uuid4())),
                            "snippet_hash": get_snippet_hash(item.get("snippet", ""), item.get("url", ""))
                        })
        except (json.JSONDecodeError, TypeError):
            pass  # Ignore if content is not a valid JSON list of objects
    return normalized_evidence

def get_snippet_hash(snippet: str, url: str) -> str:
    """
    Returns the sha256 hash of the snippet and url.
    """
    return hashlib.sha256((snippet + url).encode()).hexdigest()

def redact_provenance_payload(query_obj: Dict[str, Any], normalized_response: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Redacts sensitive information from the provenance payload.
    """
    redacted_query = query_obj.copy()
    if "api_key" in redacted_query:
        del redacted_query["api_key"]
    if "messages" in redacted_query:
        redacted_query["messages_hash"] = hashlib.sha256(json.dumps(redacted_query["messages"], sort_keys=True).encode()).hexdigest()
        del redacted_query["messages"]


    return {
        "query": redacted_query,
        "response_hash": hashlib.sha256(json.dumps(normalized_response, sort_keys=True).encode()).hexdigest(),
        "mode": "real" if os.environ.get("USEREALDEEPSEEK") == "true" else "mock",
    }
