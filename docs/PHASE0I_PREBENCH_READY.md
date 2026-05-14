# Phase 0i Pre-Bench Ready Checkpoint

## Purpose

This checkpoint fills the gap between the Phase 0h proof-prep zip and a full benchmark run.

It adds one orchestrated pre-bench pass that Codex can run once before we move to full benches.

## Why this step exists

Before full benches, we need to prove that:

- The source still passes the Rust validation flow.
- Smoke tests still pass.
- Correctness checks still match grep behavior for supported modes.
- Every chunk policy can round-trip and search correctly on the checked-in fixture.
- The benchmark harness can generate repeatable CSV/Markdown/environment reports.
- Generated corpora and compressed outputs stay in temp directories.
- No build/temp/binary/compressed artifacts are committed.

## New files

```text
scripts/phase0i_prebench_once.sh
scripts/phase0i_policy_matrix_check.sh
scripts/phase0i_artifact_hygiene_check.sh
docs/PHASE0I_PREBENCH_READY.md
docs/CODEX_PHASE0I_PREBENCH_PROMPT.md
```

The existing benchmark harness was strengthened:

```text
tools/phase0h_bench.py
```

It now supports:

```text
--mode quick
--mode prebench
--mode full
--lines
--repeats
--output
--summary
--env-report
--keep-temp
```

## Recommended Codex command

```bash
scripts/phase0i_prebench_once.sh
```

## Expected output artifacts

Small text/CSV/Markdown reports under:

```text
validation_results/
```

Expected report files include:

```text
validation_results/phase0i_prebench_once.txt
validation_results/phase0h_prebench_bench.csv
validation_results/phase0h_prebench_bench_summary.md
validation_results/phase0h_prebench_env.txt
```

## Scope guardrail

This is still not the final benchmark proof.

Do not add async, PCRE2, multiline regex, timestamp sidecars, major format changes, or performance tuning in this checkpoint unless needed to fix validation correctness.
