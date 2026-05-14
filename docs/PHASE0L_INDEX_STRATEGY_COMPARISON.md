# Phase 0l Index Strategy Comparison

## Purpose

Phase 0l answers whether the current chunk-level byte-class/bigram summaries help enough to justify their metadata cost.

The Phase 0k result showed that skip-heavy searches are fast, but common matching patterns still decode every chunk. Phase 0l adds a direct comparison between:

- `.zlg` with bitmap search summaries.
- `.zlg` with no search summaries.
- gzip/zgrep baselines.
- plain grep/rg baselines.
- zstd/zstdcat baselines when those tools are available.

## Why this phase exists

The current bitmap summary can only say whether a chunk might contain a literal. It cannot narrow the match to a line range or sub-block. If the chunk is still independently compressed as one zstd frame, any candidate match requires decoding the whole chunk.

This phase should tell us whether the summary is helping enough today, before we design a more positional postings index.

## New runtime switch

Compression now has an experimental summary mode:

```bash
zlg compress --summary-mode bitmap input.log -o input.log.zlg
zlg compress --summary-mode none input.log -o input.no-index.zlg
```

`bitmap` is the existing behavior.

`none` writes zero-length per-chunk summaries. Grep then scans all chunks because there is no index to consult. This gives us a clean no-index `.zlg` baseline while keeping the same chunking and zstd container structure.

## New stats fields

`zlg grep --stats-json PATH` now also reports:

```text
selector_kind
selector_len
```

These fields help explain whether the matcher found a literal selector or fell back to scan-all behavior.

## Phase 0l command

```bash
bash scripts/phase0l_index_strategy_once.sh
```

This runs validation, smoke checks, prebench with bitmap plus no-index `.zlg` variants, CSV preservation guard, and artifact hygiene.

## Required CSV artifact

Phase 0l must preserve:

```text
validation_results/phase0l_index_strategy_bench.csv
```

This CSV must be committed or included in the final package.

## Result files

```text
validation_results/phase0l_index_strategy_bench.csv
validation_results/phase0l_index_strategy_summary.md
validation_results/phase0l_index_strategy_env.txt
validation_results/phase0l_index_strategy_analysis.md
validation_results/phase0l_index_strategy_once.txt
```

## Decision questions

Phase 0l should answer:

1. Does bitmap metadata materially reduce decoded bytes compared with no-index `.zlg`?
2. Does bitmap metadata improve first-output latency?
3. Does bitmap metadata hurt file size enough to matter?
4. Do common matching patterns still decode all chunks?
5. Should the next index design move toward positional bigram postings or smaller independently compressed search blocks?
6. Should current bitmap summaries remain enabled by default, become optional, or be replaced?

## Expected next design if bitmap is insufficient

If common matching patterns still decode all chunks, the likely next design is not async. It is:

```text
64K logical groups
smaller independently compressed search blocks
footer bigram postings index
postings entries: block id, first line, line count
query plan: extract safe literals, derive bigrams, intersect postings, decode candidate blocks, verify regex
```

Async/parallel search should wait until the index shape is proven.
