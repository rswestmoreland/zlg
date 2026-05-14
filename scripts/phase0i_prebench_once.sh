#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

mkdir -p validation_results
report="validation_results/phase0i_prebench_once.txt"
: > "$report"

log_run() {
    echo "\$ $*" | tee -a "$report"
    "$@" 2>&1 | tee -a "$report"
}

echo "zlg Phase 0i prebench once" | tee -a "$report"
date -u '+UTC %Y-%m-%dT%H:%M:%SZ' | tee -a "$report"
echo | tee -a "$report"

log_run cargo fmt --check
log_run cargo check
log_run cargo test
log_run cargo clippy --all-targets --all-features -- -D warnings
log_run cargo build --release

log_run scripts/phase0h_smoke.sh
log_run scripts/phase0h_correctness_check.sh
log_run scripts/phase0i_policy_matrix_check.sh

log_run python3 tools/phase0h_bench.py --mode prebench --lines 125000 --repeats 3

log_run scripts/phase0i_artifact_hygiene_check.sh

echo "phase0i prebench once: pass" | tee -a "$report"
