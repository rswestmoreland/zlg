# Phase 1o - Hardening Coverage Expansion

Phase 1o extends malformed-input and stability coverage after the Phase 1n cleanup pass. It does not change the locked production stack.

Locked stack:

```text
fixed-lines8192-cap8m
+ mesh-bigram ZBM1 v2
+ combined-bitset-seen
+ current reserve behavior
+ zstd::bulk::Compressor
+ presets fast=3, standard=6, best=8
+ streaming grep with summary-first skip and memchr line splitting
```

## Scope

This checkpoint adds focused tests for malformed archive and malformed query inputs:

- truncated global header
- unsupported global version
- unsupported chunk header length
- unexpected record magic
- excessive compressed length before allocation
- truncated summary bytes
- unsupported directory entry length
- directory length overflow
- truncated directory payload
- invalid footer magic
- invalid footer length
- truncated footer payload
- invalid Rust regex construction
- invalid PCRE2 regex construction
- CLI guard for `--head` plus `--max-count`
- locked compression preset values
- hidden production-internal compress options

## Non-goals

- No file-format freeze.
- No async worker pool.
- No new production builder candidates.
- No changes to ZBM1 v2.
- No changes to the selected builder, chunk policy, reserve behavior, or presets.

## Validation

Run:

```bash
bash scripts/phase1o_hardening_coverage_once.sh
```

Expected results:

- fmt/check/test/clippy/release build pass.
- smoke/correctness/policy/selector checks pass.
- no blanket `#![allow(dead_code)]` in `src/`.
- no abandoned external sort crates are reintroduced.
- artifact hygiene passes.
