# Phase 0o - Creative Index Experiment

Phase 0o keeps zlg experimental and intentionally explores index designs that
may be larger or slower than no-index zlg, as long as the full `.zlg` result can
still compete with or beat equivalent gzip output.

## Goals

- Fix the Phase 0n `rarest_kgram_2` absent-gram flaw.
- Test smaller independently-decodable block sizes as an offline estimate.
- Add rare/selective patterns, not only common log patterns.
- Compare bigram, trigram, graph-edge, and frequency-guided k-gram strategies.
- Preserve compact CSV evidence.

## Key principle

The failure criterion is not "larger than no-index zlg." Index overhead is
expected. The failure criterion is whether the indexed `.zlg` profile becomes
larger and/or slower than the gzip/zgrep baseline without gaining search value.

## Strategies compared offline

- `bigram_block`
- `trigram_sparse`
- `bigram_graph_edges`
- `rarest_kgram_2_fixed`
- `rarest_kgram_4_fixed`
- `adaptive_rarest_25pct`
- `adaptive_rarest_10pct`

## Block sizes compared

- 512 lines
- 1024 lines
- 2048 lines
- 4096 lines

## Added pattern types

Phase 0o keeps the prior patterns and adds exact/rare selectors such as:

- `event_id=42424`
- `user=test65500`
- `key="abc9700"`
- `key="retry10060"`
- `key="deny21100"`
- `src_ip=198.51.100.55`
- `component=auth`
- `shard=7`
- `TRACEID-deadbeef-cafebabe`

## Expected result

Phase 0o should show whether graph/trigram/frequency-guided indexes are only
useful for rare literals, whether smaller blocks are required, and whether the
next real format experiment should split search blocks independently from larger
compression groups.
