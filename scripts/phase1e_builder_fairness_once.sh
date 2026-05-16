#!/usr/bin/env bash
set -euo pipefail

mkdir -p validation_results
LOG="validation_results/phase1e_builder_fairness_once.txt"
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

run python3 tools/phase1e_builder_fairness_bench.py \
  --binary target/release/zlg \
  --lines 80000 \
  --seed 4242 \
  --repeats 3 \
  --corpora high_dup,high_cardinality,unicode,binaryish \
  --output validation_results/phase1e_builder_fairness_bench.md \
  --csv validation_results/phase1e_builder_fairness_bench.csv

run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase1e_builder_fairness_bench.csv
run bash scripts/phase0i_artifact_hygiene_check.sh

if grep -q ',,' validation_results/phase1e_builder_fairness_bench.csv; then
  echo "warning: csv contains empty fields; verify max_rss_kb is populated" | tee -a "$LOG"
fi
if awk -F, 'NR==1 {for (i=1;i<=NF;i++) if ($i=="max_rss_kb") c=i; next} c && $c=="" {exit 1}' validation_results/phase1e_builder_fairness_bench.csv; then
  echo "phase1e RSS check: pass" | tee -a "$LOG"
else
  echo "phase1e RSS check: fail" | tee -a "$LOG"
  exit 1
fi

echo "phase1e builder fairness once: pass" | tee -a "$LOG"
