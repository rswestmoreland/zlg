# Next Chat Prompt - Phase 3 Validation and Release Readiness

You are continuing work on the zlg Rust project.

Use the current repository checkout as the authoritative baseline.

Goal:

Validate the Phase 2o reconciliation plus Phase 3 release-readiness package. Fix only issues required by validation. Do not expand features.

Current Phase 3 prep includes:

- command reference
- install/uninstall guide
- release checklist
- active roadmap
- man-page draft
- shell-completion design note
- release-readiness audit script
- release artifact dry-run script
- Cargo.toml readme metadata

Guardrails:

- Do not change the locked production core.
- Do not freeze the file format.
- Do not change default compression mode.
- Do not rename compression modes.
- Do not implement standalone zlg top.
- Do not add embedded gzip/bzip2/xz decoder crates.
- Do not add async worker pools.
- Keep comments and docs ASCII-only.
- Do not commit target/, generated release tarballs, checksums, generated compressed fixtures, corpora, logs, PNGs, or binary artifacts.

Required validation commands:

```bash
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
bash scripts/phase2g_archive_hardening_once.sh
bash scripts/phase2i_repeated_median_once.sh
bash scripts/phase2m_convert_once.sh
bash scripts/phase3_release_readiness_once.sh
bash scripts/phase3_release_artifact_dry_run.sh
```

Expected validation result file:

```text
validation_results/phase3_validation_2026-05-17.txt
```

Expected final response:

- commands run and pass/fail status
- files changed
- bugs/warnings fixed
- Phase 2o reconciliation validation status
- Phase 3 docs/readiness status
- release artifact dry-run status
- validation result files added
- commit hash
- remaining risks or follow-up items

Do not claim validation passed unless all required commands actually passed.
