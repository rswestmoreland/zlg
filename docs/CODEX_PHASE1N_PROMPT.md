Use the uploaded Phase 1n checkpoint as the baseline.

Run:

bash scripts/phase1n_cleanup_hardening_once.sh

You may fix compile errors, warnings, clippy findings, test failures, script
bugs, narrow hardening bugs, and formatting issues required for the Phase 1n
cleanup/hardening validation to complete correctly.

Success criteria:

- cargo fmt --check passes.
- cargo check passes.
- cargo test passes.
- cargo clippy --all-targets --all-features -- -D warnings passes.
- cargo build --release passes.
- bash scripts/phase1n_cleanup_hardening_once.sh passes.
- No blanket #![allow(dead_code)] remains in src/.
- The temporary tools/phase1m_baseline_src snapshot remains removed.
- Malformed archive and malformed summary tests pass.
- The selected production stack remains unchanged.
- Removed abandoned external sort crates remain removed.
- No new production builder candidates are added.

Commit limits:

- Commit only source fixes, docs, scripts, tests, Cargo.toml, Cargo.lock if
  needed, and compact validation result text files.
- Do not commit target/, temp directories, generated .zlg, .gz, .zst, generated
  logs, generated corpora, PNG files, binary fixtures, or other binary artifacts.
- Keep fixes narrow. Do not make unrelated refactors or runtime behavior
  changes.

Important constraints:

- Keep the default builder as combined-bitset-seen.
- Keep the default chunk policy as fixed-lines8192 with the 8 MiB cap.
- Keep the default preset as standard, zstd level 6.
- Keep fast = 3, standard = 6, best = 8.
- Keep mesh-bigram ZBM1 v2 unchanged.
- Do not reintroduce rdxsort or rdst.
- Do not add new experimental sort/hash crates.
- Do not freeze the file format.
- Do not implement async worker pools.
- Keep comments and docs ASCII-only.

Report back only:

1. Commands run and pass/fail status.
2. Files changed.
3. Commits made.
4. Any fixes required.
5. Whether the blanket dead-code allow was removed and stayed removed.
6. Whether malformed-input hardening tests passed.
7. Confirmation that the final production stack stayed unchanged.
8. Confirmation that no build/temp/binary artifacts were committed.
