# zlg Phase 1a build-speed shootout

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
| gzip |  | 839948 | 0 | 0.136913 | 0.137300 |  |  |  |  |  |  |
| zlg | current | 629104 | -210844 | 0.320765 | 0.319562 | 204772555 | 72911955 | 932959 | 279572456 | 33871 | 593089 |
| zlg | mesh-scratch | 629104 | -210844 | 0.192122 | 0.191512 | 124951281 | 36484000 | 725247 | 162949133 | 33871 | 593089 |
| zlg | zstd-bulk | 629176 | -210772 | 0.204903 | 0.211653 | 157530835 | 19934255 | 640351 | 178729830 | 33871 | 593161 |
| zlg | combined | 629176 | -210772 | 0.182186 | 0.182484 | 131361566 | 21936135 | 731516 | 154673749 | 33871 | 593161 |

## Search sanity using combined profile

| tool | query | stream | wall_s | cpu_s | decoded_ratio | lines | fixed | rust_regex | pcre2 | fast_path | rejects |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| grep_original | needle_fixed_ip |  | 0.010928 | 0.010020 |  |  |  |  |  |  |  |
| grep_original | common_fixed |  | 0.005126 | 0.004752 |  |  |  |  |  |  |  |
| grep_original | rust_regex_key |  | 0.005751 | 0.005244 |  |  |  |  |  |  |  |
| grep_original | pcre2_lookbehind_key |  | 0.005505 | 0.005390 |  |  |  |  |  |  |  |
| grep_original | pcre2_ip_range_full |  | 0.030657 | 0.029827 |  |  |  |  |  |  |  |
| grep_original | pcre2_ip_range_head1 |  | 0.030086 | 0.029296 |  |  |  |  |  |  |  |
| zgrep | needle_fixed_ip |  | 0.079357 | 0.093624 |  |  |  |  |  |  |  |
| zgrep | common_fixed |  | 0.079421 | 0.096722 |  |  |  |  |  |  |  |
| zgrep | rust_regex_key |  | 0.088006 | 0.101674 |  |  |  |  |  |  |  |
| zgrep | pcre2_lookbehind_key |  | 0.090432 | 0.106009 |  |  |  |  |  |  |  |
| zgrep | pcre2_ip_range_full |  | 0.084865 | 0.127370 |  |  |  |  |  |  |  |
| zgrep | pcre2_ip_range_head1 |  | 0.078708 | 0.114430 |  |  |  |  |  |  |  |
| zlg | needle_fixed_ip | False | 0.017124 | 0.016305 | 0.066150 | 8192 | 8192 | 0 | 0 | 0 | 0 |
| zlg | needle_fixed_ip | True | 0.013899 | 0.012743 | 0.066150 | 8192 | 8192 | 0 | 0 | 0 | 0 |
| zlg | common_fixed | False | 0.115123 | 0.105657 | 1.000000 | 125000 | 125000 | 0 | 0 | 0 | 0 |
| zlg | common_fixed | True | 0.049377 | 0.048551 | 1.000000 | 125000 | 125000 | 0 | 0 | 0 | 0 |
| zlg | rust_regex_key | False | 0.112347 | 0.120209 | 1.000000 | 125000 | 0 | 1871 | 0 | 0 | 123129 |
| zlg | rust_regex_key | True | 0.048391 | 0.051186 | 1.000000 | 125000 | 0 | 1871 | 0 | 0 | 123129 |
| zlg | pcre2_lookbehind_key | False | 0.107984 | 0.107219 | 1.000000 | 125000 | 0 | 0 | 0 | 1871 | 123129 |
| zlg | pcre2_lookbehind_key | True | 0.045069 | 0.043754 | 1.000000 | 125000 | 0 | 0 | 0 | 1871 | 123129 |
| zlg | pcre2_ip_range_full | False | 0.046175 | 0.048245 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |
| zlg | pcre2_ip_range_full | True | 0.027113 | 0.026612 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |
| zlg | pcre2_ip_range_head1 | False | 0.048491 | 0.047319 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |
| zlg | pcre2_ip_range_head1 | True | 0.027028 | 0.027075 | 0.328588 | 40960 | 0 | 0 | 0 | 0 | 40960 |

## Interpretation guide

- `mesh-scratch` tests reusable mesh buffers.
- `zstd-bulk` tests reusable `zstd::bulk::Compressor` context.
- `combined` enables both variants.
- All profiles should produce equivalent search behavior and compatible ZBM1 v2 summaries.
- This phase does not change the on-disk format.
