import pytest
from unittest.mock import patch
from keywords.expander import (
    extract_candidates,
    tfidf_candidates,
    cooccurrence_expand,
    generate_deepseek_queries,
    save_expanded,
)


def test_extract_candidates(tmp_path):
    """Tests the extract_candidates function."""
    corpus_path = tmp_path / "corpus.ndjson"
    corpus_path.write_text('{"title": "test title", "selftext": "test selftext"}\n' * 3)
    candidates = extract_candidates(str(corpus_path))
    assert len(candidates) > 0


def test_tfidf_candidates():
    """Tests the tfidf_candidates function."""
    texts = ["this is a test sentence", "this is another test sentence"]
    candidates = tfidf_candidates(texts)
    assert len(candidates) > 0


def test_cooccurrence_expand():
    """Tests the cooccurrence_expand function."""
    seed_list = ["test"]
    texts = ["this is a test sentence", "this is another test sentence"]
    expanded = cooccurrence_expand(seed_list, texts)
    assert len(expanded) > 0


def test_generate_deepseek_queries():
    """Tests the generate_deepseek_queries function."""
    canonical_claims = [
        {"canonicalid": "1", "canonicaltext": "test claim"},
    ]
    queries = generate_deepseek_queries(canonical_claims)
    assert len(queries) == 3


def test_save_expanded(tmp_path):
    """Tests the save_expanded function."""

    def mock_emitevent(module, eventtype, payload, commitsha=None, inputhash=None):
        provenance_bundle.append(
            {
                "module": module,
                "eventtype": eventtype,
                "payload": payload,
                "commitsha": commitsha,
                "inputhash": inputhash,
            }
        )

    run_id = "test_run"
    expanded_keywords = ["quantum", "consciousness", "spacetime"]
    provenance_id = "prov-123"
    provenance_bundle = []

    with patch("keywords.expander.emitevent", new=mock_emitevent):
        output_path = save_expanded(run_id, expanded_keywords, provenance_id, provenance_bundle)

    assert output_path.exists()
    assert len(provenance_bundle) == 1
