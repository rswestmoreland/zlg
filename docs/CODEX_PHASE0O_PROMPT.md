You are continuing work on the zlg Rust project.

Start with Phase 0o creative index experiment only. Do not broaden scope into
async worker pools, full benchmark proof, final file-format freeze, PCRE2,
multiline regex, timestamp sidecars, dictionary training, append mode, or
unrelated performance tuning.

Primary command:

bash scripts/phase0o_creative_index_once.sh

Hard CSV preservation gate:

The following CSV files must exist, be non-empty, not be ignored by Git, and be
included in the final commit/package:

validation_results/phase0o_creative_index_bench.csv
validation_results/phase0o_creative_index_probe.csv
validation_results/phase0o_fixed_rarest_check.csv

The Phase 0o probe should summarize smaller block sizes, rare selectors,
selector document frequency, selected-block ratios, estimated decoded-byte
ratios, and whether bigram, trigram, graph-edge, or adaptive rarest-kgram
strategies look most promising.
