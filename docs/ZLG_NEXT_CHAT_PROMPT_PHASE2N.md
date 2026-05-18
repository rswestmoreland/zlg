You are continuing work on the zlg Rust project.

Start with REVIEW ONLY. Do not write more code until the review is complete, drift is identified, and the exact validation/fix plan is clear.

Current prep checkpoint:

zlg_phase2n_extract_top_option_consistency_prep_chatgpt.zip

Current validated baseline before this prep:

- Phase 2h-2l validation commit: 260ca74
- Phase 2m helper convert validation commit: e0705a7

Current Phase 2n prep to validate:

- Replace pre-release `-o, --only-matching` with `-e, --extract`.
- Add `-t, --top` for grep-integrated aggregation of extracted matches.
- Add `-l, --limit`, default 20.
- Add `-a, --cap`, default 100000.
- Add `-r, --truncate`, default 1000 bytes.
- Add `-j, --json` for top JSON output.
- Replace `-l, --files-with-matches` with `-g, --paths`.
- Add short forms for existing public options where practical, including `-m, --mode`, `-y, --force`, `-j, --json`, `-q, --quiet`, and `-s, --strict`.
- Keep default grep streaming and low-latency.
- Keep `--strict` opt-in.
- Keep standalone `zlg top` deferred.

Guardrails:

- Do not change the locked production core.
- Do not change mesh-bigram ZBM1 v2.
- Do not freeze the file format.
- Do not change CRC scope from uncompressed chunk bytes.
- Do not change the default compression mode.
- Do not rename compression modes.
- Do not implement parser-like top lines, top tokens, or top fields.
- Do not implement standalone `zlg top` in this pass.
- Do not add embedded gzip/bzip2/xz decoder crates.
- Do not add async worker pools.
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

Phase 2n expectations:

- `zlg grep --help` shows `-e, --extract` and `-t, --top`.
- `zlg grep --help` does not show `-o` or `--only-matching`.
- `zlg grep --help` shows `-g, --paths` and does not show `--files-with-matches`.
- `zlg grep -e PATTERN file.zlg` emits extracted matches.
- `zlg grep -te PATTERN file.zlg` emits top aggregate output.
- `zlg grep -pte PATTERN file.zlg` supports stacked short flags.
- `zlg grep --top PATTERN file.zlg` fails because top requires extract.
- `zlg grep -te --cap 1 PATTERN file.zlg` fails when more than one unique value is found and emits no trusted top results.
- `zlg grep -te --truncate 3 PATTERN file.zlg` marks truncated values.
- `zlg grep -te --json PATTERN file.zlg` emits JSON top output.
- `zlg grep -g PATTERN file.zlg` prints matching input paths.
- `zlg grep -f -p PATTERN file.zlg` still fails.
- Default grep remains streaming.
- `--strict` remains opt-in and can combine with extract/top.

Expected result file:

validation_results/phase2n_validation_2026-05-17.txt

Suggested commit message:

Validate and fix phase2n extract top options
