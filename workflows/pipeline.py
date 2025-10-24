import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from ingestion.reddit_scraper import ingest_from_config
from agents.claimdetector import detectclaims
from agents.claimcanonicalizer import canonicalize
from keywords.expander import generate_deepseek_queries
from search.deepseekadapter import deepseekquery
from agents.factverifier import verifyclaim
from agents.provenance import emitevent

def run_pipeline(args):
    """Runs the full llm_echo pipeline."""
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.outdir) / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    provenance_bundle = []

    # 1. Ingestion
    raw_data = ingest_from_config()
    emitevent("ingestion", {"source": "reddit"}, provenance_bundle)

    # 2. Claim Detection
    all_claims = []
    for subreddit, threads in raw_data.items():
        for thread in threads:
            claims = detectclaims(thread["selftext"])
            for claim in claims:
                claim["thread_id"] = thread["id"]
                all_claims.append(claim)
    emitevent("claim_detection", {"claim_count": len(all_claims)}, provenance_bundle)

    # 3. Canonicalization
    canonical_claims = {}
    for claim in all_claims:
        canonical_form = canonicalize(claim["text"])
        canonical_id = canonical_form["canonicalid"]
        if canonical_id not in canonical_claims:
            canonical_claims[canonical_id] = canonical_form
            canonical_claims[canonical_id]["claims"] = []
        canonical_claims[canonical_id]["claims"].append(claim)
    emitevent("canonicalization", {"canonical_claim_count": len(canonical_claims)}, provenance_bundle)

    # 4. Evidence Retrieval (DeepSeek)
    deepseek_queries = generate_deepseek_queries(list(canonical_claims.values()))

    all_evidence = {}
    for query in deepseek_queries:
        evidence = deepseekquery(query)
        claim_id = query["claimid"]
        if claim_id not in all_evidence:
            all_evidence[claim_id] = []
        all_evidence[claim_id].extend(evidence)
    emitevent("evidence_retrieval", {"evidence_count": len(all_evidence)}, provenance_bundle)

    # 5. Verification
    verification_results = {}
    for claim_id, evidence in all_evidence.items():
        claim_text = canonical_claims[claim_id]["canonicaltext"]
        verification_record = verifyclaim(claim_id, claim_text, evidence)
        verification_results[claim_id] = verification_record
    emitevent("verification", {"verification_count": len(verification_results)}, provenance_bundle)

    # 6. Provenance Bundle
    provenance_bundle_path = Path(".github/PROVENANCE") / f"{run_id}-bundle.json"
    with open(provenance_bundle_path, "w") as f:
        json.dump(provenance_bundle, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="llm_echo pipeline")
    parser.add_argument("--sample", type=str, help="Path to sample data")
    parser.add_argument("--mock-deepseek", action="store_true", help="Use mock DeepSeek server")
    parser.add_argument("--limit", type=int, default=50, help="Limit number of items to process")
    parser.add_argument("--outdir", type=str, default="out/pr3", help="Output directory")
    args = parser.parse_args()

    if args.mock_deepseek:
        import os
        os.environ["USEREALDEEPSEEK"] = "false"

    run_pipeline(args)
