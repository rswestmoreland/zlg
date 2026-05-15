# Phase 0p - Adaptive Weighted K-Gram Planner

## Purpose

Phase 0p treats the k-gram index as a query-planning problem instead of a
static skip filter.

The experiment asks:

- Can DF/IDF-style weights tell us when the index is useful?
- Can graph-edge weights identify rare path fragments?
- Can a cost gate choose full scan when selectors are too common?
- Can an adaptive planner preserve wins for rare selectors without wasting work
  on common selectors?

This phase is offline and does not freeze or change the `.zlg` format.

## Strategies compared

The probe compares:

- `full_scan`
- `best_trigram_1`
- `best_trigram_2`
- `best_edge_1`
- `best_edge_2`
- `best_mixed_2`
- `entropy_gate_2bits`
- `entropy_gate_4bits`
- `adaptive_25pct`
- `adaptive_10pct`
- `cost_gate_75pct`
- `cost_gate_35pct`

## Features collected

For each selector literal, the probe builds candidate features:

- bigrams
- trigrams
- bigram graph edges

Each feature tracks:

- document frequency across blocks
- occurrence count
- IDF-like weighted score
- information bits

## Planner decisions

The probe records planner decisions such as:

- `use_index`
- `full_scan_forced`
- `full_scan_no_selector`
- `full_scan_no_features`
- `full_scan_low_entropy`
- `full_scan_cost_gate`

The goal is not to force index usage. The goal is to learn when index usage is
worth it.

## Expected insight

Common selectors such as `error`, `failed`, and `src_ip` may remain full scan if
they occur in most blocks.

Rare selectors such as exact event IDs, uncommon keys, rare users, and exact
source IPs should prefer index use if their chosen features have high
information value.

## Output artifacts

Phase 0p should produce:

- `validation_results/phase0p_adaptive_planner_bench.csv`
- `validation_results/phase0p_adaptive_planner_summary.md`
- `validation_results/phase0p_adaptive_planner_env.txt`
- `validation_results/phase0p_adaptive_planner_probe.csv`
- `validation_results/phase0p_adaptive_planner_probe.md`
- `validation_results/phase0p_adaptive_planner_once.txt`

Both CSV files must be present, non-empty, not ignored by Git, and included in
the final commit/package.
