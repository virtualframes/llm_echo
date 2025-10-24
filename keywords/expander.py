import re
import json
import glob
import subprocess
from pathlib import Path
from collections import Counter
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from agents import provenance
import datetime
from datetime import timezone

def extract_candidates(corpus_paths: list[str], min_freq: int = 3) -> list[dict]:
    """Extracts noun phrases and multi-word expressions from a corpus."""
    phrase_counts = Counter()
    for path in glob.glob(corpus_paths):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                text = (data.get("title", "") + " " + data.get("selftext", "")).lower()
                # Simple regex for noun phrases (adjective? noun+)
                phrases = re.findall(r"\b(?:\w+\s+){1,3}\w+\b", text)
                phrase_counts.update(phrases)

    candidates = [
        {"phrase": p, "count": c} for p, c in phrase_counts.items() if c >= min_freq
    ]
    return candidates

def tfidf_candidates(texts: list[str], topn: int = 200) -> list[str]:
    """Extracts top N candidates based on TF-IDF scores."""
    if not texts:
        return []
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(2, 4), max_features=topn)
    vectorizer.fit_transform(texts)
    return vectorizer.get_feature_names_out().tolist()

def cooccurrence_expand(seed_list: list[str], texts: list[str], window: int = 40, top_k: int = 30) -> list[str]:
    """Expands a seed list of keywords with co-occurring terms."""
    cooccurrence_counts = Counter()
    for text in texts:
        tokens = text.lower().split()
        for i, token in enumerate(tokens):
            if token in seed_list:
                start = max(0, i - window)
                end = min(len(tokens), i + window + 1)
                window_tokens = tokens[start:end]
                cooccurrence_counts.update(window_tokens)

    for seed in seed_list:
        del cooccurrence_counts[seed]

    return [term for term, count in cooccurrence_counts.most_common(top_k)]

def generate_deepseek_queries(canonical_claims: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Generates DeepSeek query variants from canonical claims."""
    queries = []
    for claim in canonical_claims:
        claim_text = claim["canonicaltext"]
        claim_id = claim["canonicalid"]

        # Concise variant
        queries.append({
            "claimid": claim_id,
            "query": claim_text,
            "variant": "concise",
            "topk": 20
        })

        # Mechanism-focused variant
        queries.append({
            "claimid": claim_id,
            "query": f"How does {claim_text} work?",
            "variant": "mechanism-focused",
            "topk": 20
        })

        # Skeptic-focused variant
        queries.append({
            "claimid": claim_id,
            "query": f"What is the evidence against the claim that {claim_text}?",
            "variant": "skeptic-focused",
            "topk": 20
        })

    return queries


def save_expanded(run_id: str, expanded: list[str], provenance_id: str, provenance_bundle: list) -> Path:
    """Saves the expanded keywords to a file."""
    output_dir = Path("data/keywords")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"expanded_keywords_{run_id}.json"

    git_commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    input_files = glob.glob("data/raw/*_threads.ndjson")

    manifest = {
        "run_id": run_id,
        "provenance_id": provenance_id,
        "keywords": expanded,
        "generated_at": datetime.datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "git_commit": git_commit,
        "input_files": input_files,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    provenance.emitevent("expanded_keywords_saved", {"path": str(output_path)}, provenance_bundle)
    return output_path
