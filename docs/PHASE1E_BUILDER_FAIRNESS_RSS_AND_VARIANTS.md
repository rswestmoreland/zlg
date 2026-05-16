# Phase 1e Builder Fairness, RSS, and Variant Probe

Phase 1e extends Phase 1d with a stricter measurement harness and additional
experimental builder profiles. The on-disk ZBM1 v2 mesh-bigram format is not
changed.

## Goals

- Make RSS capture fail-closed. A benchmark run with blank `max_rss_kb` is a
  failed run.
- Compare the serious builder candidates across multiple deterministic corpus
  shapes.
- Add the missing experimental profiles requested after Phase 1d:
  - `combined-trie-pair-bitset`
  - `combined-identity-hash`
  - `combined-rdxsort`
  - `combined-rdst`
- Keep `combined-bitset-seen` experimental, not locked.
- Keep `combined` as the safe baseline for semantic comparisons.

## New profiles

### combined-trie-pair-bitset

This is the true trie-pair profile for the current 3-byte mesh edges. It treats
an edge as:

```text
byte0 -> byte1 -> 256-bit byte2 set
```

The implementation uses a reusable first/second-byte index and per-pair 256-bit
sets. It stores original edges plus ASCII lowercase-delta edges, so it is
intended to be baseline-equivalent with `combined`.

### combined-identity-hash

This keeps the HashSet-style experiment but replaces the normal hasher with an
identity/no-op hasher for `u32` edge keys. The packed 3-byte edge is already the
key, so this tests whether avoiding the normal hash function makes set-based
pre-dedup competitive.

This is still expected to pay hash-table probing and metadata overhead.

### combined-rdxsort

This uses the external `rdxsort` crate for sorting packed `u32` edges, then
runs `dedup`. It is an isolated experiment.

### combined-rdst

This uses the external `rdst` crate with default features disabled for a
single-threaded radix-sort experiment over packed `u32` edges, then runs
`dedup`. It is an isolated experiment.

## Benchmark harness changes

`tools/phase1e_builder_fairness_bench.py` uses GNU `/usr/bin/time` with a custom
format:

```text
user_seconds=%U
system_seconds=%S
max_rss_kb=%M
```

The script exits with failure if any measured row has a blank `max_rss_kb`.
This avoids the Phase 1d issue where CPU timing could be captured while RSS was
left blank.

## Corpus set

The Phase 1e script runs deterministic temporary corpora:

- `high_dup`: log-like repeated structure and high duplicate edge pressure.
- `high_cardinality`: log-like but with many random-ish tokens.
- `unicode`: valid UTF-8 log text with Japanese/kana fields.
- `binaryish`: deterministic PNG-like binary data with embedded byte strings.

Generated corpora and compressed outputs remain temporary and must not be
committed.

## Success criteria

- `scripts/phase1e_builder_fairness_once.sh` completes.
- `cargo fmt --check`, `cargo check`, `cargo test`, `cargo clippy`, and release
  build pass.
- No CSV row has a blank `max_rss_kb`.
- `combined` round trip is byte-exact for every corpus.
- Serious profile search output matches `combined` for line-oriented corpora.
- Only compact text/CSV/Markdown validation results are committed.
- No build/temp/generated binary artifacts are committed.
