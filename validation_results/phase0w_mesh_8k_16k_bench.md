# zlg Phase 0w mesh-bigram 8K/16K benchmark

This report compares mesh-bigram only at fixed-lines4096, fixed-lines8192,
fixed-lines16384, and fixed-lines64k against gzip/zgrep and original grep.

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
- external time available: False

## Compression and storage

| tool | policy | summary | bytes | vs_original | vs_gzip6 | wall_s | cpu_s | max_rss_kb |
|---|---|---|---:|---:|---:|---:|---:|---:|
| gzip |  |  | 839949 | -8383735 | 0 | 0.173211 | 0.160250 | 21068 |
| zlg | fixed-lines4096 | mesh-bigram | 841541 | -8382143 | 1592 | 0.224923 | 0.233965 |  |
| zlg | fixed-lines8192 | mesh-bigram | 708445 | -8515239 | -131504 | 0.292750 | 0.278954 |  |
| zlg | fixed-lines16384 | mesh-bigram | 645853 | -8577831 | -194096 | 0.370816 | 0.362099 |  |
| zlg | fixed-lines64k | mesh-bigram | 601245 | -8622439 | -238704 | 0.757531 | 0.744979 | 19360 |

## Decompression

| tool | policy | summary | wall_s | cpu_s | max_rss_kb |
|---|---|---|---:|---:|---:|
| gzip |  |  | 0.055702 | 0.054440 |  |
| zlg | fixed-lines4096 | mesh-bigram | 0.033678 | 0.036076 |  |
| zlg | fixed-lines8192 | mesh-bigram | 0.040172 | 0.040733 |  |
| zlg | fixed-lines16384 | mesh-bigram | 0.137802 | 0.128372 |  |
| zlg | fixed-lines64k | mesh-bigram | 0.119341 | 0.113675 |  |

## Search

| tool | policy | query | mode | wall_s | cpu_s | max_rss_kb | decoded_ratio | chunks_decoded | chunks_total | matches | available |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| grep_original |  | needle_fixed_ip | fixed | 0.019656 | 0.018378 |  |  |  |  |  | yes |
| grep_original |  | common_fixed_failed_password | fixed | 0.022504 | 0.021543 |  |  |  |  |  | yes |
| grep_original |  | regex_key_value | rust_regex | 0.010291 | 0.007950 |  |  |  |  |  | yes |
| grep_original |  | fancy_regex_key_value | fancy_regex | 0.009603 | 0.008209 |  |  |  |  |  | yes |
| zgrep |  | needle_fixed_ip | fixed | 0.112846 | 0.137962 |  |  |  |  |  | yes |
| zgrep |  | common_fixed_failed_password | fixed | 0.099043 | 0.137369 |  |  |  |  |  | yes |
| zgrep |  | regex_key_value | rust_regex | 0.101191 | 0.123723 |  |  |  |  |  | yes |
| zgrep |  | fancy_regex_key_value | fancy_regex | 0.101401 | 0.124869 |  |  |  |  |  | yes |
| zlg | fixed-lines4096 | needle_fixed_ip | fixed | 0.019650 | 0.018468 |  | 0.032986 | 1 | 31 | 1 | yes |
| zlg | fixed-lines4096 | common_fixed_failed_password | fixed | 0.062448 | 0.061416 |  | 1.000000 | 31 | 31 | 945 | yes |
| zlg | fixed-lines4096 | regex_key_value | rust_regex | 0.051639 | 0.051186 |  | 1.000000 | 31 | 31 | 1871 | yes |
| zlg | fixed-lines4096 | fancy_regex_key_value | fancy_regex | 0.625539 | 0.616626 |  | 1.000000 | 31 | 31 | 1871 | yes |
| zlg | fixed-lines8192 | needle_fixed_ip | fixed | 0.028657 | 0.028001 |  | 0.066150 | 1 | 16 | 1 | yes |
| zlg | fixed-lines8192 | common_fixed_failed_password | fixed | 0.067396 | 0.067173 |  | 1.000000 | 16 | 16 | 945 | yes |
| zlg | fixed-lines8192 | regex_key_value | rust_regex | 0.063047 | 0.062156 |  | 1.000000 | 16 | 16 | 1871 | yes |
| zlg | fixed-lines8192 | fancy_regex_key_value | fancy_regex | 0.642295 | 0.637511 |  | 1.000000 | 16 | 16 | 1871 | yes |
| zlg | fixed-lines16384 | needle_fixed_ip | fixed | 0.037756 | 0.037614 |  | 0.132476 | 1 | 8 | 1 | yes |
| zlg | fixed-lines16384 | common_fixed_failed_password | fixed | 0.149809 | 0.153397 |  | 1.000000 | 8 | 8 | 945 | yes |
| zlg | fixed-lines16384 | regex_key_value | rust_regex | 0.154106 | 0.152794 |  | 1.000000 | 8 | 8 | 1871 | yes |
| zlg | fixed-lines16384 | fancy_regex_key_value | fancy_regex | 0.733850 | 0.731988 |  | 1.000000 | 8 | 8 | 1871 | yes |
| zlg | fixed-lines64k | needle_fixed_ip | fixed | 0.086312 | 0.082843 |  | 0.477707 | 1 | 2 | 1 | yes |
| zlg | fixed-lines64k | common_fixed_failed_password | fixed | 0.141099 | 0.139871 |  | 1.000000 | 2 | 2 | 945 | yes |
| zlg | fixed-lines64k | regex_key_value | rust_regex | 0.141390 | 0.139503 |  | 1.000000 | 2 | 2 | 1871 | yes |
| zlg | fixed-lines64k | fancy_regex_key_value | fancy_regex | 0.747506 | 0.741947 |  | 1.000000 | 2 | 2 | 1871 | yes |

## Interpretation guide

- `fixed-lines8192` and `fixed-lines16384` are the new candidates.
- `fixed-lines4096` remains as the prior selective-search reference.
- `fixed-lines64k` remains as the compression-first reference.
- Non-mesh zlg candidates are intentionally omitted from this phase.
- `regex_key_value` uses Rust's standard regex path.
- `fancy_regex_key_value` uses fancy-regex with lookbehind.
- CPU/RSS values use `/usr/bin/time -v` when available and Python `resource` fallback otherwise.
