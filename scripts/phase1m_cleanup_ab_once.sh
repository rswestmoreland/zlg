#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mkdir -p validation_results
LOG="validation_results/phase1m_cleanup_ab_once.txt"
: > "$LOG"

run() {
  echo "+ $*" | tee -a "$LOG"
  "$@" 2>&1 | tee -a "$LOG"
}

run cargo fmt --check
run cargo check
run cargo test
run cargo clippy --all-targets --all-features -- -D warnings
run cargo build --release

run bash scripts/phase0h_smoke.sh
run bash scripts/phase0h_correctness_check.sh
run bash scripts/phase0i_policy_matrix_check.sh
run bash scripts/phase0m_selector_smoke.sh

run python3 tools/phase1m_cleanup_ab_bench.py \
  --output validation_results/phase1m_cleanup_ab_bench.csv \
  --search-output validation_results/phase1m_cleanup_ab_search.csv \
  --summary-output validation_results/phase1m_cleanup_ab_summary.csv \
  --report validation_results/phase1m_cleanup_ab_report.md

run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase1m_cleanup_ab_bench.csv
run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase1m_cleanup_ab_search.csv
run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase1m_cleanup_ab_summary.csv
run bash scripts/phase0i_artifact_hygiene_check.sh

python3 - <<'PY' | tee -a "$LOG"
import csv
from pathlib import Path
for name in [
    'validation_results/phase1m_cleanup_ab_bench.csv',
    'validation_results/phase1m_cleanup_ab_search.csv',
]:
    rows = list(csv.DictReader(Path(name).open(newline='', encoding='utf-8')))
    blank_rss = sum(1 for row in rows if not row.get('max_rss_kb'))
    blank_cpu = sum(1 for row in rows if not row.get('total_cpu_seconds'))
    print(f'{name}: rows={len(rows)} blank_rss={blank_rss} blank_cpu={blank_cpu}')
    if blank_rss or blank_cpu:
        raise SystemExit(1)
print('phase1m cleanup A/B validation passed')
PY

echo "phase1m cleanup A/B checkpoint passed" | tee -a "$LOG"
