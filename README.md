# zlg Prototype

`zlg` is a prototype single-binary Linux CLI utility and `.zlg` file format for compressing, decompressing, catting, and searching plaintext logs.

This checkpoint is intended for Codex/Rust validation and benchmark iteration. The selected production candidate stack is fixed-lines8192 with an 8 MiB byte cap + mesh-bigram ZBM1 v2 + zstd::bulk::Compressor + combined-bitset-seen + streaming grep.

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
- finalized fixed-lines8192 chunking with an 8 MiB byte cap
- finalized mesh-bigram summary builder path

## Important status

This is not a stable file format.

The current file format is still experimental and must not be frozen yet. The current default compression path is fixed-lines8192 with an 8 MiB byte cap + mesh-bigram + combined-bitset-seen at the standard preset, zstd level 6.


## Active production stack

The selected strategy is:

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

`combined-bitset-seen` is the selected production builder. Earlier sort, hash, sparse, trie, paged, and lower-only builder experiments are not active production candidates and are hidden or removed from the normal CLI surface.

Compression presets are:

```text
fast     = zstd level 3
standard = zstd level 6
best     = zstd level 8
```

The standard/default preset is zstd level 6. Dropped external sort experiments no longer require `rdxsort` or `rdst` dependencies.

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
