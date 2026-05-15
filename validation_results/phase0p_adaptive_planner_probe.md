# zlg Phase 0p adaptive weighted k-gram planner probe

This offline probe treats k-gram metadata as a query-planning problem.
It compares full scan, rarest-feature selection, entropy gates, cost gates,
and adaptive IDF-style selectors. It does not change the .zlg file format.

## Corpus

- Lines: 125000
- Input bytes: 9218316
- Input sha256: 942cac75a8319eae9acbcbfe97bd52d5dc1b161175ee6f9c5908c71f2edc48c2

## Planner decision counts

| planner_decision | rows |
|---|---:|
| full_scan_no_features | 197 |
| full_scan_no_selector | 48 |
| use_index | 523 |

## Strategy wins by pattern

| strategy | pattern_wins |
|---|---:|
| best_trigram_1 | 11 |
| best_trigram_2 | 2 |
| cost_gate_75pct | 2 |
| full_scan | 1 |

## Best strategy by pattern

| pattern | block_lines | strategy | decision | selected_blocks | decoded_ratio | features | info_max | feature_summary |
|---|---:|---|---|---:|---:|---:|---:|---|
| absent_traceid | 4096 | best_trigram_1 | use_index | 0 | 0.000 | 1 | 64.00 | trigram:df=0:bits=64.00 |
| alternation_error_failed_denied | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 3 | -0.00 | trigram:df=31:bits=-0.00;trigram:df=31:bits=-0.00;trigram:df=31:bits=-0.00 |
| branch_suffix | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 2 | -0.00 | trigram:df=31:bits=-0.00;trigram:df=31:bits=-0.00 |
| component_auth | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 1 | -0.00 | trigram:df=31:bits=-0.00 |
| exact_deny_key | 512 | best_trigram_2 | use_index | 1 | 0.004 | 2 | 5.94 | trigram:df=4:bits=5.94;trigram:df=19:bits=3.69 |
| exact_error_key | 512 | best_trigram_2 | use_index | 2 | 0.008 | 2 | 5.13 | trigram:df=7:bits=5.13;trigram:df=19:bits=3.69 |
| exact_event_id | 512 | best_trigram_1 | use_index | 4 | 0.016 | 1 | 5.94 | trigram:df=4:bits=5.94 |
| exact_retry_key | 512 | cost_gate_75pct | use_index | 1 | 0.004 | 3 | 3.48 | edge:df=22:bits=3.48;edge:df=25:bits=3.29;edge:df=125:bits=0.97 |
| exact_sshd_user | 512 | cost_gate_75pct | use_index | 2 | 0.008 | 2 | 5.94 | edge:df=4:bits=5.94;edge:df=137:bits=0.84 |
| literal_failed_password | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 1 | -0.00 | trigram:df=31:bits=-0.00 |
| lookbehind_key | 4096 | full_scan | full_scan_no_selector | 31 | 1.000 | 0 | 0.00 |  |
| no_match_literal | 4096 | best_trigram_1 | use_index | 0 | 0.000 | 1 | 64.00 | trigram:df=0:bits=64.00 |
| normal_shard_7 | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 1 | -0.00 | trigram:df=31:bits=-0.00 |
| quoted_key | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 1 | -0.00 | trigram:df=31:bits=-0.00 |
| rare_failed_src | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 2 | -0.00 | trigram:df=31:bits=-0.00;trigram:df=31:bits=-0.00 |
| src_ip | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 1 | -0.00 | trigram:df=31:bits=-0.00 |

## Best strategy by pattern and block size

