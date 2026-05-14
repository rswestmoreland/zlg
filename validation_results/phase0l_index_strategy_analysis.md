# Phase 0l Index Strategy Analysis

This is pre-bench evidence only, not the final performance proof.

## Compression and metadata comparison

| name | policy | summary_mode | median_s | median_output_bytes | median_payload_bytes | median_summary_bytes | median_overhead_bytes |
|---|---|---|---:|---:|---:|---:|---:|
| gzip_6 |  |  | 0.168507 | 849250 |  |  |  |
| gzip_9 |  |  | 0.835940 | 746531 |  |  |  |
| zlg | fixed-lines64k | bitmap | 0.237546 | 623250 | 589986 | 32912 | 33264 |
| zlg | hybrid-fixed64k-cap16m | bitmap | 0.230839 | 623250 | 589986 | 32912 | 33264 |
| zlg | hybrid-fixed64k-cap8m | bitmap | 0.237188 | 623250 | 589986 | 32912 | 33264 |
| zlg | hybrid-progressive-cap16m | bitmap | 0.192119 | 672627 | 589611 | 82280 | 83016 |
| zlg | hybrid-progressive-cap8m | bitmap | 0.193923 | 672627 | 589611 | 82280 | 83016 |
| zlg | progressive-lines | bitmap | 0.193204 | 672627 | 589611 | 82280 | 83016 |
| zlg_no_index | fixed-lines64k | none | 0.157817 | 590338 | 589986 | 0 | 352 |
| zlg_no_index | hybrid-fixed64k-cap16m | none | 0.168027 | 590338 | 589986 | 0 | 352 |
| zlg_no_index | hybrid-fixed64k-cap8m | none | 0.147526 | 590338 | 589986 | 0 | 352 |
| zlg_no_index | hybrid-progressive-cap16m | none | 0.110016 | 590347 | 589611 | 0 | 736 |
| zlg_no_index | hybrid-progressive-cap8m | none | 0.112471 | 590347 | 589611 | 0 | 736 |
| zlg_no_index | progressive-lines | none | 0.110943 | 590347 | 589611 | 0 | 736 |

## Search timing comparison

