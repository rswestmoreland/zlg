# CLI Design Decisions for Phase 2

This document records the CLI decisions made after the production core was locked.

## Terminology

Use `compression mode`, not `preset`.

Compression modes:

```text
none
fast
standard
best
```

Mode mapping:

```text
none     = no zstd compression, payloads stored inside .zlg chunks
fast     = zstd level 3
standard = zstd level 6
best     = zstd level 8
```

The default mode is `standard`.

## Option style

- Short options must be lowercase.
- Long options must be lowercase.
- Avoid command and option aliases.
- Do not use uppercase feature flags.
- Use `-p`, `--pcre2` instead of `-P`.
- Use `-f`, `--fixed` instead of `-F`.
- Use `-m`, `--head` as the stop option; do not carry both `--head` and `--max-count`.
- Every public option should have a lowercase short form and lowercase long form where practical. Use `-y`, `--force` for intentional output overwrite. Do not use short `-f` for force because `grep -f` is already locked for fixed-string search.

## Command style

Subcommands are the selected command model.

Commands to include:

```text
help
version
compress
decompress
cat
grep
head
tail
test
info
stats
convert
```

Sort and uniq remain open design topics. They should not be broad Unix clones without a clear zlg-specific reason.

## Naming

Use `compress` and `decompress` rather than `pack` and `unpack` for now.

Reason: `.zlg` is currently a compressed searchable log format, not a multi-file archive/package format. If zlg later becomes a multi-file container, `pack` and `unpack` can be revisited.

## License and author

License:

```text
MIT OR Apache-2.0
```

Author/contact:

```text
Richard S. Westmoreland

dev@rswestmore.land
```

## Phase 2 validation status

The Phase 2 CLI validation/fix pass at commit 6eab4a3 passed the required Rust validation flow and Phase 2 CLI smoke script. Phase 2c builds on that checkpoint.

## Head/tail metadata

Efficient `tail` requires line counts in the directory or metadata associated with chunks. Phase 2c uses the existing footer/directory metadata for file-backed `tail`, `info`, and `stats`. Phase 2e keeps `stats` as a zlg-specific archive report rather than wc-style output. The safety pass refuses output overwrite by default and uses `-y`, `--force` for intentional replacement. Phase 2g adds `zlg test --json` and `zlg test --quiet`, and makes file-backed `zlg test` validate metadata totals against decoded totals.

Store:

- per-chunk line count
- per-chunk uncompressed bytes
- archive total lines
- archive total uncompressed bytes

Line-count semantics:

- final unterminated non-empty line counts as one line.
- empty archive counts as zero lines.

## Convert scope

Initial convert support should stay lean and should focus only on already-compressed inputs. Plain logs should use `zlg compress`.

Command shape:

```text
zlg convert <compressed-input> [output.zlg]
```

Rules:

- no `-o` or `--output` option
- omitted output removes the last extension and adds `.zlg`
- reuse `--mode` for output compression mode
- reuse `-y`, `--force` for intentional overwrite
- reject plain logs with a message pointing users to `zlg compress`
- do not invoke helpers through a shell

Initial decoder strategy:

- `.zst`: internal zstd decoder already present in zlg
- `.gz`: external `gzip -dc` helper
- `.bz2`: external `bzip2 -dc` helper
- `.xz`: external `xz -dc` helper

The helper-based approach intentionally avoids new codec crates and keeps binary-size growth near zero. If helper availability is a problem, embedded decoder crates can be measured later.

## Final core must not drift

Do not reopen these decisions during CLI work:

```text
fixed-lines8192-cap8m
mesh-bigram ZBM1 v2
combined-bitset-seen
current reserve behavior
zstd::bulk::Compressor
fast/standard/best levels 3/6/8
summary-first search skip
memchr line splitting
```


## Test command output

`zlg test` should be useful for both humans and scripts. Normal output is readable text, `--json` is for scripted validation, and `--quiet` is for exit-code-only checks. `--json` and `--quiet` conflict by design. For file-backed inputs, `zlg test` should validate both the seekable metadata and the decoded chunk payloads. For stdin, it should fall back to streaming validation.


## Phase 2n extract/top design

- Use `-e`, `--extract` instead of `-o`, `--only-matching`.
- Use `-t`, `--top` for top aggregation of extracted matches.
- `--top` requires `-e`, `--extract`.
- Use `-l`, `--limit` for number of top rows, default 20.
- Use `-a`, `--cap` for maximum distinct extracted values, default 100000. If exceeded, exit with an error and emit no top results.
- Use `-r`, `--truncate` for maximum stored/displayed bytes per extracted value, default 1000.
- Use `-j`, `--json` for top JSON output.
- Use `-g`, `--paths` instead of `--files-with-matches`.
- Do not implement parser-like top lines, top tokens, or top fields. This phase is extraction aggregation only.
- A standalone `zlg top` remains deferred.

## Phase 2h-2l additions

- Use `-s`, `--strict` for grep candidate-chunk verification before output.
- Default grep remains streaming and low-latency.
- The chunk CRC is over uncompressed chunk bytes.
- `zlg info` and `zlg stats` should use sectioned, screenshot-friendly text output plus JSON for scripts.
- Benchmarks should include repeated median support before default-mode decisions.
- Head/tail smoke coverage should include zero lines, over-large counts, empty input, single-line input, and final-line-without-newline cases.


## Future grep pipeline cleanup

Phase 2n intentionally prioritized validated behavior over internal refactor. A future cleanup should introduce a `GrepContext` or `GrepPipelineContext` for the grep execution path so helper functions do not keep growing argument lists. The existing `GrepOptions` remains the user-selected option set; the future context should group runtime state.
