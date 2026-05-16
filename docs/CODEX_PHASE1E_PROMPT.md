# Codex Phase 1e Prompt

Use the uploaded Phase 1e checkpoint as the baseline.

Run the validation script:

```bash
bash scripts/phase1e_builder_fairness_once.sh
```

You may fix compile errors, warnings, clippy findings, test failures, benchmark
script bugs, dependency/API issues, RSS measurement bugs, and narrow bugs in the
new Phase 1e build profiles.

Success criteria:

- `cargo fmt --check` passes.
- `cargo check` passes.
- `cargo test` passes.
- `cargo clippy --all-targets --all-features -- -D warnings` passes.
- `cargo build --release` passes.
- `bash scripts/phase1e_builder_fairness_once.sh` passes.
- `validation_results/phase1e_builder_fairness_bench.csv` has no blank
  `max_rss_kb` values.
- The benchmark report and CSV are committed as compact text artifacts.

Commit limits:

- Commit only source fixes, docs, scripts, tests, benchmark code, Cargo.toml,
  Cargo.lock if dependencies are resolved, and compact validation result text,
  CSV, or Markdown files.
- Do not commit `target/`, temp directories, generated `.zlg`, `.gz`, `.zst`,
  generated logs, generated corpora, PNG files, binary fixtures, or other binary
  artifacts.
- Keep fixes narrow. Do not make unrelated refactors or runtime behavior changes.

Report back only:

1. Commands run and pass/fail status.
2. Files changed.
3. Commits made.
4. Any fixes required.
5. Whether RSS was captured for every row.
6. Phase 1e ranking summary.
7. Confirmation that no build/temp/binary artifacts were committed.
