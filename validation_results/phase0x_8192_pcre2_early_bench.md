# zlg Phase 0x 8192 PCRE2 and early-stop benchmark

- Lines: 125000
- Input bytes: 11536300
- Input sha256: 90dcbd421feac85487d6d0b90a7e0969c39c3a3575667a06d39d09c81eae53bb
- Needle IP: 198.18.99.123
- Needle line: 100001
- Range hit lines: 100000

## Compression and decompression

| tool | operation | policy | bytes | vs_gzip6 | wall_s | cpu_s | max_rss_kb |
|---|---|---|---:|---:|---:|---:|---:|
| gzip | compress |  | 957564 | 0 | 0.095832 | 0.095084 | 0 |
| gzip | decompress |  |  |  | 0.039798 | 0.038507 | 0 |
| zlg | compress | fixed-lines8192 | 617291 | -340273 | 0.162467 | 0.161965 | 0 |
| zlg | decompress | fixed-lines8192 | 617291 |  | 0.021770 | 0.020350 | 0 |

## Search

| tool | query | head | wall_s | cpu_s | max_rss_kb | decoded_ratio | decoded_chunks | total_chunks | matches | rc |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| grep_original | needle_fixed_ip |  |  | 0.008421 | 0.008124 | 0 |  |  |  |  |  |  | 0 |
| zgrep | needle_fixed_ip |  |  | 0.072090 | 0.085817 | 0 |  |  |  |  |  |  | 0 |
| zlg | needle_fixed_ip |  | full | 0.012979 | 0.012878 | 0 | 0.056330 | 1 | 16 | 0 | 0 | 1 | 0 |
| zlg | needle_fixed_ip |  | stream | 0.009235 | 0.008963 | 0 | 0.056330 | 1 | 16 | 1 | 0 | 1 | 0 |
| grep_original | common_fixed_failed_password |  |  | 0.007925 | 0.007645 | 0 |  |  |  |  |  |  | 0 |
| zgrep | common_fixed_failed_password |  |  | 0.059833 | 0.072249 | 0 |  |  |  |  |  |  | 0 |
| zlg | common_fixed_failed_password |  | full | 0.017676 | 0.017245 | 0 | 0.176222 | 4 | 16 | 0 | 0 | 189 | 0 |
| zlg | common_fixed_failed_password |  | stream | 0.013216 | 0.012799 | 0 | 0.176222 | 4 | 16 | 4 | 0 | 189 | 0 |
| grep_original | rust_regex_key_value |  |  | 0.004529 | 0.004277 | 0 |  |  |  |  |  |  | 0 |
| zgrep | rust_regex_key_value |  |  | 0.062094 | 0.072420 | 0 |  |  |  |  |  |  | 0 |
| zlg | rust_regex_key_value |  | full | 0.037301 | 0.036968 | 0 | 1.000000 | 16 | 16 | 0 | 0 | 100259 | 0 |
| zlg | rust_regex_key_value |  | stream | 0.033209 | 0.033677 | 0 | 1.000000 | 16 | 16 | 16 | 0 | 100259 | 0 |
| grep_original | pcre2_lookbehind_key |  |  | 0.004649 | 0.004002 | 0 |  |  |  |  |  |  | 0 |
| zgrep | pcre2_lookbehind_key |  |  | 0.069268 | 0.080741 | 0 |  |  |  |  |  |  | 0 |
| zlg | pcre2_lookbehind_key |  | full | 0.273505 | 0.273056 | 0 | 1.000000 | 16 | 16 | 0 | 0 | 100259 | 0 |
| zlg | pcre2_lookbehind_key |  | stream | 0.276462 | 0.276091 | 0 | 1.000000 | 16 | 16 | 16 | 0 | 100259 | 0 |
| grep_original | pcre2_ip_range_full |  |  | 0.004316 | 0.004038 | 0 |  |  |  |  |  |  | 0 |
| zgrep | pcre2_ip_range_full |  |  | 0.061527 | 0.072081 | 0 |  |  |  |  |  |  | 0 |
| zlg | pcre2_ip_range_full |  | full | 0.040792 | 0.041827 | 0 | 0.880108 | 13 | 16 | 0 | 0 | 100000 | 0 |
| zlg | pcre2_ip_range_full |  | stream | 0.035698 | 0.035371 | 0 | 0.880108 | 13 | 16 | 13 | 0 | 100000 | 0 |
| grep_original | pcre2_ip_range_head1 | 1 |  | 0.009446 | 0.016214 | 0 |  |  |  |  |  |  | 0 |
| zgrep | pcre2_ip_range_head1 | 1 |  | 0.033896 | 0.049518 | 0 |  |  |  |  |  |  | 0 |
| zlg | pcre2_ip_range_head1 | 1 | full | 0.013217 | 0.012893 | 0 | 0.067914 | 1 | 1 | 0 | 0 | 1 | 0 |
| zlg | pcre2_ip_range_head1 | 1 | stream | 0.006726 | 0.006353 | 0 | 0.005681 | 1 | 1 | 0 | 1 | 1 | 0 |

## Notes

- `-P` uses the pcre2 crate in this phase.
- `--head 1` is a synchronous early-stop path that stops scanning after the first emitted match.
- Full mode decodes a selected chunk into memory before line scanning.
- Stream mode uses zstd streaming decode and scans lines without materializing the whole uncompressed chunk.
- In stream mode, early stop may leave CRC unchecked for the partially decoded chunk; stats expose this.