| pattern | block_lines | strategy | decision | selected_blocks | decoded_ratio | info_sum |
|---|---:|---|---|---:|---:|---:|
| absent_traceid | 512 | best_trigram_1 | use_index | 0 | 0.000 | 64.00 |
| absent_traceid | 1024 | best_trigram_1 | use_index | 0 | 0.000 | 64.00 |
| absent_traceid | 2048 | best_trigram_1 | use_index | 0 | 0.000 | 64.00 |
| absent_traceid | 4096 | best_trigram_1 | use_index | 0 | 0.000 | 64.00 |
| alternation_error_failed_denied | 512 | best_trigram_1 | use_index | 245 | 1.000 | 0.01 |
| alternation_error_failed_denied | 1024 | best_trigram_1 | use_index | 123 | 1.000 | 0.01 |
| alternation_error_failed_denied | 2048 | best_trigram_1 | use_index | 62 | 1.000 | 0.02 |
| alternation_error_failed_denied | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 0.00 |
| branch_suffix | 512 | best_trigram_1 | use_index | 245 | 1.000 | 0.01 |
| branch_suffix | 1024 | best_trigram_1 | use_index | 123 | 1.000 | 0.01 |
| branch_suffix | 2048 | best_trigram_1 | use_index | 62 | 1.000 | 0.02 |
| branch_suffix | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 0.00 |
| component_auth | 512 | best_trigram_1 | use_index | 245 | 1.000 | 0.00 |
| component_auth | 1024 | best_trigram_1 | use_index | 123 | 1.000 | 0.00 |
| component_auth | 2048 | best_trigram_1 | use_index | 62 | 1.000 | 0.00 |
| component_auth | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 0.00 |
| exact_deny_key | 512 | best_trigram_2 | use_index | 1 | 0.004 | 9.63 |
| exact_deny_key | 1024 | cost_gate_75pct | use_index | 1 | 0.008 | 7.64 |
| exact_deny_key | 2048 | cost_gate_75pct | use_index | 1 | 0.016 | 6.08 |
| exact_deny_key | 4096 | cost_gate_75pct | use_index | 1 | 0.033 | 4.66 |
| exact_error_key | 512 | best_trigram_2 | use_index | 2 | 0.008 | 8.82 |
| exact_error_key | 1024 | cost_gate_75pct | use_index | 2 | 0.016 | 7.64 |
| exact_error_key | 2048 | cost_gate_75pct | use_index | 2 | 0.033 | 6.08 |
| exact_error_key | 4096 | cost_gate_75pct | use_index | 2 | 0.065 | 4.08 |
| exact_event_id | 512 | best_trigram_1 | use_index | 4 | 0.016 | 5.94 |
| exact_event_id | 1024 | best_trigram_1 | use_index | 3 | 0.024 | 5.36 |
| exact_event_id | 2048 | best_trigram_1 | use_index | 3 | 0.049 | 4.37 |
| exact_event_id | 4096 | best_trigram_1 | use_index | 3 | 0.097 | 3.37 |
| exact_retry_key | 512 | cost_gate_75pct | use_index | 1 | 0.004 | 7.74 |
| exact_retry_key | 1024 | best_trigram_2 | use_index | 2 | 0.016 | 5.52 |
| exact_retry_key | 2048 | cost_gate_75pct | use_index | 2 | 0.033 | 4.28 |
| exact_retry_key | 4096 | cost_gate_75pct | use_index | 2 | 0.066 | 3.50 |
| exact_sshd_user | 512 | cost_gate_75pct | use_index | 2 | 0.008 | 6.78 |
| exact_sshd_user | 1024 | best_trigram_1 | use_index | 4 | 0.032 | 4.94 |
| exact_sshd_user | 2048 | best_trigram_1 | use_index | 4 | 0.065 | 3.95 |
| exact_sshd_user | 4096 | best_trigram_1 | use_index | 4 | 0.130 | 2.95 |
| literal_failed_password | 512 | best_trigram_1 | use_index | 245 | 1.000 | 0.00 |
| literal_failed_password | 1024 | best_trigram_1 | use_index | 123 | 1.000 | 0.00 |
| literal_failed_password | 2048 | best_trigram_1 | use_index | 62 | 1.000 | 0.00 |
| literal_failed_password | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 0.00 |
| lookbehind_key | 512 | full_scan | full_scan_no_selector | 245 | 1.000 | 0.00 |
| lookbehind_key | 1024 | full_scan | full_scan_no_selector | 123 | 1.000 | 0.00 |
| lookbehind_key | 2048 | full_scan | full_scan_no_selector | 62 | 1.000 | 0.00 |
| lookbehind_key | 4096 | full_scan | full_scan_no_selector | 31 | 1.000 | 0.00 |
| no_match_literal | 512 | best_trigram_1 | use_index | 0 | 0.000 | 64.00 |
| no_match_literal | 1024 | best_trigram_1 | use_index | 0 | 0.000 | 64.00 |
| no_match_literal | 2048 | best_trigram_1 | use_index | 0 | 0.000 | 64.00 |
| no_match_literal | 4096 | best_trigram_1 | use_index | 0 | 0.000 | 64.00 |
| normal_shard_7 | 512 | best_trigram_1 | use_index | 245 | 1.000 | 0.00 |
| normal_shard_7 | 1024 | best_trigram_1 | use_index | 123 | 1.000 | 0.00 |
| normal_shard_7 | 2048 | best_trigram_1 | use_index | 62 | 1.000 | 0.00 |
| normal_shard_7 | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 0.00 |
| quoted_key | 512 | best_trigram_1 | use_index | 245 | 1.000 | 0.00 |
| quoted_key | 1024 | best_trigram_1 | use_index | 123 | 1.000 | 0.00 |
| quoted_key | 2048 | best_trigram_1 | use_index | 62 | 1.000 | 0.00 |
| quoted_key | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 0.00 |
| rare_failed_src | 512 | best_trigram_1 | use_index | 245 | 1.000 | 0.00 |
| rare_failed_src | 1024 | best_trigram_1 | use_index | 123 | 1.000 | 0.00 |
| rare_failed_src | 2048 | best_trigram_1 | use_index | 62 | 1.000 | 0.00 |
| rare_failed_src | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 0.00 |
| src_ip | 512 | best_trigram_1 | use_index | 245 | 1.000 | 0.00 |
| src_ip | 1024 | best_trigram_1 | use_index | 123 | 1.000 | 0.00 |
| src_ip | 2048 | best_trigram_1 | use_index | 62 | 1.000 | 0.00 |
| src_ip | 4096 | best_trigram_1 | use_index | 31 | 1.000 | 0.00 |

## Interpretation guide

- `use_index` means the planner found a useful selective feature set.
- `full_scan_low_entropy` means selector features were too common to be worth index use.
- `full_scan_cost_gate` means estimated decode ratio stayed too high.
- High chosen_info_max means at least one selector feature is rare in the block population.
- If common patterns remain full scan, that is acceptable; the planner is learning not to waste index work.
- A useful future on-disk profile should store only the statistics and postings needed by winning planner variants.
