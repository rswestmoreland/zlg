# Phase 2e Options, Stats, and Fast Mode Bench

Phase 2e follows the validated Phase 2d benchmark reliability pass at commit `2c5b8c8`.

## Purpose

Phase 2e continues CLI maturity without changing the locked production core.

Goals:

1. Make `zlg stats` pleasant to read in terminal output and screenshots.
2. Keep `zlg stats --json` script-friendly.
3. Extend the performance smoke bench to compare `--mode fast` and `--mode standard`.
4. Keep head/tail/search parity checks across plain, gzip, zlg fast, and zlg standard.

## Stats output policy

`zlg stats` is not intended to mimic Unix `wc` formatting. The normal text output should be readable and screenshot-friendly, with grouped sections such as:

```text
zlg archive stats
=================

Content
  Lines                        1,000,000
  Uncompressed bytes           126,450,608 B (120.59 MiB)
  Chunks                       123

Storage
  Archive bytes                12,945,933 B (12.35 MiB)
  Payload bytes                10,000,000 B (9.54 MiB)
  Summary bytes                2,000,000 B (1.91 MiB)
  Compression ratio            9.77x

Format
  Compression mode             standard
  Chunk policy                 fixed-lines8192-cap8m
  Metadata source              seekable
```

`zlg stats --json` remains the stable ingestion path for scripts and should include raw numeric fields for lines, bytes, chunks, component accounting, compression ratio, archive/raw percent, mode, policy, and metadata source.

## Fast mode comparison

The Phase 2d bench showed strong search/head/tail behavior but standard mode was slower to build than gzip on the large needle corpus. Static source review confirmed that the approved optimized build stack was carried forward, so Phase 2e does not add a build-regression A/B bench.

Instead, Phase 2e adds a direct comparison of:

```text
gzip -6
zlg --mode fast
zlg --mode standard
```

This helps determine whether fast mode approaches gzip build-time parity while preserving useful storage and search behavior. The default remains `standard` for now.

## Script

```text
scripts/phase2e_perf_modes_head_tail_once.sh
```

Tool:

```text
tools/phase2e_perf_modes_head_tail_bench.py
```

Expected outputs:

```text
validation_results/phase2e_perf_modes_head_tail_smoke.csv
validation_results/phase2e_perf_modes_head_tail_smoke.md
validation_results/phase2e_perf_modes_head_tail_smoke_once.txt
```

Generated logs, gzip files, zlg archives, and command outputs must stay in temporary directories and must not be committed.

## Required validation

```text
cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
bash scripts/phase0h_smoke.sh
bash scripts/phase0h_correctness_check.sh
bash scripts/phase0i_policy_matrix_check.sh
bash scripts/phase0m_selector_smoke.sh
bash scripts/phase0i_artifact_hygiene_check.sh
bash scripts/phase2_cli_smoke.sh
bash scripts/phase2d_perf_head_tail_once.sh
bash scripts/phase2e_perf_modes_head_tail_once.sh
```

The Phase 2e bench should fail rather than silently producing blank CPU/RSS fields.

## Additional pre-validation safety work

Before the next Codex validation pass, the prep package also adds long-only `--force` output overwrite safety. This is intentionally separate from the grep `-f` fixed-string option.

Expected behavior:

- `zlg compress -o existing.zlg` fails unless `--force` is provided.
- `zlg cat -o existing.log` fails unless `--force` is provided.
- `zlg decompress -o existing.log` fails unless `--force` is provided.

The Phase 2 CLI smoke script checks this behavior so accidental truncation does not become the default user experience.
