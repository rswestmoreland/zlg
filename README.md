# zlg

`zlg` is a single-binary Linux CLI utility and experimental `.zlg` file format for compressing, decompressing, catting, and searching plaintext logs.

The selected production core is locked. The Phase 2 CLI pass has been validated through commit 6eab4a3, and Phase 2c adds seekable metadata use for file-backed info/stats/tail plus a compact performance smoke bench. Top and convert remain design/deferred work.

## Current status

This repository is still pre-1.0. The core compression/search stack has been validated and hardened, and the public CLI is aligned with the Phase 2 lowercase option design. The file format remains experimental and must not be frozen yet.

## Locked production core

```text
fixed-lines8192 with 8 MiB byte cap
+ mesh-bigram ZBM1 v2
+ zstd::bulk::Compressor
+ combined-bitset-seen
+ current reserve behavior
+ streaming grep
+ summary-first skip
+ memchr line splitting
+ Rust regex default
+ PCRE2 for pcre2 mode
+ literal prefiltering
+ positive-lookbehind fast path
+ head-style early stop
```

Compression modes are the user-facing compression choices:

```text
none     = store payloads uncompressed inside .zlg chunks
fast     = zstd level 3
standard = zstd level 6
best     = zstd level 8
```

The default compression mode is `standard`.

## Locked CLI design decisions

- Use subcommands.
- Use lowercase short options only.
- Use lowercase long options only.
- Do not carry uppercase feature flags such as `-P` or `-F`.
- Do not expose the full numeric compression-level range in the normal CLI.
- Use `--mode`, not `--preset`.
- Use `-p`, `--pcre2` for PCRE2 mode.
- Include `head` and `tail` as first-class commands.
- Store and use line-count and byte-count metadata so file-backed `tail`, `info`, and `stats` can be efficient.
- Put wc-style behavior under `stats`, not a separate `wc` command.
- Keep sort/uniq design open, likely through top/extract/count/sort workflows first.
- Keep conversion support lean; plain and `.zst` should be straightforward, `.gz` should be measured for binary-size impact before locking.

## Planned command surface

```text
zlg help
zlg version
zlg compress
zlg decompress
zlg cat
zlg grep
zlg head
zlg tail
zlg test
zlg info
zlg stats
zlg top
zlg convert
```

`sort` and `uniq` remain design topics. They should not become broad clones of Unix `sort` and `uniq` without a clear zlg-specific purpose.

## Current implemented commands

Implemented and validated in Phase 2:

- `zlg help` through the normal clap help command path
- `zlg version`
- `zlg compress` with `--mode <none|fast|standard|best>`
- `zlg decompress`
- `zlg cat`
- `zlg grep` with lowercase `-f`, `-p`, and `--head`
- `zlg head`
- `zlg tail` with a seekable metadata path for file inputs
- `zlg test`
- `zlg info` using metadata for file inputs
- `zlg stats` using metadata for file inputs

Deferred command design topics:

- `zlg top`
- `zlg convert`
- sort/uniq-like workflows

## Author

Richard S. Westmoreland

dev@rswestmore.land

## License

Dual licensed under MIT OR Apache-2.0.

See:

- `LICENSE`
- `LICENSE-MIT`
- `LICENSE-APACHE`

## Validation baseline

The Phase 2 CLI validation/fix pass at commit 6eab4a3 passed:

```text
cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
phase0h smoke
phase0h correctness
phase0i policy matrix
phase0m selector smoke
phase0i artifact hygiene
phase2 CLI smoke
```

## Phase 2c work

Phase 2c focuses on:

- seekable footer/directory metadata reading
- metadata-backed `tail`, `info`, and `stats` for file inputs
- help/version/docs alignment
- a compact performance smoke bench comparing plain `grep`, `zgrep`, and `zlg grep`

Recommended active documents:

```text
docs/CLI_DESIGN_DECISIONS_PHASE2.md
docs/PHASE2C_METADATA_AND_PERF_SMOKE.md
docs/ZLG_NEXT_CHAT_PROMPT_PHASE2C.md
```
