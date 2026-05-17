# zlg

`zlg` is a single-binary Linux CLI utility and experimental `.zlg` file format for compressing, decompressing, catting, and searching plaintext logs.

The selected production core is locked. The Phase 2 CLI pass has been validated through commit 6eab4a3, Phase 2c through commit d1179fc, Phase 2d through commit 2c5b8c8, and Phase 2e/2g through commit 3623975. The current pre-validation package finishes Phase 2h-2l maturity work: `zlg grep --strict`, repeated-median benchmarks, polished info/stats output, and stronger head/tail edge coverage. Top and convert remain design/deferred work.

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
- Keep `stats` as a pleasant zlg-specific report, with `--json` for scripts. Do not add a separate `wc` command.
- Refuse to overwrite output files by default; use long-only `--force` when replacement is intentional.
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
- `zlg compress` with `--mode <none|fast|standard|best>` and long-only `--force` for intentional overwrite
- `zlg decompress` with long-only `--force` for intentional overwrite
- `zlg cat` with long-only `--force` for intentional overwrite
- `zlg grep` with lowercase `-f`, `-p`, `--head`, and opt-in `--strict`
- `zlg head`
- `zlg tail` with a seekable metadata path for file inputs
- `zlg test` with readable text output, `--json`, and `--quiet`
- `zlg info` using metadata for file inputs
- `zlg stats` using metadata for file inputs, with readable text output and JSON output

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

## Phase 2c and Phase 2d work

Phase 2c implemented and validated:

- seekable footer/directory metadata reading
- metadata-backed `tail`, `info`, and `stats` for file inputs
- help/version/docs alignment
- a compact performance smoke bench comparing plain `grep`, `zgrep`, and `zlg grep`

Phase 2d implemented and validated:

- reliable CPU/RSS capture using Linux `os.wait4()`
- larger needle-in-haystack search testing
- `head` and `tail` comparisons against raw logs and gzip streams
- stronger output-hash parity checks for head/tail paths

Phase 2e and Phase 2g are validated and Phase 2h-2l prepare the next validation pass:

- screenshot-friendly `zlg stats` text output
- expanded `zlg stats --json` fields
- fast-vs-standard performance comparison against gzip and plain log baselines
- continued search/head/tail/tail_large output parity checks
- output overwrite safety for `compress`, `cat`, and `decompress`
- stronger smoke checks for `--force` and invalid archive rejection
- `zlg test` text/json/quiet output modes
- file-backed `zlg test` metadata totals checked against decoded totals
- archive corruption probe for malformed metadata and payload cases
- `zlg grep --strict` for opt-in candidate-chunk verification before output
- repeated-median benchmark wrapper for fast-vs-standard results
- polished `zlg info` layout and expanded component-share `zlg stats` fields
- stronger `head` and `tail` edge-case smoke coverage

Recommended active documents:

```text
docs/CLI_DESIGN_DECISIONS_PHASE2.md
docs/PHASE2C_METADATA_AND_PERF_SMOKE.md
docs/PHASE2D_BENCH_RELIABILITY_HEAD_TAIL.md
docs/PHASE2E_OPTIONS_STATS_AND_FAST_MODE_BENCH.md
docs/BENCHMARK_MEASUREMENT_RELIABILITY.md
docs/ZLG_NEXT_CHAT_PROMPT_PHASE2E.md
docs/PHASE2F_CLI_SAFETY_AND_HARDENING.md
docs/ZLG_NEXT_CHAT_PROMPT_PHASE2F.md
docs/PHASE2G_ARCHIVE_HARDENING_AND_TEST_OUTPUT.md
docs/ZLG_NEXT_CHAT_PROMPT_PHASE2G.md
docs/PHASE2H_TO_2L_FINAL_CLI_MATURITY.md
docs/ZLG_NEXT_CHAT_PROMPT_PHASE2H_TO_2L.md
```
