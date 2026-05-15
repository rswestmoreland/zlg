# zlg Phase 0n k-gram graph probe

This is an offline design probe. It does not change the .zlg format.

## Corpus

- Lines: 125000
- Input bytes: 9218316
- Input sha256: 942cac75a8319eae9acbcbfe97bd52d5dc1b161175ee6f9c5908c71f2edc48c2
- Block lines: 4096
- Blocks: 31

## Estimated raw index sizes

These are lower-bound comparison estimates before delta/varint coding or compression.

| index | estimated bytes |
|---|---:|
| bigram_postings_est_bytes | 56748 |
| trigram_postings_est_bytes | 372554 |
| graph_edge_est_bytes | 425776 |

## Best strategy by pattern

| pattern | selector | best_strategy | selected_blocks | decoded_ratio |
|---|---|---|---:|---:|
| alternation_error_failed_denied | any:3 | bigram_block | 31 | 1.000 |
| branch_suffix | any:2 | bigram_block | 31 | 1.000 |
| literal_failed_password | all:1 | bigram_block | 31 | 1.000 |
| lookbehind_key | none:0 | bigram_block | 31 | 1.000 |
| no_match_literal | all:1 | bigram_block | 0 | 0.000 |
| quoted_key | all:1 | bigram_block | 31 | 1.000 |
| src_ip | all:1 | bigram_block | 31 | 1.000 |

## Full strategy table

| pattern | selector | strategy | selected_blocks | selected_ratio | decoded_ratio |
|---|---|---|---:|---:|---:|
| literal_failed_password | all:1 | bigram_block | 31 | 1.000 | 1.000 |
| literal_failed_password | all:1 | trigram_sparse | 31 | 1.000 | 1.000 |
| literal_failed_password | all:1 | bigram_graph_edges | 31 | 1.000 | 1.000 |
| literal_failed_password | all:1 | rarest_kgram_2 | 31 | 1.000 | 1.000 |
| alternation_error_failed_denied | any:3 | bigram_block | 31 | 1.000 | 1.000 |
| alternation_error_failed_denied | any:3 | trigram_sparse | 31 | 1.000 | 1.000 |
| alternation_error_failed_denied | any:3 | bigram_graph_edges | 31 | 1.000 | 1.000 |
| alternation_error_failed_denied | any:3 | rarest_kgram_2 | 31 | 1.000 | 1.000 |
| quoted_key | all:1 | bigram_block | 31 | 1.000 | 1.000 |
| quoted_key | all:1 | trigram_sparse | 31 | 1.000 | 1.000 |
| quoted_key | all:1 | bigram_graph_edges | 31 | 1.000 | 1.000 |
| quoted_key | all:1 | rarest_kgram_2 | 31 | 1.000 | 1.000 |
| branch_suffix | any:2 | bigram_block | 31 | 1.000 | 1.000 |
| branch_suffix | any:2 | trigram_sparse | 31 | 1.000 | 1.000 |
| branch_suffix | any:2 | bigram_graph_edges | 31 | 1.000 | 1.000 |
| branch_suffix | any:2 | rarest_kgram_2 | 31 | 1.000 | 1.000 |
| src_ip | all:1 | bigram_block | 31 | 1.000 | 1.000 |
| src_ip | all:1 | trigram_sparse | 31 | 1.000 | 1.000 |
| src_ip | all:1 | bigram_graph_edges | 31 | 1.000 | 1.000 |
| src_ip | all:1 | rarest_kgram_2 | 31 | 1.000 | 1.000 |
| lookbehind_key | none:0 | bigram_block | 31 | 1.000 | 1.000 |
| lookbehind_key | none:0 | trigram_sparse | 31 | 1.000 | 1.000 |
| lookbehind_key | none:0 | bigram_graph_edges | 31 | 1.000 | 1.000 |
| lookbehind_key | none:0 | rarest_kgram_2 | 31 | 1.000 | 1.000 |
| no_match_literal | all:1 | bigram_block | 0 | 0.000 | 0.000 |
| no_match_literal | all:1 | trigram_sparse | 0 | 0.000 | 0.000 |
| no_match_literal | all:1 | bigram_graph_edges | 0 | 0.000 | 0.000 |
| no_match_literal | all:1 | rarest_kgram_2 | 0 | 0.000 | 0.000 |

## Interpretation

- bigram_block models current block-level bigram presence.
- trigram_sparse models sparse trigram postings.
- bigram_graph_edges models overlapping bigram edges, equivalent to observed trigrams.
- rarest_kgram_2 chooses the two rarest bigrams/trigrams from each selector literal.

A strategy is promising only if it materially reduces estimated decoded bytes while keeping estimated index bytes low enough that total .zlg size can still beat gzip.
