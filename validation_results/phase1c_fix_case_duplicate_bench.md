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
| gzip |  | 839948 | 0 | 0.162405 | 0.160375 |  |  |  |  |  |  |  |  |  |
| zlg | combined | 629176 | -210772 | 0.234926 | 0.233473 | 156197684 | 34149507 | 1150229 | 192470135 | 33871 | 9223652 | 9833800 | 28255 | 0.997127 |
| zlg | combined-case-raw | 629173 | -210775 | 0.210209 | 0.206321 | 136798701 | 40616860 | 1612990 | 179855302 | 33868 | 9223652 | 9223652 | 28252 | 0.996937 |
| zlg | combined-lower-only | 629158 | -210790 | 0.228404 | 0.225300 | 152413371 | 31670877 | 994988 | 186002515 | 33853 | 9223652 | 9223652 | 28247 | 0.996938 |
| zlg | combined-inline-lower-delta | 629176 | -210772 | 0.245052 | 0.236256 | 169692068 | 35559076 | 1281599 | 207337683 | 33871 | 9223652 | 9223660 | 28255 | 0.996937 |
| zlg | combined-bitset-seen | 629176 | -210772 | 0.139716 | 0.148916 | 74338768 | 34556351 | 1031894 | 110929024 | 33871 | 9223652 | 28255 | 28255 | 0.000000 |
| zlg | combined-bucket256 | 629176 | -210772 | 0.257662 | 0.252342 | 179016244 | 35576546 | 1184139 | 216638751 | 33871 | 9223652 | 9833800 | 28255 | 0.997127 |

## Build profile ranking

| rank | profile | wall_s | total_ns | summary_ns | pushed_edges | unique_edges | duplicate_ratio | bytes |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | combined-bitset-seen | 0.139716 | 110929024 | 74338768 | 28255 | 28255 | 0.000000 | 629176 |
| 2 | combined-case-raw | 0.210209 | 179855302 | 136798701 | 9223652 | 28252 | 0.996937 | 629173 |
| 3 | combined-lower-only | 0.228404 | 186002515 | 152413371 | 9223652 | 28247 | 0.996938 | 629158 |
| 4 | combined | 0.234926 | 192470135 | 156197684 | 9833800 | 28255 | 0.997127 | 629176 |
| 5 | combined-inline-lower-delta | 0.245052 | 207337683 | 169692068 | 9223660 | 28255 | 0.996937 | 629176 |
| 6 | combined-bucket256 | 0.257662 | 216638751 | 179016244 | 9833800 | 28255 | 0.997127 | 629176 |

## Best non-bitset profile

| profile | wall_s | total_ns | summary_ns | pushed_edges | unique_edges | duplicate_ratio | bytes |
|---|---:|---:|---:|---:|---:|---:|---:|
| combined-case-raw | 0.210209 | 179855302 | 136798701 | 9223652 | 28252 | 0.996937 | 629173 |

## Search sanity using combined profile

| tool | query | stream | wall_s | cpu_s | decoded_ratio | lines | fixed | rust_regex | pcre2 | fast_path | rejects |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| grep_original | needle_fixed_ip |  | 0.016227 | 0.015397 |  |  |  |  |  |  |  |
| grep_original | common_fixed |  | 0.008713 | 0.007857 |  |  |  |  |  |  |  |
| grep_original | rust_regex_key |  | 0.011062 | 0.010789 |  |  |  |  |  |  |  |
| grep_original | pcre2_lookbehind_key |  | 0.008190 | 0.009152 |  |  |  |  |  |  |  |
| grep_original | pcre2_ip_range_full |  | 0.035266 | 0.033639 |  |  |  |  |  |  |  |
| grep_original | pcre2_ip_range_head1 |  | 0.034011 | 0.032937 |  |  |  |  |  |  |  |
| zgrep | needle_fixed_ip |  | 0.101380 | 0.125265 |  |  |  |  |  |  |  |
| zgrep | common_fixed |  | 0.101555 | 0.123083 |  |  |  |  |  |  |  |
| zgrep | rust_regex_key |  | 0.112023 | 0.124158 |  |  |  |  |  |  |  |
| zgrep | pcre2_lookbehind_key |  | 0.101184 | 0.122026 |  |  |  |  |  |  |  |
| zgrep | pcre2_ip_range_full |  | 0.109148 | 0.151259 |  |  |  |  |  |  |  |
| zgrep | pcre2_ip_range_head1 |  | 0.122838 | 0.159882 |  |  |  |  |  |  |  |
| zlg | needle_fixed_ip | False | 0.031243 | 0.030431 | 0.066150 | 8192 | 8192 | 0 | 0 | 0 | 0 |
| zlg | needle_fixed_ip | True | 0.021485 | 0.020752 | 0.066150 | 8192 | 8192 | 0 | 0 | 0 | 0 |
| zlg | common_fixed | False | 0.160522 | 0.159562 | 1.000000 | 125000 | 125000 | 0 | 0 | 0 | 0 |
| zlg | common_fixed | True | 0.066038 | 0.062747 | 1.000000 | 125000 | 125000 | 0 | 0 | 0 | 0 |
| zlg | rust_regex_key | False | 0.152204 | 0.151325 | 1.000000 | 125000 | 0 | 1871 | 0 | 0 | 123129 |
| zlg | rust_regex_key | True | 0.065618 | 0.064820 | 1.000000 | 125000 | 0 | 1871 | 0 | 0 | 123129 |
| zlg | pcre2_lookbehind_key | False | 0.142091 | 0.146653 | 1.000000 | 125000 | 0 | 0 | 0 | 1871 | 123129 |
| zlg | pcre2_lookbehind_key | True | 0.065003 | 0.063806 | 1.000000 | 125000 | 0 | 0 | 0 | 1871 | 123129 |
| zlg | pcre2_ip_range_full | False | 0.058747 | 0.057913 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |
| zlg | pcre2_ip_range_full | True | 0.035448 | 0.035112 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |
| zlg | pcre2_ip_range_head1 | False | 0.059226 | 0.058386 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |
| zlg | pcre2_ip_range_head1 | True | 0.037590 | 0.035263 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |

## Interpretation guide

- `combined` is the Phase 1a/1b winner and remains the control.
- `combined-case-raw` stores exact byte edges only and is a case-sensitive control.
- `combined-lower-only` stores lowercase-normalized edges only and is an experimental permissive skip filter.
- `combined-inline-lower-delta` stores original edges and only adds lowercase edges when they differ.
- `combined-bitset-seen` deduplicates with a reusable 2 MiB u24 presence bitset before sorting.
- `combined-bucket256` buckets by high byte before sorting and deduping smaller ranges.
- All profiles should produce equivalent search behavior and compatible ZBM1 v2 summaries.
- This phase does not change the on-disk format.
