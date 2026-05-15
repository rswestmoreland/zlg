# zlg Phase 0r path-aware traversal probe

This offline probe tests path-aware literal traversal over bigram, trigram,
4-gram, and longer window variants. It also tracks first-seen, span, count,
density, information, and estimated storage overhead per strategy.

## Corpus

- Lines: 125000
- Input bytes: 9223684
- Input sha256: fea507e974d3f1bd542665e11e2d93e07c155b670f53b9d5874dce74a3c50c5e
- Needle IP: 198.18.99.123
- Needle line: 100001
- Needle line ratio: 0.800

## Best needle strategies

| pattern | block_lines | strategy | selected_blocks | decoded_ratio | feature | first_seen | count | compressed_index_est |
|---|---:|---|---:|---:|---|---:|---:|---:|
| needle_ip_value | 512 | literal_exact_scan | 1 | 0.004134 | 198.18.99.123 | 195 | 1 | 11 |
| needle_request_id_prefix | 512 | literal_exact_scan | 1 | 0.004134 | NEEDLE-001000 | 195 | 1 | 11 |
| needle_ip_value | 512 | rarest_window_12 | 1 | 0.004134 | 198.18.99.12 | 195 | 1 | 11 |
| needle_request_id_prefix | 512 | rarest_window_12 | 1 | 0.004134 | EEDLE-001000 | 195 | 1 | 11 |
| needle_ip_value | 512 | rarest_window_4 | 1 | 0.004134 | 18.9 | 195 | 1 | 11 |
| needle_request_id_prefix | 512 | rarest_window_4 | 1 | 0.004134 | -001 | 195 | 1 | 11 |
| needle_ip_value | 512 | rarest_window_6 | 1 | 0.004134 | .18.99 | 195 | 1 | 11 |
| needle_request_id_prefix | 512 | rarest_window_6 | 1 | 0.004134 | -00100 | 195 | 1 | 11 |
| needle_ip_value | 512 | rarest_window_8 | 1 | 0.004134 | .18.99.1 | 195 | 1 | 11 |
| needle_request_id_prefix | 512 | rarest_window_8 | 1 | 0.004134 | DLE-0010 | 195 | 1 | 11 |
| needle_ip_value | 512 | bigram_path_traversal | 1 | 0.004134 | 19 | 0 | 14436 | 16 |
| needle_request_id_prefix | 512 | bigram_path_traversal | 1 | 0.004134 | NE | 195 | 1 | 16 |

## Strategy decoded-ratio summary

| strategy | mean_decoded_ratio | min | max | rows |
|---|---:|---:|---:|---:|
| bigram_path_traversal | 0.681814 | 0.000000 | 1.000000 | 112 |
| fourgram_path_traversal | 0.681814 | 0.000000 | 1.000000 | 112 |
| literal_exact_scan | 0.681814 | 0.000000 | 1.000000 | 112 |
| rarest_window_12 | 0.681814 | 0.000000 | 1.000000 | 112 |
| rarest_window_6 | 0.681814 | 0.000000 | 1.000000 | 112 |
| rarest_window_8 | 0.681814 | 0.000000 | 1.000000 | 112 |
| trigram_path_traversal | 0.681814 | 0.000000 | 1.000000 | 112 |
| fourgram_all_membership | 0.682102 | 0.000000 | 1.000000 | 112 |
| trigram_all_membership | 0.685027 | 0.000000 | 1.000000 | 112 |
| rarest_window_4 | 0.685107 | 0.000000 | 1.000000 | 112 |
| bigram_all_membership | 0.751305 | 0.000000 | 1.000000 | 112 |
| full_scan | 1.000000 | 1.000000 | 1.000000 | 112 |

## Interpretation

- Membership strategies ask whether all grams exist somewhere in the block.
- Path traversal asks whether the grams reconstruct the selector literal contiguously.
- Rarest windows use longer contiguous byte windows as selective features.
- `feature_first_seen_block`, `feature_occurrence_count`, and `feature_block_span`
  are the first step toward a weighted planner with locality awareness.
- Storage estimates are heuristic and must be replaced by real encoded footer
  measurements before format freeze.
