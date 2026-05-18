# Phase 2f CLI Safety and Hardening

Phase 2f is a small safety pass layered on top of the Phase 2e option and benchmark work. It keeps the locked compression/search core unchanged.

## Goals

1. Refuse accidental output overwrite by default.
2. Add `-y`, `--force` for intentional replacement.
3. Keep `-f` reserved for `zlg grep --fixed`.
4. Strengthen smoke coverage for overwrite behavior.
5. Strengthen smoke coverage for invalid archive rejection.

## Output overwrite policy

Commands that can write an output file should create the file only when it does not already exist. If the path exists, the command should fail with a message that points the user to `--force`.

Commands covered in this pass:

```text
zlg compress -o <path>
zlg cat -o <path>
zlg decompress -o <path>
```

The `--force` option uses `-y, --force`. This avoids ambiguity with `zlg grep -f`, which means fixed-string search.

## Smoke checks

The Phase 2 CLI smoke script should verify:

- `zlg compress --help` includes `--force`.
- `zlg cat --help` includes `--force`.
- `zlg compress` refuses to overwrite an existing archive without `--force`.
- `zlg compress --force` overwrites intentionally.
- `zlg cat -o` refuses to overwrite without `--force`.
- `zlg cat -o --force` overwrites intentionally.
- `zlg test` rejects a non-zlg input file.

## Deferred hardening

Additional malformed archive tests remain useful after this pass:

- bad global magic
- truncated chunk header
- truncated payload
- bad footer magic
- bad directory magic
- directory count mismatch
- chunk offset outside the file
- CRC mismatch

Those are good candidates for a focused malformed-archive unit/integration test pass.
