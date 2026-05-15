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
| edge_postings_trigram | 0.578082 | 0.000000 | 1.000000 | 467449 | 208 |
| sorted_edge_table_trigram | 0.578082 | 0.000000 | 1.000000 | 467449 | 208 |
| per_group_mesh_trigram | 0.578087 | 0.000000 | 1.000000 | 620504 | 208 |
| edge_postings_bigram | 0.580005 | 0.000000 | 1.000000 | 132647 | 208 |
| sorted_edge_table_bigram | 0.580005 | 0.000000 | 1.000000 | 132647 | 208 |
| hybrid_bigram_trigram | 0.580551 | 0.000000 | 1.000000 | 467449 | 208 |
| rarest_edge_traversal_trigram | 0.580551 | 0.000000 | 1.000000 | 467449 | 208 |
| per_group_mesh_bigram | 0.580637 | 0.000000 | 1.000000 | 153773 | 208 |
| path_exact_bigram | 0.581619 | 0.000000 | 1.000000 | 132647 | 208 |
| path_exact_trigram | 0.581619 | 0.000000 | 1.000000 | 467449 | 208 |
| rarest_edge_traversal_bigram | 0.582664 | 0.000000 | 1.000000 | 132647 | 208 |

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
| alternation_error_failed_denied | path_exact_bigram | 2048 | 16384 | 61 | 0.999421 | 95124 | 0 | 148 | 62 |
| branch_suffix | path_exact_bigram | 2048 | 16384 | 61 | 0.999421 | 95124 | 0 | 148 | 62 |
| component_auth | edge_postings_bigram | 4096 | 16384 | 31 | 1.000000 | 62534 | 0 | 164 | 31 |
| exact_deny_key | edge_postings_bigram | 4096 | 16384 | 0 | 0.000000 | 62534 | -1 | 0 | 0 |
| exact_error_key | path_exact_bigram | 512 | 16384 | 1 | 0.004034 | 214579 | 18 | 2 | 172 |
| exact_event_id | edge_postings_trigram | 4096 | 16384 | 0 | 0.000000 | 372560 | -1 | 0 | 0 |
| exact_retry_key | edge_postings_bigram | 4096 | 16384 | 0 | 0.000000 | 62534 | -1 | 0 | 0 |
| exact_sshd_user | edge_postings_trigram | 4096 | 16384 | 0 | 0.000000 | 372560 | -1 | 0 | 0 |
| literal_failed_password | edge_postings_bigram | 4096 | 16384 | 31 | 1.000000 | 62534 | 0 | 120 | 31 |
| lookbehind_key | edge_postings_bigram | 4096 | 16384 | 31 | 1.000000 | 62534 | 0 | 239 | 31 |
| needle_exact_ip_regex_escaped | edge_postings_bigram | 4096 | 16384 | 0 | 0.000000 | 62534 | -1 | 0 | 0 |
| needle_ip_fixed | edge_postings_bigram | 4096 | 16384 | 0 | 0.000000 | 62534 | -1 | 0 | 0 |
| needle_request_id_prefix | edge_postings_bigram | 4096 | 16384 | 0 | 0.000000 | 62534 | -1 | 0 | 0 |
| needle_src_ip_fixed | edge_postings_bigram | 4096 | 16384 | 0 | 0.000000 | 62534 | -1 | 0 | 0 |
| no_match_literal | edge_postings_bigram | 4096 | 16384 | 0 | 0.000000 | 62534 | -1 | 0 | 0 |
| normal_shard_7 | edge_postings_bigram | 4096 | 16384 | 31 | 1.000000 | 62534 | 0 | 2026 | 31 |
| quoted_key | edge_postings_bigram | 4096 | 16384 | 31 | 1.000000 | 62534 | 0 | 239 | 31 |
| rare_failed_src | edge_postings_bigram | 4096 | 16384 | 31 | 1.000000 | 62534 | 0 | 318 | 31 |
| src_ip | edge_postings_bigram | 4096 | 16384 | 31 | 1.000000 | 62534 | 0 | 15872 | 31 |

## Interpretation guide

- Edge postings variants store postings for graph transitions.
- Sorted edge table variants model a compact footer-friendly layout.
- Rarest-edge traversal starts at the most selective edge in the query path.
- Per-group mesh variants model local mesh indexes under larger logical groups.
- These are heuristic storage estimates, not final serialized file sizes.
- A future runtime phase should serialize only the top one or two variants.
