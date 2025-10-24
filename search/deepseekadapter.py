def deepseekquery(html, provenance_bundle=None, instructions=None, schema=None):
    # call proxy or DeepSeek client and receive normalized evidence
    from agents.jules.deepseek_proxy import querydeepseekviaapi

    result = querydeepseekviaapi(
        html, instructions or "", schema or {}, provenance_bundle or {}
    )
    # Build payload: include provenance_bundle and evidence separately
    payload = {"provenancebundle": provenance_bundle or {}, "evidence": result.get("evidence")}
    return payload