| name | policy | summary_mode | pattern | median_s | first_output_s | chunks_skipped | chunks_decoded | decoded_bytes | matching_lines |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| grep_plain |  |  | alternation_error_failed_denied | 0.034647 | 0.010413 |  |  |  |  |
| grep_plain |  |  | branch_suffix | 0.022431 | 0.010549 |  |  |  |  |
| grep_plain |  |  | literal_failed_password | 0.019752 | 0.009926 |  |  |  |  |
| grep_plain |  |  | no_match_literal | 0.015473 |  |  |  |  |  |
| grep_plain |  |  | quoted_key | 0.018552 | 0.008650 |  |  |  |  |
| grep_plain |  |  | src_ip | 0.104967 | 0.007663 |  |  |  |  |
| rg_plain |  |  | alternation_error_failed_denied | 0.036161 | 0.016378 |  |  |  |  |
| rg_plain |  |  | branch_suffix | 0.043288 | 0.020705 |  |  |  |  |
| rg_plain |  |  | literal_failed_password | 0.033725 | 0.017020 |  |  |  |  |
| rg_plain |  |  | no_match_literal | 0.030281 |  |  |  |  |  |
| rg_plain |  |  | quoted_key | 0.032915 | 0.017775 |  |  |  |  |
| rg_plain |  |  | src_ip | 0.141075 | 0.016371 |  |  |  |  |
| zgrep_gzip6 |  |  | alternation_error_failed_denied | 0.096914 | 0.041133 |  |  |  |  |
| zgrep_gzip6 |  |  | branch_suffix | 0.104258 | 0.050973 |  |  |  |  |
| zgrep_gzip6 |  |  | literal_failed_password | 0.096595 | 0.043849 |  |  |  |  |
| zgrep_gzip6 |  |  | no_match_literal | 0.105741 |  |  |  |  |  |
| zgrep_gzip6 |  |  | quoted_key | 0.097721 | 0.041998 |  |  |  |  |
| zgrep_gzip6 |  |  | src_ip | 0.153006 | 0.046084 |  |  |  |  |
| zlg_grep | fixed-lines64k | bitmap | alternation_error_failed_denied | 0.136723 | 0.067895 | 0 | 2 | 9218316 | 2816 |
| zlg_grep | fixed-lines64k | bitmap | branch_suffix | 0.129839 | 0.067425 | 0 | 2 | 9218316 | 1871 |
| zlg_grep | fixed-lines64k | bitmap | literal_failed_password | 0.141874 | 0.078847 | 0 | 2 | 9218316 | 945 |
| zlg_grep | fixed-lines64k | bitmap | lookbehind_key | 0.016653 |  | 2 | 0 | 0 | 0 |
| zlg_grep | fixed-lines64k | bitmap | no_match_literal | 0.015090 |  | 2 | 0 | 0 | 0 |
| zlg_grep | fixed-lines64k | bitmap | quoted_key | 0.131100 | 0.072179 | 0 | 2 | 9218316 | 2115 |
| zlg_grep | fixed-lines64k | bitmap | src_ip | 0.215605 | 0.064698 | 0 | 2 | 9218316 | 125000 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | alternation_error_failed_denied | 0.127574 | 0.066584 | 0 | 2 | 9218316 | 2816 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | branch_suffix | 0.128313 | 0.069548 | 0 | 2 | 9218316 | 1871 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | literal_failed_password | 0.129671 | 0.068781 | 0 | 2 | 9218316 | 945 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | lookbehind_key | 0.016482 |  | 2 | 0 | 0 | 0 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | no_match_literal | 0.015635 |  | 2 | 0 | 0 | 0 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | quoted_key | 0.132672 | 0.073688 | 0 | 2 | 9218316 | 2115 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | src_ip | 0.197367 | 0.065048 | 0 | 2 | 9218316 | 125000 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | alternation_error_failed_denied | 0.127375 | 0.064844 | 0 | 2 | 9218316 | 2816 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | branch_suffix | 0.137363 | 0.072282 | 0 | 2 | 9218316 | 1871 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | literal_failed_password | 0.124971 | 0.068819 | 0 | 2 | 9218316 | 945 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | lookbehind_key | 0.017057 |  | 2 | 0 | 0 | 0 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | no_match_literal | 0.013825 |  | 2 | 0 | 0 | 0 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | quoted_key | 0.130159 | 0.069578 | 0 | 2 | 9218316 | 2115 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | src_ip | 0.208034 | 0.067756 | 0 | 2 | 9218316 | 125000 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | alternation_error_failed_denied | 0.162151 | 0.026025 | 0 | 5 | 9218316 | 2816 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | branch_suffix | 0.162200 | 0.026874 | 0 | 5 | 9218316 | 1871 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | literal_failed_password | 0.165292 | 0.036461 | 0 | 5 | 9218316 | 945 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | lookbehind_key | 0.016717 |  | 5 | 0 | 0 | 0 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | no_match_literal | 0.014631 |  | 5 | 0 | 0 | 0 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | quoted_key | 0.174986 | 0.028192 | 0 | 5 | 9218316 | 2115 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | src_ip | 0.228949 | 0.016992 | 0 | 5 | 9218316 | 125000 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | alternation_error_failed_denied | 0.165929 | 0.025912 | 0 | 5 | 9218316 | 2816 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | branch_suffix | 0.166408 | 0.025296 | 0 | 5 | 9218316 | 1871 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | literal_failed_password | 0.159296 | 0.036385 | 0 | 5 | 9218316 | 945 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | lookbehind_key | 0.017777 |  | 5 | 0 | 0 | 0 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | no_match_literal | 0.013250 |  | 5 | 0 | 0 | 0 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | quoted_key | 0.173606 | 0.028934 | 0 | 5 | 9218316 | 2115 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | src_ip | 0.246020 | 0.019583 | 0 | 5 | 9218316 | 125000 |
| zlg_grep | progressive-lines | bitmap | alternation_error_failed_denied | 0.168850 | 0.025952 | 0 | 5 | 9218316 | 2816 |
| zlg_grep | progressive-lines | bitmap | branch_suffix | 0.169985 | 0.027543 | 0 | 5 | 9218316 | 1871 |
| zlg_grep | progressive-lines | bitmap | literal_failed_password | 0.165310 | 0.041230 | 0 | 5 | 9218316 | 945 |
| zlg_grep | progressive-lines | bitmap | lookbehind_key | 0.016543 |  | 5 | 0 | 0 | 0 |
| zlg_grep | progressive-lines | bitmap | no_match_literal | 0.014785 |  | 5 | 0 | 0 | 0 |
| zlg_grep | progressive-lines | bitmap | quoted_key | 0.162212 | 0.026023 | 0 | 5 | 9218316 | 2115 |
| zlg_grep | progressive-lines | bitmap | src_ip | 0.252437 | 0.018754 | 0 | 5 | 9218316 | 125000 |
| zlg_grep_no_index | fixed-lines64k | none | alternation_error_failed_denied | 0.136270 | 0.072219 | 0 | 2 | 9218316 | 2816 |
| zlg_grep_no_index | fixed-lines64k | none | branch_suffix | 0.122616 | 0.065344 | 0 | 2 | 9218316 | 1871 |
| zlg_grep_no_index | fixed-lines64k | none | literal_failed_password | 0.133879 | 0.072634 | 0 | 2 | 9218316 | 945 |
| zlg_grep_no_index | fixed-lines64k | none | lookbehind_key | 0.668581 | 0.107359 | 0 | 2 | 9218316 | 2115 |
| zlg_grep_no_index | fixed-lines64k | none | no_match_literal | 0.139586 |  | 0 | 2 | 9218316 | 0 |
| zlg_grep_no_index | fixed-lines64k | none | quoted_key | 0.144004 | 0.077531 | 0 | 2 | 9218316 | 2115 |
| zlg_grep_no_index | fixed-lines64k | none | src_ip | 0.219173 | 0.063328 | 0 | 2 | 9218316 | 125000 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | alternation_error_failed_denied | 0.132890 | 0.069216 | 0 | 2 | 9218316 | 2816 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | branch_suffix | 0.134152 | 0.070097 | 0 | 2 | 9218316 | 1871 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | literal_failed_password | 0.133021 | 0.073163 | 0 | 2 | 9218316 | 945 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | lookbehind_key | 0.704264 | 0.113601 | 0 | 2 | 9218316 | 2115 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | no_match_literal | 0.140585 |  | 0 | 2 | 9218316 | 0 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | quoted_key | 0.128308 | 0.068067 | 0 | 2 | 9218316 | 2115 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | src_ip | 0.199376 | 0.068271 | 0 | 2 | 9218316 | 125000 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | alternation_error_failed_denied | 0.127861 | 0.065947 | 0 | 2 | 9218316 | 2816 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | branch_suffix | 0.131010 | 0.067968 | 0 | 2 | 9218316 | 1871 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | literal_failed_password | 0.129327 | 0.068573 | 0 | 2 | 9218316 | 945 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | lookbehind_key | 0.673565 | 0.106318 | 0 | 2 | 9218316 | 2115 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | no_match_literal | 0.136782 |  | 0 | 2 | 9218316 | 0 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | quoted_key | 0.129181 | 0.071782 | 0 | 2 | 9218316 | 2115 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | src_ip | 0.198268 | 0.066962 | 0 | 2 | 9218316 | 125000 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | alternation_error_failed_denied | 0.160389 | 0.024730 | 0 | 5 | 9218316 | 2816 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | branch_suffix | 0.164273 | 0.025617 | 0 | 5 | 9218316 | 1871 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | literal_failed_password | 0.164667 | 0.036257 | 0 | 5 | 9218316 | 945 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | lookbehind_key | 0.704852 | 0.062828 | 0 | 5 | 9218316 | 2115 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | no_match_literal | 0.170659 |  | 0 | 5 | 9218316 | 0 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | quoted_key | 0.167535 | 0.029418 | 0 | 5 | 9218316 | 2115 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | src_ip | 0.248157 | 0.020188 | 0 | 5 | 9218316 | 125000 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | alternation_error_failed_denied | 0.165583 | 0.026609 | 0 | 5 | 9218316 | 2816 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | branch_suffix | 0.165167 | 0.026257 | 0 | 5 | 9218316 | 1871 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | literal_failed_password | 0.163370 | 0.035250 | 0 | 5 | 9218316 | 945 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | lookbehind_key | 0.730833 | 0.065148 | 0 | 5 | 9218316 | 2115 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | no_match_literal | 0.175360 |  | 0 | 5 | 9218316 | 0 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | quoted_key | 0.163015 | 0.026989 | 0 | 5 | 9218316 | 2115 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | src_ip | 0.231413 | 0.017660 | 0 | 5 | 9218316 | 125000 |
| zlg_grep_no_index | progressive-lines | none | alternation_error_failed_denied | 0.160281 | 0.026013 | 0 | 5 | 9218316 | 2816 |
| zlg_grep_no_index | progressive-lines | none | branch_suffix | 0.172967 | 0.027172 | 0 | 5 | 9218316 | 1871 |
| zlg_grep_no_index | progressive-lines | none | literal_failed_password | 0.157757 | 0.034992 | 0 | 5 | 9218316 | 945 |
| zlg_grep_no_index | progressive-lines | none | lookbehind_key | 0.716066 | 0.064608 | 0 | 5 | 9218316 | 2115 |
| zlg_grep_no_index | progressive-lines | none | no_match_literal | 0.176277 |  | 0 | 5 | 9218316 | 0 |
| zlg_grep_no_index | progressive-lines | none | quoted_key | 0.160632 | 0.026345 | 0 | 5 | 9218316 | 2115 |
| zlg_grep_no_index | progressive-lines | none | src_ip | 0.235051 | 0.018708 | 0 | 5 | 9218316 | 125000 |

