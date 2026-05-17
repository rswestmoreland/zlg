#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mkdir -p validation_results
LOG="validation_results/phase2c_perf_smoke_once.txt"
: > "$LOG"

{
  echo "Phase 2c performance smoke bench"
  echo "timestamp_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "zlg_bin=${ZLG_BIN:-target/release/zlg}"
  echo
  python3 tools/phase2c_perf_smoke_bench.py \
    --zlg-bin "${ZLG_BIN:-target/release/zlg}" \
    --out-csv validation_results/phase2c_perf_smoke.csv \
    --out-md validation_results/phase2c_perf_smoke.md \
    "${@}"
  echo
  echo "Phase 2c performance smoke bench complete"
} 2>&1 | tee "$LOG"
