You are continuing work on the zlg Rust project.

Start with Phase 0v 4096-vs-64K mesh-bigram performance validation only. Do
not broaden scope into async worker pools, trigram mesh, path-window,
rare-window, per-group mesh, full benchmark proof, final file-format freeze,
PCRE2, multiline regex, timestamp sidecars, dictionary training, append mode,
or unrelated performance tuning.

Primary command:

bash scripts/phase0v_4096_64k_perf_once.sh

The run must produce and preserve:

validation_results/phase0v_4096_64k_bench.csv
validation_results/phase0v_4096_64k_bench.md
validation_results/phase0v_4096_64k_perf_once.txt
