# zlg Phase 0o creative index probe

This offline probe fixes the Phase 0n rarest-kgram absent-gram flaw and compares
smaller block sizes, rare selectors, sparse trigrams, bigram graph edges, and adaptive
rarest-kgram strategies. It does not change the .zlg file format.

## Corpus

- Lines: 125000
- Input bytes: 9218316
- Input sha256: 942cac75a8319eae9acbcbfe97bd52d5dc1b161175ee6f9c5908c71f2edc48c2

## Best strategy by pattern

| pattern | block_lines | strategy | selected_blocks | decoded_ratio | index_bytes | df_min | df_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| absent_traceid | 4096 | bigram_block | 0 | 0.000 | 56748 | 0 | 2.02 |
| alternation_error_failed_denied | 4096 | bigram_block | 31 | 1.000 | 56748 | 31 | 31.00 |
| branch_suffix | 4096 | bigram_block | 31 | 1.000 | 56748 | 31 | 31.00 |
| component_auth | 4096 | bigram_block | 31 | 1.000 | 56748 | 31 | 31.00 |
| exact_deny_key | 512 | trigram_sparse | 1 | 0.004 | 1924307 | 4 | 208.11 |
| exact_error_key | 512 | trigram_sparse | 2 | 0.008 | 1924307 | 7 | 192.61 |
| exact_event_id | 512 | trigram_sparse | 4 | 0.016 | 1924307 | 4 | 228.82 |
| exact_retry_key | 512 | trigram_sparse | 1 | 0.004 | 1924307 | 22 | 205.38 |
| exact_sshd_user | 512 | trigram_sparse | 2 | 0.008 | 1924307 | 4 | 204.04 |
| literal_failed_password | 4096 | bigram_block | 31 | 1.000 | 56748 | 31 | 31.00 |
| lookbehind_key | 4096 | bigram_block | 31 | 1.000 | 56748 | 0 | 0.00 |
| no_match_literal | 4096 | bigram_block | 0 | 0.000 | 56748 | 0 | 3.10 |
| normal_shard_7 | 4096 | bigram_block | 31 | 1.000 | 56748 | 31 | 31.00 |
| quoted_key | 4096 | bigram_block | 31 | 1.000 | 56748 | 31 | 31.00 |
| rare_failed_src | 4096 | bigram_block | 31 | 1.000 | 56748 | 31 | 31.00 |
| src_ip | 4096 | bigram_block | 31 | 1.000 | 56748 | 31 | 31.00 |

## Best strategy per pattern and block size

