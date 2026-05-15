# Phase 1a - Mesh-Bigram Build-Speed Shootout

## Purpose

Phase 1a keeps the current on-disk format unchanged and tests implementation
variants for building the fixed-lines8192 + mesh-bigram stack faster.

The current winning stack is:

```text
fixed-lines8192
mesh-bigram ZBM1 v2
streaming grep
Rust regex default
PCRE2 -P with literal prefiltering
positive-lookbehind fast path
```

Phase 0z made the mesh summary compact. The next bottleneck is build time.

## Variants

All variants produce the same `.zlg` format.

```text
current
  existing SearchSummary::from_bigram_mesh + zstd::stream::encode_all

mesh-scratch
  reusable mesh edge/lowercase/summary buffers + zstd::stream::encode_all

zstd-bulk
  existing mesh build + reusable zstd::bulk::Compressor

combined
  reusable mesh buffers + reusable zstd::bulk::Compressor
```

## Why zstd bulk is tested

The zstd crate documents `stream::encode_all` as a convenience function that
returns a new `Vec<u8>` containing a complete compressed frame. The zstd bulk
API is intended for small independent blocks and its `Compressor` reuses a zstd
context across jobs, which may reduce allocations across many chunks.

## Instrumentation

`zlg compress` now accepts:

```text
--build-profile current|mesh-scratch|zstd-bulk|combined
--build-stats-json PATH
```

The stats file reports:

```text
chunks
summary_ns
zstd_ns
write_ns
total_ns
summary_bytes
compressed_bytes
uncompressed_bytes
```

## Scope

This phase does not implement async and does not change the file format.
It is a build-speed implementation shootout only.
