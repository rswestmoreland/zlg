#!/usr/bin/env bash
set -euo pipefail

mkdir -p validation_results
LOG="validation_results/phase1k_final_stack_memory_once.txt"
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

run python3 tools/phase1k_final_stack_memory_bench.py \
  --binary target/release/zlg \
  --output validation_results/phase1k_final_stack_memory.md \
  --csv validation_results/phase1k_final_stack_memory.csv \
  --chunks-csv validation_results/phase1k_final_stack_memory_chunks.csv

run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase1k_final_stack_memory.csv
run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase1k_final_stack_memory_chunks.csv
run bash scripts/phase0i_artifact_hygiene_check.sh

python3 - <<'PY' | tee -a "$LOG"
import csv
from pathlib import Path
main = Path('validation_results/phase1k_final_stack_memory.csv')
chunk = Path('validation_results/phase1k_final_stack_memory_chunks.csv')
rows = list(csv.DictReader(main.open(newline='', encoding='utf-8')))
blank_rss = [r for r in rows if not r.get('max_rss_kb')]
blank_cpu = [r for r in rows if not r.get('total_cpu_seconds')]
zlg = [r for r in rows if r.get('tool') == 'zlg']
missing_components = [r for r in zlg if not r.get('zlg_total_bytes') or not r.get('max_chunk_uncompressed_bytes')]
missing_roundtrip = [r for r in zlg if r.get('roundtrip_ok') != 'true']
chunk_rows = list(csv.DictReader(chunk.open(newline='', encoding='utf-8')))
if blank_rss or blank_cpu or missing_components or missing_roundtrip or not chunk_rows:
    raise SystemExit(
        f'phase1k validation failed blank_rss={len(blank_rss)} blank_cpu={len(blank_cpu)} '
        f'missing_components={len(missing_components)} roundtrip_fail={len(missing_roundtrip)} chunk_rows={len(chunk_rows)}'
    )
needed_final = {'final-cap8m-l3', 'final-cap8m-l6', 'final-cap8m-l8', 'final-cap8m-l9'}
needed_diag = {'no-summary-cap8m-l6', 'no-summary-cap8m-l8', 'no-summary-cap8m-l9', 'default-cli'}
found_modes = {r.get('mode') for r in zlg}
missing_modes = (needed_final | needed_diag) - found_modes
if missing_modes:
    raise SystemExit(f'missing zlg modes: {sorted(missing_modes)}')
for corpus in {r['corpus'] for r in rows}:
    gz = {r.get('gzip_level') for r in rows if r.get('corpus') == corpus and r.get('tool') == 'gzip'}
    if {'6','8','9'} - gz:
        raise SystemExit(f'missing gzip levels for {corpus}: {gz}')
    default_rows = [r for r in zlg if r.get('corpus') == corpus and r.get('mode') == 'default-cli']
    explicit_rows = [r for r in zlg if r.get('corpus') == corpus and r.get('mode') == 'final-cap8m-l6']
    if default_rows and explicit_rows and default_rows[0].get('output_bytes') != explicit_rows[0].get('output_bytes'):
        raise SystemExit(f'default CLI output differs from explicit standard stack for {corpus}')
print(f'phase1k csv validation passed rows={len(rows)} chunk_rows={len(chunk_rows)}')
PY

echo "phase1k final-stack memory diagnostic passed" | tee -a "$LOG"
