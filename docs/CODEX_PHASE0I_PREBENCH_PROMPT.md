# Minimal Codex Prompt for Phase 0i Pre-Bench

```text
You are continuing zlg from the validated Phase 0g baseline plus Phase 0h proof-prep files.

Authoritative input bundle:

zlg_phase0i_prebench_ready.zip

Goal:

Run one pre-bench readiness pass. Make only bounded fixes required for validation, smoke, correctness, policy-matrix, benchmark-harness, or artifact-hygiene failures. Do not broaden scope.

Primary command:

scripts/phase0i_prebench_once.sh

This script runs:

cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
scripts/phase0h_smoke.sh
scripts/phase0h_correctness_check.sh
scripts/phase0i_policy_matrix_check.sh
python3 tools/phase0h_bench.py --mode prebench --lines 125000 --repeats 3
scripts/phase0i_artifact_hygiene_check.sh

Guardrails:

- Do not add async/concurrency yet.
- Do not freeze or redesign the file format.
- Do not add PCRE2.
- Do not add multiline regex.
- Do not add unsafe Rust.
- Do not add large fixtures or generated corpora.
- Do not commit target/, build artifacts, temp files, .zlg files, .gz files, .zst files, binaries, or large outputs.
- Keep generated corpora and compressed outputs in temp directories.
- Small text/CSV/Markdown reports under validation_results/ are allowed.
- Cargo.lock may remain committed if Cargo updates it legitimately.
- Keep comments and docs ASCII-only.
- Keep fixes minimal and explain each one.

Expected allowed output reports:

validation_results/phase0i_prebench_once.txt
validation_results/phase0h_prebench_bench.csv
validation_results/phase0h_prebench_bench_summary.md
validation_results/phase0h_prebench_env.txt

Final response should include:

1. Files reviewed.
2. Exact commands run and pass/fail status.
3. Summary of benchmark CSV/Markdown outputs.
4. Files changed.
5. Any remaining issues.
6. Artifact hygiene confirmation.
7. Whether the project is ready for the full benchmark run.
```