## Bitmap versus no-index delta

| policy | pattern | bitmap_s | no_index_s | bitmap/no_index | bitmap_decoded_bytes | no_index_decoded_bytes |
|---|---|---:|---:|---:|---:|---:|
| fixed-lines64k | alternation_error_failed_denied | 0.136723 | 0.136270 | 1.003 | 9218316 | 9218316 |
| fixed-lines64k | branch_suffix | 0.129839 | 0.122616 | 1.059 | 9218316 | 9218316 |
| fixed-lines64k | literal_failed_password | 0.141874 | 0.133879 | 1.060 | 9218316 | 9218316 |
| fixed-lines64k | lookbehind_key | 0.016653 | 0.668581 | 0.025 | 0 | 9218316 |
| fixed-lines64k | no_match_literal | 0.015090 | 0.139586 | 0.108 | 0 | 9218316 |
| fixed-lines64k | quoted_key | 0.131100 | 0.144004 | 0.910 | 9218316 | 9218316 |
| fixed-lines64k | src_ip | 0.215605 | 0.219173 | 0.984 | 9218316 | 9218316 |
| hybrid-fixed64k-cap16m | alternation_error_failed_denied | 0.127574 | 0.132890 | 0.960 | 9218316 | 9218316 |
| hybrid-fixed64k-cap16m | branch_suffix | 0.128313 | 0.134152 | 0.956 | 9218316 | 9218316 |
| hybrid-fixed64k-cap16m | literal_failed_password | 0.129671 | 0.133021 | 0.975 | 9218316 | 9218316 |
| hybrid-fixed64k-cap16m | lookbehind_key | 0.016482 | 0.704264 | 0.023 | 0 | 9218316 |
| hybrid-fixed64k-cap16m | no_match_literal | 0.015635 | 0.140585 | 0.111 | 0 | 9218316 |
| hybrid-fixed64k-cap16m | quoted_key | 0.132672 | 0.128308 | 1.034 | 9218316 | 9218316 |
| hybrid-fixed64k-cap16m | src_ip | 0.197367 | 0.199376 | 0.990 | 9218316 | 9218316 |
| hybrid-fixed64k-cap8m | alternation_error_failed_denied | 0.127375 | 0.127861 | 0.996 | 9218316 | 9218316 |
| hybrid-fixed64k-cap8m | branch_suffix | 0.137363 | 0.131010 | 1.048 | 9218316 | 9218316 |
| hybrid-fixed64k-cap8m | literal_failed_password | 0.124971 | 0.129327 | 0.966 | 9218316 | 9218316 |
| hybrid-fixed64k-cap8m | lookbehind_key | 0.017057 | 0.673565 | 0.025 | 0 | 9218316 |
| hybrid-fixed64k-cap8m | no_match_literal | 0.013825 | 0.136782 | 0.101 | 0 | 9218316 |
| hybrid-fixed64k-cap8m | quoted_key | 0.130159 | 0.129181 | 1.008 | 9218316 | 9218316 |
| hybrid-fixed64k-cap8m | src_ip | 0.208034 | 0.198268 | 1.049 | 9218316 | 9218316 |
| hybrid-progressive-cap16m | alternation_error_failed_denied | 0.162151 | 0.160389 | 1.011 | 9218316 | 9218316 |
| hybrid-progressive-cap16m | branch_suffix | 0.162200 | 0.164273 | 0.987 | 9218316 | 9218316 |
| hybrid-progressive-cap16m | literal_failed_password | 0.165292 | 0.164667 | 1.004 | 9218316 | 9218316 |
| hybrid-progressive-cap16m | lookbehind_key | 0.016717 | 0.704852 | 0.024 | 0 | 9218316 |
| hybrid-progressive-cap16m | no_match_literal | 0.014631 | 0.170659 | 0.086 | 0 | 9218316 |
| hybrid-progressive-cap16m | quoted_key | 0.174986 | 0.167535 | 1.044 | 9218316 | 9218316 |
| hybrid-progressive-cap16m | src_ip | 0.228949 | 0.248157 | 0.923 | 9218316 | 9218316 |
| hybrid-progressive-cap8m | alternation_error_failed_denied | 0.165929 | 0.165583 | 1.002 | 9218316 | 9218316 |
| hybrid-progressive-cap8m | branch_suffix | 0.166408 | 0.165167 | 1.008 | 9218316 | 9218316 |
| hybrid-progressive-cap8m | literal_failed_password | 0.159296 | 0.163370 | 0.975 | 9218316 | 9218316 |
| hybrid-progressive-cap8m | lookbehind_key | 0.017777 | 0.730833 | 0.024 | 0 | 9218316 |
| hybrid-progressive-cap8m | no_match_literal | 0.013250 | 0.175360 | 0.076 | 0 | 9218316 |
| hybrid-progressive-cap8m | quoted_key | 0.173606 | 0.163015 | 1.065 | 9218316 | 9218316 |
| hybrid-progressive-cap8m | src_ip | 0.246020 | 0.231413 | 1.063 | 9218316 | 9218316 |
| progressive-lines | alternation_error_failed_denied | 0.168850 | 0.160281 | 1.053 | 9218316 | 9218316 |
| progressive-lines | branch_suffix | 0.169985 | 0.172967 | 0.983 | 9218316 | 9218316 |
| progressive-lines | literal_failed_password | 0.165310 | 0.157757 | 1.048 | 9218316 | 9218316 |
| progressive-lines | lookbehind_key | 0.016543 | 0.716066 | 0.023 | 0 | 9218316 |
| progressive-lines | no_match_literal | 0.014785 | 0.176277 | 0.084 | 0 | 9218316 |
| progressive-lines | quoted_key | 0.162212 | 0.160632 | 1.010 | 9218316 | 9218316 |
| progressive-lines | src_ip | 0.252437 | 0.235051 | 1.074 | 9218316 | 9218316 |

## Preliminary decision notes

- Bitmap summaries faster than no-index in 24 grouped comparisons.
- Bitmap summaries slower than no-index in 18 grouped comparisons.
- Keep or remove bitmap summaries should be decided by decoded-byte reduction, first-output latency, and metadata overhead, not by one timing alone.
- If common matching patterns still decode all chunks, next work should prioritize selector extraction and/or smaller independently compressed search blocks before async.
- zstd/zstdcat baselines should be reviewed when those tools are available in the environment.
