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
| gzip | compress | 957563 |  |  |  |  | 0.098379 | 0.097532 |
| gzip | decompress |  |  |  |  |  | 0.038464 | 0.037557 |
| zlg | compress | 546493 | 514915 | 29434 | 1024 | 1088 | 0.159761 | 0.156587 |
| zlg | decompress | 546493 | 514915 | 29434 | 1024 | 1088 | 0.021153 | 0.020583 |

## Search hot-path counters

| tool | mode | query | wall_s | cpu_s | decoded_ratio | matches | lines | fixed | rust_regex | pcre2 | fast_path | prefilter_rejects |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| grep_original | grep_original | needle_fixed_ip | 0.008635 | 0.008320 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | needle_fixed_ip | 0.060005 | 0.072554 |  |  |  |  |  |  |  |  |
| zlg | full | needle_fixed_ip | 0.013687 | 0.013227 | 0.056330 | 1 | 8192 | 8192 | 0 | 0 | 0 | 0 |
| zlg | stream | needle_fixed_ip | 0.009367 | 0.008856 | 0.056330 | 1 | 8192 | 8192 | 0 | 0 | 0 | 0 |
| grep_original | grep_original | common_fixed | 0.008251 | 0.008085 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | common_fixed | 0.059130 | 0.072515 |  |  |  |  |  |  |  |  |
| zlg | full | common_fixed | 0.018423 | 0.018395 | 0.176222 | 189 | 26696 | 26696 | 0 | 0 | 0 | 0 |
| zlg | stream | common_fixed | 0.015386 | 0.014996 | 0.176222 | 189 | 26696 | 26696 | 0 | 0 | 0 | 0 |
| grep_original | grep_original | rust_regex_key | 0.004156 | 0.003845 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | rust_regex_key | 0.063060 | 0.069328 |  |  |  |  |  |  |  |  |
| zlg | full | rust_regex_key | 0.041765 | 0.041326 | 1.000000 | 100259 | 125000 | 0 | 100259 | 0 | 0 | 24741 |
| zlg | stream | rust_regex_key | 0.037876 | 0.037035 | 1.000000 | 100259 | 125000 | 0 | 100259 | 0 | 0 | 24741 |
| grep_original | grep_original | pcre2_lookbehind_key | 0.004616 | 0.004381 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | pcre2_lookbehind_key | 0.058619 | 0.066975 |  |  |  |  |  |  |  |  |
| zlg | full | pcre2_lookbehind_key | 0.040989 | 0.042361 | 1.000000 | 100259 | 125000 | 0 | 0 | 0 | 100259 | 24741 |
| zlg | stream | pcre2_lookbehind_key | 0.036135 | 0.036020 | 1.000000 | 100259 | 125000 | 0 | 0 | 0 | 100259 | 24741 |
| grep_original | grep_original | pcre2_ip_range_full | 0.004432 | 0.003900 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | pcre2_ip_range_full | 0.061375 | 0.072428 |  |  |  |  |  |  |  |  |
| zlg | full | pcre2_ip_range_full | 0.047320 | 0.046946 | 0.880108 | 100000 | 106496 | 0 | 0 | 100000 | 0 | 6496 |
| zlg | stream | pcre2_ip_range_full | 0.045612 | 0.045133 | 0.880108 | 100000 | 106496 | 0 | 0 | 100000 | 0 | 6496 |
| grep_original | grep_original | pcre2_ip_range_head1 | 0.009989 | 0.015755 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | pcre2_ip_range_head1 | 0.031450 | 0.047162 |  |  |  |  |  |  |  |  |
| zlg | full | pcre2_ip_range_head1 | 0.011635 | 0.010674 | 0.067914 | 1 | 1 | 0 | 0 | 1 | 0 | 0 |
| zlg | stream | pcre2_ip_range_head1 | 0.006469 | 0.006200 | 0.005681 | 1 | 1 | 0 | 0 | 1 | 0 | 0 |

## Interpretation guide

- `pcre2_calls` should drop when the literal prefilter or lookbehind fast path is effective.
- `fast_path_calls` is used for simple positive-lookbehind extraction such as `(?<=key=")[^"]+`.
- `prefilter_rejects` shows how many lines were rejected before invoking Rust regex or PCRE2.
- Storage components split the zlg total into compressed payload, mesh summary, chunk headers, and directory/footer bytes.
