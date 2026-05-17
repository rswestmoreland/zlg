#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mkdir -p validation_results
LOG="validation_results/phase1n_cleanup_hardening_once.txt"
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

run bash scripts/phase0i_artifact_hygiene_check.sh

python3 - <<'PY' | tee -a "$LOG"
from pathlib import Path
bad = []
for path in Path('src').glob('*.rs'):
    text = path.read_text(encoding='utf-8')
    if '#![allow(dead_code)]' in text:
        bad.append(str(path))
if bad:
    raise SystemExit('blanket dead_code allow remains: ' + ', '.join(bad))
if Path('tools/phase1m_baseline_src').exists():
    raise SystemExit('temporary Phase 1m baseline source snapshot still exists')
print('phase1n cleanup checks passed')
PY

echo "phase1n cleanup and hardening checkpoint passed" | tee -a "$LOG"
