Use the uploaded Phase 1m checkpoint as the baseline.

Run:

```bash
bash scripts/phase1m_cleanup_ab_once.sh
```

You may fix compile errors, warnings, clippy findings, test failures, benchmark
script bugs, RSS/CPU measurement bugs, CLI argument bugs, A/B benchmark bugs,
cache-control bugs, and narrow issues required for the Phase 1m validation run
to complete correctly.

Success criteria:

- cargo fmt --check passes.
- cargo check passes.
- cargo test passes.
- cargo clippy --all-targets --all-features -- -D warnings passes.
- cargo build --release passes.
- bash scripts/phase1m_cleanup_ab_once.sh passes.
- validation_results/phase1m_cleanup_ab_bench.csv has no blank max_rss_kb values.
- validation_results/phase1m_cleanup_ab_bench.csv has no blank total_cpu_seconds values.
- validation_results/phase1m_cleanup_ab_search.csv has no blank max_rss_kb values.
- validation_results/phase1m_cleanup_ab_search.csv has no blank total_cpu_seconds values.
- baseline_phase1k and final_phase1m compression rows are present.
- baseline_phase1k and final_phase1m search rows are present.
- final_phase1m compression rows round trip exactly.
- baseline_phase1k compression rows round trip exactly.
- search output hashes match between baseline_phase1k and final_phase1m for every query.
- the normal production CLI surface keeps the selected stack and presets.
- abandoned external sort crates remain removed.
- no new production builder candidates are added.

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
5. Whether RSS and CPU were captured for every compression and search row.
6. Whether search output matched between baseline_phase1k and final_phase1m.
7. Compression A/B summary: baseline_phase1k versus final_phase1m.
8. Search A/B summary: baseline_phase1k versus final_phase1m.
9. Cache-control method used by the benchmark.
10. Confirmation that no build/temp/binary artifacts were committed.
