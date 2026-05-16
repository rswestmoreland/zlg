Use the uploaded Phase 1l checkpoint as the baseline.

Run:

```bash
bash scripts/phase1l_final_stack_streamline_once.sh
```

You may fix compile errors, warnings, clippy findings, test failures, benchmark script bugs, RSS/CPU measurement bugs, CLI argument bugs, size-accounting bugs, reserve-profile routing bugs, search-skip correctness bugs, streaming decode bugs, and narrow issues required for the Phase 1l validation run to complete correctly.

Success criteria:

- cargo fmt --check passes.
- cargo check passes.
- cargo test passes.
- cargo clippy --all-targets --all-features -- -D warnings passes.
- cargo build --release passes.
- bash scripts/phase1l_final_stack_streamline_once.sh passes.
- validation_results/phase1l_final_stack_streamline.csv has no blank max_rss_kb values.
- validation_results/phase1l_final_stack_streamline.csv has no blank total_cpu_seconds values.
- gzip -6 rows are present for every corpus.
- zlg reserve rows are present for:
  - combined-bitset-seen
  - combined-bitset-seen-reserve-none
  - combined-bitset-seen-reserve-capped
  - combined-bitset-seen-reserve-prev-unique
- zlg rows include populated build stats for:
  - build_raw_edge_windows
  - build_candidate_edge_events
  - build_pushed_edges
  - build_unique_edges
  - build_edge_scratch_capacity_bytes
  - build_edge_capacity_before
  - build_edge_capacity_after
- all zlg reserve rows round trip exactly.
- all reserve variants produce byte-identical zlg output to combined-bitset-seen for each corpus.
- removed abandoned external sort crates remain removed.
- no new production builder candidates are added.

Commit limits:

- Commit only source fixes, docs, scripts, tests, benchmark code, Cargo.toml, Cargo.lock if needed, and compact validation result text, CSV, or Markdown files.
- Do not commit target/, temp directories, generated .zlg, .gz, .zst, generated logs, generated corpora, PNG files, binary fixtures, or other binary artifacts.
- Keep fixes narrow. Do not make unrelated refactors or runtime behavior changes.

Important constraints:

- Keep the default builder as combined-bitset-seen.
- Keep the default chunk policy as fixed-lines8192-cap8m.
- Keep the default level as 6.
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
5. Whether RSS and CPU were captured for every row.
6. Whether all reserve variants produced byte-identical output to current reserve.
7. Reserve strategy ranking summary.
8. Search-skip and streaming decode correctness notes, if any fixes were required.
9. Confirmation that no build/temp/binary artifacts were committed.
