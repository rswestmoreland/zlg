#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mkdir -p validation_results
LOG="validation_results/phase3_release_readiness_once.txt"
: > "$LOG"

run() {
  echo "+ $*" | tee -a "$LOG"
  "$@" 2>&1 | tee -a "$LOG"
}

run python3 tools/phase3_doc_audit.py

for script in scripts/*.sh; do
  run bash -n "$script"
done

echo "phase3 release-readiness prep checks completed" | tee -a "$LOG"
