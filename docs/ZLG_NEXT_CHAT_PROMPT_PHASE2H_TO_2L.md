# ZLG Next Chat Prompt - Phase 2h-2l Validation

You are continuing work on the zlg Rust project.

Start with validation/fix only. Do not add new features unless a required
validation failure proves a narrow fix is needed.

Authoritative scope:

- Validate Phase 2h-2l final CLI maturity prep.
- Preserve the locked compression/search core.
- Keep `zlg grep --strict` as the opt-in candidate-chunk verification mode.
- Keep default `zlg grep` streaming and low-latency.
- Validate repeated-median benchmark support.
- Validate improved info/stats text and JSON output.
- Validate head/tail edge cases.
- Validate archive hardening probe updates.

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
bash scripts/phase2g_archive_hardening_once.sh
bash scripts/phase2i_repeated_median_once.sh
```

Expected validation outputs:

```text
validation_results/phase2e_perf_modes_head_tail_smoke.csv
validation_results/phase2e_perf_modes_head_tail_smoke.md
validation_results/phase2g_archive_hardening.csv
validation_results/phase2g_archive_hardening.md
validation_results/phase2i_repeated_median_smoke.csv
validation_results/phase2i_repeated_median_smoke.md
validation_results/phase2h_to_2l_validation_2026-05-17.txt
```

Guardrails:

- Do not change mesh-bigram ZBM1 v2.
- Do not change the CRC scope from uncompressed chunk bytes.
- Do not change the default grep mode to strict.
- Do not change the default compression mode.
- Do not rename compression modes in this pass.
- Do not freeze the file format.
- Do not implement top or convert.
- Do not add async worker pools.
- Do not add `.bz2` or `.xz` support.
- Keep comments and docs ASCII-only.
- Do not commit generated archives, corpora, target, temp files, logs, PNGs, or binary artifacts.

Expected final response:

- commands run and pass/fail status
- files changed
- bugs/warnings fixed
- strict grep validation status
- default streaming grep status
- info/stats validation status
- head/tail edge validation status
- archive hardening result summary
- repeated-median benchmark summary
- validation result files added
- commit hash
- remaining risks or follow-up items
