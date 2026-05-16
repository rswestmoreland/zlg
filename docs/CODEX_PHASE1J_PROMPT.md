Use the uploaded Phase 1j checkpoint as the baseline.

Run:

```bash
bash scripts/phase1j_memory_chunk_buffer_once.sh
```

You may fix compile errors, warnings, clippy findings, test failures, benchmark script bugs, RSS/CPU measurement bugs, CLI argument bugs, size-accounting bugs, and narrow issues required for the Phase 1j diagnostic run to complete correctly.

Success criteria:

- cargo fmt --check passes.
- cargo check passes.
- cargo test passes.
- cargo clippy --all-targets --all-features -- -D warnings passes.
- cargo build --release passes.
- bash scripts/phase1j_memory_chunk_buffer_once.sh passes.
- validation_results/phase1j_memory_chunk_buffer.csv has no blank max_rss_kb values.
- validation_results/phase1j_memory_chunk_buffer.csv has no blank total_cpu_seconds values.
- gzip -6 and gzip -9 rows are present for every corpus.
- locked zlg rows are present for zstd levels 3, 6, and 9.
- stream-per-chunk zstd diagnostic rows are present for levels 6 and 9.
- no-summary diagnostic rows are present for levels 6 and 9.
- fixed-lines8192 byte-cap diagnostic rows are present for 4 MiB, 8 MiB, and 16 MiB caps at levels 6 and 9.
- zlg rows include populated component and chunk-buffer fields:
  - zlg_total_bytes
  - zlg_summary_bytes
  - zlg_compressed_payload_bytes
  - max_chunk_uncompressed_bytes
  - max_chunk_compressed_payload_bytes
  - max_chunk_summary_bytes
- validation_results/phase1j_memory_chunk_buffer_chunks.csv includes per-chunk rows.
- Round-trip checks pass for every zlg row.
- Removed abandoned external sort crates remain removed.
- No new production builder candidates are added.

Commit limits:

- Commit only source fixes, docs, scripts, tests, benchmark code, Cargo.toml, Cargo.lock if needed, and compact validation result text, CSV, or Markdown files.
- Do not commit target/, temp directories, generated .zlg, .gz, .zst, generated logs, generated corpora, PNG files, binary fixtures, or other binary artifacts.
- Keep fixes narrow. Do not make unrelated refactors or runtime behavior changes.

Important constraints:

- This is a memory and chunk-buffer diagnostic pass for the selected stack.
- Do not change the default production builder away from combined-bitset-seen.
- Do not change mesh-bigram ZBM1 v2.
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
6. gzip -6 versus gzip -9 summary.
7. zlg level 6 versus zlg level 9 summary.
8. Whether stream-per-chunk zstd reduced RSS versus bulk zstd.
9. Whether fixed-lines8192 byte caps reduced long-line RSS.
10. Confirmation that no build/temp/binary artifacts were committed.
