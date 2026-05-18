You are continuing work on the zlg Rust project.

Start with REVIEW ONLY. Do not write code until the review is complete, drift is identified, and the exact validation/fix plan is clear.

Current prep checkpoint:

zlg_phase2o_closure_reconciliation_prep_chatgpt.zip

Current validated baseline before this prep:

- Phase 2n extract/top validation commit: dca51a6

Current Phase 2o prep to validate:

- Remove external `zstd` CLI dependency from Phase 2m convert validation.
- Keep `.zst` conversion based on the existing internal zstd crate.
- Add a Rust unit test that creates `.zst` bytes with the existing zstd crate and verifies `zlg convert` round-trips through `.zlg`.
- Harden external helper cleanup for `.gz`, `.bz2`, and `.xz` conversion by killing/waiting on helper failure and cleaning temporary output.
- Preserve Phase 2n `grep -e --top` behavior and option consistency.
- Add roadmap item for a future GrepContext/GrepPipelineContext cleanup to replace growing grep helper argument lists.

Locked production core:

fixed-lines8192-cap8m
+ mesh-bigram ZBM1 v2
+ combined-bitset-seen
+ current reserve behavior
+ zstd::bulk::Compressor
+ streaming grep by default
+ summary-first skip
+ memchr line splitting
+ Rust regex default
+ PCRE2 mode
+ literal prefiltering
+ positive-lookbehind fast path
+ head-style early stop

Guardrails:

- Do not change the locked production core.
- Do not change mesh-bigram ZBM1 v2.
- Do not freeze the file format.
- Do not change CRC scope from uncompressed chunk bytes.
- Do not change default grep to strict mode.
- Do not change the default compression mode.
- Do not rename compression modes.
- Do not implement parser-like top lines, top tokens, or top fields.
- Do not implement standalone `zlg top` in this pass.
- Do not add embedded gzip/bzip2/xz decoder crates.
- Do not add new Cargo dependencies.
- Do not invoke helpers through a shell.
- Keep comments and docs ASCII-only.
- Keep changes narrow and validation-driven.

Required validation commands:

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

Phase 2o expectations:

- No `zstd` command is required by scripts/phase2m_convert_once.sh.
- `.zst` conversion is covered by a Rust test using the existing zstd crate.
- `.gz`, `.bz2`, and `.xz` helper convert checks still run when helpers are present.
- Helper subprocess cleanup compiles and remains narrow.
- Failed helper conversions do not leave final partial output files behind.
- No new Cargo dependencies are added.
- Phase 2n grep extract/top behavior remains validated.
- The roadmap includes a future GrepContext/GrepPipelineContext cleanup item.

Expected result file:

validation_results/phase2o_validation_2026-05-17.txt

Suggested commit message:

Validate and fix phase2o closure reconciliation

Do not claim validation passed unless all required commands actually passed.
