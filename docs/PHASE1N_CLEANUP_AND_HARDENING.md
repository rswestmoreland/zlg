# Phase 1n - Production Cleanup and Hardening

Purpose: clean the final zlg stack after Phase 1m validation and add narrow
malformed-input hardening without changing the selected compression/search
strategy.

Locked production stack:

```text
fixed-lines8192-cap8m
+ mesh-bigram ZBM1 v2
+ combined-bitset-seen
+ current reserve behavior
+ zstd::bulk::Compressor
+ presets: fast=3, standard=6, best=8
+ streaming grep
+ summary-first skip
+ memchr line splitting
+ Rust regex default
+ PCRE2 for -P
+ literal prefiltering
+ positive-lookbehind fast path
+ --head / --max-count early stop
```

Cleanup performed in this checkpoint:

- Removed the blanket `#![allow(dead_code)]` from `src/search.rs`.
- Removed old experimental mesh builder functions from production source.
- Removed the temporary Phase 1m baseline source snapshot from `tools/`.
- Kept only the selected build profile on the normal CLI surface.
- Added comments around the final chunk cap, reader allocation limits, and
  production bitset builder.

Hardening added in this checkpoint:

- Reader allocation guards for excessive summary and compressed-payload lengths.
- Checked directory length multiplication to avoid overflow.
- Checked legacy summary length arithmetic during summary decode.
- Tests for invalid global magic, excessive summary length, truncated compressed
  payloads, CRC mismatch, truncated ZBM1 varints, and trailing bytes in ZBM1
  summaries.

This checkpoint is not a usability pass. Defer CLI cosmetic design, globbing,
conversion from other compressed formats, top-N aggregation, and async/parallel
pipeline work until after cleanup/hardening validation is green.
