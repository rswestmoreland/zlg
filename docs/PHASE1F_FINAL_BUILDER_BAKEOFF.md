# Phase 1f Final Builder Bakeoff

Phase 1f narrows builder testing to the remaining production-facing candidates:

- `combined`
- `combined-bitset-seen`
- `combined-sparse-first-bitset`
- `combined-trie-pair-bitset`

The benchmark also records gzip `-6` compression as the external build-speed,
CPU, RSS, and size baseline. This is part of the project success criteria:
zlg must eventually compress logs faster than gzip while producing competitive
or smaller files and avoiding excessive memory use.

## Corpus set

The Phase 1f benchmark covers:

- `high_dup`
- `high_cardinality`
- `unicode`
- `binaryish`
- `realistic_mixed_log`
- `long_line_log`
- `short_line_log`

## Metrics

The benchmark records, for each compression row:

- wall seconds
- user CPU seconds
- system CPU seconds
- total CPU seconds
- max RSS KB
- output bytes
- zlg component accounting
- zlg build stats and scratch accounting

RSS and CPU capture are fail-closed. A blank `max_rss_kb` or blank
`total_cpu_seconds` fails the benchmark.

## Correctness checks

The script validates:

- byte-exact combined round trip for every corpus
- search-output equivalence for candidate profiles against `combined` on
  line-oriented corpora
- no blank RSS or CPU rows
- compact CSV/Markdown artifacts only

The benchmark keeps the mesh-bigram ZBM1 v2 on-disk format unchanged.
