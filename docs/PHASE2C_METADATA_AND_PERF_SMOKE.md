# Phase 2c Metadata Efficiency and Performance Smoke

Phase 2c follows the validated Phase 2 CLI implementation at commit 6eab4a3.

## Scope

Phase 2c is a narrow implementation phase:

- add a seekable footer/directory metadata reader for the current experimental format
- use metadata for file-backed `tail`, `info`, and `stats`
- keep streaming fallback behavior for stdin/non-seekable paths
- keep normal help free of hidden benchmark/developer options
- improve `version --long` with format/core defaults
- add a compact performance smoke bench comparing plain `grep`, `zgrep`, and `zlg grep`

This phase does not freeze the file format.

## Locked production core

Do not reopen these decisions in Phase 2c:

```text
fixed-lines8192-cap8m
+ mesh-bigram ZBM1 v2
+ combined-bitset-seen
+ current reserve behavior
+ zstd::bulk::Compressor
+ streaming grep
+ summary-first skip
+ memchr line splitting
+ Rust regex default
+ PCRE2 mode
+ literal prefiltering
+ positive-lookbehind fast path
+ head-style early stop
```

## Metadata reader

The current writer already records:

- global format version
- chunk policy id
- compression mode id
- per-chunk offsets
- per-chunk summary bytes
- per-chunk compressed payload bytes
- per-chunk uncompressed bytes
- per-chunk line counts
- archive total lines
- archive total uncompressed bytes
- directory offset and length

Phase 2c adds a seekable reader for this existing footer/directory layout. It validates:

- global magic and format version
- footer magic and footer length
- directory magic and entry length
- directory/footer chunk-count agreement
- directory length agreement
- directory/footer layout boundaries
- per-entry summary/payload boundaries
- total line and byte counts

The reader is additive and format-aware, not a format freeze.

## Command behavior

### tail

For file inputs, `tail` reads footer/directory metadata, walks chunk entries backward until enough lines are covered, decodes only the selected trailing chunks, and emits the last N lines.

For stdin, `tail` keeps the streaming VecDeque fallback.

### info

For file inputs, `info` uses metadata and avoids decoding all chunks. It reports:

- format
- format version
- chunk count
- line count
- uncompressed bytes
- payload bytes
- summary bytes
- directory bytes
- known component bytes
- archive bytes
- compression mode
- chunk policy
- metadata source

### stats

For file inputs, `stats` uses metadata. Phase 2e changes normal text output from the initial wc-style placeholder into a screenshot-friendly archive report while preserving `--json` for scripts:

```text
<lines> <bytes>
```

JSON output includes chunk/component/archive fields.

## Help and version polish

Normal help must not expose:

```text
--preset
--level
-P
-F
--max-count
--build-profile
--summary-mode
--chunk-policy
--build-stats-json
--stats-json
```

Normal help should expose:

```text
--mode
-f, --fixed
-p, --pcre2
--head
```

`zlg version --long` should include:

- package version
- author/contact
- license
- format version
- default compression mode
- default chunk policy
- default summary type
- default build profile
- supported compression modes

## Performance smoke bench

Phase 2c adds a compact smoke bench, not a full benchmark matrix.

Script:

```text
scripts/phase2c_perf_smoke_once.sh
```

Tool:

```text
tools/phase2c_perf_smoke_bench.py
```

The bench compares:

- plain log with `grep`
- gzip log with `zgrep`
- zlg archive with `zlg grep`

Scenarios:

1. repeated regex
   - deterministic log with frequent matching auth-style status values
   - regex search using `grep -E`, `zgrep -E`, and `zlg grep`

2. needle in haystack
   - deterministic log with one fixed-string needle around 80 percent deep
   - fixed-string search using `grep -F`, `zgrep -F`, and `zlg grep -f`

Measurements:

- storage bytes
- build/compress wall time where applicable
- search wall time
- user CPU seconds
- system CPU seconds
- CPU percent
- max RSS KB
- exit code
- output bytes
- output SHA-256
- match count

Expected compact outputs when run:

```text
validation_results/phase2c_perf_smoke.csv
validation_results/phase2c_perf_smoke.md
validation_results/phase2c_perf_smoke_once.txt
```

Generated logs, gzip files, zlg archives, and search outputs must stay in temporary directories and must not be committed.

## Required validation

After Phase 2c implementation, run:

```text
cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
scripts/phase0h_smoke.sh
scripts/phase0h_correctness_check.sh
scripts/phase0i_policy_matrix_check.sh
scripts/phase0m_selector_smoke.sh
scripts/phase0i_artifact_hygiene_check.sh
scripts/phase2_cli_smoke.sh
scripts/phase2c_perf_smoke_once.sh
```

If gzip or zgrep are missing, record that clearly in validation results instead of claiming the three-way bench passed.
