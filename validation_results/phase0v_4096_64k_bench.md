# zlg Phase 0v 4096 vs 64K benchmark

This report compares the focused mesh-bigram candidate at fixed-lines4096
and fixed-lines64k against no-index zlg, gzip/zgrep, and original grep.

## Corpus

- Lines: 125000
- Input bytes: 9223684
- Input sha256: fea507e974d3f1bd542665e11e2d93e07c155b670f53b9d5874dce74a3c50c5e
- Needle IP: 198.18.99.123
- Needle line: 100001
- Needle ratio: 0.800
- gzip available: True
- zgrep available: True
- grep available: True
- /usr/bin/time available: False

## Compression and storage

| tool | policy | summary | bytes | vs_gzip6 | overhead_vs_none | wall_s | cpu_s | max_rss_kb |
|---|---|---|---:|---:|---:|---:|---:|---:|
| gzip |  |  | 839949 |  |  | 0.102660 |  |  |
| zlg | fixed-lines4096 | mesh-bigram | 841541 | 1592 | 207452 | 0.123434 |  |  |
| zlg | fixed-lines4096 | none | 634089 | -205860 | 0 | 0.039663 |  |  |
| zlg | fixed-lines64k | mesh-bigram | 601245 | -238704 | 17564 | 0.404812 |  |  |
| zlg | fixed-lines64k | none | 583681 | -256268 | 0 | 0.086592 |  |  |

## Decompression

| tool | policy | summary | wall_s | cpu_s | max_rss_kb |
|---|---|---|---:|---:|---:|
| gzip |  |  | 0.034365 |  |  |
| zlg | fixed-lines4096 | mesh-bigram | 0.016330 |  |  |
| zlg | fixed-lines4096 | none | 0.016502 |  |  |
| zlg | fixed-lines64k | mesh-bigram | 0.057735 |  |  |
| zlg | fixed-lines64k | none | 0.056945 |  |  |

## Search

| tool | policy | summary | query | mode | wall_s | cpu_s | max_rss_kb | decoded_ratio | chunks_decoded | chunks_total | matches | available |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| grep_original |  |  | needle_fixed_ip | fixed | 0.009653 |  |  |  |  |  |  | yes |
| grep_original |  |  | general_fixed_failed_password | fixed | 0.005370 |  |  |  |  |  |  | yes |
| grep_original |  |  | fancy_regex_key_value | fancy_regex | 0.005222 |  |  |  |  |  |  | yes |
| zgrep |  |  | needle_fixed_ip | fixed | 0.065080 |  |  |  |  |  |  | yes |
| zgrep |  |  | general_fixed_failed_password | fixed | 0.059217 |  |  |  |  |  |  | yes |
| zgrep |  |  | fancy_regex_key_value | fancy_regex | 0.061678 |  |  |  |  |  |  | yes |
| zlg | fixed-lines4096 | mesh-bigram | needle_fixed_ip | fixed | 0.011236 |  |  | 0.032986 | 1 | 31 | 1 | yes |
| zlg | fixed-lines4096 | mesh-bigram | general_fixed_failed_password | fixed | 0.029170 |  |  | 1.000000 | 31 | 31 | 945 | yes |
| zlg | fixed-lines4096 | mesh-bigram | fancy_regex_key_value | fancy_regex | 0.330420 |  |  | 1.000000 | 31 | 31 | 1871 | yes |
| zlg | fixed-lines4096 | none | needle_fixed_ip | fixed | 0.028747 |  |  | 1.000000 | 31 | 31 | 1 | yes |
| zlg | fixed-lines4096 | none | general_fixed_failed_password | fixed | 0.030134 |  |  | 1.000000 | 31 | 31 | 945 | yes |
| zlg | fixed-lines4096 | none | fancy_regex_key_value | fancy_regex | 0.322684 |  |  | 1.000000 | 31 | 31 | 1871 | yes |
| zlg | fixed-lines64k | mesh-bigram | needle_fixed_ip | fixed | 0.041509 |  |  | 0.477707 | 1 | 2 | 1 | yes |
| zlg | fixed-lines64k | mesh-bigram | general_fixed_failed_password | fixed | 0.072667 |  |  | 1.000000 | 2 | 2 | 945 | yes |
| zlg | fixed-lines64k | mesh-bigram | fancy_regex_key_value | fancy_regex | 0.347767 |  |  | 1.000000 | 2 | 2 | 1871 | yes |
| zlg | fixed-lines64k | none | needle_fixed_ip | fixed | 0.072090 |  |  | 1.000000 | 2 | 2 | 1 | yes |
| zlg | fixed-lines64k | none | general_fixed_failed_password | fixed | 0.070893 |  |  | 1.000000 | 2 | 2 | 945 | yes |
| zlg | fixed-lines64k | none | fancy_regex_key_value | fancy_regex | 0.364420 |  |  | 1.000000 | 2 | 2 | 1871 | yes |

## Interpretation guide

- `fixed-lines4096` is the new storage/search compromise candidate.
- `fixed-lines64k` is the compression-friendly baseline candidate.
- `mesh-bigram` is the only indexed candidate in this phase.
- `none` shows the cost of zlg chunking without search summaries.
- `grep_original` measures plain grep over the uncompressed corpus.
- `zgrep` measures gzip-compressed search when available.
- CPU fields come from `/usr/bin/time -v` when available.
