Use the uploaded Phase 1i checkpoint as the baseline.

Run:

bash scripts/phase1i_level_memory_once.sh

You may fix compile errors, warnings, clippy findings, test failures, benchmark
script bugs, RSS/CPU measurement bugs, size-accounting bugs, CLI argument bugs,
and narrow issues required for the Phase 1i diagnostic run to complete
correctly.

Success criteria:

- cargo fmt --check passes.
- cargo check passes.
- cargo test passes.
- cargo clippy --all-targets --all-features -- -D warnings passes.
- cargo build --release passes.
- bash scripts/phase1i_level_memory_once.sh passes.
- validation_results/phase1i_level_memory_archive.csv has no blank max_rss_kb values.
- validation_results/phase1i_level_memory_archive.csv has no blank total_cpu_seconds values.
- gzip -6 rows are present for every corpus.
- locked zlg mesh rows are present for zstd levels 3, 4, 5, and 6.
- diagnostic zlg no-summary rows are present for zstd levels 3, 4, 5, and 6.
- component accounting is populated for every zlg row.
- validation_results/phase1i_level_memory_chunks.csv includes per-chunk rows.
- validation_results/phase1i_level_memory_memory.csv includes mesh versus no-summary RSS deltas.
- Removed abandoned external sort crates remain removed.
- No new production candidates are added.

Commit limits:

- Commit only source fixes, docs, scripts, tests, benchmark code, Cargo.toml,
  Cargo.lock if needed, and compact validation result text, CSV, or Markdown
  files.
- Do not commit target/, temp directories, generated .zlg, .gz, .zst,
  generated logs, generated corpora, PNG files, binary fixtures, or other binary
  artifacts.
- Keep fixes narrow. Do not make unrelated refactors or runtime behavior
  changes.

Important constraints:

- This is a diagnostic-only pass for the locked stack.
- Do not change fixed-lines8192.
- Do not change mesh-bigram ZBM1 v2.
- Do not change combined-bitset-seen behavior.
- Do not add new builder candidates.
- Do not reintroduce rdxsort or rdst.
- Do not add new experimental sort/hash crates.
- Do not change the on-disk format.
- Do not freeze the file format.
- Do not implement async worker pools.
- Do not add unrelated runtime features.
- Keep comments and docs ASCII-only.

Report back only:

1. Commands run and pass/fail status.
2. Files changed.
3. Commits made.
4. Any fixes required.
5. Whether RSS and CPU were captured for every archive row.
6. Whether zstd levels 4, 5, and 6 were tested for the locked mesh profile.
7. Whether diagnostic no-summary rows were captured.
8. Whether levels 4, 5, or 6 close the payload-size gap for realistic_mixed_log and short_line_log.
9. Main memory finding: gzip RSS, zlg no-summary RSS, and zlg mesh RSS.
10. Confirmation that no build/temp/binary artifacts were committed.
