#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

LOG="validation_results/phase1h_size_diagnosis_once.txt"
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
run python3 tools/phase1h_size_diagnosis_bench.py \
  --binary target/release/zlg \
  --lines 80000 \
  --seed 4242 \
  --repeats 3 \
  --output validation_results/phase1h_size_diagnosis.md \
  --archive-csv validation_results/phase1h_size_diagnosis_archive.csv \
  --chunk-csv validation_results/phase1h_size_diagnosis_chunks.csv
run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase1h_size_diagnosis_archive.csv
run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase1h_size_diagnosis_chunks.csv
run bash scripts/phase0i_artifact_hygiene_check.sh

echo "phase1h size diagnosis: PASS" | tee -a "$LOG"
