# Phase 0g Handoff

## Purpose

This checkpoint converts the Phase 0 design pack into a concrete Rust prototype for validation and benchmark preparation.

## What is included

- Rust crate skeleton.
- CLI command contract.
- Provisional binary format writer/reader.
- Chunking policy implementations.
- Per-chunk byte-class and bigram search summaries.
- Streaming-readable chunk layout.
- Footer directory prototype.
- Basic grep implementation with fixed-string, Rust regex, and fancy-regex modes.

## What is intentionally not complete

- No async worker pool yet.
- No benchmark harness yet.
- No final v1 format freeze.
- No PCRE2 backend.
- No multiline regex mode.
- No timestamp sidecar.
- No dictionary training.
- No append/update mode.

## Recommended Codex workflow

1. Run the validation flow.
2. Fix compile, fmt, clippy, and test issues only.
3. Run the smoke tests.
4. Report changed files and exact command results.
5. Do not broaden scope into async, benches, or format changes until the prototype compiles and smoke tests pass.

## Required validation commands

```bash
cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
```

## Phase 0g acceptance

Phase 0g is acceptable when:

- All validation commands pass.
- Basic compress/cat/decompress round trip works.
- Basic grep returns expected lines.
- `-o`, `-n`, `-i`, `-c`, `-v`, and `-P` smoke tests work.
- No temp files are used.
- Memory remains bounded by chunk size and one active chunk in this prototype.
