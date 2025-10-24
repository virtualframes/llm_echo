# llm_echo — Minimal runnable MVP

Quickstart (local VM):

1. Create venv and install:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`

2. Run pipeline (ingest + audit):
   - `PYTHONPATH=. python workflows/pipeline.py --config ingestion/subreddits.json`

3. Generate visualization:
   - `PYTHONPATH=. python visualizations/plotly_timeseries.py`

4. Artifacts:
   - raw data: `data/raw/*.ndjson`
   - audits: `data/audits/*_audits.json`
   - provenance: `.github/PROVENANCE/audit_trace.jsonl`
   - visualizations: `visualizations/*.html`, `*.png`, `*.meta.json`

Notes:
- This MVP uses public Reddit JSON endpoints only; no account or OAuth required.
- Authors are hashed to avoid PII exposure.
- Jules extension points are marked with "JULES EXTENSION" TODOs inside files.
