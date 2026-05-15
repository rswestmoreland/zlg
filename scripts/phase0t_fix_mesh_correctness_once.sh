#!/usr/bin/env bash
set -euo pipefail

mkdir -p validation_results
LOG="validation_results/phase0t_fix_mesh_correctness_once.txt"
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
run bash scripts/phase0l_no_index_smoke.sh
run bash scripts/phase0m_selector_smoke.sh

run python3 tools/phase0t_mesh_shootout.py \
  --lines 125000 \
  --needle-ratio 0.80 \
  --block-lines 512,1024,2048,4096 \
  --group-lines 16384,65536 \
  --output validation_results/phase0t_fix_mesh_shootout.md \
  --csv validation_results/phase0t_fix_mesh_shootout.csv

run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase0t_fix_mesh_shootout.csv
run bash scripts/phase0i_artifact_hygiene_check.sh

echo "phase0t fix mesh correctness once: pass" | tee -a "$LOG"
