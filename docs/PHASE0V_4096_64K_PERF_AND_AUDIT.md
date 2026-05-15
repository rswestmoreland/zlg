# Phase 0v - 4096 vs 64K Mesh-Bigram Performance and Audit

## Purpose

Phase 0v narrows the runtime/storage comparison to the current winning index
family: mesh-bigram.

This phase drops 1024/2048 from the benchmark matrix and compares:

- `fixed-lines4096`
- `fixed-lines64k`

Each policy is tested with:

- `mesh-bigram`
- `none`

The benchmark compares zlg against:

- gzip -6 compression
- gzip decompression
- zgrep search
- plain grep over the original corpus

## Benchmark dimensions

The Phase 0v probe records:

- compression wall time
- decompression wall time
- fixed-string needle search time
- fixed-string common search time
- fancy-regex search time
- user CPU seconds
- system CPU seconds
- maximum resident set size when `/usr/bin/time -v` is available
- output bytes
- storage delta versus gzip -6
- storage overhead versus no-index zlg
- chunks total/skipped/decoded
- decoded bytes and decoded ratio
- selector kind/length/count

## Code audit notes

The current code has several hot paths worth watching:

1. Mesh summary build
   - `SearchSummary::from_bigram_mesh` builds a vector of packed 24-bit edges,
     sorts it, and deduplicates it.
   - This is likely the dominant mesh-compression overhead.
   - Phase 0v adds a small allocation optimization: reserve capacity up front.

2. Lowercase summary duplication
   - Earlier code always allocated a lowercase copy for mesh/path summaries.
   - Phase 0v avoids that allocation unless the chunk contains ASCII uppercase.

3. Summary decode
   - `SearchSummary::decode` reads mesh summaries into a vector.
   - Future work can avoid re-sorting if the format guarantees sorted unique
     edge tables.

4. Per-line fancy regex
   - `fancy-regex` operates on strings, so grep currently converts candidate
     lines with `String::from_utf8_lossy`.
   - This is acceptable for now but should be watched in the fancy-regex rows.

5. Chunk decode
   - `RawChunk::decode` uses `zstd::stream::decode_all`, allocating a decoded
     chunk buffer.
   - This is simple and bounded by chunk size, but future streaming decode could
     reduce peak RSS for large chunks.

6. Chunker allocation
   - The chunker creates a fresh chunk buffer for each chunk.
   - Reusing buffers may reduce allocations later, but should be measured first.

7. Trait-object I/O wrappers
   - `open_input` and `open_output` return boxed trait objects.
   - This keeps CLI code simple. It is unlikely to dominate versus zstd and regex
     work, but can be revisited after larger bottlenecks are measured.

## Intentional non-goals

This phase does not add:

- trigram mesh
- path-window
- rare-window
- per-group mesh
- async/concurrency
- PCRE2
- final format freeze

## Expected output

Phase 0v should produce:

- `validation_results/phase0v_4096_64k_bench.csv`
- `validation_results/phase0v_4096_64k_bench.md`
- `validation_results/phase0v_4096_64k_perf_once.txt`

The CSV must be committed and preserved.
