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
- Use `--head` as the stop option; do not carry both `--head` and `--max-count`.

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
top
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

## Head/tail metadata

Efficient `tail` requires line counts in the directory or metadata associated with chunks.

Store:

- per-chunk line count
- per-chunk uncompressed bytes
- archive total lines
- archive total uncompressed bytes

Line-count semantics:

- final unterminated non-empty line counts as one line.
- empty archive counts as zero lines.

## Convert scope

Initial convert support should stay lean.

Recommended order:

1. plain input
2. `.zst` input using existing zstd dependency
3. `.gz` input after measuring binary-size impact

Defer by default:

- `.bz2`
- `.xz`

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
