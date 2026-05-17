#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mkdir -p validation_results
LOG="validation_results/phase2e_perf_modes_head_tail_smoke_once.txt"
: > "$LOG"

{
  echo "Phase 2e fast/standard performance, head, and tail smoke bench"
  echo "timestamp_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "zlg_bin=${ZLG_BIN:-target/release/zlg}"
  echo "measurement=python os.wait4 resource accounting"
  echo
  python3 tools/phase2e_perf_modes_head_tail_bench.py \
    --zlg-bin "${ZLG_BIN:-target/release/zlg}" \
    --out-csv validation_results/phase2e_perf_modes_head_tail_smoke.csv \
    --out-md validation_results/phase2e_perf_modes_head_tail_smoke.md \
    "${@}"
  echo
  echo "Phase 2e fast/standard performance, head, and tail smoke bench complete"
} 2>&1 | tee "$LOG"
