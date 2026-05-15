You are continuing work on the zlg Rust project.

Start with Phase 0y regex hot-path and mesh-overhead validation only. Do not
broaden scope into async worker pools, non-8192 candidates, trigram mesh,
path-window, rare-window, per-group mesh, final file-format freeze, multiline
regex, timestamp sidecars, dictionary training, append mode, tail/sort/uniq
runtime implementation, or unrelated performance tuning.

Primary command:

bash scripts/phase0y_regex_mesh_hotpath_once.sh

The run must produce and preserve:

validation_results/phase0y_regex_mesh_hotpath_bench.csv
validation_results/phase0y_regex_mesh_hotpath_bench.md
validation_results/phase0y_regex_mesh_hotpath_once.txt
