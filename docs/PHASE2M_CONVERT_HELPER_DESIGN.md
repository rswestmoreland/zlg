# Phase 2m convert helper design

Phase 2m starts `zlg convert` as a lean bridge from already-compressed log files into `.zlg` archives.

## Command shape

```text
zlg convert <compressed-input> [output.zlg]
```

Rules:

- `convert` is for already-compressed input only.
- Plain logs should use `zlg compress`.
- There is no `-o` or `--output` option.
- If output is omitted, zlg removes the last extension and adds `.zlg`.
- `--mode <none|fast|standard|best>` controls the output `.zlg` archive.
- `--force` is required to overwrite an existing output file.

Examples:

```text
zlg convert app.log.zst
zlg convert app.log.gz
zlg convert app.log.bz2
zlg convert app.log.xz
zlg convert app.log.gz app-archive.zlg --mode fast
zlg convert app.log.xz app-archive.zlg --force
```

## Decoder strategy

The first implementation favors binary size and maintainability over embedded support for every codec.

| Input | Strategy | New Cargo dependency | Runtime helper |
|---|---|---:|---|
| `.zst` | internal zstd decoder | no | no |
| `.gz` | helper pipe | no | `gzip` |
| `.bz2` | helper pipe | no | `bzip2` |
| `.xz` | helper pipe | no | `xz` |

Helpers are invoked directly with `std::process::Command`; no shell is used.

## Missing helper behavior

If a helper is missing, `zlg convert` should fail clearly instead of silently falling back or producing partial output. `.zst` is not a helper path and does not require the external `zstd` command.

Example:

```text
app.log.xz conversion requires the xz command in PATH
```

## Failure cleanup

External helper paths write to a temporary `.zlg` path first. If zlg fails while consuming helper output, it kills/waits for the helper and removes the temporary output before returning the error. The final output path is only installed after a successful conversion.

## Why not embed codecs yet

Embedding gzip, bzip2, or xz decoders would add crate and binary-size overhead. The helper model gives immediate support for common Linux compressed logs while keeping the zlg binary lean.

Later work can measure embedded decoder overhead for:

- `flate2` for gzip
- `bzip2` crate for bzip2
- pure Rust xz/LZMA candidates or `xz2` as a reference

## Deferred

- tar/archive container handling
- brotli/snappy/lz4 conversion
- embedded gzip/bzip2/xz decoders
- shell-based helper invocation
- additional helper formats beyond gzip, bzip2, and xz
