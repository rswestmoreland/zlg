#!/usr/bin/env bash
set -euo pipefail

mkdir -p validation_results
LOG="validation_results/phase0q_selector_needle_once.txt"
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

run python3 - <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, str(Path("tools").resolve()))
from phase0m_postings_probe import selector
mode, literals = selector(r'(?<=key=\")[^\"]+', 'fancy')
assert mode == 'all', (mode, literals)
assert literals == [b'key="'], (mode, literals)
print('lookbehind selector fixed:', mode, literals[0].decode('ascii'))
PY

run python3 tools/phase0q_needle_corpus_probe.py \
  --lines 125000 \
  --needle-ratio 0.80 \
  --block-lines 512,1024,2048,4096 \
  --output validation_results/phase0q_needle_probe.md \
  --csv validation_results/phase0q_needle_probe.csv

run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase0q_needle_probe.csv
run bash scripts/phase0i_artifact_hygiene_check.sh

echo "phase0q selector needle once: pass" | tee -a "$LOG"
