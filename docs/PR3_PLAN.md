# PR 3 Plan: llm_echo MVP with DeepSeek Integration

## Overview and Goals

This document outlines the plan for PR 3, which focuses on replacing the bespoke "Forensic Debate Analysis" layer with standardized NLP tasks, integrating DeepSeek as the primary evidence retriever, and producing a production-ready pipeline with tests, CI, provenance, and documentation.

## Module Descriptions and API Contracts

### Agents

-   **`claimdetector.py`**: Detects and segments claims from text.
    -   `detectclaims(threadtext: str) -> List[{"claimid": str, "text": str, "span": [s,e], "confidence": float, "provenancetoken": str}]`
-   **`claimcanonicalizer.py`**: Normalizes claims to a canonical form.
    -   `canonicalize(claimtext: str) -> {"canonicalid": str, "canonicaltext": str, "aliases": [str], "provenancetoken": str}`
-   **`factverifier.py`**: Verifies claims against evidence.
    -   `verifyclaim(claimid, claimtext, evidencelist) -> {"supporting": int,"contradicting": int,"neutral": int,"topsupporting":[], "topcontradicting":[], "verificationscore": float, "provenancetoken": str}`
-   **`stancedetector.py`**: Detects the stance of a reply to a claim.
    -   `detectstance(replytext: str, claim_id: str) -> {"stance":"support|oppose|neutral|query","score": float}`
-   **`nliadapter.py`**: Performs Natural Language Inference.
    -   `nli_status(premise: str, hypothesis: str) -> {"label":"entailment|contradiction|neutral","score": float}`
-   **`argumentminer.py`**: Tags the roles of arguments in a text.
    -   `tag_roles(text: str) -> [{"span":[s,e],"role":"premise|claim|warrant|rebuttal","score": float}]`
-   **`citationdetector.py`**: Detects citations in a text.
    -   `detectcitations(text: str) -> [citation_records]`

### Search

-   **`deepseekadapter.py`**: Interacts with the DeepSeek API.
    -   `deepseekquery(queryobj: {"claimid","query","variant","topk"}) -> List[{"evidenceid","url","snippet","title","score","provenanceid"}]`

## DeepSeek Integration Details and Provenance Schema Snippet

-   **Query Variants**: concise, mechanism-focused, skeptic-focused.
-   **Provenance Fields**: `eventtype`, `timestampiso`, `module`, `commitsha`, `inputhash`, `outputhash`, `provenancetoken`.

## Runbook and Example Commands

-   Install dependencies: `pip install -r requirements.txt`
-   Start mock DeepSeek server: `python search/mock_deepseek.py &`
-   Run pipeline (mock): `./run.sh --sample data/sample_threads.ndjson --mock-deepseek --limit 50 --outdir out/pr3`
-   Run unit tests: `pytest -q tests/`
-   Run integration tests: `DEEPSEEKMOCK=1 pytest -q tests/integration/test_end_to_end_pr3.py`

## Privacy Note

All personally identifiable information (PII), such as Reddit author names, must be hashed (using SHA256) before being persisted.
