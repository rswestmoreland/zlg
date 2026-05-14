# Codex Prompt - Phase 0j Instrumented Prebench

Copy/paste prompt:

```text
You are continuing work on the zlg Rust project.

Start with validation and instrumented pre-bench readiness only. Do not broaden scope into async worker pools, full benchmark proof, file-format redesign, PCRE2, multiline regex, timestamp sidecars, dictionary training, append mode, or performance tuning yet.

Project context:

zlg is a single-binary Linux CLI utility and .zlg file format for compressing, decompressing/catting, and searching plaintext logs. It uses zstd internally with independent chunks, inline byte-class/bigram search summaries, and a footer directory prototype.

Current goal:

Validate Phase 0j instrumentation and produce one clean instrumented pre-bench result set. The purpose is to expose search counters, first-output latency, chunk counts, compressed-payload bytes, summary bytes, metadata overhead, decoded bytes, and match counts before full benchmark work begins.

Primary command:

bash scripts/phase0j_instrumented_prebench_once.sh

If the script fails:

1. Identify the exact failing command.
2. Make the smallest bounded fix required.
3. Re-run the failed command or the full script as appropriate.
4. Do not broaden project scope.
5. Record the result clearly.

Guardrails:

- Do not commit binary files.
- Do not commit target/, build artifacts, temp files, generated .zlg files, generated logs, or large benchmark outputs.
- Do not add heavy fixtures or generated corpora.
- Do not add async/concurrency yet.
- Do not add PCRE2.
- Do not redesign the file format unless required to fix a correctness issue in the current prototype.
- Do not add multiline regex or timestamp indexing.
- Do not add unsafe Rust.
- Keep comments and docs ASCII-only.
- Keep path names short and repo-friendly.
- Prefer small text, CSV, and Markdown reports only.
- Keep changes limited to validation, correctness, scripts, docs, harness instrumentation, or minimal source fixes needed for the instrumented pre-bench flow.

Required validation flow, either through the one-command script or individually if debugging:

cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
bash scripts/phase0h_smoke.sh
bash scripts/phase0h_correctness_check.sh
bash scripts/phase0i_policy_matrix_check.sh
python3 tools/phase0h_bench.py --mode prebench --lines 125000 --repeats 3 --output validation_results/phase0j_prebench_bench.csv --summary validation_results/phase0j_prebench_bench_summary.md --env-report validation_results/phase0j_prebench_env.txt
bash scripts/phase0j_csv_presence_check.sh validation_results/phase0j_prebench_bench.csv
bash scripts/phase0i_artifact_hygiene_check.sh

Expected output reports:

validation_results/phase0j_instrumented_prebench_once.txt
validation_results/phase0j_prebench_bench.csv
validation_results/phase0j_prebench_bench_summary.md
validation_results/phase0j_prebench_env.txt

Allowed output artifacts:

- Source fixes, only if required.
- Script fixes, only if required.
- Docs fixes, only if required.
- Cargo.lock if Cargo updates it.
- Small text/CSV/Markdown validation results under validation_results/.

Final response should include:

1. Summary of what was reviewed.
2. Exact commands run and pass/fail status.
3. Whether scripts/phase0j_instrumented_prebench_once.sh passed.
4. Pre-bench result file names produced, including the CSV.
5. Short summary of the pre-bench numbers, including chunk skip counters and metadata overhead if available.
6. Files changed.
7. Any remaining issues or warnings.
8. Confirmation that build/temp/binary artifacts were not committed.
```
