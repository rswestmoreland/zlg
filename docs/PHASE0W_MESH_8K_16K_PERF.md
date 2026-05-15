# Phase 0w - Mesh-Bigram 8K/16K Performance

## Purpose

Phase 0w focuses on storage efficiency and runtime performance for the current
winning strategy: mesh-bigram.

This phase drops non-mesh zlg candidates and tests whether 8K or 16K line
chunks can stay below gzip size while preserving the search advantage over
zgrep.

## Policies tested

- fixed-lines4096
- fixed-lines8192
- fixed-lines16384
- fixed-lines64k

## Summary mode

Only this summary mode is tested:

- mesh-bigram

## Baselines

The benchmark compares against:

- gzip -6 compression
- gzip decompression
- zgrep
- original/plain grep over the uncompressed corpus

## Query categories

The benchmark runs:

- needle fixed string: exact IP address appearing once near 80 percent volume
- common fixed string: `failed password`
- Rust regex: `key="[^"]+"`
- fancy-regex: `(?<=key=")[^"]+`

The Rust regex and fancy-regex comparison is intentional. Rust's standard
`regex` crate is fast but does not support lookbehind. The `fancy-regex` crate
supports lookbehind by using a backtracking engine where needed, which can be
much slower on broad searches.

## Metrics

The benchmark records:

- output size
- size versus original input
- size versus gzip -6
- compression time
- decompression time
- search time
- user CPU seconds
- system CPU seconds
- total CPU seconds
- max RSS memory
- chunks skipped and decoded
- decoded byte ratio
- matching lines
- selector metadata

CPU/RSS values use `/usr/bin/time -v` when available and Python `resource`
fallback otherwise.
