import os
import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timedelta
import requests

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

USERAGENT = os.getenv("REDDIT_USER_AGENT", "llm-echo/0.1 (by /u/yourusername)")


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def save_ndjson(path: Path, items):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")


def fetch_reddit_json(subreddit: str, limit: int = 100):
    # subreddit expected in form "r/Name"
    name = subreddit[2:] if subreddit.startswith("r/") else subreddit
    url = f"https://www.reddit.com/r/{name}/new.json?limit={min(limit, 100)}"
    headers = {"User-Agent": USERAGENT}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()
    out = []
    for child in data.get("data", {}).get("children", []):
        d = child.get("data", {})
        author = d.get("author", "") or ""
        out.append(
            {
                "id": d.get("id"),
                "title": d.get("title", ""),
                "selftext": d.get("selftext", ""),
                "author_hash": sha256_hex(author),
                "created_utc": int(d.get("created_utc", 0)),
                "num_comments": int(d.get("num_comments", 0)),
                "subreddit": f"r/{d.get('subreddit', '')}",
                "claims": [],  # Placeholder for claims
            }
        )
    return out


def ingest_from_config(config_path: str = "ingestion/subreddits.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    out = {}
    for sub in cfg.get("targets", []):
        try:
            items = fetch_reddit_json(sub, limit=cfg.get("threads_per_subreddit", 100))
            out[sub] = items
            outfile = DATA_DIR / f"{sub[2:]}_threads.ndjson"
            save_ndjson(outfile, items)
            print(f"[ingest] saved {len(items)} threads -> {outfile}")
            time.sleep(2)  # polite pause
        except Exception as e:
            print(f"[ingest] error fetching {sub}: {e}")
    return out


if __name__ == "__main__":
    ingest_from_config()
