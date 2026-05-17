# Phase 2b CLI Roadmap and Checklist

This document records the Phase 2b CLI plan and completion status. Phase 2 CLI validation passed at commit 6eab4a3. Active next-phase work is tracked in `docs/PHASE2C_METADATA_AND_PERF_SMOKE.md`.

## Current validated base

Use the current repository checkout as authoritative. The production compression/search core is locked and should not be reopened during CLI work.

Validated core stack:

```text
fixed-lines8192-cap8m
+ mesh-bigram ZBM1 v2
+ combined-bitset-seen
+ current reserve behavior
+ zstd::bulk::Compressor
+ streaming grep
+ summary-first skip
+ memchr line splitting
+ Rust regex default
+ PCRE2 mode
+ literal prefiltering
+ positive-lookbehind fast path
+ head-style early stop
```

Validated compression modes:

```text
none     = uncompressed payloads inside .zlg chunks
fast     = zstd level 3
standard = zstd level 6
best     = zstd level 8
```

Default compression mode:

```text
standard
```

## Licensing and metadata

License decision:

```text
MIT OR Apache-2.0
```

Author/contact:

```text
Richard S. Westmoreland

dev@rswestmore.land
```

Checklist:

- [x] Update `Cargo.toml` license expression to `MIT OR Apache-2.0`.
- [x] Add author metadata in `Cargo.toml`.
- [x] Add `LICENSE`, `LICENSE-MIT`, and `LICENSE-APACHE`.
- [x] Update README with author/contact/license.
- [x] Ensure `zlg version` reports author/contact in long output once implemented.

## Global CLI rules

- [x] Use subcommands.
- [x] Use lowercase short options only.
- [x] Use lowercase long options only.
- [x] Avoid behavioral aliases.
- [x] Support normal help conventions: `zlg help`, `zlg --help`, `zlg <command> --help`.
- [x] Support `zlg version` and `zlg --version`.
- [x] Do not expose internal benchmark profiles in normal help output.
- [x] Do not expose the full numeric compression-level range in the normal CLI.
- [x] Use `--mode` for compression mode.
- [x] Do not use `--preset` in the final CLI.

## Planned command set

- [x] `zlg help`
- [x] `zlg version`
- [x] `zlg compress`
- [x] `zlg decompress`
- [x] `zlg cat`
- [x] `zlg grep`
- [x] `zlg head`
- [x] `zlg tail`
- [x] `zlg test`
- [x] `zlg info`
- [x] `zlg stats`
- [ ] `zlg top`
- [x] `zlg convert`

Open for later discussion:

- [ ] `zlg sort`
- [ ] `zlg uniq`

## Command plans

### help

Purpose: discoverable help.

Forms:

```text
zlg help
zlg help grep
zlg <command> --help
```

Checklist:

- [x] General command list.
- [x] Command-specific help.
- [ ] Short examples.
- [x] Hide production-internal options.

### version

Purpose: version and build metadata.

Forms:

```text
zlg version
zlg --version
zlg version --long
```

Short output should stay concise. Long output may include:

- zlg version
- author/contact
- license
- format version
- default compression mode
- default chunk policy
- default summary type
- build commit/date if available

### compress

Purpose: create `.zlg` archives.

Examples:

```text
zlg compress app.log
zlg compress app.log -o app.zlg
zlg compress app.log --mode fast
zlg compress app.log --mode standard
zlg compress app.log --mode best
zlg compress app.log --mode none
```

Options:

- [x] `-o`, `--output <path>`
- [x] `--mode <none|fast|standard|best>`
- [ ] `-f`, `--force`
- [ ] `--stats`
- [ ] `--json` with stats, if implemented
- [ ] `-q`, `--quiet`

Remove or hide from final normal CLI:

- [x] public numeric `--level` removed from normal CLI
- [x] `--preset` removed from normal CLI
- [x] public `--build-profile` hidden from normal help
- [x] public `--summary-mode` hidden from normal help
- [x] public `--chunk-policy` hidden from normal help

### decompress

Purpose: restore original bytes.

Examples:

```text
zlg decompress app.zlg -o app.log
zlg decompress app.zlg --stdout
```

Options:

- [ ] `-o`, `--output <path>`
- [ ] `-c`, `--stdout`
- [ ] `-f`, `--force`
- [ ] `-q`, `--quiet`

### cat

Purpose: write decompressed bytes to stdout.

Example:

```text
zlg cat app.zlg > app.log
```

Checklist:

- [ ] Output raw decompressed bytes only.
- [ ] No metadata by default.
- [x] Decode errors should fail cleanly.

### grep

Purpose: accelerated search.

Examples:

```text
zlg grep "error" app.zlg
zlg grep -i "failed login" auth.zlg
zlg grep -f "literal text" app.zlg
zlg grep -p '(?<=user=)[^ ]+' auth.zlg
zlg grep -o 'src_ip=[0-9.]+' firewall.zlg
zlg grep --head 10 "error" app.zlg
```

Options:

