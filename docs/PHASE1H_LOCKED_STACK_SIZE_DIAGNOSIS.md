# Phase 1h Locked-Stack Size Diagnosis

Phase 1h is a diagnostic-only size pass. It does not reopen the builder decision,
chunk policy decision, search path decision, or on-disk summary format decision.

## Locked stack

```text
fixed-lines8192
+ mesh-bigram ZBM1 v2
+ zstd::bulk::Compressor
+ combined-bitset-seen
+ streaming grep
+ Rust regex default
+ PCRE2 for -P
+ literal prefiltering
+ positive-lookbehind fast path
+ --head / --max-count early stop
```

## Purpose

Phase 1g showed that equivalent builders produce identical .zlg sizes. The next
question is not whether to change builders. The next question is why the locked
stack is larger than gzip on some corpora.

The Phase 1h benchmark records archive-level and chunk-level component data so
we can separate these causes:

- zstd compressed payload bytes
- mesh summary bytes
- chunk header bytes
- directory/footer bytes
- global header bytes
- per-chunk payload ratio
- per-chunk summary ratio
- per-chunk mesh edge count
- per-chunk line count and average line bytes

## Scope

In scope:

- Run the locked combined-bitset-seen stack.
- Record gzip -6 as the size, speed, CPU, and RSS baseline.
- Carry combined-sparse-first-bitset as the memory reference.
- Carry combined as the historical reference baseline.
- Produce compact CSV and Markdown diagnostics.
- Fail if RSS or CPU fields are blank.
- Fail if required size component fields are blank.

Out of scope:

- New builder candidates.
- Revisiting fixed-lines8192.
- Changing mesh-bigram ZBM1 v2.
- Adaptive summary skipping.
- Zstd level changes.
- Larger or smaller active chunk policies.
- Async worker pools.
- Runtime feature additions.

## Outputs

Expected outputs after Codex validation:

- validation_results/phase1h_size_diagnosis_once.txt
- validation_results/phase1h_size_diagnosis.md
- validation_results/phase1h_size_diagnosis_archive.csv
- validation_results/phase1h_size_diagnosis_chunks.csv

## Interpretation rules

Use combined-bitset-seen rows for the locked-stack size diagnosis.

Use combined-sparse-first-bitset only as a memory reference.

Use combined only as the historical reference baseline.

Do not treat this phase as a builder bakeoff.
