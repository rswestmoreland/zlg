#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

LOG="validation_results/phase1l_final_stack_streamline_once.txt"
mkdir -p validation_results
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
run python3 tools/phase1l_final_stack_streamline_bench.py \
  --binary target/release/zlg \
  --output validation_results/phase1l_final_stack_streamline.md \
  --csv validation_results/phase1l_final_stack_streamline.csv \
  --chunks-csv validation_results/phase1l_final_stack_streamline_chunks.csv
run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase1l_final_stack_streamline.csv
run bash scripts/phase0i_artifact_hygiene_check.sh

python3 - <<'PY' | tee -a "$LOG"
import csv
from pathlib import Path
p = Path('validation_results/phase1l_final_stack_streamline.csv')
rows = list(csv.DictReader(p.open()))
blank_rss = [r for r in rows if not r.get('max_rss_kb')]
blank_cpu = [r for r in rows if not r.get('total_cpu_seconds')]
profiles = {'combined-bitset-seen','combined-bitset-seen-reserve-none','combined-bitset-seen-reserve-capped','combined-bitset-seen-reserve-prev-unique'}
seen = {r.get('build_profile') for r in rows if r.get('tool') == 'zlg'}
missing = profiles - seen
mismatch = [r for r in rows if r.get('tool') == 'zlg' and r.get('matches_current_output') != 'true']
roundtrip = [r for r in rows if r.get('tool') == 'zlg' and r.get('roundtrip_ok') != 'true']
print(f'phase1l rows={len(rows)} blank_rss={len(blank_rss)} blank_cpu={len(blank_cpu)}')
print(f'phase1l missing_profiles={sorted(missing)} mismatches={len(mismatch)} roundtrip_failures={len(roundtrip)}')
if blank_rss or blank_cpu or missing or mismatch or roundtrip:
    raise SystemExit(1)
PY

echo "phase1l final-stack streamlining benchmark passed" | tee -a "$LOG"
