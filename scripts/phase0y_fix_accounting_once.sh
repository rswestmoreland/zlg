#!/usr/bin/env bash
set -euo pipefail

mkdir -p validation_results
LOG="validation_results/phase0y_fix_accounting_once.txt"
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

run python3 tools/phase0y_regex_mesh_hotpath_bench.py \
  --binary target/release/zlg \
  --lines 125000 \
  --needle-ratio 0.80 \
  --repeats 3 \
  --output validation_results/phase0y_fix_accounting_bench.md \
  --csv validation_results/phase0y_fix_accounting_bench.csv

run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase0y_fix_accounting_bench.csv
run bash scripts/phase0i_artifact_hygiene_check.sh

echo "phase0y fix accounting once: pass" | tee -a "$LOG"
