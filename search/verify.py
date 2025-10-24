import requests
import requests_cache
import hashlib
from datetime import timedelta
import xml.etree.ElementTree as ET

def _http_get(url: str) -> requests.Response:
    """Makes a cached HTTP GET request."""
    response = requests.get(url, headers={"User-Agent": "llm-echo/0.1"})
    response.raise_for_status()
    return response

requests_cache.install_cache("http_cache", expire_after=timedelta(days=1))

def _sha256(content: bytes) -> str:
    """Computes the SHA256 hash of a byte string."""
    return hashlib.sha256(content).hexdigest()

def wikisearch(query: str, limit: int = 3) -> list[dict]:
    """Searches Wikipedia for a given query."""
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&srlimit={limit}&format=json"
    response = _http_get(url)
    data = response.json()

    results = []
    for item in data.get("query", {}).get("search", []):
        results.append({
            "title": item["title"],
            "snippet": item["snippet"],
            "url": f"https://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}",
            "http_sha256": _sha256(response.content),
        })
    return results

def arxiv_search(query: str, max_results: int = 3) -> list[dict]:
    """Searches arXiv for a given query."""
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    response = _http_get(url)
    root = ET.fromstring(response.content)
    results = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        results.append({
            "id": entry.find("{http://www.w3.org/2005/Atom}id").text,
            "title": entry.find("{http://www.w3.org/2005/Atom}title").text,
            "summary": entry.find("{http://www.w3.org/2005/Atom}summary").text,
            "url": entry.find("{http://www.w3.org/2005/Atom}id").text,
            "http_sha256": _sha256(response.content),
        })
    return results

def crossref_lookup(doi_or_query: str) -> dict:
    """Looks up a DOI or query on Crossref."""
    url = f"https://api.crossref.org/works?query={doi_or_query}&rows=1"
    response = _http_get(url)
    return {"metadata": response.json(), "http_sha256": _sha256(response.content)}

def verify_evidence(candidate: dict, claim_tokens: set) -> dict:
    """Verifies a piece of evidence against a set of claim tokens."""
    title = candidate.get("title", "").lower()
    snippet = candidate.get("snippet", "").lower()

    title_tokens = set(title.split())
    snippet_tokens = set(snippet.split())

    title_overlap = len(title_tokens.intersection(claim_tokens)) / len(claim_tokens) if claim_tokens else 0

    verification_status = "unverified"
    if title_overlap >= 0.6:
        verification_status = "verified"

    return {
        "verification_status": verification_status,
        "match_score": title_overlap,
        "http_sha256": candidate.get("http_sha256"),
        "meta": {"title": title, "snippet": snippet},
    }
