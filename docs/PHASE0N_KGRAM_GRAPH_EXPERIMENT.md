# Phase 0n - K-gram graph/postings experiment

## Purpose

Phase 0n evaluates an experimental graph/postings family before changing the
`.zlg` on-disk format.

The current bitmap summary is useful for no-match and skip-heavy searches, but
it adds storage/compression overhead and common matching patterns still decode
all chunks. Phase 0n asks whether stronger block-level k-gram logic can reduce
candidate blocks enough to justify a future index profile.

## Experimental strategies

The offline probe compares four strategies over deterministic search blocks:

```text
bigram_block
  Block-level bigram presence.

trigram_sparse
  Sparse observed trigram postings.

bigram_graph_edges
  Overlapping bigram graph edges. A trigram abc is represented as ab -> bc.

rarest_kgram_2
  Select the two rarest bigrams/trigrams from each selector literal.
```

## Regex handling

Regex syntax is not indexed directly. The search planner first extracts safe
literal selectors from the pattern, then turns those literals into grams or
paths.

Examples:

```text
error|failed|denied
  selector: any(error, failed, denied)

(?:foo|bar)[0-9]
  selector: any(foo, bar)

key="[^"]+"
  selector: all(key=")

(?<=key=")[^"]+
  selector: all(key=")
```

Patterns with no safe literal selector scan normally.

## Why this remains offline

This phase does not write a new `.zlg` index format. It estimates selected
blocks and decoded bytes first. A format change should only happen if the probe
shows a large decoded-byte reduction and acceptable index-size estimates.

## Required outputs

```text
validation_results/phase0n_kgram_graph_bench.csv
validation_results/phase0n_kgram_graph_summary.md
validation_results/phase0n_kgram_graph_env.txt
validation_results/phase0n_kgram_graph_probe.md
validation_results/phase0n_kgram_graph_probe.csv
validation_results/phase0n_kgram_graph_once.txt
```

Both CSV files must be preserved in the final commit/package.

## Acceptance

Phase 0n is accepted when:

```text
cargo fmt/check/test/clippy/build pass
existing smoke/correctness/policy checks pass
Phase 0m selector smoke passes
prebench CSV is generated and preserved
k-gram graph probe CSV is generated and preserved
artifact hygiene passes
```
