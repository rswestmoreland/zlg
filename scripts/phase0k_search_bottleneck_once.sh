#!/usr/bin/env bash
set -euo pipefail

LOG="validation_results/phase0k_search_bottleneck_once.txt"
mkdir -p validation_results
: > "$LOG"

run() {
  echo "\$ $*" | tee -a "$LOG"
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
run python3 tools/phase0h_bench.py --mode prebench --lines 125000 --repeats 3 --output validation_results/phase0k_search_bottleneck_bench.csv --summary validation_results/phase0k_search_bottleneck_summary.md --env-report validation_results/phase0k_search_bottleneck_env.txt
run python3 tools/phase0k_analyze_search.py --csv validation_results/phase0k_search_bottleneck_bench.csv --output validation_results/phase0k_search_bottleneck_analysis.md
run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase0k_search_bottleneck_bench.csv
run bash scripts/phase0i_artifact_hygiene_check.sh

echo "phase0k search bottleneck flow completed" | tee -a "$LOG"
