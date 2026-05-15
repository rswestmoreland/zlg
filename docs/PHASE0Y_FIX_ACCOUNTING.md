# Phase 0y-fix - ZLG Component Accounting

## Purpose

Phase 0y improved regex hot-path behavior but exposed a benchmark accounting bug
in the `.zlg` component parser. The reported compressed payload bytes were far
larger than the whole file, so the storage split could not be trusted.

This phase fixes only the accounting parser and reruns the same focused
benchmark matrix.

## Fix

The parser now uses the actual `ZCH1` chunk header offsets:

```text
0  magic [4]
4  header_len u16
6  flags u16
8  chunk_index u64
16 first_line_number u64
24 line_count u64
32 uncompressed_len u64
40 compressed_len u64
48 summary_len u32
52 crc32 u32
56 reserved u64
```

The previous parser read compressed and summary lengths from incorrect offsets.

## Sanity checks

The parser now fails if:

- a chunk header is truncated
- a chunk record exceeds file size
- directory/footer accounting exceeds file size
- any component exceeds total file size
- global header + chunk headers + summaries + payload + directory/footer does
  not equal total file size

## Scope

This phase does not change the `.zlg` format or runtime search behavior.
It only corrects benchmark accounting and reruns the Phase 0y matrix.
