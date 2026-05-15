You are continuing work on the zlg Rust project.

Start with Phase 0x 8192 mesh-bigram PCRE2, early-stop, and streaming decode
validation only. Do not broaden scope into a full async worker pool, final
file-format freeze, trigram mesh, path-window, rare-window, per-group mesh,
multiline regex, timestamp sidecars, dictionary training, append mode,
tail/sort/uniq runtime implementation, or unrelated performance tuning.

Primary command:

bash scripts/phase0x_8192_pcre2_early_once.sh

The run must produce and preserve:

validation_results/phase0x_8192_pcre2_early_bench.csv
validation_results/phase0x_8192_pcre2_early_bench.md
validation_results/phase0x_8192_pcre2_early_once.txt

The benchmark must compare zlg grep full-decode mode and zlg grep
--stream-decode mode.
