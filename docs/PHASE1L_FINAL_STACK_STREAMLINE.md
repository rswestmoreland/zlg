# Phase 1l - Final Stack Streamlining Prep

This checkpoint keeps the selected production stack fixed and prepares a narrow validation run for safe micro-optimizations and edge reserve strategies.

Selected stack remains:

```text
fixed-lines8192-cap8m
+ mesh-bigram ZBM1 v2
+ zstd::bulk::Compressor
+ combined-bitset-seen
+ zstd presets 3/6/8
+ streaming grep
+ Rust regex default
+ PCRE2 for -P
+ literal prefiltering
+ positive-lookbehind fast path
+ --head / --max-count early stop
```

## Implemented prep changes

- Added summary-first search read path:
  - read chunk header and summary first
  - run summary filter before reading compressed payload
  - skip compressed payload bytes for rejected chunks
- Changed streaming decode line splitting to use `memchr`.
- Added direct slice matching for lines that are fully contained in a decode buffer.
- Kept line accumulation only for lines crossing decode-buffer boundaries.
- Reused the chunker line scratch buffer across reads.
- Avoided copying pending overflow lines by swapping buffers when the 8 MiB cap spills a line into the next chunk.
- Added moderate chunk data preallocation.
- Added line scratch shrink threshold for pathological oversized lines.
- Kept incremental CRC during chunk assembly.
- Added build-stat fields for candidate edge events and edge Vec capacity tracking.
- Added reserve-strategy benchmark profiles for combined-bitset-seen:
  - current reserve: `combined-bitset-seen`
  - no upfront reserve: `combined-bitset-seen-reserve-none`
  - capped reserve: `combined-bitset-seen-reserve-capped`
  - previous-unique reserve: `combined-bitset-seen-reserve-prev-unique`

## Purpose

The production default is not changed away from `combined-bitset-seen`. The reserve variants are diagnostic profiles only until benchmark results prove one should replace the current reserve behavior.

## Validation artifacts

Expected compact outputs:

- `validation_results/phase1l_final_stack_streamline.csv`
- `validation_results/phase1l_final_stack_streamline_chunks.csv`
- `validation_results/phase1l_final_stack_streamline.md`
- `validation_results/phase1l_final_stack_streamline_once.txt`

The benchmark fails if:

- RSS or CPU is blank.
- any zlg row fails round trip.
- any reserve variant produces output bytes different from the current reserve path.
- required reserve profiles are missing.
