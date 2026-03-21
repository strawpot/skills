#!/usr/bin/env bash
# Creates all pipeline/* labels across every repo in a GitHub org.
# Usage: ./setup-labels.sh [org-name]
# Defaults to STRAWPOT_ORG env var, then "strawpot".

set -euo pipefail

ORG="${1:-${STRAWPOT_ORG:-strawpot}}"

declare -A LABELS=(
  ["pipeline/triage"]="d4c5f9"
  ["pipeline/approved"]="0e8a16"
  ["pipeline/planning"]="fbca04"
  ["pipeline/planned"]="1d76db"
  ["pipeline/implementing"]="5319e7"
  ["pipeline/review"]="f9d0c4"
  ["pipeline/done"]="0e8a16"
  ["pipeline/blocked"]="e11d48"
  ["pipeline/sub-issue"]="bfdadc"
)

repos=$(gh repo list "$ORG" --no-archived --limit 100 --json nameWithOwner -q '.[].nameWithOwner')

for repo in $repos; do
  echo "Setting up labels for $repo..."
  for label in "${!LABELS[@]}"; do
    color="${LABELS[$label]}"
    gh label create "$label" --repo "$repo" --color "$color" --force 2>/dev/null || true
  done
done

echo "Done. Labels created across all repos in $ORG."
