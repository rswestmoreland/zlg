#!/usr/bin/env bash
set -euo pipefail

mkdir -p validation_results
LOG="validation_results/phase1o_hardening_coverage_once.txt"
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

if grep -R '#!\[allow(dead_code)\]' src >/dev/null 2>&1; then
  echo 'phase1o check failed: blanket dead-code allow found in src/' | tee -a "$LOG"
  exit 1
fi

if grep -R 'rdxsort\|rdst' Cargo.toml Cargo.lock src >/dev/null 2>&1; then
  echo 'phase1o check failed: abandoned external sort crate reference found' | tee -a "$LOG"
  exit 1
fi

if [ -d tools/phase1m_baseline_src ]; then
  echo 'phase1o check failed: temporary phase1m baseline source snapshot is present' | tee -a "$LOG"
  exit 1
fi

run bash scripts/phase0i_artifact_hygiene_check.sh

echo 'phase1o hardening coverage passed' | tee -a "$LOG"
