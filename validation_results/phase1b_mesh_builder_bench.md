# zlg Phase 1b mesh-builder shootout

This report compares implementation profiles for the same format:
fixed-lines8192 + mesh-bigram ZBM1 v2.

## Corpus

- Lines: 125000
- Input bytes: 9223684
- Input sha256: fea507e974d3f1bd542665e11e2d93e07c155b670f53b9d5874dce74a3c50c5e
- Needle IP: 198.18.99.123
- Needle line: 100001
- Needle ratio: 0.800

## Compression and build profile

| tool | profile | bytes | vs_gzip6 | wall_s | cpu_s | summary_ns | zstd_ns | write_ns | total_ns | summary_bytes | payload_bytes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gzip |  | 839948 | 0 | 0.136245 | 0.135419 |  |  |  |  |  |  |
| zlg | current | 629104 | -210844 | 0.319615 | 0.318932 | 207188682 | 70772284 | 865693 | 279783585 | 33871 | 593089 |
| zlg | combined | 629176 | -210772 | 0.190024 | 0.189432 | 125787132 | 24783169 | 797452 | 152110152 | 33871 | 593161 |
| zlg | combined-radix | 629176 | -210772 | 0.274468 | 0.265630 | 185917299 | 27118949 | 926910 | 214778046 | 33871 | 593161 |
| zlg | combined-hash | 629176 | -210772 | 0.262408 | 0.253744 | 208591993 | 26583120 | 1044658 | 236915421 | 33871 | 593161 |

## Search sanity using combined profile

| tool | query | stream | wall_s | cpu_s | decoded_ratio | lines | fixed | rust_regex | pcre2 | fast_path | rejects |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| grep_original | needle_fixed_ip |  | 0.012865 | 0.012317 |  |  |  |  |  |  |  |
| grep_original | common_fixed |  | 0.006283 | 0.005771 |  |  |  |  |  |  |  |
| grep_original | rust_regex_key |  | 0.006546 | 0.006090 |  |  |  |  |  |  |  |
| grep_original | pcre2_lookbehind_key |  | 0.007003 | 0.006594 |  |  |  |  |  |  |  |
| grep_original | pcre2_ip_range_full |  | 0.033666 | 0.031501 |  |  |  |  |  |  |  |
| grep_original | pcre2_ip_range_head1 |  | 0.033505 | 0.034799 |  |  |  |  |  |  |  |
| zgrep | needle_fixed_ip |  | 0.083759 | 0.110205 |  |  |  |  |  |  |  |
| zgrep | common_fixed |  | 0.080353 | 0.095320 |  |  |  |  |  |  |  |
| zgrep | rust_regex_key |  | 0.081166 | 0.096400 |  |  |  |  |  |  |  |
| zgrep | pcre2_lookbehind_key |  | 0.090477 | 0.106223 |  |  |  |  |  |  |  |
| zgrep | pcre2_ip_range_full |  | 0.096143 | 0.132772 |  |  |  |  |  |  |  |
| zgrep | pcre2_ip_range_head1 |  | 0.082429 | 0.122146 |  |  |  |  |  |  |  |
| zlg | needle_fixed_ip | False | 0.017209 | 0.016907 | 0.066150 | 8192 | 8192 | 0 | 0 | 0 | 0 |
| zlg | needle_fixed_ip | True | 0.014458 | 0.012829 | 0.066150 | 8192 | 8192 | 0 | 0 | 0 | 0 |
| zlg | common_fixed | False | 0.107837 | 0.105131 | 1.000000 | 125000 | 125000 | 0 | 0 | 0 | 0 |
| zlg | common_fixed | True | 0.049574 | 0.045309 | 1.000000 | 125000 | 125000 | 0 | 0 | 0 | 0 |
| zlg | rust_regex_key | False | 0.111187 | 0.111708 | 1.000000 | 125000 | 0 | 1871 | 0 | 0 | 123129 |
| zlg | rust_regex_key | True | 0.049278 | 0.050903 | 1.000000 | 125000 | 0 | 1871 | 0 | 0 | 123129 |
| zlg | pcre2_lookbehind_key | False | 0.110160 | 0.111893 | 1.000000 | 125000 | 0 | 0 | 0 | 1871 | 123129 |
| zlg | pcre2_lookbehind_key | True | 0.044629 | 0.044050 | 1.000000 | 125000 | 0 | 0 | 0 | 1871 | 123129 |
| zlg | pcre2_ip_range_full | False | 0.045181 | 0.045172 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |
| zlg | pcre2_ip_range_full | True | 0.028115 | 0.027713 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |
| zlg | pcre2_ip_range_head1 | False | 0.048725 | 0.048274 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |
| zlg | pcre2_ip_range_head1 | True | 0.029290 | 0.029486 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |

## Interpretation guide

- `current` is the pre-optimization baseline.
- `combined` is the Phase 1a winner: reusable mesh scratch plus zstd bulk compressor.
- `combined-radix` keeps zstd bulk but replaces sort_unstable with a u24 radix sort.
- `combined-hash` keeps zstd bulk but deduplicates with a HashSet before sorting.
- All profiles should produce equivalent search behavior and compatible ZBM1 v2 summaries.
- This phase does not change the on-disk format.