| pattern | block_lines | strategy | selected_blocks | decoded_ratio | index_bytes |
|---|---:|---|---:|---:|---:|
| absent_traceid | 512 | bigram_block | 0 | 0.000 | 418302 |
| absent_traceid | 1024 | bigram_block | 0 | 0.000 | 218586 |
| absent_traceid | 2048 | bigram_block | 0 | 0.000 | 112464 |
| absent_traceid | 4096 | bigram_block | 0 | 0.000 | 56748 |
| alternation_error_failed_denied | 512 | bigram_block | 245 | 1.000 | 418302 |
| alternation_error_failed_denied | 1024 | bigram_block | 123 | 1.000 | 218586 |
| alternation_error_failed_denied | 2048 | bigram_block | 62 | 1.000 | 112464 |
| alternation_error_failed_denied | 4096 | bigram_block | 31 | 1.000 | 56748 |
| branch_suffix | 512 | bigram_block | 245 | 1.000 | 418302 |
| branch_suffix | 1024 | bigram_block | 123 | 1.000 | 218586 |
| branch_suffix | 2048 | bigram_block | 62 | 1.000 | 112464 |
| branch_suffix | 4096 | bigram_block | 31 | 1.000 | 56748 |
| component_auth | 512 | bigram_block | 245 | 1.000 | 418302 |
| component_auth | 1024 | bigram_block | 123 | 1.000 | 218586 |
| component_auth | 2048 | bigram_block | 62 | 1.000 | 112464 |
| component_auth | 4096 | bigram_block | 31 | 1.000 | 56748 |
| exact_deny_key | 512 | trigram_sparse | 1 | 0.004 | 1924307 |
| exact_deny_key | 1024 | trigram_sparse | 1 | 0.008 | 1345449 |
| exact_deny_key | 2048 | trigram_sparse | 1 | 0.016 | 703710 |
| exact_deny_key | 4096 | trigram_sparse | 1 | 0.033 | 372554 |
| exact_error_key | 512 | trigram_sparse | 2 | 0.008 | 1924307 |
| exact_error_key | 1024 | trigram_sparse | 2 | 0.016 | 1345449 |
| exact_error_key | 2048 | trigram_sparse | 2 | 0.033 | 703710 |
| exact_error_key | 4096 | trigram_sparse | 2 | 0.065 | 372554 |
| exact_event_id | 512 | trigram_sparse | 4 | 0.016 | 1924307 |
| exact_event_id | 1024 | trigram_sparse | 3 | 0.024 | 1345449 |
| exact_event_id | 2048 | trigram_sparse | 3 | 0.049 | 703710 |
| exact_event_id | 4096 | trigram_sparse | 3 | 0.097 | 372554 |
| exact_retry_key | 512 | trigram_sparse | 1 | 0.004 | 1924307 |
| exact_retry_key | 1024 | trigram_sparse | 2 | 0.016 | 1345449 |
| exact_retry_key | 2048 | trigram_sparse | 2 | 0.033 | 703710 |
| exact_retry_key | 4096 | trigram_sparse | 2 | 0.066 | 372554 |
| exact_sshd_user | 512 | trigram_sparse | 2 | 0.008 | 1924307 |
| exact_sshd_user | 1024 | trigram_sparse | 4 | 0.032 | 1345449 |
| exact_sshd_user | 2048 | trigram_sparse | 4 | 0.065 | 703710 |
| exact_sshd_user | 4096 | trigram_sparse | 4 | 0.130 | 372554 |
| literal_failed_password | 512 | bigram_block | 245 | 1.000 | 418302 |
| literal_failed_password | 1024 | bigram_block | 123 | 1.000 | 218586 |
| literal_failed_password | 2048 | bigram_block | 62 | 1.000 | 112464 |
| literal_failed_password | 4096 | bigram_block | 31 | 1.000 | 56748 |
| lookbehind_key | 512 | bigram_block | 245 | 1.000 | 418302 |
| lookbehind_key | 1024 | bigram_block | 123 | 1.000 | 218586 |
| lookbehind_key | 2048 | bigram_block | 62 | 1.000 | 112464 |
| lookbehind_key | 4096 | bigram_block | 31 | 1.000 | 56748 |
| no_match_literal | 512 | bigram_block | 0 | 0.000 | 418302 |
| no_match_literal | 1024 | bigram_block | 0 | 0.000 | 218586 |
| no_match_literal | 2048 | bigram_block | 0 | 0.000 | 112464 |
| no_match_literal | 4096 | bigram_block | 0 | 0.000 | 56748 |
| normal_shard_7 | 512 | bigram_block | 245 | 1.000 | 418302 |
| normal_shard_7 | 1024 | bigram_block | 123 | 1.000 | 218586 |
| normal_shard_7 | 2048 | bigram_block | 62 | 1.000 | 112464 |
| normal_shard_7 | 4096 | bigram_block | 31 | 1.000 | 56748 |
| quoted_key | 512 | bigram_block | 245 | 1.000 | 418302 |
| quoted_key | 1024 | bigram_block | 123 | 1.000 | 218586 |
| quoted_key | 2048 | bigram_block | 62 | 1.000 | 112464 |
| quoted_key | 4096 | bigram_block | 31 | 1.000 | 56748 |
| rare_failed_src | 512 | bigram_block | 245 | 1.000 | 418302 |
| rare_failed_src | 1024 | bigram_block | 123 | 1.000 | 218586 |
| rare_failed_src | 2048 | bigram_block | 62 | 1.000 | 112464 |
| rare_failed_src | 4096 | bigram_block | 31 | 1.000 | 56748 |
| src_ip | 512 | bigram_block | 245 | 1.000 | 418302 |
| src_ip | 1024 | bigram_block | 123 | 1.000 | 218586 |
| src_ip | 2048 | bigram_block | 62 | 1.000 | 112464 |
| src_ip | 4096 | bigram_block | 31 | 1.000 | 56748 |

## Interpretation guide

- If decoded_ratio stays 1.000, that selector is too common for gram indexing at that block size.
- If decoded_ratio falls only at smaller block sizes, the future format needs smaller independently decodable search blocks.
- If trigram/graph does not beat bigram, the corpus likely has common literals in every block.
- If rarest-kgram beats all-grams, frequency-guided query planning is worth carrying forward.
- Index overhead is acceptable only while total .zlg size remains below comparable gzip outputs.
