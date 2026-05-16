Use the uploaded Phase 1k checkpoint as the baseline.

Run:

```bash
bash scripts/phase1k_final_stack_memory_once.sh
```

You may fix compile errors, warnings, clippy findings, test failures, benchmark
script bugs, RSS/CPU measurement bugs, CLI argument bugs, size-accounting bugs,
default-setting bugs, CRC correctness bugs, and narrow issues required for the
Phase 1k diagnostic run to complete correctly.

Success criteria:

- cargo fmt --check passes.
- cargo check passes.
- cargo test passes.
- cargo clippy --all-targets --all-features -- -D warnings passes.
- cargo build --release passes.
- bash scripts/phase1k_final_stack_memory_once.sh passes.
- validation_results/phase1k_final_stack_memory.csv has no blank max_rss_kb values.
- validation_results/phase1k_final_stack_memory.csv has no blank total_cpu_seconds values.
- gzip -6, gzip -8, and gzip -9 rows are present for every corpus.
- final zlg rows are present for zstd levels 3, 6, 8, and 9.
- no-summary diagnostic rows are present for zstd levels 6, 8, and 9.
- default-cli rows are present and match explicit final-cap8m-l6 output bytes.
- long_line_log includes uncapped reference rows for levels 6, 8, and 9.
- zlg rows include populated component and chunk-buffer fields:
  - zlg_total_bytes
  - zlg_summary_bytes
  - zlg_compressed_payload_bytes
  - max_chunk_uncompressed_bytes
  - max_chunk_compressed_payload_bytes
  - max_chunk_summary_bytes
- validation_results/phase1k_final_stack_memory_chunks.csv includes per-chunk rows.
- Round-trip checks pass for every zlg row.
- Removed abandoned external sort crates remain removed.
- No new production builder candidates are added.

Commit limits:

- Commit only source fixes, docs, scripts, tests, benchmark code, Cargo.toml,
  Cargo.lock if needed, and compact validation result text, CSV, or Markdown files.
- Do not commit target/, temp directories, generated .zlg, .gz, .zst,
  generated logs, generated corpora, PNG files, binary fixtures, or other binary artifacts.
- Keep fixes narrow. Do not make unrelated refactors or runtime behavior changes.

Important constraints:

- This is a final-stack memory and level diagnostic pass.
- Keep the default builder as combined-bitset-seen.
- Keep the default chunk policy as fixed-lines8192 with the 8 MiB cap.
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
5. Whether RSS and CPU were captured for every archive row.
6. gzip -8 versus gzip -9 summary.
7. zlg level 8 versus zlg level 9 summary.
8. Whether zstd level 8 is a useful best/alternative-best option.
9. Whether the 8 MiB cap controlled long-line RSS versus uncapped reference rows.
10. Whether default-cli matched explicit final-cap8m-l6 output bytes.
11. Confirmation that no build/temp/binary artifacts were committed.
