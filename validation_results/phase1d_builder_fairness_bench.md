# zlg Phase 1d builder fairness and robustness shootout

This report compares builder profiles and scratch-memory tradeoffs for the same format:
fixed-lines8192 + mesh-bigram ZBM1 v2.

## Corpus

- Lines: 125000
- Input bytes: 9223684
- Input sha256: fea507e974d3f1bd542665e11e2d93e07c155b670f53b9d5874dce74a3c50c5e
- Needle IP: 198.18.99.123
- Needle line: 100001
- Needle ratio: 0.800

## Compression and build profile

| tool | profile | bytes | vs_gzip6 | wall_s | cpu_s | total_ns | summary_ns | scratch_bytes | bitset_bytes | first_bitset_bytes | grouped_bucket_bytes | pushed_edges | unique_edges | duplicate_ratio |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gzip |  | 839948 | 0 | 0.138565 | 0.137688 |  |  |  |  |  |  |  |  |  |
| zlg | combined | 629176 | -210772 | 0.220672 | 0.211681 | 188486259 | 153197336 | 10122022 | 0 | 0 | 0 | 9833800 | 28255 | 0.997127 |
| zlg | combined-inline-lower-delta | 629176 | -210772 | 0.187701 | 0.190895 | 159861009 | 133604131 | 9511872 | 0 | 0 | 0 | 9223660 | 28255 | 0.996937 |
| zlg | combined-bitset-seen | 629176 | -210772 | 0.095819 | 0.094993 | 70475547 | 49064371 | 11609024 | 2097152 | 0 | 0 | 28255 | 28255 | 0.000000 |
| zlg | combined-lower-only-bitset-seen | 629158 | -210790 | 0.097847 | 0.096141 | 66313354 | 42998088 | 6855136 | 2097152 | 0 | 0 | 28247 | 28247 | 0.000000 |
| zlg | combined-sparse-first-bitset | 629176 | -210772 | 0.140179 | 0.127643 | 136203053 | 106272778 | 9872320 | 0 | 360448 | 0 | 28255 | 28255 | 0.000000 |
| zlg | combined-grouped-buckets | 629176 | -210772 | 0.166349 | 0.172292 | 137004571 | 112165489 | 3722600 | 0 | 0 | 3706160 | 9223660 | 28255 | 0.996937 |
| zlg | combined-bucket256 | 629176 | -210772 | 0.199734 | 0.198782 | 171096490 | 144719056 | 19629798 | 0 | 0 | 0 | 9833800 | 28255 | 0.997127 |
| zlg | combined-radix | 629176 | -210772 | 0.244754 | 0.244209 | 216588086 | 188094649 | 19629798 | 0 | 0 | 0 | 9833800 | 28255 | 0.997127 |
| zlg | combined-case-raw | 629173 | -210775 | 0.155736 | 0.158940 | 128032291 | 104186587 | 4757984 | 0 | 0 | 0 | 9223652 | 28252 | 0.996937 |
| zlg | combined-lower-only | 629158 | -210790 | 0.177325 | 0.169384 | 149837567 | 123063698 | 4757984 | 0 | 0 | 0 | 9223652 | 28247 | 0.996938 |

## Build profile ranking

| rank | profile | wall_s | total_ns | summary_ns | scratch_bytes | bitset_bytes | first_bitset_bytes | grouped_bucket_bytes | pushed_edges | unique_edges | duplicate_ratio | bytes |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | combined-bitset-seen | 0.095819 | 70475547 | 49064371 | 11609024 | 2097152 | 0 | 0 | 28255 | 28255 | 0.000000 | 629176 |
| 2 | combined-lower-only-bitset-seen | 0.097847 | 66313354 | 42998088 | 6855136 | 2097152 | 0 | 0 | 28247 | 28247 | 0.000000 | 629158 |
| 3 | combined-sparse-first-bitset | 0.140179 | 136203053 | 106272778 | 9872320 | 0 | 360448 | 0 | 28255 | 28255 | 0.000000 | 629176 |
| 4 | combined-case-raw | 0.155736 | 128032291 | 104186587 | 4757984 | 0 | 0 | 0 | 9223652 | 28252 | 0.996937 | 629173 |
| 5 | combined-grouped-buckets | 0.166349 | 137004571 | 112165489 | 3722600 | 0 | 0 | 3706160 | 9223660 | 28255 | 0.996937 | 629176 |
| 6 | combined-lower-only | 0.177325 | 149837567 | 123063698 | 4757984 | 0 | 0 | 0 | 9223652 | 28247 | 0.996938 | 629158 |
| 7 | combined-inline-lower-delta | 0.187701 | 159861009 | 133604131 | 9511872 | 0 | 0 | 0 | 9223660 | 28255 | 0.996937 | 629176 |
| 8 | combined-bucket256 | 0.199734 | 171096490 | 144719056 | 19629798 | 0 | 0 | 0 | 9833800 | 28255 | 0.997127 | 629176 |
| 9 | combined | 0.220672 | 188486259 | 153197336 | 10122022 | 0 | 0 | 0 | 9833800 | 28255 | 0.997127 | 629176 |
| 10 | combined-radix | 0.244754 | 216588086 | 188094649 | 19629798 | 0 | 0 | 0 | 9833800 | 28255 | 0.997127 | 629176 |

