# ZLG Phase 2c Codex Validation Prompt

You are continuing work on the zlg Rust project.

Use the current GitHub repository checkout as the authoritative baseline.

Goal for this Codex run:

Build, test, validate, and fix only issues required to make the Phase 2c metadata/help/docs/performance-smoke implementation compile cleanly and pass validation. This is a validation and fix pass, not a feature expansion pass.

Current validated baseline:

The Phase 2 CLI implementation was validated at commit 6eab4a3.

Current Phase 2c implementation to validate:

- seekable footer/directory metadata reader
- metadata-backed file-input `tail`
- metadata-backed file-input `info` and `stats`
- hidden developer/bench stats options in normal help
- improved `version --long`
- compact performance smoke bench comparing plain `grep`, `zgrep`, and `zlg grep`

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
scripts/phase0h_smoke.sh
scripts/phase0h_correctness_check.sh
scripts/phase0i_policy_matrix_check.sh
scripts/phase0m_selector_smoke.sh
scripts/phase0i_artifact_hygiene_check.sh
scripts/phase2_cli_smoke.sh
scripts/phase2c_perf_smoke_once.sh
```

Validation/fix instructions:

1. Inspect git status.
2. Run `cargo fmt --check`; if it fails, run `cargo fmt` and record formatting remediation.
3. Run `cargo check`; fix compile errors.
4. Run `cargo test`; fix test failures.
5. Run clippy with `-D warnings`; fix warnings without broad suppressions.
6. Run release build.
7. Run all required scripts.
8. Run the Phase 2c performance smoke bench.
9. If gzip or zgrep are missing, record the missing dependency clearly in validation results.
10. If any old script still uses uppercase CLI options, update it narrowly to the locked lowercase policy.
11. Add a compact validation result file under `validation_results/` with exact commands and outcomes.
12. Commit only source, tests, scripts, docs, and compact validation results.

Suggested validation result file:

```text
validation_results/phase2c_metadata_perf_validation_2026-05-17.txt
```

Suggested commit message:

```text
Validate and fix phase2c metadata and perf smoke
```

Expected final response:

- commands run and pass/fail status
- files changed
- bugs/warnings fixed
- metadata reader and command behavior fixes
- tests/scripts/docs updated
- performance smoke result summary
- validation result files added
- commit hash
- remaining risks or follow-up items

Do not claim validation passed unless all required commands actually passed.
