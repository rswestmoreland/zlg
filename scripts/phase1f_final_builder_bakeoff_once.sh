#!/usr/bin/env bash
set -euo pipefail

mkdir -p validation_results
LOG="validation_results/phase1f_final_builder_bakeoff_once.txt"
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

run python3 tools/phase1f_final_builder_bakeoff_bench.py \
  --binary target/release/zlg \
  --lines 80000 \
  --seed 4242 \
  --repeats 3 \
  --corpora high_dup,high_cardinality,unicode,binaryish,realistic_mixed_log,long_line_log,short_line_log \
  --output validation_results/phase1f_final_builder_bakeoff.md \
  --csv validation_results/phase1f_final_builder_bakeoff.csv

run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase1f_final_builder_bakeoff.csv
run bash scripts/phase0i_artifact_hygiene_check.sh

if awk -F, 'NR==1 {for (i=1;i<=NF;i++) {if ($i=="max_rss_kb") rss=i; if ($i=="total_cpu_seconds") cpu=i}; next} rss && cpu && ($rss=="" || $cpu=="") {exit 1}' validation_results/phase1f_final_builder_bakeoff.csv; then
  echo "phase1f RSS/CPU check: pass" | tee -a "$LOG"
else
  echo "phase1f RSS/CPU check: fail" | tee -a "$LOG"
  exit 1
fi

echo "phase1f final builder bakeoff once: pass" | tee -a "$LOG"
