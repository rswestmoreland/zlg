# zlg Prototype

`zlg` is a prototype single-binary Linux CLI utility and `.zlg` file format for compressing, decompressing, catting, and searching plaintext logs.

This checkpoint is intended for Codex/Rust validation and benchmark iteration. The active benchmark baseline is fixed-lines8192 + mesh-bigram ZBM1 v2 + zstd::bulk::Compressor + streaming grep.

## Current scope

Implemented as source files:

- `zlg compress`
- `zlg decompress`
- `zlg cat`
- `zlg grep`
- provisional `ZLG1P0` container format
- independent zstd-compressed chunks
- inline per-chunk search summaries
- footer directory prototype
- fixed-string grep
- default Rust regex grep
- enhanced `-P` mode using PCRE2 bytes regex
- line-number, only-matching, count, ignore-case, invert-match, and files-with-matches flags
- fixed-line, progressive-line, byte-target, and hybrid chunk policy options
- build profiles for mesh-bigram summary builder experiments

## Important status

This is not a stable file format.

The current file format is still experimental and must not be frozen yet. The current default compression path is fixed-lines8192 + mesh-bigram + combined.


## Active build-profile baseline

The locked benchmark strategy is:

```text
fixed-lines8192
+ mesh-bigram ZBM1 v2
+ zstd::bulk::Compressor
+ streaming grep
+ Rust regex default
+ PCRE2 for -P
+ literal prefiltering
+ positive-lookbehind fast path
+ --head / --max-count early stop
```

Phase 1f narrowed the production builder candidates. `combined-bitset-seen` is the leading build-speed candidate, while `combined-sparse-first-bitset` remains the second candidate for lower-memory comparison. Phase 1g focuses on size overhead versus gzip and adds `combined-bitset-paged-seen`, a full-u24 paged bitset variant that performs the same dedupe-before-push function as `combined-bitset-seen` but stores the bitset as 256 first-byte pages.

Current carry-forward build profiles are:

- `combined-bitset-seen`: leading candidate, baseline-equivalent, full contiguous 2 MiB u24 dedup table.
- `combined-sparse-first-bitset`: second candidate, baseline-equivalent, sparse first-byte to two-byte-suffix bitsets.
- `combined-bitset-paged-seen`: experimental Phase 1g variant, baseline-equivalent, full 2 MiB u24 space stored as first-byte pages.
- `combined`: safe semantic baseline and reference builder.

Dropped external sort experiments no longer require `rdxsort` or `rdst` dependencies. Legacy build-profile names may remain parseable for now, but they are not active production candidates.

## Success criteria

The project should eventually prove that `zlg` can:

1. Compress plaintext logs faster than gzip.
2. Produce `.zlg` files smaller than gzip output.
3. Search compressed logs faster than zgrep.
4. Avoid temp files.
5. Avoid memory exhaustion.
6. Preserve normal Unix pipe behavior.
7. Preserve grep-like correctness for line-oriented log search.

## Basic usage

```bash
zlg compress input.log -o input.log.zlg
zlg cat input.log.zlg
zlg decompress input.log.zlg -o input.log
zlg grep 'error|failed|denied' input.log.zlg
zlg grep -o 'key="[^"]+"' input.log.zlg
zlg grep -P '(?<=key=")[^"]+' input.log.zlg
```

Pipe examples:

```bash
cat input.log | zlg compress > input.log.zlg
cat input.log.zlg | zlg cat
cat input.log.zlg | zlg grep 'error'
```

## Suggested validation in Codex

```bash
cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
```

## Suggested smoke tests in Codex

```bash
printf 'alpha\nerror key="abc"\nfailed password\n' > /tmp/zlg-smoke.log

cargo run -- compress /tmp/zlg-smoke.log -o /tmp/zlg-smoke.log.zlg
cargo run -- cat /tmp/zlg-smoke.log.zlg
cargo run -- grep 'error|failed' /tmp/zlg-smoke.log.zlg
cargo run -- grep -o 'key="[^"]+"' /tmp/zlg-smoke.log.zlg
cargo run -- grep -n 'failed password' /tmp/zlg-smoke.log.zlg
cargo run -- grep -P '(?<=key=")[^"]+' /tmp/zlg-smoke.log.zlg
```

## Phase 0h proof-prep helpers

This checkpoint includes small proof-prep helpers:

```bash
scripts/phase0h_smoke.sh
scripts/phase0h_correctness_check.sh
python3 tools/phase0h_bench.py --quick
```

These scripts use temporary directories and should not commit generated `.zlg`, `.gz`, `target/`, or temporary files.


## Phase 0i pre-bench readiness

The checkpoint includes a one-command pre-bench readiness pass:

```bash
scripts/phase0i_prebench_once.sh
```

This validates the Rust build, smoke tests, correctness checks, all chunk policies, a repeatable pre-bench harness, and artifact hygiene before full benchmark work.
