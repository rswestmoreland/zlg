# Phase 0h Correctness and Benchmark Prep

## Purpose

Phase 0h prepares a repeatable proof harness for `zlg` without changing the core runtime implementation.

The immediate goals are:

1. Preserve the validated Phase 0g baseline.
2. Add repeatable smoke checks.
3. Add correctness comparison checks against plain grep behavior where possible.
4. Add a lightweight benchmark-prep harness.
5. Keep artifacts small and text-only.

## Acceptance criteria

Phase 0h is acceptable when:

```text
cargo fmt --check passes
cargo check passes
cargo test passes
cargo clippy --all-targets --all-features -- -D warnings passes
cargo build --release passes
scripts/phase0h_smoke.sh passes
scripts/phase0h_correctness_check.sh passes
python3 tools/phase0h_bench.py --quick completes or reports missing external tools clearly
no build artifacts are committed
no temp files are committed
no .zlg files are committed
```

## Required scripts

```text
scripts/phase0h_smoke.sh
scripts/phase0h_correctness_check.sh
tools/phase0h_bench.py
```

## Script behavior

Scripts must:

```text
use temporary directories
remove temporary files on exit
avoid writing binary outputs into the repo
write optional small text results under validation_results/
fail clearly on mismatched output
```

## Correctness focus

Initial correctness comparisons should cover:

```text
cat/decompress round trip
regex line matching
fixed-string line matching
-o extraction
-n line numbers
-i ignore case
-c counts
-v invert match
-P only-matching extraction for fancy-regex
```

## Benchmark focus

The first benchmark harness is not the final proof. It should prepare CSV measurements for:

```text
compress wall time
compressed size
cat wall time
grep wall time
first smoke-level correctness before timing
candidate chunk policy
pattern
engine mode
```

## External baseline tools

Use these when available:

```text
gzip
gunzip
zgrep
grep
```

Optional tools may be detected and skipped if missing:

```text
rg
zstd
zstdcat
```

## Non-goals

Do not attempt to prove final performance in Phase 0h.

Do not freeze the format.

Do not add async/concurrency.

Do not make broad source refactors.
