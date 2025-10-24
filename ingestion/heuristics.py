import re
from typing import List

GPT_STYLE_PATTERNS = [
    r"as an ai language model",
    r"as an ai",
    r"i am an ai",
    r"as a (large|small) language model",
    r"the model predicts",
    r"the model suggests",
    r"based on token entropy"
]

CITATION_PATTERNS = [
    r"\[\d+\]",
    r"\([A-Za-z]+ et al\., \d{4}\)",
    r"arxiv\.org/abs/",
    r"doi\.org/",
    r"\bdoi:\b"
]

MISUSE_KEYWORDS = [
    "qualia", "panpsychism", "microtubule", "spacetime emergence", "observer-collapse", "token entropy"
]

def detect_gpt_style(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t) for p in GPT_STYLE_PATTERNS)

def detect_citation_pattern(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t) for p in CITATION_PATTERNS)

def detect_misuse_keywords(text: str) -> List[str]:
    t = (text or "").lower()
    return [k for k in MISUSE_KEYWORDS if k in t]

def detect_echo_amplification(texts: List[str], threshold: float = 0.6):
    # naive token-set Jaccard detection for near-duplicates in a small list
    def toks(s):
        return set(re.findall(r"\w+", (s or "").lower()))
    toks_list = [toks(s) for s in texts]
    pairs = []
    n = len(toks_list)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = toks_list[i], toks_list[j]
            if not a or not b:
                continue
            jaccard = len(a & b) / len(a | b)
            if jaccard >= threshold:
                pairs.append((i, j, jaccard))
    return pairs
