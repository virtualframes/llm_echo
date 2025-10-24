import json
from pathlib import Path
from ingestion.heuristics import detect_gpt_style, detect_citation_pattern, detect_misuse_keywords
from agents.provenance import emit, input_sha256_text

AUDITS_DIR = Path("data/audits")
AUDITS_DIR.mkdir(parents=True, exist_ok=True)

def classify_text_block(text: str):
    flags = []
    evidence = []
    if detect_gpt_style(text):
        flags.append("GPT_style")
        evidence.append("gpt_style_phrase")
    if detect_citation_pattern(text):
        flags.append("CitationPattern")
        evidence.append("citation_pattern")
    misuse = detect_misuse_keywords(text)
    if misuse:
        flags.append("MisuseTerminology")
        evidence.extend(misuse)
    if not flags:
        flags.append("NoFlag")
    confidence = min(0.95, 0.5 + 0.15 * len(flags))
    return {"flags": flags, "confidence": confidence, "evidence": evidence}

def audit_threads(ndjson_path: str, seed: int = 42):
    results = []
    with open(ndjson_path, "r", encoding="utf-8") as fh:
        for line in fh:
            t = json.loads(line)
            combined = (t.get("title", "") + "\n" + t.get("selftext", "")).strip()
            audit = classify_text_block(combined)
            audit_record = {
                "thread_id": t.get("id"),
                "subreddit": t.get("subreddit"),
                "title": t.get("title"),
                "created_utc": t.get("created_utc"),
                "flags": audit["flags"],
                "confidence": audit["confidence"],
                "evidence": audit["evidence"],
                "input_sha256": input_sha256_text(combined)
            }
            prov = emit("audit_flagged", {"thread_id": t.get("id"), "subreddit": t.get("subreddit"), "flags": audit_record["flags"]})
            audit_record["provenance_id"] = prov["id"]
            results.append(audit_record)
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python agents/hallucination_auditor.py data/raw/<sub>_threads.ndjson")
        raise SystemExit(1)
    out = audit_threads(sys.argv[1])
    print(json.dumps(out, indent=2))
