# Phase 2g Archive Hardening and Test Output

Phase 2g is a narrow hardening pass layered on top of the Phase 2e/2f CLI maturity work. It keeps the locked compression/search core unchanged and does not freeze the file format.

## Goals

1. Make `zlg test` more useful for humans and scripts.
2. Ensure `zlg test` validates both payload decode and seekable metadata for file-backed inputs.
3. Add focused corruption checks for malformed archives.
4. Keep generated corrupt archives out of the repository.

## `zlg test` behavior

Normal text output is human-readable:

```text
zlg test
========
status: ok
chunks: 16
lines: 120000
uncompressed-bytes: 15692090
metadata: checked
```

Script-friendly output is available with JSON:

```text
zlg test --json archive.zlg
```

Quiet mode is available for exit-code-only checks:

```text
zlg test --quiet archive.zlg
```

`--json` and `--quiet` intentionally conflict because one asks for structured output and the other asks for no output.

For file-backed input, `zlg test` now reads and validates archive metadata first, then decodes all chunks and verifies the decoded chunk, line, and byte totals match the metadata totals. For stdin, `zlg test` uses the streaming reader and reports `metadata: streamed` because seekable footer/directory validation is not available.

## Archive corruption probe

Phase 2g adds:

```text
tools/phase2g_archive_hardening_probe.py
scripts/phase2g_archive_hardening_once.sh
```

The probe builds temporary valid archives, mutates copies, and confirms commands reject malformed inputs. It covers cases such as:

- non-zlg input
- bad global magic
- unsupported format version
- bad footer magic
- bad directory magic
- directory/footer count mismatch
- payload bounds outside the archive
- chunk header/directory mismatch
- CRC mismatch
- truncated summary or payload

The probe writes compact results only:

```text
validation_results/phase2g_archive_hardening.csv
validation_results/phase2g_archive_hardening.md
```

Temporary raw logs and corrupt archives are generated under a temporary directory and must not be committed.

## Validation command

```text
bash scripts/phase2g_archive_hardening_once.sh
```

This should run after the normal Rust validation and after the existing Phase 2 CLI smoke checks.

## Guardrails

- Do not change mesh-bigram ZBM1 v2.
- Do not change the locked production compression/search core.
- Do not freeze the file format.
- Do not add new builder profiles or experimental candidates.
- Do not commit generated raw logs, `.zlg` archives, gzip files, corrupt test files, or binary artifacts.
