# ZLG Next Chat Prompt - Phase 2d Validation/Fix

You are continuing work on the zlg Rust project.

Use the current GitHub repository checkout as the authoritative baseline.

Goal for this Codex run:

Build, test, validate, run the new Phase 2d benchmark, and fix only issues required to make the current Phase 2d implementation pass. This is a validation and fix pass, not a feature expansion pass.

Current validated baseline:

- Phase 2 CLI validation/fix commit: 6eab4a3
- Phase 2c metadata/performance validation/fix commit: d1179fc

Current Phase 2d implementation to validate:

- reliable benchmark resource measurement using Python os.wait4()
- documentation explaining benchmark CPU/RSS capture reliability
- larger needle-in-haystack benchmark scenario
- head and tail benchmark comparisons against raw logs and gzip streams
- stronger Phase 2 CLI smoke parity checks for head/tail output

Locked production core:

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

Compression modes:

```text
none     = store payloads uncompressed inside .zlg chunks
fast     = zstd level 3
standard = zstd level 6
best     = zstd level 8
```

Use the term "compression mode", not "preset".

CLI decisions to preserve:

- use subcommands
- use lowercase short options only
- use lowercase long options only
- avoid aliases
- use -p/--pcre2 instead of -P
- use -f/--fixed instead of -F
- use --mode, not --preset
- do not expose the full numeric compression-level range in normal CLI
- do not expose hidden benchmark/developer options in normal help
- use --head, not --max-count
- include help, version, head, tail, test, info, and stats
- keep top and convert deferred

Guardrails:

- do not change the locked production core
- do not change mesh-bigram ZBM1 v2
- do not freeze the file format
- do not reintroduce rdxsort or rdst
- do not add new experimental builder candidates
- do not add async worker pools
- do not add .bz2 or .xz support
- keep comments and docs ASCII-only
- keep path names short
- do not commit target/, temp dirs, generated .zlg/.gz/.zst files, corpora, logs, PNGs, or binary artifacts
- keep changes narrow and validation-driven

Required validation commands:

```text
cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
bash scripts/phase0h_smoke.sh
bash scripts/phase0h_correctness_check.sh
bash scripts/phase0i_policy_matrix_check.sh
bash scripts/phase0m_selector_smoke.sh
bash scripts/phase0i_artifact_hygiene_check.sh
bash scripts/phase2_cli_smoke.sh
bash scripts/phase2d_perf_head_tail_once.sh
```

Phase 2d benchmark expectations:

- CPU/RSS metrics must be populated through os.wait4() resource accounting.
- The bench should fail rather than silently producing blank wall/user/system/CPU/RSS fields.
- Search must compare plain grep, gzip zgrep, and zlg grep.
- Head must compare plain head, gzip -dc | head, and zlg head.
- Tail must compare plain tail, gzip -dc | tail, and zlg tail.
- The needle scenario should be much larger than the Phase 2c 6 MB smoke case so zlg has many chunks available to skip.
- Output hashes must match across equivalent backends.
- Generated logs, gzip files, zlg archives, and command outputs must not be committed.

Expected result files:

```text
validation_results/phase2d_perf_head_tail_smoke.csv
validation_results/phase2d_perf_head_tail_smoke.md
validation_results/phase2d_perf_head_tail_smoke_once.txt
validation_results/phase2d_validation_2026-05-17.txt
```

Validation/fix workflow:

1. Inspect git status.
2. Run cargo fmt --check; if it fails, run cargo fmt and record formatting remediation.
3. Run cargo check; fix compile errors.
4. Run cargo test; fix test failures.
5. Run clippy with -D warnings; fix warnings without broad suppressions.
6. Run release build.
7. Run all required scripts through bash.
8. Run the Phase 2d benchmark script.
9. If any required dependency such as gzip, zgrep, head, tail, or bash is missing, record the missing dependency clearly and do not claim the comparison passed.
10. If the bench emits blank resource metrics, fix the measurement code; do not accept blank CPU/RSS fields.
11. Add a compact validation result file under validation_results/ with exact commands and outcomes.
12. Commit only source, tests, scripts, docs, and compact validation results.

Suggested commit message:

```text
Validate and fix phase2d benchmark reliability
```

Expected final response:

- commands run and pass/fail status
- files changed
- bugs/warnings fixed
- test/script/docs updates
- benchmark resource capture status
- search/head/tail result summary
- validation result files added
- commit hash
- remaining risks or follow-up items

Do not claim validation passed unless all required commands actually passed.