## Best non-bitset profile

| profile | wall_s | total_ns | summary_ns | scratch_bytes | grouped_bucket_bytes | pushed_edges | unique_edges | duplicate_ratio | bytes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| combined-case-raw | 0.155736 | 128032291 | 104186587 | 4757984 | 0 | 9223652 | 28252 | 0.996937 | 629173 |

## Search sanity using combined profile

| tool | query | stream | wall_s | cpu_s | decoded_ratio | lines | fixed | rust_regex | pcre2 | fast_path | rejects |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| grep_original | needle_fixed_ip |  | 0.012537 | 0.011142 |  |  |  |  |  |  |  |
| grep_original | common_fixed |  | 0.006084 | 0.005001 |  |  |  |  |  |  |  |
| grep_original | rust_regex_key |  | 0.007042 | 0.005208 |  |  |  |  |  |  |  |
| grep_original | pcre2_lookbehind_key |  | 0.006426 | 0.006179 |  |  |  |  |  |  |  |
| grep_original | pcre2_ip_range_full |  | 0.033145 | 0.031947 |  |  |  |  |  |  |  |
| grep_original | pcre2_ip_range_head1 |  | 0.030853 | 0.032784 |  |  |  |  |  |  |  |
| zgrep | needle_fixed_ip |  | 0.079768 | 0.100000 |  |  |  |  |  |  |  |
| zgrep | common_fixed |  | 0.076533 | 0.089721 |  |  |  |  |  |  |  |
| zgrep | rust_regex_key |  | 0.078340 | 0.092810 |  |  |  |  |  |  |  |
| zgrep | pcre2_lookbehind_key |  | 0.078563 | 0.108636 |  |  |  |  |  |  |  |
| zgrep | pcre2_ip_range_full |  | 0.078003 | 0.121818 |  |  |  |  |  |  |  |
| zgrep | pcre2_ip_range_head1 |  | 0.074988 | 0.120212 |  |  |  |  |  |  |  |
| zlg | needle_fixed_ip | False | 0.018404 | 0.016698 | 0.066150 | 8192 | 8192 | 0 | 0 | 0 | 0 |
| zlg | needle_fixed_ip | True | 0.014783 | 0.015213 | 0.066150 | 8192 | 8192 | 0 | 0 | 0 | 0 |
| zlg | common_fixed | False | 0.119564 | 0.112839 | 1.000000 | 125000 | 125000 | 0 | 0 | 0 | 0 |
| zlg | common_fixed | True | 0.051294 | 0.051652 | 1.000000 | 125000 | 125000 | 0 | 0 | 0 | 0 |
| zlg | rust_regex_key | False | 0.117502 | 0.116998 | 1.000000 | 125000 | 0 | 1871 | 0 | 0 | 123129 |
| zlg | rust_regex_key | True | 0.048110 | 0.049405 | 1.000000 | 125000 | 0 | 1871 | 0 | 0 | 123129 |
| zlg | pcre2_lookbehind_key | False | 0.107390 | 0.106802 | 1.000000 | 125000 | 0 | 0 | 0 | 1871 | 123129 |
| zlg | pcre2_lookbehind_key | True | 0.044895 | 0.043407 | 1.000000 | 125000 | 0 | 0 | 0 | 1871 | 123129 |
| zlg | pcre2_ip_range_full | False | 0.046582 | 0.046606 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |
| zlg | pcre2_ip_range_full | True | 0.039984 | 0.038501 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |
| zlg | pcre2_ip_range_head1 | False | 0.046768 | 0.046335 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |
| zlg | pcre2_ip_range_head1 | True | 0.028137 | 0.027653 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |

## Interpretation guide

- `combined` is the Phase 1a/1b winner and remains the control.
- `combined-case-raw` stores exact byte edges only and is a case-sensitive control.
- `combined-lower-only` stores lowercase-normalized edges only and is an experimental permissive skip filter.
- `combined-inline-lower-delta` stores original edges and only adds lowercase edges when they differ.
- `combined-bitset-seen` deduplicates with a reusable 2 MiB u24 presence bitset before sorting.
- `combined-lower-only-bitset-seen` is lower-only and experimental; it is not semantically equivalent for case-sensitive uppercase queries.
- `combined-sparse-first-bitset` uses a sparse first-byte to two-byte-suffix bitset. It is baseline-equivalent and allocates 8 KiB only for first bytes touched during the run.
- `combined-grouped-buckets` uses grouped first-byte arrays: digit, uppercase, lowercase a-z buckets, and ordered spill buckets. It is baseline-equivalent and avoids a full u24 bitset.
- `combined-bucket256` buckets by high byte before sorting and deduping smaller ranges.
- Only `combined`, `combined-inline-lower-delta`, `combined-bitset-seen`, `combined-sparse-first-bitset`, `combined-grouped-buckets`, `combined-bucket256`, and `combined-radix` are intended to preserve baseline search pruning semantics.
- `combined-case-raw`, `combined-lower-only`, and `combined-lower-only-bitset-seen` are controls with narrower semantics.
- This phase does not change the on-disk format.
