# Phase 2d Benchmark Reliability, Head, and Tail

Phase 2d follows the validated Phase 2c metadata implementation at commit `d1179fc`.

## Purpose

Phase 2d has three goals:

1. Fix benchmark CPU/RSS measurement reliability.
2. Use a larger needle-in-haystack corpus to better showcase zlg chunk skipping.
3. Benchmark `zlg head` and `zlg tail` against plain log and gzip equivalents.

## Measurement reliability

The Phase 2c smoke bench produced useful wall-time and storage data, but CPU and RSS fields were blank. Phase 2d fixes this by using Python `os.wait4()` resource accounting as the primary measurement source.

The policy is documented in:

```text
docs/BENCHMARK_MEASUREMENT_RELIABILITY.md
```

Benchmark CSV rows must include wall time, user CPU, system CPU, CPU percent, and max RSS. Missing resource metrics are treated as invalid unless the script is explicitly run with an allow-missing option and the validation log explains why.

## Phase 2d bench script

Script:

```text
scripts/phase2d_perf_head_tail_once.sh
```

Tool:

```text
tools/phase2d_perf_head_tail_bench.py
```

Expected compact outputs:

```text
validation_results/phase2d_perf_head_tail_smoke.csv
validation_results/phase2d_perf_head_tail_smoke.md
validation_results/phase2d_perf_head_tail_smoke_once.txt
```

Generated raw logs, gzip files, zlg archives, and command outputs must stay in temporary directories and must not be committed.

## Compared backends

Search comparisons:

```text
plain_grep = grep on raw log
gzip_zgrep = zgrep on gzip log
zlg = zlg grep on zlg archive
```

Head comparisons:

```text
plain_grep = head on raw log
gzip_zgrep = gzip -dc file.gz | head
zlg = zlg head
```

Tail comparisons:

```text
plain_grep = tail on raw log
gzip_zgrep = gzip -dc file.gz | tail
zlg = zlg tail
```

The backend names remain `plain_grep`, `gzip_zgrep`, and `zlg` for CSV continuity, even when the operation is `head` or `tail`.

## Scenarios

### repeated_regex

A moderate deterministic auth-style log with frequent matches. This tests a dense regex workload where output cost dominates and chunk skipping is not expected to be the main advantage.

Default line count:

```text
120000
```

Search pattern:

```text
status=(failed|denied)
```

### needle_haystack_large

A larger deterministic log with a fixed string appearing exactly once around 80 percent deep into the file. This better showcases summary-first chunk skipping because zlg has many more chunks available to reject before decoding.

Default line count:

```text
1000000
```

Needle position ratio:

```text
0.80
```

## Head and tail checks

The bench compares output hashes across plain, gzip, and zlg for:

```text
search
head
tail
tail_large
```

Defaults:

```text
head -n 10
tail -n 10
tail -n 5000
```

`tail_large` is intended to cross chunk boundaries and exercise zlg's metadata-backed tail path more meaningfully than a tiny last-10-lines test.

## Required validation

After Phase 2d implementation, run:

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
```

The Phase 2d bench should fail rather than silently producing blank CPU/RSS fields.
