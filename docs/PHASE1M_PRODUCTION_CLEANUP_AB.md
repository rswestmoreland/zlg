# Phase 1m - Production Cleanup and Controlled A/B Validation

## Scope

Phase 1m corrects the missed cleanup from Phase 1l and validates the final
stack against a Phase 1k baseline in the same benchmark run.

The production stack remains:

```text
fixed-lines8192 with 8 MiB byte cap
+ mesh-bigram ZBM1 v2
+ zstd::bulk::Compressor
+ combined-bitset-seen
+ streaming grep
+ Rust regex default
+ PCRE2 for -P
+ literal prefiltering
+ positive-lookbehind fast path
+ --head / --max-count early stop
```

Compression presets:

```text
fast     = zstd level 3
standard = zstd level 6
best     = zstd level 8
```

## Cleanup performed in the prep

- Normal CLI build-profile surface is reduced to the selected
  `combined-bitset-seen` path.
- The build-profile argument is hidden from normal help output.
- Summary mode and chunk policy arguments are hidden from normal help output.
- `--preset fast|standard|best` is added for the final compression design.
- `--level` remains as an advanced override, but cannot be combined with
  `--preset`.
- The writer path is simplified to the selected mesh-bigram builder.
- Abandoned external sort crates remain removed.

Historical encoder helper functions may remain in source until Codex validates
whether they can be safely removed without disrupting tests or previous support
scripts. They are not reachable through the normal production CLI surface.

## A/B benchmark design

The benchmark builds two release binaries in temporary target directories:

```text
baseline_phase1k:
  source snapshot from tools/phase1m_baseline_src/src

final_phase1m:
  current cleaned source checkout
```

The benchmark compares:

- compression build speed
- CPU time
- RSS
- output size
- round-trip correctness
- search speed and RSS for selective/common/regex/PCRE2/head queries

The benchmark alternates command order by repeat to reduce order bias.

## Cache control

The benchmark attempts to reduce OS cache skew before every measured command:

1. If running as root and `/proc/sys/vm/drop_caches` is writable, it runs
   `sync` and writes `3` to `drop_caches`.
2. Otherwise it reads a temporary cache-buster file before each measured
   command.

The selected cache-control method is recorded in the CSV and report. This does
not claim perfect cache isolation on all systems, but it avoids a fixed warm-cache
ordering bias.

## Expected outputs

```text
validation_results/phase1m_cleanup_ab_bench.csv
validation_results/phase1m_cleanup_ab_search.csv
validation_results/phase1m_cleanup_ab_summary.csv
validation_results/phase1m_cleanup_ab_report.md
validation_results/phase1m_cleanup_ab_once.txt
```

## Success criteria

- fmt/check/test/clippy/release build pass.
- Phase 0 smoke/correctness/policy/selector checks pass.
- Phase 1m A/B benchmark passes.
- RSS and CPU are captured for every measured row.
- Compression round trips pass for every row.
- Search outputs match between baseline and final for every query.
- No build/temp/generated archive/corpus/binary artifacts are committed.
