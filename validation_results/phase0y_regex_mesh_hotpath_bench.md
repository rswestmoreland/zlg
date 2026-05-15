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
| gzip | compress | 957563 |  |  |  |  | 0.096940 | 0.094401 |
| gzip | decompress |  |  |  |  |  | 0.038780 | 0.038370 |
| zlg | compress | 617291 | 145053930487808 | 0 | 64 | 0 | 0.167841 | 0.168375 |
| zlg | decompress | 617291 | 145053930487808 | 0 | 64 | 0 | 0.022686 | 0.022373 |

## Search hot-path counters

| tool | mode | query | wall_s | cpu_s | decoded_ratio | matches | lines | fixed | rust_regex | pcre2 | fast_path | prefilter_rejects |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| grep_original | grep_original | needle_fixed_ip | 0.009202 | 0.008695 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | needle_fixed_ip | 0.063145 | 0.083802 |  |  |  |  |  |  |  |  |
| zlg | full | needle_fixed_ip | 0.012951 | 0.012422 | 0.056330 | 1 | 8192 | 8192 | 0 | 0 | 0 | 0 |
| zlg | stream | needle_fixed_ip | 0.009440 | 0.009104 | 0.056330 | 1 | 8192 | 8192 | 0 | 0 | 0 | 0 |
| grep_original | grep_original | common_fixed | 0.009016 | 0.008718 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | common_fixed | 0.066368 | 0.079305 |  |  |  |  |  |  |  |  |
| zlg | full | common_fixed | 0.022099 | 0.023511 | 0.176222 | 189 | 26696 | 26696 | 0 | 0 | 0 | 0 |
| zlg | stream | common_fixed | 0.015685 | 0.015344 | 0.176222 | 189 | 26696 | 26696 | 0 | 0 | 0 | 0 |
| grep_original | grep_original | rust_regex_key | 0.005400 | 0.005013 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | rust_regex_key | 0.074842 | 0.088431 |  |  |  |  |  |  |  |  |
| zlg | full | rust_regex_key | 0.041944 | 0.041471 | 1.000000 | 100259 | 125000 | 0 | 100259 | 0 | 0 | 24741 |
| zlg | stream | rust_regex_key | 0.039056 | 0.038436 | 1.000000 | 100259 | 125000 | 0 | 100259 | 0 | 0 | 24741 |
| grep_original | grep_original | pcre2_lookbehind_key | 0.006062 | 0.004794 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | pcre2_lookbehind_key | 0.065897 | 0.071926 |  |  |  |  |  |  |  |  |
| zlg | full | pcre2_lookbehind_key | 0.041554 | 0.042334 | 1.000000 | 100259 | 125000 | 0 | 0 | 0 | 100259 | 24741 |
| zlg | stream | pcre2_lookbehind_key | 0.038001 | 0.038622 | 1.000000 | 100259 | 125000 | 0 | 0 | 0 | 100259 | 24741 |
| grep_original | grep_original | pcre2_ip_range_full | 0.004649 | 0.004400 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | pcre2_ip_range_full | 0.065782 | 0.077806 |  |  |  |  |  |  |  |  |
| zlg | full | pcre2_ip_range_full | 0.047909 | 0.047116 | 0.880108 | 100000 | 106496 | 0 | 0 | 100000 | 0 | 6496 |
| zlg | stream | pcre2_ip_range_full | 0.043686 | 0.043336 | 0.880108 | 100000 | 106496 | 0 | 0 | 100000 | 0 | 6496 |
| grep_original | grep_original | pcre2_ip_range_head1 | 0.009536 | 0.013459 |  |  |  |  |  |  |  |  |
| zgrep | zgrep | pcre2_ip_range_head1 | 0.031451 | 0.049788 |  |  |  |  |  |  |  |  |
| zlg | full | pcre2_ip_range_head1 | 0.012370 | 0.011999 | 0.067914 | 1 | 1 | 0 | 0 | 1 | 0 | 0 |
| zlg | stream | pcre2_ip_range_head1 | 0.006733 | 0.006434 | 0.005681 | 1 | 1 | 0 | 0 | 1 | 0 | 0 |

## Interpretation guide

- `pcre2_calls` should drop when the literal prefilter or lookbehind fast path is effective.
- `fast_path_calls` is used for simple positive-lookbehind extraction such as `(?<=key=")[^"]+`.
- `prefilter_rejects` shows how many lines were rejected before invoking Rust regex or PCRE2.
- Storage components split the zlg total into compressed payload, mesh summary, chunk headers, and directory/footer bytes.
