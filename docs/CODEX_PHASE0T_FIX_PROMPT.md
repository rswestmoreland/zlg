You are continuing work on the zlg Rust project.

Start with Phase 0t-fix mesh correctness validation only. Do not broaden scope
into async worker pools, runtime mesh serialization, full benchmark proof, final
file-format freeze, PCRE2, multiline regex, timestamp sidecars, dictionary
training, append mode, or unrelated performance tuning.

Primary command:

bash scripts/phase0t_fix_mesh_correctness_once.sh

The run must produce and preserve:

validation_results/phase0t_fix_mesh_shootout.csv
validation_results/phase0t_fix_mesh_shootout.md
validation_results/phase0t_fix_mesh_correctness_once.txt
