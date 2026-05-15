# Phase 0x - 8192 Mesh-Bigram, PCRE2, Early Stop, and Streaming Decode

## Purpose

Phase 0x keeps the narrowed strategy stack focused on:

- fixed-lines8192
- mesh-bigram summaries
- Rust regex for the default regex path
- PCRE2 for `-P`
- built-in early stop through `-m` / `--max-count` and `--head`
- a new streaming decode grep path for comparison

This phase does not freeze the file format and does not implement a full async
worker pool.

## PCRE2

The previous fancy-regex `-P` path is replaced by `pcre2::bytes` so the `-P`
behavior is closer to grep-style PCRE support.

The default non-`-P` regex path remains Rust `regex`.

## Early stop

The CLI now supports:

```text
-m, --max-count <N>
--head <N>
```

`--head 1` is intended as the built-in equivalent of piping match output to
`head -n1`, while allowing `zlg` to stop scanning internally.

## Streaming decode

The new grep option:

```text
--stream-decode
```

uses a zstd streaming decoder and scans decoded lines as they are produced,
without materializing the entire selected chunk into one `Vec<u8>`.

The existing full-chunk decode path remains available for comparison. Full mode
still decodes a selected chunk into memory before scanning.

In streaming mode:

- normal full-chunk scans validate decoded length and CRC at the end
- early-stopped chunks may not complete CRC validation
- stats expose `stream_decode`, `crc_checked_chunks`, and
  `stream_early_stopped_chunks`

## Current decompression model

`zlg cat` still uses the full-chunk decode path in this phase. The streaming
experiment is focused on grep/search first.

## Benchmark focus

The benchmark compares only:

- zlg fixed-lines8192 mesh-bigram
- original/plain grep
- gzip -6
- gzip decompression
- zgrep

For zlg grep, it records both:

- full decode mode
- stream decode mode

## Query categories

The benchmark runs:

- needle fixed IP: `198.18.99.123`
- common fixed string: `failed password`
- Rust regex: `key="[^"]+"`
- PCRE2 lookbehind: `(?<=key=")[^"]+`
- PCRE2 IP range full output: `src_ip=192\.168\.10[234]`
- PCRE2 IP range early stop: `--head 1 -P 'src_ip=192\.168\.10[234]'`

## Output artifacts

Phase 0x should produce:

- `validation_results/phase0x_8192_pcre2_early_bench.csv`
- `validation_results/phase0x_8192_pcre2_early_bench.md`
- `validation_results/phase0x_8192_pcre2_early_once.txt`
