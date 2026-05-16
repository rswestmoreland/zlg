Use the uploaded Phase 1g checkpoint as the baseline.

Run:

bash scripts/phase1g_size_overhead_once.sh

You may fix compile errors, warnings, clippy findings, test failures, benchmark
script bugs, RSS/CPU measurement bugs, dependency cleanup issues, and narrow
bugs required for the Phase 1g benchmark to complete correctly.

Success criteria:

- cargo fmt --check passes.
- cargo check passes.
- cargo test passes.
- cargo clippy --all-targets --all-features -- -D warnings passes.
- cargo build --release passes.
- bash scripts/phase1g_size_overhead_once.sh passes.
- validation_results/phase1g_size_overhead.csv has no blank max_rss_kb values.
- validation_results/phase1g_size_overhead.csv has no blank total_cpu_seconds values.
- gzip -6 compression rows are present for every corpus.
- Search-output equivalence checks pass for candidate profiles against combined.
- Combined round-trip checks pass for every corpus, including unicode and binaryish.
- Cargo.toml no longer depends on rdxsort or rdst.

Commit limits:

- Commit only source fixes, docs, scripts, tests, benchmark code, Cargo.toml,
  Cargo.lock if needed, and compact validation result text, CSV, or Markdown
  files.
- Do not commit target/, temp directories, generated .zlg, .gz, .zst,
  generated logs, generated corpora, PNG files, binary fixtures, or other binary
  artifacts.
- Keep fixes narrow. Do not make unrelated refactors or runtime behavior
  changes.

Report back only:

1. Commands run and pass/fail status.
2. Files changed.
3. Commits made.
4. Any fixes required.
5. Whether RSS and CPU were captured for every row.
6. Phase 1g size-overhead ranking summary.
7. Confirmation that rdxsort and rdst were removed from active dependencies.
8. Confirmation that no build/temp/binary artifacts were committed.
