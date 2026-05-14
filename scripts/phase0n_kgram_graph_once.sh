#!/usr/bin/env bash
set -euo pipefail

mkdir -p validation_results
log="validation_results/phase0n_kgram_graph_once.txt"
bench_csv="validation_results/phase0n_kgram_graph_bench.csv"
bench_summary="validation_results/phase0n_kgram_graph_summary.md"
bench_env="validation_results/phase0n_kgram_graph_env.txt"
probe_md="validation_results/phase0n_kgram_graph_probe.md"
probe_csv="validation_results/phase0n_kgram_graph_probe.csv"

{
  echo "phase0n kgram graph once: start"
  date -u '+utc %Y-%m-%dT%H:%M:%SZ'

  cargo fmt --check
  cargo check
  cargo test
  cargo clippy --all-targets --all-features -- -D warnings
  cargo build --release

  bash scripts/phase0h_smoke.sh
  bash scripts/phase0h_correctness_check.sh
  bash scripts/phase0i_policy_matrix_check.sh
  bash scripts/phase0l_no_index_smoke.sh
  bash scripts/phase0m_selector_smoke.sh

  python3 tools/phase0h_bench.py \
    --mode prebench \
    --lines 125000 \
    --repeats 3 \
    --include-no-index \
    --output "$bench_csv" \
    --summary "$bench_summary" \
    --env-report "$bench_env"

  python3 tools/phase0n_kgram_graph_probe.py \
    --lines 125000 \
    --block-lines 4096 \
    --output "$probe_md" \
    --csv "$probe_csv"

  bash scripts/phase0k_csv_commit_guard.sh "$bench_csv"
  bash scripts/phase0k_csv_commit_guard.sh "$probe_csv"
  bash scripts/phase0i_artifact_hygiene_check.sh

  echo "phase0n kgram graph once: pass"
} 2>&1 | tee "$log"
