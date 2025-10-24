import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from ingestion.reddit_scraper import ingest_from_config
from keywords.expander import generate_deepseek_queries
from search.deepseekadapter import deepseekquery
from agents.provenance import emitevent

def run_pipeline(args):
    """Runs the full llm_echo pipeline."""
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.outdir) / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    provenance_bundle = []

    # 1. Ingestion
    raw_data = ingest_from_config()
    emitevent("ingestion", "ingestion", {"source": "reddit"}, provenance_bundle)

    # 2. Generate Dummy Queries
    dummy_claims = [{"canonicalid": "1", "canonicaltext": "test claim"}]
    deepseek_queries = generate_deepseek_queries(dummy_claims)

    # 3. Evidence Retrieval (DeepSeek)
    all_evidence = {}
    for query in deepseek_queries:
        evidence = deepseekquery(query, provenance_bundle)
        claim_id = query["claimid"]
        if claim_id not in all_evidence:
            all_evidence[claim_id] = []
        all_evidence[claim_id].extend(evidence)
    emitevent("evidence_retrieval", "evidence_retrieval", {"evidence_count": len(all_evidence)}, provenance_bundle)

    # 4. Provenance Bundle
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
