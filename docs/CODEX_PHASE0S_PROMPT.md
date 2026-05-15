You are continuing work on the zlg Rust project.

Start with Phase 0s path-window runtime prototype validation only. Do not
broaden scope into async worker pools, full benchmark proof, final file-format
freeze, PCRE2, multiline regex, timestamp sidecars, dictionary training, append
mode, or unrelated performance tuning.

Primary command:

bash scripts/phase0s_path_window_runtime_once.sh

The run must produce and preserve:

validation_results/phase0s_path_window_runtime.csv
validation_results/phase0s_path_window_runtime.md
validation_results/phase0s_path_window_runtime_once.txt
