You are continuing work on the zlg Rust project.

Start with Phase 0p adaptive weighted k-gram planner experiment only. Do not
broaden scope into async worker pools, full benchmark proof, final file-format
freeze, PCRE2, multiline regex, timestamp sidecars, dictionary training, append
mode, or unrelated performance tuning.

Primary command:

bash scripts/phase0p_adaptive_planner_once.sh

The script must produce and preserve:

validation_results/phase0p_adaptive_planner_bench.csv
validation_results/phase0p_adaptive_planner_probe.csv

Both CSV files must be present, non-empty, not ignored by Git, and included in
the final commit/package.
