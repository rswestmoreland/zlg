# Phase 0j - Instrumentation and Full-Bench Prep

## Purpose

Phase 0j prepares `zlg` for full benchmark work by adding measurement instrumentation and compact result preservation.

This phase is still not the final benchmark proof and does not freeze the file format.

## Scope

Allowed in this phase:

```text
search counter instrumentation
first-output latency capture in the Python harness
compressed payload versus metadata accounting
CSV preservation checks
small script and documentation updates
minimal source changes required for instrumentation
```

Not allowed in this phase:

```text
async worker pool
format redesign
format freeze
PCRE2 backend
multiline regex
timestamp sidecar
dictionary training
append mode
large fixtures
binary artifacts
large benchmark outputs
```

## Runtime instrumentation

`zlg grep` now has an instrumentation option:

```bash
zlg grep --stats-json /tmp/zlg-stats.json PATTERN file.zlg
```

The JSON file contains compact counters:

```text
files
chunks_total
chunks_skipped
candidate_chunks
chunks_decoded
decoded_bytes
matching_lines
```

The option is intended for benchmark harnesses and should not change normal grep output.

## Harness instrumentation

`tools/phase0h_bench.py` now records additional fields in the CSV:

```text
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
```

These fields are needed to determine whether zlg is slower because:

```text
too many chunks are selected
summaries are not selective enough
chunks are too large
metadata overhead is too high
regex verification dominates runtime
```

## One-command readiness flow

Codex should run:

```bash
bash scripts/phase0j_instrumented_prebench_once.sh
```

This runs:

```text
cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
phase0h smoke checks
phase0h correctness checks
phase0i policy matrix checks
instrumented prebench harness
CSV column presence check
artifact hygiene check
```

## Expected small reports

```text
validation_results/phase0j_instrumented_prebench_once.txt
validation_results/phase0j_prebench_bench.csv
validation_results/phase0j_prebench_bench_summary.md
validation_results/phase0j_prebench_env.txt
```

## Phase 0j acceptance criteria

Phase 0j is acceptable when:

```text
one-command readiness flow passes
CSV is preserved and non-empty
CSV includes instrumentation columns
summary includes zlg grep counter medians
no build/temp/compressed artifacts are committed
no scope-broadening changes are introduced
```

## Next phase

After Phase 0j passes in Codex, the next phase should be Phase 0k full benchmark candidate run.

Phase 0k should use the instrumented CSV and summaries to compare:

```text
gzip -6 and gzip -9 compression speed and size
zlg compression speed and size by chunk policy
zgrep search speed
zlg grep search speed and skip counters
first-output latency
metadata overhead
```
