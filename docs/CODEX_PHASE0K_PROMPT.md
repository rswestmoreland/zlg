# CODEX Phase 0k prompt

Focus only on Phase 0k search bottleneck analysis and CSV preservation.

1. Run:
   - `bash scripts/phase0k_search_bottleneck_once.sh`
2. If a command fails, apply the smallest fix and rerun.
3. Confirm CSV commit readiness:
   - `test -s validation_results/phase0k_search_bottleneck_bench.csv`
   - `git check-ignore validation_results/phase0k_search_bottleneck_bench.csv && exit 1 || true`
   - `git status --short validation_results/phase0k_search_bottleneck_bench.csv`
4. Keep scope bounded to validation/scripts/docs and minimal required fixes.
