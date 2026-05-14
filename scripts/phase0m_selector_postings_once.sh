#!/usr/bin/env bash
set -euo pipefail

mkdir -p validation_results
log="validation_results/phase0m_selector_postings_once.txt"
csv="validation_results/phase0m_selector_postings_bench.csv"
summary="validation_results/phase0m_selector_postings_summary.md"
env_report="validation_results/phase0m_selector_postings_env.txt"
analysis="validation_results/phase0m_selector_postings_analysis.md"
postings="validation_results/phase0m_postings_probe.md"

{
  echo "phase0m selector postings once: start"
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
  bash scripts/phase0m_selector_smoke.sh

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

  python3 tools/phase0m_postings_probe.py \
    --lines 125000 \
    --block-lines 4096 \
    --output "$postings"

  bash scripts/phase0k_csv_commit_guard.sh "$csv"
  bash scripts/phase0i_artifact_hygiene_check.sh

  echo "phase0m selector postings once: pass"
} 2>&1 | tee "$log"
