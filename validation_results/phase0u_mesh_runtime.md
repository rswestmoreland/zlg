# zlg Phase 0u sorted bigram mesh runtime probe

This runtime probe focuses on the current winning strategy only:
compact sorted bigram-edge summaries over small search blocks.

## Corpus

- Lines: 125000
- Input bytes: 9223684
- Input sha256: fea507e974d3f1bd542665e11e2d93e07c155b670f53b9d5874dce74a3c50c5e
- Needle IP: 198.18.99.123
- Needle line: 100001
- Needle ratio: 0.800
- gzip available: True
- zgrep available: True
- gzip -6 bytes: 839949
- zgrep seconds: 0.103005

## Runtime/storage table

| policy | summary | bytes | overhead_vs_none | compress_s | grep_s | chunks | decoded | decoded_ratio | gzip6_bytes | zgrep_s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed-lines1024 | bitmap | 2738625 |  | 0.109683 | 0.025135 | 123 | 57 | 0.466813 | 839949 | 0.103005 |
| fixed-lines1024 | mesh-bigram | 1470625 |  | 0.158834 | 0.010785 | 123 | 1 | 0.008222 | 839949 | 0.103005 |
| fixed-lines1024 | none | 714537 | 0 | 0.050897 | 0.041503 | 123 | 123 | 1.000000 | 839949 | 0.103005 |
| fixed-lines2048 | bitmap | 1725111 |  | 0.106623 | 0.034371 | 62 | 53 | 0.868095 | 839949 | 0.103005 |
| fixed-lines2048 | mesh-bigram | 1098891 |  | 0.158247 | 0.012531 | 62 | 1 | 0.016402 | 839949 | 0.103005 |
| fixed-lines2048 | none | 704839 | 0 | 0.049253 | 0.039052 | 62 | 62 | 1.000000 | 839949 | 0.103005 |
| fixed-lines64k | bitmap | 616593 |  | 0.184115 | 0.104714 | 2 | 2 | 1.000000 | 839949 | 0.103005 |
| fixed-lines64k | mesh-bigram | 601245 |  | 0.547044 | 0.061553 | 2 | 1 | 0.477707 | 839949 | 0.103005 |
| fixed-lines64k | none | 583681 | 0 | 0.125547 | 0.102987 | 2 | 2 | 1.000000 | 839949 | 0.103005 |

## Interpretation guide

- `mesh-bigram` is the focused experimental winner from Phase 0t-fix.
- `bitmap` is the previous fixed-size per-block summary baseline.
- `none` is compressed zstd chunks with no search summary.
- `overhead_vs_none` is a direct storage-efficiency estimate for the summary mode.
- A successful mesh candidate should stay below gzip -6 size while decoding fewer chunks than none and preferably beating zgrep on the needle query.
