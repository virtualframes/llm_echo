#!/usr/bin/env bash
set -euo pipefail
PYTHONPATH=. python workflows/pipeline.py --config ingestion/subreddits.json
PYTHONPATH=. python visualizations/plotly_timeseries.py
echo "Run complete. Open visualizations/*.html"
