# PR 3 Changelog

## Summary of Changes

This pull request introduces the llm_echo MVP, a reproducible audit pipeline for detecting and analyzing LLM-style hallucinations on Reddit. It replaces the previous "Forensic Debate Analysis" layer with a more standardized set of NLP tasks and integrates the DeepSeek API as the primary evidence retriever.

## Files Added/Modified

### Added

-   `agents/claimdetector.py`
-   `agents/claimcanonicalizer.py`
-   `agents/factverifier.py`
-   `agents/stancedetector.py`
-   `agents/nliadapter.py`
-   `agents/argumentminer.py`
-   `agents/citationdetector.py`
-   `agents/provenance.py`
-   `search/deepseekadapter.py`
-   `search/mock_deepseek.py`
-   `search/verify.py`
-   `ingestion/heuristics.py`
-   `workflows/pipeline.py`
-   `workflows/checkpoints.json`
-   `docs/PR3_PLAN.md`
-   `docs/DEEPSEEK_INTEGRATION.md`
-   `tests/test_claimdetector.py`
-   `tests/test_canonicalizer.py`
-   `tests/test_factverifier.py`
-   `tests/test_stancedetector.py`
-   `tests/test_nliadapter.py`
-   `tests/test_argumentminer.py`
-   `tests/test_citationdetector.py`
-   `tests/test_deepseekadapter.py`
-   `tests/integration/test_end_to_end_pr3.py`
-   `ci/mocks/deepseekmock.py`
-   `.github/workflows/pr3_pipeline.yml`
-   `.github/PROVENANCE_SCHEMA.json`

### Modified

-   `ingestion/reddit_scraper.py`
-   `keywords/expander.py`
-   `requirements.txt`
-   `.gitignore`

## Testing and CI

-   Unit tests have been added for all new modules.
-   An end-to-end integration test has been added to verify the pipeline with a mock DeepSeek server.
-   A GitHub Actions workflow has been added to run unit tests, integration tests, and provenance checks.

## Provenance and Privacy

-   All significant events in the pipeline emit a provenance token.
-   The pipeline generates a provenance bundle for each run.
-   All personally identifiable information (PII) is hashed before being persisted.

## Reviewer Checklist

-   [ ] Code has been reviewed.
-   [ ] Tests have been reviewed and are sufficient.
-   [ ] Documentation has been reviewed and is clear.
-   [ ] The pipeline runs successfully with the mock DeepSeek server.