- [x] `-i`, `--ignore-case`
- [x] `-f`, `--fixed`
- [x] `-p`, `--pcre2`
- [x] `-o`, `--only-matching`
- [x] `-n`, `--line-number`
- [x] `-c`, `--count`
- [x] `-l`, `--files-with-matches`
- [ ] `-q`, `--quiet`
- [x] `--head <n>`

Remove/replace:

- [x] Replace `-P` with `-p`, `--pcre2`.
- [x] Replace `-F` with `-f`, `--fixed`.
- [x] Remove `--max-count`; use `--head` as the stop option.

### head

Purpose: first N decompressed lines.

Options:

- [x] `-n`, `--lines <n>`, default 10.
- [ ] Multi-file behavior later.

### tail

Purpose: last N decompressed lines using line-count metadata.

Options:

- [x] `-n`, `--lines <n>`, default 10.

Planner:

```text
read directory
walk chunks backward summing line_count
select enough chunks
decode selected chunks forward
emit last N lines
```

### test

Purpose: archive integrity check.

Options:

- [ ] `--full`
- [ ] `-q`, `--quiet`

### info

Purpose: human metadata.

Options:

- [x] `--json`
- [ ] `--chunks`

### stats

Purpose: component stats and wc-style counts.

Options:

- [x] `--json`
- [ ] `--chunks`

Stats should include:

- line count
- uncompressed byte count
- compressed payload bytes
- summary bytes
- total archive bytes
- chunk count
- compression ratio
- summary ratio
- max/average chunk bytes
- max/average chunk lines

### top

Purpose: search/extract/count/sort top values.

Examples:

```text
zlg top auth.zlg --where "failed login" --extract 'user=([^ ]+)' --limit 10
zlg top firewall.zlg --extract 'src_ip=([0-9.]+)' --limit 10
```

Options:

- [ ] `--where <pattern>`
- [ ] `--extract <regex>`
- [ ] `-p`, `--pcre2`
- [ ] `-i`, `--ignore-case`
- [ ] `-f`, `--fixed` for `--where`
- [ ] `--limit <n>`, default 10
- [ ] `--sort <count|value>`
- [ ] `--min-count <n>`
- [ ] `--json`

### convert

Purpose: convert already-compressed inputs to `.zlg`. Plain logs should use `zlg compress`.

Initial design:

- [ ] plain input, no new dependency.
- [ ] `.zst` input using existing zstd dependency.
- [ ] `.gz` input only after measuring binary-size impact of `flate2`.
- [ ] Defer `.bz2` and `.xz` by default.

Options:

- [x] `-o`, `--output <path>`
- [x] `--mode <none|fast|standard|best>`
- [ ] `-f`, `--force`
- [ ] `--from <plain|gz|zst>`
- [ ] `--stats`
- [ ] `--json`

## Metadata work for head/tail/stats

Add or confirm archive-level metadata:

- [ ] format version
- [ ] zlg version used to create archive
- [ ] compression mode
- [ ] zstd level or no-compression marker
- [ ] chunk policy id
- [ ] summary kind/version
- [ ] chunk count
- [ ] total lines
- [ ] total uncompressed bytes
- [ ] total compressed payload bytes
- [ ] total summary bytes
- [ ] total archive bytes

Add or confirm per-chunk metadata:

- [ ] compressed offset
- [ ] compressed length
- [ ] summary length
- [ ] uncompressed bytes
- [ ] line count
- [ ] crc32
- [ ] flags

Line-count semantics:

- [ ] A final unterminated non-empty line counts as one line.
- [ ] Empty files have zero lines.
- [ ] Tests must cover chunk boundaries and unterminated final lines.

## Sort and uniq discussion

Do not implement broad Unix `sort` or `uniq` clones yet.

Potential direction:

- [ ] Use `top` for extract/count/sort descending.
- [ ] Consider `top --all --sort value` for unique extracted values.
- [ ] Consider a future line-level unique/count mode only after top is implemented.

## Parallel/async future discussion

Do not implement async/parallel in Phase 2b.

Carry forward for later:

- [ ] bounded build pipeline: chunk -> summary/compress -> ordered write.
- [ ] bounded search pipeline: summary scan -> candidate decode -> ordered output.
- [ ] queue depth must be small and memory capped.
- [ ] preserve deterministic output order unless explicitly changed later.

## Validation guardrails for next implementation phase

Required after code changes:

```text
cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
scripts/phase0h_smoke.sh
scripts/phase0h_correctness_check.sh
scripts/phase0i_policy_matrix_check.sh
scripts/phase0m_selector_smoke.sh
scripts/phase0i_artifact_hygiene_check.sh
```

Do not commit:

- `target/`
- temp directories
- generated `.zlg`, `.gz`, `.zst`
- generated corpora/logs
- binary fixtures
- PNGs or images

## Phase 2 implementation status update

The current Phase 2m prep adds helper-based `convert` for already-compressed `.zst`, `.gz`, `.bz2`, and `.xz` inputs. `top` remains deferred. The file format remains experimental and should not be frozen in this phase.
