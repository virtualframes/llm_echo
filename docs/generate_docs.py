import json
import glob
from pathlib import Path


def generate_keywords_doc(expanded_path: str, out_path: str, run_id: str):
    """Generates a Markdown document for the expanded keywords."""
    with open(expanded_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Expanded Keywords for Run: {run_id}\n\n")
        f.write("## Top Keywords\n")
        for keyword in data.get("keywords", [])[:20]:
            f.write(f"- `{keyword}`\n")


def generate_contradictions_doc(contradictions_path: str, out_path: str, top_n: int = 25):
    """Generates a Markdown document for the top contradictions."""
    all_contradictions = []
    for path in glob.glob(contradictions_path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            all_contradictions.extend(data)

    # Sort by contradiction_score
    all_contradictions.sort(key=lambda x: x.get("contradiction_score", 0), reverse=True)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Top Contradiction Candidates\n\n")
        for contradiction in all_contradictions[:top_n]:
            f.write(f"## Claim: {contradiction.get('claim_excerpt', '')}\n")
            f.write(f"- **Thread ID:** {contradiction.get('thread_id', '')}\n")
            f.write(
                f"- **Contradiction Score:** {contradiction.get('contradiction_score', 0):.2f}\n"
            )
            f.write("\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--runid", required=True)
    args = parser.parse_args()

    keywords_file = f"data/keywords/expanded_keywords_{args.runid}.json"
    contradictions_glob = "data/contradictions/*.json"

    generate_keywords_doc(keywords_file, "docs/KEYWORDS.md", args.runid)
    generate_contradictions_doc(contradictions_glob, "docs/CONTRADICTIONS.md")
