# Phase 1k Final Stack Memory and Level Diagnostic

## Purpose

Phase 1k consolidates the selected stack and runs one focused diagnostic pass for
compression levels and memory behavior. This is not a builder bakeoff.

Selected stack for this checkpoint:

```text
fixed-lines8192 with 8 MiB byte cap
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

## Locked changes in this checkpoint

- Default chunk policy is now `fixed-lines8192-cap8m`.
- Default compression level is now `6`.
- Default mesh build profile is now `combined-bitset-seen`.
- CRC32 is computed while the chunk is assembled, avoiding a later full extra
  pass over the chunk during archive writing.

The 8 MiB cap is intended to prevent very large line-count chunks from driving
peak RSS on long-line inputs. It is not a new candidate family.

## Diagnostic rows

The Phase 1k benchmark records:

- gzip levels 6, 8, and 9.
- final zlg stack at zstd levels 3, 6, 8, and 9.
- no-summary diagnostic rows at levels 6, 8, and 9.
- default CLI rows to verify that defaults match the explicit standard stack.
- uncapped long-line reference rows only for memory comparison.

## What this should answer

- Whether gzip -8 changes the comparison against zstd -8.
- Whether zstd -8 is a useful `best` or alternative-best preset.
- Whether level 6 remains the best default/standard preset.
- Whether the 8 MiB cap keeps long-line RSS under control.
- Whether moving CRC computation into chunk assembly has any visible timing or
  memory effect.
- Whether no-summary rows show that mesh overhead remains a smaller part of RSS
  than chunk buffering and zstd workspace.

## Non-goals

- Do not change ZBM1 v2.
- Do not change the selected builder away from `combined-bitset-seen`.
- Do not reintroduce dropped sort/hash experiments.
- Do not add async worker pools.
- Do not freeze the file format.
