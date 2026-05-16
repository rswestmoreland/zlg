# Phase 1i Zstd Level and Memory Diagnosis

Phase 1i is a diagnostic confirmation pass. It does not reopen the builder,
chunking, summary, search, or file-format decisions.

## Locked stack

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

## Questions

Phase 1h showed that realistic_mixed_log and short_line_log are larger than
gzip mostly because the zstd payload is larger, not because summary overhead is
large. Phase 1i tests whether levels 4, 5, and 6 close that payload gap while
preserving the speed advantage against gzip -6.

Phase 1i also investigates RSS by comparing:

- gzip -6
- locked zlg mesh profile at levels 3, 4, 5, and 6
- diagnostic zlg no-summary mode at levels 3, 4, 5, and 6

The no-summary rows are diagnostic only. They estimate the RSS baseline for
zlg chunking, zstd compression, and writer behavior before mesh-summary
construction is added.

## Outputs

- validation_results/phase1i_level_memory.md
- validation_results/phase1i_level_memory_archive.csv
- validation_results/phase1i_level_memory_chunks.csv
- validation_results/phase1i_level_memory_memory.csv
- validation_results/phase1i_level_memory_once.txt

## Success criteria

- RSS and total CPU are captured for every archive row.
- gzip -6 rows are present for every corpus.
- locked mesh rows exist for zstd levels 3, 4, 5, and 6.
- diagnostic no-summary rows exist for zstd levels 3, 4, 5, and 6.
- component accounting is populated for every zlg row.
- per-chunk rows are produced for every zlg archive.
- no new production candidate is introduced.
- fixed-lines8192, mesh-bigram ZBM1 v2, and combined-bitset-seen remain unchanged.

## Notes on gzip memory

Gzip/deflate has a small and mature streaming memory shape built around a
sliding window and compression state. zlg intentionally adds independent zstd
chunks, per-chunk summaries, a footer directory, and search acceleration state.
This phase measures how much RSS appears before and after summary construction
so memory tuning can be separated from builder selection.
