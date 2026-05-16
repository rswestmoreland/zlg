# Phase 1d - Builder Fairness and Robustness

## Purpose

Phase 1d keeps the on-disk ZBM1 v2 mesh-bigram format unchanged and narrows the build strategy after the Phase 1c-fix result. The goal is to compare `combined-bitset-seen` fairly against lower-memory alternatives before deciding whether the 2 MiB u24 presence table is worth adopting.

`combined-bitset-seen` is not locked as the default. The active safe baseline remains:

```text
fixed-lines8192
+ mesh-bigram ZBM1 v2
+ zstd::bulk::Compressor
+ streaming grep
+ Rust regex default
+ PCRE2 for -P
+ literal prefiltering
+ positive-lookbehind fast path
+ --head / --max-count early stop
```

## Drift addressed

- The CLI compression defaults now match the active benchmark baseline: `fixed-lines8192`, `mesh-bigram`, and `combined`.
- README wording was updated from the older Phase 0g/fancy-regex description to the current PCRE2 and mesh-bigram baseline.
- Phase 1c wording was corrected so `combined-case-raw` and `combined-lower-only` are not described as semantically equivalent to the baseline.
- Build stats now expose scratch/memory-oriented fields so bitset and bucket strategies can be compared more fairly.

## New build profiles

### combined-lower-only-bitset-seen

Experimental lower-only profile. It uses the full u24 presence bitset but inserts only ASCII-lowercase-normalized 3-byte windows.

This profile is not baseline-equivalent. It can be useful for ASCII ignore-case experiments, but it can false-reject case-sensitive uppercase searches because original uppercase edges are not stored.

### combined-sparse-first-bitset

Baseline-equivalent profile. It stores original edges plus ASCII lowercase-delta edges, but deduplicates with a sparse first-byte to two-byte-suffix bitset:

```text
first byte -> 65536-bit suffix table for byte2+byte3
```

Each first-byte table is 8 KiB and is allocated only when that first byte is touched during the writer lifetime. Worst case is still 2 MiB, but log-like data may use less memory than a full u24 table.

### combined-grouped-buckets

Baseline-equivalent profile based on the grouped-array idea. It stores original edges plus ASCII lowercase-delta edges, then pushes edges into grouped first-byte buckets before sorting and deduping each bucket.

The groups are ordered so encoded edges remain globally sorted:

```text
0..47 spill
0..9 digit
58..64 spill
A..Z uppercase spill
91..96 spill
a
b
...
z
123..255 spill
```

This is close to the requested `a` through `z`, uppercase spillover, integer spillover, and everything else design. The "everything else" range is split into ordered spill buckets so the final ZBM1 delta stream remains sorted without a second global sort.

## Existing comparison profiles retained

- `combined`: safe semantic baseline.
- `combined-inline-lower-delta`: baseline-equivalent, avoids full lowercase chunk copy.
- `combined-bitset-seen`: baseline-equivalent, full 2 MiB u24 dedup table.
- `combined-bucket256`: baseline-equivalent, dense first-byte bucket sorting.
- `combined-radix`: baseline-equivalent internal radix sort.
- `combined-case-raw`: control only, exact-byte edges.
- `combined-lower-only`: control only, lowercase-normalized edges.

## New build stats fields

The build stats JSON now includes:

- `bitset_resizes`
- `bitset_cleared_edges`
- `touched_first_buckets`
- `scratch_bytes`
- `bitset_scratch_bytes`
- `first_bitset_scratch_bytes`
- `edge_scratch_capacity_bytes`
- `sort_scratch_capacity_bytes`
- `lower_scratch_capacity_bytes`
- `summary_scratch_capacity_bytes`
- `group_bucket_scratch_bytes`

These are intended to make bitset, sparse-bitset, and bucket strategies easier to compare. Wall time remains the primary benchmark value, but scratch bytes are now visible.

## Robustness tests added

Inline tests now cover:

- baseline equivalence for `combined-sparse-first-bitset` and `combined-grouped-buckets`
- lower-only equivalence for `combined-lower-only-bitset-seen` versus `combined-lower-only`
- UTF-8 mesh summary behavior as byte-oriented data
- binary-like mesh summary behavior
- in-memory round trip for UTF-8 payload bytes
- in-memory round trip for binary-like payload bytes

The mesh summary remains byte-oriented. It does not perform Unicode normalization or Unicode case folding.

## External sort crates

No external sort crate was added in this checkpoint. The current environment cannot validate new crate APIs or Cargo resolution, and the existing internal `combined-radix` profile remains available as the low-friction radix-sort control. Add `rdxsort` or `rdst` only after reviewing API, maintenance, license, and packed-u32 support in a Rust-capable validation environment.

## Validation command

```bash
scripts/phase1d_builder_fairness_once.sh
```

This runs formatting, check, tests, clippy, release build, existing smoke checks, and the Phase 1d benchmark harness.
