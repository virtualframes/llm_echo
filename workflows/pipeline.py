import argparse
import json
from pathlib import Path
from ingestion.reddit_scraper import ingest_from_config
from agents.hallucination_auditor import audit_threads
from agents.provenance import emit
from keywords.expander import (
    extract_candidates,
    tfidf_candidates,
    cooccurrence_expand,
    save_expanded,
)
from agents.contradiction_detector import (
    discover_candidates,
    fetch_and_verify,
    score_contradictions,
    attach_to_audit,
)
from docs.generate_docs import generate_keywords_doc, generate_contradictions_doc
import glob

def run_pipeline(config="ingestion/subreddits.json", dry_run=False, seed=42, stage="all"):
    emit("run_start", {"config": config, "dry_run": dry_run, "seed": seed, "stage": stage})

    if stage in ["all", "ingest"]:
        if not dry_run:
            ingest_from_config(config)

    if stage in ["all", "audit"]:
        src_dir = Path("data/raw")
        out_dir = Path("data/audits")
        out_dir.mkdir(parents=True, exist_ok=True)
        ndjson_files = glob.glob(str(src_dir / "*_threads.ndjson"))
        for f in ndjson_files:
            emit("ingested_threads", {"file": f})
            audits = audit_threads(f, seed=seed)
            base = Path(f).stem.replace("_threads", "")
            outfile = out_dir / f"{base}_audits.json"
            with open(outfile, "w", encoding="utf-8") as fh:
                json.dump(audits, fh, indent=2)
            emit("audits_saved", {"outfile": str(outfile), "count": len(audits)})

    if stage in ["all", "expand_contradict"]:
        # Keyword Expansion
        raw_files_glob = "data/raw/*_threads.ndjson"
        texts = []
        for f in glob.glob(raw_files_glob):
             with open(f, "r", encoding="utf-8") as fh:
                for line in fh:
                    texts.append(json.loads(line).get("selftext", ""))

        run_id = f"{seed}_{Path(config).stem}"
        expanded_keywords = cooccurrence_expand(["ai", "llm"], texts)
        prov_id = emit("keywords_expanded", {"count": len(expanded_keywords)})["id"]
        save_expanded(run_id, expanded_keywords, prov_id)

        # Contradiction Detection
        audit_files = glob.glob("data/audits/*_audits.json")
        for audit_file in audit_files:
            with open(audit_file, "r", encoding="utf-8") as fh:
                audits = json.load(fh)

            for audit in audits:
                if "GPT_style" in audit["flags"] or "CitationPattern" in audit["flags"]:
                    candidates = [{"scoreable_text": audit["title"] + " " + audit.get("selftext", "")}]
                    verified_evidence = fetch_and_verify(candidates)
                    score = score_contradictions(verified_evidence)
                    attach_to_audit(audit, verified_evidence, score)

            with open(audit_file, "w", encoding="utf-8") as fh:
                json.dump(audits, fh, indent=2)
            emit("contradictions_attached", {"file": audit_file})

    if stage in ["all", "doc"]:
        run_id = f"{seed}_{Path(config).stem}"
        keywords_file = f"data/keywords/expanded_keywords_{run_id}.json"
        contradictions_glob = "data/contradictions/*.json"

        if Path(keywords_file).exists():
            generate_keywords_doc(keywords_file, "docs/KEYWORDS.md", run_id)

        if glob.glob(contradictions_glob):
            generate_contradictions_doc(contradictions_glob, "docs/CONTRADICTIONS.md")

    emit("run_finish", {"success": True})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="ingestion/subreddits.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--stage", default="all", choices=["all", "ingest", "audit", "expand_contradict", "doc"])
    args = parser.parse_args()
    run_pipeline(config=args.config, dry_run=args.dry_run, seed=args.seed, stage=args.stage)
