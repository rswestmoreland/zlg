# zlg Phase 0q needle-in-haystack probe

This offline probe creates deterministic sample data where one specific IP
appears exactly once, about 80 percent into the log volume.

The generated corpus is not committed. Only compact CSV/Markdown results are saved.

## Corpus

- Lines: 125000
- Input bytes: 9223684
- Input sha256: fea507e974d3f1bd542665e11e2d93e07c155b670f53b9d5874dce74a3c50c5e
- Needle IP: 198.18.99.123
- Needle line: 100001
- Needle line ratio: 0.800

## Best candidate selections

| block_lines | strategy | selected_blocks | decoded_ratio | contains_needle | info_bits |
|---:|---|---:|---:|---|---:|
| 2048 | edge_all | 61 | 0.999421 | yes | 0.02 |
| 2048 | rarest_1_edge | 61 | 0.999421 | yes | 0.02 |
| 2048 | rarest_2_mixed | 61 | 0.999421 | yes | 0.02 |
| 2048 | rarest_4_mixed | 61 | 0.999421 | yes | 0.02 |
| 2048 | trigram_all | 61 | 0.999421 | yes | 0.02 |
| 1024 | edge_all | 122 | 0.999421 | yes | 0.01 |
| 1024 | rarest_1_edge | 122 | 0.999421 | yes | 0.01 |
| 1024 | rarest_2_mixed | 122 | 0.999421 | yes | 0.01 |

## Full table

| block_lines | total_blocks | needle_block | strategy | selected_blocks | selected_ratio | decoded_ratio | contains_needle |
|---:|---:|---:|---|---:|---:|---:|---|
| 512 | 245 | 195 | full_scan | 245 | 1.000000 | 1.000000 | yes |
| 512 | 245 | 195 | bigram_all | 245 | 1.000000 | 1.000000 | yes |
| 512 | 245 | 195 | trigram_all | 244 | 0.995918 | 0.999421 | yes |
| 512 | 245 | 195 | edge_all | 244 | 0.995918 | 0.999421 | yes |
| 512 | 245 | 195 | rarest_1_edge | 244 | 0.995918 | 0.999421 | yes |
| 512 | 245 | 195 | rarest_2_mixed | 244 | 0.995918 | 0.999421 | yes |
| 512 | 245 | 195 | rarest_4_mixed | 244 | 0.995918 | 0.999421 | yes |
| 1024 | 123 | 97 | full_scan | 123 | 1.000000 | 1.000000 | yes |
| 1024 | 123 | 97 | bigram_all | 123 | 1.000000 | 1.000000 | yes |
| 1024 | 123 | 97 | trigram_all | 122 | 0.991870 | 0.999421 | yes |
| 1024 | 123 | 97 | edge_all | 122 | 0.991870 | 0.999421 | yes |
| 1024 | 123 | 97 | rarest_1_edge | 122 | 0.991870 | 0.999421 | yes |
| 1024 | 123 | 97 | rarest_2_mixed | 122 | 0.991870 | 0.999421 | yes |
| 1024 | 123 | 97 | rarest_4_mixed | 122 | 0.991870 | 0.999421 | yes |
| 2048 | 62 | 48 | full_scan | 62 | 1.000000 | 1.000000 | yes |
| 2048 | 62 | 48 | bigram_all | 62 | 1.000000 | 1.000000 | yes |
| 2048 | 62 | 48 | trigram_all | 61 | 0.983871 | 0.999421 | yes |
| 2048 | 62 | 48 | edge_all | 61 | 0.983871 | 0.999421 | yes |
| 2048 | 62 | 48 | rarest_1_edge | 61 | 0.983871 | 0.999421 | yes |
| 2048 | 62 | 48 | rarest_2_mixed | 61 | 0.983871 | 0.999421 | yes |
| 2048 | 62 | 48 | rarest_4_mixed | 61 | 0.983871 | 0.999421 | yes |
| 4096 | 31 | 24 | full_scan | 31 | 1.000000 | 1.000000 | yes |
| 4096 | 31 | 24 | bigram_all | 31 | 1.000000 | 1.000000 | yes |
| 4096 | 31 | 24 | trigram_all | 31 | 1.000000 | 1.000000 | yes |
| 4096 | 31 | 24 | edge_all | 31 | 1.000000 | 1.000000 | yes |
| 4096 | 31 | 24 | rarest_1_bigram | 31 | 1.000000 | 1.000000 | yes |
| 4096 | 31 | 24 | rarest_2_bigram | 31 | 1.000000 | 1.000000 | yes |
| 4096 | 31 | 24 | rarest_4_mixed | 31 | 1.000000 | 1.000000 | yes |

## Interpretation

If a strategy selects one block and contains the needle block, the offline index
has enough selectivity to support a real sparse search-block prototype.

The next runtime experiment should test whether the same decoded-ratio gain
turns into wall-clock speedup after adding independently decodable search blocks.
