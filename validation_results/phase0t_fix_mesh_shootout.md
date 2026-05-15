# zlg Phase 0t k-gram mesh shootout

This offline probe compares multiple k-gram mesh implementation variants
before changing the .zlg format.

## Corpus

- Lines: 125000
- Input bytes: 9223684
- Input sha256: fea507e974d3f1bd542665e11e2d93e07c155b670f53b9d5874dce74a3c50c5e
- Needle IP: 198.18.99.123
- Needle line: 100001
- Needle ratio: 0.800

## Variant aggregate summary

| variant | mean_decoded_ratio | min | max | avg_compressed_index_est | rows |
|---|---:|---:|---:|---:|---:|
| path_exact_bigram | 0.581619 | 0.000000 | 1.000000 | 132647 | 208 |
| path_exact_trigram | 0.581619 | 0.000000 | 1.000000 | 467449 | 208 |
| edge_postings_trigram | 0.581929 | 0.000000 | 1.000000 | 467449 | 208 |
| sorted_edge_table_trigram | 0.581929 | 0.000000 | 1.000000 | 467449 | 208 |
| per_group_mesh_trigram | 0.582489 | 0.000000 | 1.000000 | 620504 | 208 |
| edge_postings_bigram | 0.585080 | 0.000000 | 1.000000 | 132647 | 208 |
| sorted_edge_table_bigram | 0.585080 | 0.000000 | 1.000000 | 132647 | 208 |
| hybrid_bigram_trigram | 0.585165 | 0.000000 | 1.000000 | 467449 | 208 |
| rarest_edge_traversal_trigram | 0.585165 | 0.000000 | 1.000000 | 467449 | 208 |
| rarest_edge_traversal_bigram | 0.586937 | 0.000000 | 1.000000 | 132647 | 208 |
| per_group_mesh_bigram | 0.593557 | 0.000000 | 1.000000 | 153773 | 208 |

## Best needle rows

| pattern | block | group | variant | gram_k | selected_blocks | decoded_ratio | index_est | extra |
|---|---:|---:|---|---:|---:|---:|---:|---|
| needle_exact_ip_regex_escaped | 512 | 16384 | edge_postings_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_ip_fixed | 512 | 16384 | edge_postings_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_src_ip_fixed | 512 | 16384 | edge_postings_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_request_id_prefix | 512 | 16384 | edge_postings_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_exact_ip_regex_escaped | 512 | 65536 | edge_postings_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_ip_fixed | 512 | 65536 | edge_postings_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_src_ip_fixed | 512 | 65536 | edge_postings_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_request_id_prefix | 512 | 65536 | edge_postings_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_exact_ip_regex_escaped | 512 | 16384 | path_exact_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_ip_fixed | 512 | 16384 | path_exact_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_src_ip_fixed | 512 | 16384 | path_exact_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_request_id_prefix | 512 | 16384 | path_exact_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_exact_ip_regex_escaped | 512 | 65536 | path_exact_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_ip_fixed | 512 | 65536 | path_exact_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_src_ip_fixed | 512 | 65536 | path_exact_bigram | 2 | 1 | 0.004134 | 214579 |  |
| needle_request_id_prefix | 512 | 65536 | path_exact_bigram | 2 | 1 | 0.004134 | 214579 |  |

## Best variant by pattern

| pattern | variant | block | group | selected_blocks | decoded_ratio | index_est | first_seen | count | span |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| absent_traceid | edge_postings_bigram | 4096 | 16384 | 0 | 0.000000 | 62534 | -1 | 0 | 0 |
| alternation_error_failed_denied | edge_postings_bigram | 2048 | 16384 | 61 | 0.999421 | 95124 | 0 | 582 | 61 |
| branch_suffix | edge_postings_bigram | 2048 | 16384 | 61 | 0.999421 | 95124 | 0 | 582 | 61 |
| component_auth | edge_postings_bigram | 4096 | 16384 | 31 | 1.000000 | 62534 | 0 | 1289 | 31 |
| exact_deny_key | edge_postings_bigram | 512 | 16384 | 1 | 0.004090 | 214579 | 41 | 1 | 1 |
| exact_error_key | path_exact_bigram | 512 | 16384 | 1 | 0.004034 | 214579 | 18 | 2 | 172 |
| exact_event_id | path_exact_bigram | 512 | 16384 | 1 | 0.004088 | 214579 | 0 | 19 | 84 |
| exact_retry_key | edge_postings_bigram | 4096 | 16384 | 0 | 0.000000 | 62534 | -1 | 0 | 0 |
| exact_sshd_user | path_exact_bigram | 512 | 16384 | 1 | 0.004091 | 214579 | 12 | 2 | 116 |
| literal_failed_password | edge_postings_bigram | 4096 | 16384 | 31 | 1.000000 | 62534 | 0 | 945 | 31 |
| lookbehind_key | edge_postings_bigram | 4096 | 16384 | 31 | 1.000000 | 62534 | 0 | 1871 | 31 |
| needle_exact_ip_regex_escaped | edge_postings_bigram | 512 | 16384 | 1 | 0.004134 | 214579 | 195 | 1 | 1 |
| needle_ip_fixed | edge_postings_bigram | 512 | 16384 | 1 | 0.004134 | 214579 | 195 | 1 | 1 |
| needle_request_id_prefix | edge_postings_bigram | 512 | 16384 | 1 | 0.004134 | 214579 | 195 | 1 | 1 |
| needle_src_ip_fixed | edge_postings_bigram | 512 | 16384 | 1 | 0.004134 | 214579 | 195 | 1 | 1 |
| no_match_literal | edge_postings_bigram | 4096 | 16384 | 0 | 0.000000 | 62534 | -1 | 0 | 0 |
| normal_shard_7 | edge_postings_bigram | 4096 | 16384 | 31 | 1.000000 | 62534 | 0 | 18246 | 31 |
| quoted_key | edge_postings_bigram | 4096 | 16384 | 31 | 1.000000 | 62534 | 0 | 1871 | 31 |
| rare_failed_src | edge_postings_bigram | 4096 | 16384 | 31 | 1.000000 | 62534 | 0 | 2893 | 31 |
| src_ip | edge_postings_bigram | 4096 | 16384 | 31 | 1.000000 | 62534 | 0 | 125000 | 31 |

## Interpretation guide

- Edge postings variants store postings for graph transitions.
- Sorted edge table variants model a compact footer-friendly layout.
- Rarest-edge traversal starts at the most selective edge in the query path.
- Per-group mesh variants model local mesh indexes under larger logical groups.
- These are heuristic storage estimates, not final serialized file sizes.
- A future runtime phase should serialize only the top one or two variants.
