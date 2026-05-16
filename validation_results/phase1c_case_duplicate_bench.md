# zlg Phase 1c case and duplicate-control shootout

This report compares case and duplicate-control profiles for the same format:
fixed-lines8192 + mesh-bigram ZBM1 v2.

## Corpus

- Lines: 125000
- Input bytes: 9223684
- Input sha256: fea507e974d3f1bd542665e11e2d93e07c155b670f53b9d5874dce74a3c50c5e
- Needle IP: 198.18.99.123
- Needle line: 100001
- Needle ratio: 0.800

## Compression and build profile

| tool | profile | bytes | vs_gzip6 | wall_s | cpu_s | summary_ns | zstd_ns | write_ns | total_ns | summary_bytes | raw_edges | pushed_edges | unique_edges | duplicate_ratio |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gzip |  | 839948 | 0 | 0.140944 | 0.139832 |  |  |  |  |  |  |  |  |  |
| zlg | combined | 886897 | 46949 | 0.193868 | 0.197551 | 133303203 | 23410825 | 1049846 | 158439862 | 291592 | 9223652 | 9833800 | 28255 | 0.997127 |
| zlg | combined-case-raw | 886885 | 46937 | 0.159804 | 0.156670 | 106060471 | 20690705 | 897052 | 128341739 | 291580 | 9223652 | 9223652 | 28252 | 0.996937 |
| zlg | combined-lower-only | 886825 | 46877 | 0.176361 | 0.176460 | 123883875 | 21957981 | 862226 | 147895026 | 291520 | 9223652 | 9223652 | 28247 | 0.996938 |
| zlg | combined-inline-lower-delta | 886897 | 46949 | 0.186152 | 0.180399 | 131426076 | 21565371 | 1066323 | 154713444 | 291592 | 9223652 | 9223660 | 28255 | 0.996937 |
| zlg | combined-bitset-seen | 886897 | 46949 | 0.104833 | 0.104831 | 49495149 | 21752996 | 717368 | 72641487 | 291592 | 9223652 | 28255 | 28255 | 0.000000 |
| zlg | combined-bucket256 | 886897 | 46949 | 0.196372 | 0.192086 | 133121259 | 21294815 | 989442 | 156077391 | 291592 | 9223652 | 9833800 | 28255 | 0.997127 |

## Search sanity using combined profile

| tool | query | stream | wall_s | cpu_s | decoded_ratio | lines | fixed | rust_regex | pcre2 | fast_path | rejects |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| grep_original | needle_fixed_ip |  | 0.012717 | 0.012353 |  |  |  |  |  |  |  |
| grep_original | common_fixed |  | 0.005455 | 0.005059 |  |  |  |  |  |  |  |
| grep_original | rust_regex_key |  | 0.006286 | 0.005599 |  |  |  |  |  |  |  |
| grep_original | pcre2_lookbehind_key |  | 0.005634 | 0.005135 |  |  |  |  |  |  |  |
| grep_original | pcre2_ip_range_full |  | 0.030320 | 0.029547 |  |  |  |  |  |  |  |
| grep_original | pcre2_ip_range_head1 |  | 0.031355 | 0.031000 |  |  |  |  |  |  |  |
| zgrep | needle_fixed_ip |  | 0.078744 | 0.099333 |  |  |  |  |  |  |  |
| zgrep | common_fixed |  | 0.075529 | 0.090838 |  |  |  |  |  |  |  |
| zgrep | rust_regex_key |  | 0.076901 | 0.087920 |  |  |  |  |  |  |  |
| zgrep | pcre2_lookbehind_key |  | 0.086209 | 0.098452 |  |  |  |  |  |  |  |
| zgrep | pcre2_ip_range_full |  | 0.074466 | 0.112641 |  |  |  |  |  |  |  |
| zgrep | pcre2_ip_range_head1 |  | 0.077862 | 0.115684 |  |  |  |  |  |  |  |
| zlg | needle_fixed_ip | no | 0.007907 | 0.007412 |  |  |  |  |  |  |  |
| zlg | needle_fixed_ip | yes | 0.007342 | 0.007103 |  |  |  |  |  |  |  |
| zlg | common_fixed | no | 0.015480 | 0.015074 |  |  |  |  |  |  |  |
| zlg | common_fixed | yes | 0.012878 | 0.012297 |  |  |  |  |  |  |  |
| zlg | rust_regex_key | no | 0.019471 | 0.019099 |  |  |  |  |  |  |  |
| zlg | rust_regex_key | yes | 0.014761 | 0.014364 |  |  |  |  |  |  |  |
| zlg | pcre2_lookbehind_key | no | 0.015728 | 0.016299 |  |  |  |  |  |  |  |
| zlg | pcre2_lookbehind_key | yes | 0.012530 | 0.012275 |  |  |  |  |  |  |  |
| zlg | pcre2_ip_range_full | no | 0.007728 | 0.007402 |  |  |  |  |  |  |  |
| zlg | pcre2_ip_range_full | yes | 0.007173 | 0.007092 |  |  |  |  |  |  |  |
| zlg | pcre2_ip_range_head1 | no | 0.007347 | 0.006629 |  |  |  |  |  |  |  |
| zlg | pcre2_ip_range_head1 | yes | 0.007360 | 0.007425 |  |  |  |  |  |  |  |

## Interpretation guide

- `combined` is the Phase 1a/1b winner and remains the control.
- `combined-case-raw` stores exact byte edges only and is a case-sensitive control.
- `combined-lower-only` stores lowercase-normalized edges only and is an experimental permissive skip filter.
- `combined-inline-lower-delta` stores original edges and only adds lowercase edges when they differ.
- `combined-bitset-seen` deduplicates with a reusable 2 MiB u24 presence bitset before sorting.
- `combined-bucket256` buckets by high byte before sorting and deduping smaller ranges.
- All profiles should produce equivalent search behavior and compatible ZBM1 v2 summaries.
- This phase does not change the on-disk format.
