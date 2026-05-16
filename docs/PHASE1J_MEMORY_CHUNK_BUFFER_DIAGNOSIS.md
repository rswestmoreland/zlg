# Phase 1j Memory and Chunk-Buffer Diagnosis

Phase 1j is a focused optimization/diagnostic pass after selecting the production builder stack.

The selected stack remains:

```text
fixed-lines8192
+ mesh-bigram ZBM1 v2
+ zstd::bulk::Compressor
+ combined-bitset-seen
+ streaming grep
+ Rust regex default
+ PCRE2 for -P
+ literal prefiltering
+ positive-lookbehind fast path
+ --head / --max-count early stop
```

This phase does not reopen the builder decision. It investigates memory usage and compression levels.

## Questions

1. Does zstd level 9 compare favorably with gzip -9 for a future best mode?
2. Can zstd level 6 remain the likely standard mode after Phase 1i?
3. How much RSS comes from chunk buffering versus mesh summary work?
4. Does a stream-per-chunk zstd path reduce memory compared with the reusable bulk compressor?
5. Do 8192-line chunks with byte caps reduce long-line RSS while preserving line-aligned chunks?

## Diagnostic modes

The benchmark includes:

- gzip -6
- gzip -9
- locked zlg level 3, 6, and 9
- stream-per-chunk zlg level 6 and 9
- no-summary zlg level 6 and 9
- fixed-lines8192 with 4 MiB, 8 MiB, and 16 MiB byte caps at levels 6 and 9

The stream-per-chunk profile uses the same mesh summary builder, but avoids the reusable zstd bulk compressor. It is a diagnostic profile, not a new production builder decision.

The byte-capped policies are diagnostic candidates for memory control. They preserve the 8192-line maximum but allow earlier chunk boundaries when a chunk exceeds the byte cap.

## Expected outputs

- `validation_results/phase1j_memory_chunk_buffer.md`
- `validation_results/phase1j_memory_chunk_buffer.csv`
- `validation_results/phase1j_memory_chunk_buffer_chunks.csv`
- `validation_results/phase1j_memory_chunk_buffer_once.txt`

## Guardrails

- Do not add new builder candidates.
- Do not change ZBM1 v2.
- Do not change the selected builder behavior.
- Do not freeze the file format.
- Do not add async worker pools.
- Do not reintroduce external sort crates.
- Do not commit generated archives, corpora, binary fixtures, or build artifacts.
