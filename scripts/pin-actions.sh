#!/bin/bash
set -e

MODE="preview"
if [[ "$1" == "--apply" ]]; then
  MODE="apply"
fi

echo "Running in $MODE mode..."

WORKFLOW_DIR=".github/workflows"
PROVENANCE_DIR=".github/PROVENANCE"
PIN_FILE="$PROVENANCE_DIR/actions-pin.json"

mkdir -p "$PROVENANCE_DIR"
> "$PIN_FILE"

function pin_action() {
  local line="$1"
  if [[ "$line" =~ uses:\ ([^@]+)@([v0-9]+) ]]; then
    local action="${BASH_REMATCH[1]}"
    local version="${BASH_REMATCH[2]}"
    local api_url="https://api.github.com/repos/${action}/commits/${version}"
    local sha=$(curl -s "$api_url" | jq -r '.sha')
    if [[ "$sha" == "null" || -z "$sha" ]]; then
      echo "❌ Failed to resolve SHA for $action@$version"
      return
    fi
    echo "✅ $action@$version → $sha"
    echo "{\"action\":\"$action\",\"version\":\"$version\",\"sha\":\"$sha\"}" >> "$PIN_FILE"
    if [[ "$MODE" == "apply" ]]; then
      sed -i "s|$action@$version|$action@$sha|g" "$WORKFLOW_DIR"/*.yml
    fi
  fi
}

grep -r "uses: " "$WORKFLOW_DIR"/*.yml | while read -r line; do
  pin_action "$line"
done

echo "✅ Pinning complete. Output written to $PIN_FILE"
