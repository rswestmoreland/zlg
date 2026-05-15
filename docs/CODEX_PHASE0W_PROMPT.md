You are continuing work on the zlg Rust project.

Start with Phase 0w mesh-bigram 8K/16K performance validation only. Do not
broaden scope into async worker pools, non-mesh candidates, trigram mesh,
path-window, rare-window, per-group mesh, full benchmark proof, final
file-format freeze, PCRE2, multiline regex, timestamp sidecars, dictionary
training, append mode, or unrelated performance tuning.

Primary command:

bash scripts/phase0w_mesh_8k_16k_once.sh

The run must produce and preserve:

validation_results/phase0w_mesh_8k_16k_bench.csv
validation_results/phase0w_mesh_8k_16k_bench.md
validation_results/phase0w_mesh_8k_16k_once.txt
