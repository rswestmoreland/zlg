# Phase 2h-2l Final CLI Maturity Prep

This prep package closes the remaining Phase 2 maturity tasks before Codex
validation.

## Scope

The scope is deliberately narrow:

- Add `zlg grep --strict` as an opt-in integrity-before-output mode.
- Keep default `zlg grep` streaming for low latency and lower memory use.
- Add repeated-median benchmark support for the existing fast-vs-standard bench.
- Improve `zlg info` text output so it is more readable.
- Expand `zlg stats` component percentages while keeping `--json` script-friendly.
- Strengthen smoke coverage for head/tail edge cases.
- Extend archive hardening probes to cover strict grep on valid and corrupt archives.

## Strict grep behavior

Default grep behavior remains optimized for normal use:

```text
zlg grep PATTERN file.zlg
```

Default grep streams candidate chunk output as it decodes. If the CRC check fails
later, the command reports the error and exits nonzero. This matches the usual
streaming tradeoff used by compressed tools: low latency first, error once
integrity failure is known.

Strict grep is opt-in:

```text
zlg grep --strict PATTERN file.zlg
```

`--strict` verifies each candidate chunk before emitting matches from that
chunk. It does not preverify the entire archive before all output. Summary-first
skip still applies, so chunks rejected by the search summary are not decoded.

The chunk CRC remains over the uncompressed chunk bytes.

## Repeated median benchmark

Phase 2i adds a wrapper around the Phase 2e benchmark:

```text
scripts/phase2i_repeated_median_once.sh
```

It writes:

```text
validation_results/phase2i_repeated_median_smoke.csv
validation_results/phase2i_repeated_median_smoke.md
```

The wrapper runs the Phase 2e matrix repeatedly and adds median rows for wall
time, user CPU, system CPU, CPU percent, and max RSS. It keeps per-run rows so
regressions can be inspected.

## Info and stats polish

`zlg info` now uses a sectioned report:

```text
zlg archive info
================

Format
Archive
Layout
```

`zlg stats` keeps the existing screenshot-friendly sections and adds component
shares:

```text
Payload share
Summary share
Directory share
Metadata share
Other overhead share
```

JSON output remains available for scripts.

## Head/tail maturity

The Phase 2 CLI smoke now verifies additional edge cases:

- `head -n 0`
- `tail -n 0`
- `n > total lines`
- empty input
- single-line input
- final line without a trailing newline
- all compression modes in the normal loop

## Deferred

Still deferred:

- `top`
- `convert`
- mode renaming
- default mode change
- file format freeze
- async worker pools
- `.bz2` and `.xz` support
