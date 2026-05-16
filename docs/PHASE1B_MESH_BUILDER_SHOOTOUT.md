# Phase 1b - Mesh Summary Builder Shootout

## Purpose

Phase 1b keeps the Phase 0z on-disk format unchanged and focuses only on
reducing mesh summary build time for the current winning stack:

```text
fixed-lines8192
mesh-bigram ZBM1 v2
streaming grep
Rust regex default
PCRE2 -P with literal prefiltering and positive-lookbehind fast path
```

Phase 1a showed that the combined profile was the best build profile and that
summary construction remained the largest build-time cost. Phase 1b compares
multiple summary builder implementations while preserving the same serialized
summary format.

## Build profiles

- `current`: original summary builder and stream zstd encode path.
- `combined`: Phase 1a winner using reusable mesh scratch buffers and reusable
  `zstd::bulk::Compressor`.
- `combined-radix`: same as combined but uses a three-pass radix sort for packed
  u24 mesh edges instead of `sort_unstable`.
- `combined-hash`: same as combined but uses a `HashSet` to deduplicate edges
  during collection before sorting.

## Metrics

The benchmark records:

- output size
- compression wall and CPU time
- build stats JSON timing
- summary build time
- zstd encode time
- write time
- total build time
- summary bytes
- compressed payload bytes
- storage component split
- search sanity using the combined profile
- hot-path regex counters

## Guardrail

This phase does not change the on-disk format. All build profiles must emit
compatible ZBM1 v2 summaries and preserve search behavior.
