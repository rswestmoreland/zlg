You are continuing work on the zlg Rust project.

Start with Phase 0z mesh-bigram summary optimization validation only. Do not
broaden scope into async worker pools, non-8192 candidates, trigram mesh,
bitmap, path-window, rare-window, per-group mesh, final file-format freeze,
multiline regex, timestamp sidecars, dictionary training, append mode,
tail/sort/uniq runtime implementation, or unrelated performance tuning.

Primary command:

bash scripts/phase0z_mesh_summary_opt_once.sh

The run must produce and preserve:

validation_results/phase0z_mesh_summary_opt_bench.csv
validation_results/phase0z_mesh_summary_opt_bench.md
validation_results/phase0z_mesh_summary_opt_once.txt
