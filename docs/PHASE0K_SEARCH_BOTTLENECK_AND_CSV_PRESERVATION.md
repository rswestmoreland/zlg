# Phase 0k: Search bottleneck analysis and CSV preservation

Phase 0k adds a single-command validation flow for search bottleneck analysis and enforces CSV preservation in Git.

## Goal

- Run the existing validation stack.
- Produce compact Phase 0k reports under `validation_results/`.
- Ensure `validation_results/phase0k_search_bottleneck_bench.csv` is not ignored and is commit-ready.

## Primary command

```bash
bash scripts/phase0k_search_bottleneck_once.sh
```

## Generated outputs

- `validation_results/phase0k_search_bottleneck_bench.csv`
- `validation_results/phase0k_search_bottleneck_summary.md`
- `validation_results/phase0k_search_bottleneck_env.txt`
- `validation_results/phase0k_search_bottleneck_analysis.md`
- `validation_results/phase0k_search_bottleneck_once.txt`

## CSV preservation gate

Use:

```bash
bash scripts/phase0k_csv_commit_guard.sh validation_results/phase0k_search_bottleneck_bench.csv
```

The guard fails if the CSV is missing, empty, or ignored by Git.
