import json
from pathlib import Path
from agents.provenance import emit
from search.verify import wikisearch, arxiv_search, crossref_lookup, verify_evidence

def discover_candidates(audits_paths: list[str]) -> list[dict]:
    """Discovers contradiction candidates from a list of audit files."""
    candidates = []
    for path in audits_paths:
        with open(path, "r", encoding="utf-8") as f:
            audits = json.load(f)
            for audit in audits:
                if "GPT_style" in audit["flags"] or "CitationPattern" in audit["flags"]:
                    candidates.append({
                        "claim_excerpt": audit["title"],
                        "thread_id": audit["thread_id"],
                        "subreddit": audit["subreddit"],
                        "scoreable_text": audit["title"] + " " + audit.get("selftext", ""),
                    })
    return candidates

def fetch_and_verify(candidates: list[dict], top_k: int = 3, run_id: str = "", seed: int = 42) -> list[dict]:
    """Fetches and verifies evidence for a list of contradiction candidates."""
    verified_evidence = []
    for candidate in candidates:
        query = candidate["scoreable_text"]
        claim_tokens = set(query.lower().split())

        # Wikipedia
        wiki_results = wikisearch(query, limit=top_k)
        for result in wiki_results:
            verified_evidence.append(verify_evidence(result, claim_tokens))

        # arXiv
        arxiv_results = arxiv_search(query, max_results=top_k)
        for result in arxiv_results:
            verified_evidence.append(verify_evidence(result, claim_tokens))

        # Crossref
        crossref_result = crossref_lookup(query)
        if crossref_result.get("metadata"):
             verified_evidence.append(verify_evidence(crossref_result, claim_tokens))

    return verified_evidence

def score_contradictions(evidence_list: list[dict]) -> float:
    """Scores a list of evidence and returns a contradiction score."""
    if not evidence_list:
        return 0.0

    verified_scores = [e.get("match_score", 0) for e in evidence_list if e["verification_status"] == "verified"]
    unverified_count = sum(1 for e in evidence_list if e["verification_status"] == "unverified")

    v = sum(verified_scores) / len(verified_scores) if verified_scores else 0
    u_penalty = 0.2 * unverified_count

    return max(0, min(1, v - u_penalty))

def attach_to_audit(audit_record: dict, contradiction_hits: list[dict], contradiction_score: float) -> dict:
    """Attaches contradiction information to an audit record."""
    audit_record["contradiction_hits"] = contradiction_hits
    audit_record["contradiction_score"] = contradiction_score
    return audit_record
