You are continuing work on the zlg Rust project.

Start with Phase 0r path traversal and storage model validation only. Do not
broaden scope into async worker pools, full benchmark proof, final file-format
freeze, PCRE2, multiline regex, timestamp sidecars, dictionary training, append
mode, or unrelated performance tuning.

Primary command:

bash scripts/phase0r_path_traversal_once.sh

The run must produce and preserve:

validation_results/phase0r_path_traversal_probe.csv
validation_results/phase0r_path_traversal_probe.md
validation_results/phase0r_path_traversal_once.txt
