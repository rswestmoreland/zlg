#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mkdir -p validation_results
LOG="validation_results/release_readiness_once.txt"
: > "$LOG"

run() {
  echo "+ $*" | tee -a "$LOG"
  "$@" 2>&1 | tee -a "$LOG"
}

run python3 tools/doc_audit.py

for script in scripts/*.sh; do
  run bash -n "$script"
done

echo "release-readiness checks completed" | tee -a "$LOG"
