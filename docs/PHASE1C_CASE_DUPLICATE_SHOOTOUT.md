# Phase 1c - Case Strategy and Duplicate-Control Shootout

## Purpose

Phase 1c keeps the current on-disk format unchanged and explores whether the
mesh-bigram summary builder can be made faster by reducing case-handling work
or duplicate edge volume before sorting.

The Phase 1b winner remains the control:

```text
fixed-lines8192 + mesh-bigram ZBM1 v2 + zstd bulk + reusable mesh scratch
```

## Profiles

Phase 1c compares:

- `combined`
- `combined-case-raw`
- `combined-lower-only`
- `combined-inline-lower-delta`
- `combined-bitset-seen`
- `combined-bucket256`

## Profile meanings

### combined

Current winning profile. It stores original-case edges and, if uppercase exists
in the chunk, also stores edges from a lowercased chunk copy.

### combined-case-raw

Stores only exact-byte edges from the original chunk. This is a speed and size
control for measuring the cost of case support.

This profile is not intended as the default because it may lose pruning power
for ignore-case searches.

### combined-lower-only

Stores only ASCII-lowercase-normalized edges. This measures whether a single
normalized edge set is faster and smaller.

This profile is intentionally experimental. Because the summary is only a skip
filter and decoded chunks are verified by the real matcher, it is useful for
measurement, but it should not become default until query-side semantics are
fully designed.

### combined-inline-lower-delta

Stores original edges and adds the lowercase edge only when the lowercase edge
differs. This avoids the full lowercase chunk copy and avoids pushing lowercase
edges that are identical to original edges.

### combined-bitset-seen

Uses a reusable 2 MiB u24 presence bitset to deduplicate packed 3-byte edges
before sorting. It stores the same logical edge set as inline-lower-delta but
tries to reduce duplicate sorting cost.

### combined-bucket256

Buckets by the high byte of the packed u24 edge, then sorts and deduplicates
smaller bucket ranges. This tests whether bucket-local sorting improves cache
behavior versus one large `sort_unstable`.

## Metrics

The benchmark records:

- compression wall/CPU time
- build stats timing
- summary bytes
- compressed payload bytes
- raw edge windows
- pushed edge count
- unique edge count
- duplicate ratio
- search sanity timings
- hot-path matcher counters

## Scope

This phase does not change the on-disk format and does not introduce async.
