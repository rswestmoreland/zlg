#!/usr/bin/env bash
set -euo pipefail

mkdir -p validation_results
LOG="validation_results/phase1j_memory_chunk_buffer_once.txt"
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

run python3 tools/phase1j_memory_chunk_buffer_bench.py \
  --binary target/release/zlg \
  --output validation_results/phase1j_memory_chunk_buffer.md \
  --csv validation_results/phase1j_memory_chunk_buffer.csv \
  --chunks-csv validation_results/phase1j_memory_chunk_buffer_chunks.csv

run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase1j_memory_chunk_buffer.csv
run bash scripts/phase0k_csv_commit_guard.sh validation_results/phase1j_memory_chunk_buffer_chunks.csv
run bash scripts/phase0i_artifact_hygiene_check.sh

python3 - <<'PY' | tee -a "$LOG"
import csv
from pathlib import Path
main = Path('validation_results/phase1j_memory_chunk_buffer.csv')
chunk = Path('validation_results/phase1j_memory_chunk_buffer_chunks.csv')
rows = list(csv.DictReader(main.open(newline='', encoding='utf-8')))
blank_rss = [r for r in rows if not r.get('max_rss_kb')]
blank_cpu = [r for r in rows if not r.get('total_cpu_seconds')]
zlg = [r for r in rows if r.get('tool') == 'zlg']
missing_components = [r for r in zlg if not r.get('zlg_total_bytes') or not r.get('max_chunk_uncompressed_bytes')]
missing_roundtrip = [r for r in zlg if r.get('roundtrip_ok') != 'true']
chunk_rows = list(csv.DictReader(chunk.open(newline='', encoding='utf-8')))
if blank_rss or blank_cpu or missing_components or missing_roundtrip or not chunk_rows:
    raise SystemExit(
        f'phase1j validation failed blank_rss={len(blank_rss)} blank_cpu={len(blank_cpu)} '
        f'missing_components={len(missing_components)} roundtrip_fail={len(missing_roundtrip)} chunk_rows={len(chunk_rows)}'
    )
needed_modes = {
    'locked-l3', 'locked-l6', 'locked-l9', 'stream-zstd-l6', 'stream-zstd-l9',
    'no-summary-l6', 'no-summary-l9',
    'capped-fixed-lines8192-cap4m-l6', 'capped-fixed-lines8192-cap8m-l6', 'capped-fixed-lines8192-cap16m-l6',
    'capped-fixed-lines8192-cap4m-l9', 'capped-fixed-lines8192-cap8m-l9', 'capped-fixed-lines8192-cap16m-l9',
}
found_modes = {r.get('mode') for r in zlg}
missing_modes = needed_modes - found_modes
if missing_modes:
    raise SystemExit(f'missing zlg modes: {sorted(missing_modes)}')
for corpus in {r['corpus'] for r in rows}:
    gz = {r.get('gzip_level') for r in rows if r.get('corpus') == corpus and r.get('tool') == 'gzip'}
    if {'6','9'} - gz:
        raise SystemExit(f'missing gzip levels for {corpus}: {gz}')
print(f'phase1j csv validation passed rows={len(rows)} chunk_rows={len(chunk_rows)}')
PY

echo "phase1j memory/chunk-buffer diagnostic passed" | tee -a "$LOG"
