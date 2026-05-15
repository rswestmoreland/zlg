You are continuing work on the zlg Rust project.

Start with Phase 0q regex selector and needle corpus validation only. Do not
broaden scope into async worker pools, full benchmark proof, final file-format
freeze, PCRE2, multiline regex, timestamp sidecars, dictionary training, append
mode, or unrelated performance tuning.

Primary command:

bash scripts/phase0q_selector_needle_once.sh

The run must confirm the positive lookbehind selector extracts key=" from:

(?<=key=\")[^\"]+

The run must also produce and preserve:

validation_results/phase0q_needle_probe.csv
validation_results/phase0q_needle_probe.md
validation_results/phase0q_selector_needle_once.txt
