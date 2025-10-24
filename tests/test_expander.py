import pytest
import json
from pathlib import Path
from keywords.expander import (
    extract_candidates,
    tfidf_candidates,
    cooccurrence_expand,
    save_expanded,
)

@pytest.fixture
def mock_corpus(tmp_path):
    """Creates a mock corpus for testing."""
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()

    data = [
        {"title": "The quick brown fox", "selftext": "jumps over the lazy dog."},
        {"title": "The five boxing wizards", "selftext": "jump quickly."},
        {"title": "The quick brown fox", "selftext": "jumps over the lazy dog again."},
    ]

    for i, item in enumerate(data):
        with open(corpus_dir / f"doc_{i}.ndjson", "w") as f:
            json.dump(item, f)

    return str(corpus_dir / "*.ndjson")

def test_extract_candidates(mock_corpus):
    """Tests the extract_candidates function."""
    candidates = extract_candidates(mock_corpus, min_freq=2)
    assert len(candidates) > 0
    # Check for the presence of a known phrase, accommodating variations
    assert any("quick brown" in p for p in [c["phrase"] for c in candidates])

def test_tfidf_candidates():
    """Tests the tfidf_candidates function."""
    texts = [
        "the quick brown fox",
        "the lazy dog",
        "the quick brown fox jumps over the lazy dog",
    ]
    candidates = tfidf_candidates(texts, topn=2)
    assert len(candidates) == 2
    assert "brown fox" in candidates

def test_cooccurrence_expand():
    """Tests the cooccurrence_expand function."""
    seed_list = ["fox", "wizards"]
    texts = [
        "the quick brown fox jumps over the lazy dog",
        "the five boxing wizards jump quickly and majestically",
    ]
    expanded = cooccurrence_expand(seed_list, texts, window=4, top_k=15)
    assert "brown" in expanded
    assert "boxing" in expanded
    assert "majestically" in expanded

def test_save_expanded(tmp_path):
    """Tests the save_expanded function."""
    run_id = "test_run"
    expanded_keywords = ["quantum", "consciousness", "spacetime"]
    provenance_id = "prov-123"

    output_path = save_expanded(run_id, expanded_keywords, provenance_id)

    assert output_path.exists()

    with open(output_path, "r") as f:
        manifest = json.load(f)

    assert manifest["run_id"] == run_id
    assert manifest["provenance_id"] == provenance_id
    assert manifest["keywords"] == expanded_keywords
