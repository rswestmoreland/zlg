# ZLG Next Chat Prompt - Phase 2f Validation/Fix

You are continuing work on the zlg Rust project.

Use the current GitHub repository checkout as the authoritative baseline.

Goal: validate and fix the current Phase 2e/2f implementation. Codex should build, test, run scripts and benches, fix only validation failures, and commit the fixes plus compact validation results.

Current prep includes:

- screenshot-friendly `zlg stats` text output
- expanded `zlg stats --json`
- fast-vs-standard performance smoke benchmark
- output overwrite safety using `-y`, `--force`
- stronger Phase 2 CLI smoke checks for head/tail/stats/force/invalid archive behavior

Locked core:

```text
fixed-lines8192-cap8m
mesh-bigram ZBM1 v2
combined-bitset-seen
current reserve behavior
zstd::bulk::Compressor
streaming grep
summary-first skip
memchr line splitting
Rust regex default
PCRE2 mode
literal prefiltering
positive-lookbehind fast path
head-style early stop
```

Guardrails:

- Do not change the locked production core.
- Do not change mesh-bigram ZBM1 v2.
- Do not freeze the file format.
- Do not add async worker pools.
- Do not add .bz2 or .xz support.
- Keep comments and docs ASCII-only.
- Keep path names short.
- Do not commit target/, temp dirs, generated logs, corpora, `.zlg`, `.gz`, `.zst`, PNGs, or binary artifacts.

Required validation:

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
bash scripts/phase2e_perf_modes_head_tail_once.sh
```

Add a compact validation result file under `validation_results/` with exact commands and outcomes.

Suggested commit message:

```text
Validate and fix phase2e phase2f CLI maturity
```
