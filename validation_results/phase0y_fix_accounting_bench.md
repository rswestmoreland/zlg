# zlg Phase 0y regex hot-path and mesh-overhead benchmark

## Corpus

- Lines: 125000
- Input bytes: 11536300
- Input sha256: 90dcbd421feac85487d6d0b90a7e0969c39c3a3575667a06d39d09c81eae53bb
- Needle IP: 198.18.99.123
- Needle line: 100001
- Range-hit lines: 100000

## Storage components

| tool | operation | bytes | payload | summary | chunk_headers | directory_footer | wall_s | cpu_s |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| gzip | compress | 957563 |  |  |  |  | 0.148838 | 0.148568 |
| gzip | decompress |  |  |  |  |  | 0.056620 | 0.056256 |
| zlg | compress | 617291 | 514915 | 100232 | 1024 | 1088 | 0.233894 | 0.233081 |
| zlg | decompress | 617291 | 514915 | 100232 | 1024 | 1088 | 0.034824 | 0.036159 |

## Search hot-path counters

| tool | mode | query | wall_s | cpu_s | decoded_ratio | matches | lines | fixed | rust_regex | pcre2 | fast_path | prefilter_rejects |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| grep_original | grep_original | needle_fixed_ip | 0.016020 | 0.012987 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | needle_fixed_ip | 0.103278 | 0.126922 |  |  |  |  |  |  |  |  |
| zlg | full | needle_fixed_ip | 0.019358 | 0.017866 | 0.056330 | 1 | 8192 | 8192 | 0 | 0 | 0 | 0 |
| zlg | stream | needle_fixed_ip | 0.014755 | 0.013494 | 0.056330 | 1 | 8192 | 8192 | 0 | 0 | 0 | 0 |
| grep_original | grep_original | common_fixed | 0.012311 | 0.011792 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | common_fixed | 0.092325 | 0.109248 |  |  |  |  |  |  |  |  |
| zlg | full | common_fixed | 0.028679 | 0.028078 | 0.176222 | 189 | 26696 | 26696 | 0 | 0 | 0 | 0 |
| zlg | stream | common_fixed | 0.023329 | 0.022943 | 0.176222 | 189 | 26696 | 26696 | 0 | 0 | 0 | 0 |
| grep_original | grep_original | rust_regex_key | 0.006040 | 0.005609 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | rust_regex_key | 0.086079 | 0.102577 |  |  |  |  |  |  |  |  |
| zlg | full | rust_regex_key | 0.060598 | 0.057196 | 1.000000 | 100259 | 125000 | 0 | 100259 | 0 | 0 | 24741 |
| zlg | stream | rust_regex_key | 0.060105 | 0.059864 | 1.000000 | 100259 | 125000 | 0 | 100259 | 0 | 0 | 24741 |
| grep_original | grep_original | pcre2_lookbehind_key | 0.006681 | 0.006231 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | pcre2_lookbehind_key | 0.088851 | 0.104325 |  |  |  |  |  |  |  |  |
| zlg | full | pcre2_lookbehind_key | 0.069258 | 0.068395 | 1.000000 | 100259 | 125000 | 0 | 0 | 0 | 100259 | 24741 |
| zlg | stream | pcre2_lookbehind_key | 0.062568 | 0.065184 | 1.000000 | 100259 | 125000 | 0 | 0 | 0 | 100259 | 24741 |
| grep_original | grep_original | pcre2_ip_range_full | 0.007865 | 0.006879 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | pcre2_ip_range_full | 0.097823 | 0.111200 |  |  |  |  |  |  |  |  |
| zlg | full | pcre2_ip_range_full | 0.073986 | 0.073567 | 0.880108 | 100000 | 106496 | 0 | 0 | 100000 | 0 | 6496 |
| zlg | stream | pcre2_ip_range_full | 0.067948 | 0.070428 | 0.880108 | 100000 | 106496 | 0 | 0 | 100000 | 0 | 6496 |
| grep_original | grep_original | pcre2_ip_range_head1 | 0.016048 | 0.025076 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | pcre2_ip_range_head1 | 0.048265 | 0.067553 |  |  |  |  |  |  |  |  |
| zlg | full | pcre2_ip_range_head1 | 0.018067 | 0.017648 | 0.067914 | 1 | 1 | 0 | 0 | 1 | 0 | 0 |
| zlg | stream | pcre2_ip_range_head1 | 0.010264 | 0.009969 | 0.005681 | 1 | 1 | 0 | 0 | 1 | 0 | 0 |

## Interpretation guide

- `pcre2_calls` should drop when the literal prefilter or lookbehind fast path is effective.
- `fast_path_calls` is used for simple positive-lookbehind extraction such as `(?<=key=")[^"]+`.
- `prefilter_rejects` shows how many lines were rejected before invoking Rust regex or PCRE2.
- Storage components split the zlg total into compressed payload, mesh summary, chunk headers, and directory/footer bytes.
