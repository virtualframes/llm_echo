import json
from agents import provenance
from typing import List, Dict, Any
from agents.jules.ioutils import sha256hexof
from agents.jules.deepseekproxy import query_deepseek
import hashlib

def deepseekquery(query_obj: Dict[str, Any], provenance_bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Queries the DeepSeek API with the given query object.
    """
    normalized_response = query_deepseek(query_obj)

    query_json = json.dumps(query_obj, sort_keys=True, separators=(",", ":"))
    input_hash = sha256hexof(query_json)

    payload = {
        "provenance_bundle": provenance_bundle,
        "evidence": normalized_response,
        "redacted_query": redact_query(query_obj)
    }

    provenance.emitevent(
        module="deepseekadapter",
        eventtype="deepseek_api_call",
        payload=payload,
        inputhash=input_hash
    )
    return normalized_response

def redact_query(query_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redacts sensitive information from the query object.
    """
    redacted_query = query_obj.copy()
    if "api_key" in redacted_query:
        del redacted_query["api_key"]
    if "messages" in redacted_query:
        redacted_query["messages_hash"] = hashlib.sha256(json.dumps(redacted_query["messages"], sort_keys=True).encode()).hexdigest()
        del redacted_query["messages"]
    return redacted_query
