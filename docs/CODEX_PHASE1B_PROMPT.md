You are continuing work on the zlg Rust project.

Start with Phase 1b mesh summary builder shootout validation only. Do not
broaden scope into async worker pools, non-8192 candidates, trigram mesh,
bitmap, path-window, rare-window, per-group mesh, final file-format freeze,
multiline regex, timestamp sidecars, dictionary training, append mode,
tail/sort/uniq runtime implementation, or unrelated performance tuning.

Primary command:

bash scripts/phase1b_mesh_builder_once.sh

The run must produce and preserve:

validation_results/phase1b_mesh_builder_bench.csv
validation_results/phase1b_mesh_builder_bench.md
validation_results/phase1b_mesh_builder_once.txt
