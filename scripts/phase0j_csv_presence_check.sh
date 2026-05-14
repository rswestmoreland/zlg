#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

csv="${1:-validation_results/phase0j_prebench_bench.csv}"

if [[ ! -s "$csv" ]]; then
    echo "phase0j csv presence failure: missing or empty $csv" >&2
    exit 1
fi

required_columns=(
    first_output_seconds
    chunk_count
    zlg_compressed_payload_bytes
    zlg_summary_bytes
    zlg_overhead_bytes
    chunks_total
    chunks_skipped
    candidate_chunks
    chunks_decoded
    decoded_bytes
    matching_lines
)

header="$(head -n 1 "$csv")"
for column in "${required_columns[@]}"; do
    if [[ ",$header," != *",$column,"* ]]; then
        echo "phase0j csv presence failure: missing column $column in $csv" >&2
        exit 1
    fi
done

printf 'phase0j csv presence: pass %s\n' "$csv"
