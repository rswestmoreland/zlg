#!/usr/bin/env bash
set -euo pipefail

mkdir -p validation_results
log="validation_results/phase0l_index_strategy_once.txt"
csv="validation_results/phase0l_index_strategy_bench.csv"
summary="validation_results/phase0l_index_strategy_summary.md"
env_report="validation_results/phase0l_index_strategy_env.txt"
analysis="validation_results/phase0l_index_strategy_analysis.md"

{
  echo "phase0l index strategy once: start"
  date -u '+utc %Y-%m-%dT%H:%M:%SZ'

  cargo fmt --check
  cargo check
  cargo test
  cargo clippy --all-targets --all-features -- -D warnings
  cargo build --release

  bash scripts/phase0h_smoke.sh
  bash scripts/phase0h_correctness_check.sh
  bash scripts/phase0i_policy_matrix_check.sh
  bash scripts/phase0l_no_index_smoke.sh

  python3 tools/phase0h_bench.py \
    --mode prebench \
    --lines 125000 \
    --repeats 3 \
    --include-no-index \
    --output "$csv" \
    --summary "$summary" \
    --env-report "$env_report"

  python3 tools/phase0l_analyze_index_strategy.py \
    --csv "$csv" \
    --output "$analysis"

  bash scripts/phase0k_csv_commit_guard.sh "$csv"
  bash scripts/phase0i_artifact_hygiene_check.sh

  echo "phase0l index strategy once: pass"
} 2>&1 | tee "$log"
