# Phase 1g Size Overhead Pass

Phase 1g moves past broad builder exploration and focuses on production-sized
questions for the remaining candidates.

Carried-forward builders:

- `combined-bitset-seen`: leading production candidate using a full contiguous
  u24 presence bitset.
- `combined-sparse-first-bitset`: second-best candidate using first-byte to
  two-byte-suffix bitsets allocated only for touched first bytes.
- `combined-bitset-paged-seen`: new full u24 bitset variant organized as 256
  first-byte pages. It performs the same dedupe-before-push function as
  `combined-bitset-seen`, but uses the page layout lesson from
  `combined-sparse-first-bitset` while still allocating the full 2 MiB u24
  space.
- `combined`: reference baseline only.

External comparison:

- `gzip -6` is included for build speed, CPU, RSS, and output size.

Why the paged variant exists:

`combined-bitset-seen` uses one contiguous 2 MiB bitset addressed by the packed
u24 edge. `combined-sparse-first-bitset` showed that first-byte paging can lower
memory when fewer first-byte buckets are touched. `combined-bitset-paged-seen`
keeps the exact full-u24 behavior but stores the bitset as 256 fixed pages of
8 KiB each. This tests whether page-local indexing or allocation behavior helps
without changing semantics or the on-disk ZBM1 v2 output.

Benchmark corpora:

- `high_dup`
- `high_cardinality`
- `unicode`
- `binaryish`
- `realistic_mixed_log`
- `long_line_log`
- `short_line_log`

Metrics:

- wall time
- total CPU seconds
- max RSS KiB
- output bytes
- zlg compressed payload bytes
- zlg summary bytes
- zlg chunk header bytes
- zlg directory/footer bytes
- builder scratch bytes
- pushed and unique edge counts
- duplicate ratio

Fail-closed requirements:

- blank `max_rss_kb` fails the benchmark
- blank `total_cpu_seconds` fails the benchmark
- search output for candidate profiles must match `combined` on line-oriented
  corpora
- `combined` round trip must be byte-exact for every corpus, including unicode
  and binaryish
- gzip rows must be present for every corpus

Dependency cleanup:

Phase 1g removes the abandoned external sort experiment dependencies from
`Cargo.toml`. Legacy profile names remain parseable, but they no longer pull
`rdxsort` or `rdst` into normal builds.

No format change:

All carried-forward zlg builders must emit the same ZBM1 v2 mesh-bigram summary
format. The file format remains experimental and is not frozen.
