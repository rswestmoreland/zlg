# zlg Phase 0h/0i prebench benchmark summary

This is pre-bench evidence only, not the final performance proof.

## Corpus

- Lines: 125000
- Input bytes: 9218316
- Input sha256: 942cac75a8319eae9acbcbfe97bd52d5dc1b161175ee6f9c5908c71f2edc48c2

## Median timings

| kind | name | policy | pattern | repeats | median_s | min_s | max_s | first_output_s | output_bytes |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| cat | zlg_cat | fixed-lines64k |  | 3 | 0.087027 | 0.080355 | 0.095977 |  | 9218316 |
| cat | zlg_cat | hybrid-fixed64k-cap16m |  | 3 | 0.086397 | 0.084970 | 0.087063 |  | 9218316 |
| cat | zlg_cat | hybrid-fixed64k-cap8m |  | 3 | 0.086477 | 0.084341 | 0.087190 |  | 9218316 |
| cat | zlg_cat | hybrid-progressive-cap16m |  | 3 | 0.113322 | 0.111876 | 0.119227 |  | 9218316 |
| cat | zlg_cat | hybrid-progressive-cap8m |  | 3 | 0.109136 | 0.108626 | 0.113914 |  | 9218316 |
| cat | zlg_cat | progressive-lines |  | 3 | 0.106722 | 0.106311 | 0.113433 |  | 9218316 |
| compress | gzip_6 |  |  | 3 | 0.136680 | 0.135044 | 0.138440 |  | 849250 |
| compress | gzip_9 |  |  | 3 | 0.694694 | 0.688879 | 0.695056 |  | 746531 |
| compress | zlg | fixed-lines64k |  | 3 | 0.161291 | 0.158774 | 0.188338 |  | 623250 |
| compress | zlg | hybrid-fixed64k-cap16m |  | 3 | 0.161742 | 0.157406 | 0.165943 |  | 623250 |
| compress | zlg | hybrid-fixed64k-cap8m |  | 3 | 0.167495 | 0.159942 | 0.169606 |  | 623250 |
| compress | zlg | hybrid-progressive-cap16m |  | 3 | 0.130470 | 0.130116 | 0.134976 |  | 672627 |
| compress | zlg | hybrid-progressive-cap8m |  | 3 | 0.130695 | 0.129324 | 0.136216 |  | 672627 |
| compress | zlg | progressive-lines |  | 3 | 0.130002 | 0.125944 | 0.132236 |  | 672627 |
| grep | zlg_grep | fixed-lines64k | alternation_error_failed_denied | 3 | 0.099891 | 0.091665 | 0.100137 | 0.052186 | 175364 |
| grep | zlg_grep | fixed-lines64k | branch_suffix | 3 | 0.095492 | 0.089260 | 0.097743 | 0.050528 | 111409 |
| grep | zlg_grep | fixed-lines64k | literal_failed_password | 3 | 0.092605 | 0.088714 | 0.099245 | 0.050322 | 63955 |
| grep | zlg_grep | fixed-lines64k | lookbehind_key | 3 | 0.011912 | 0.010839 | 0.012156 |  | 0 |
| grep | zlg_grep | fixed-lines64k | no_match_literal | 3 | 0.010428 | 0.009032 | 0.011202 |  | 0 |
| grep | zlg_grep | fixed-lines64k | quoted_key | 3 | 0.091321 | 0.091200 | 0.095896 | 0.050838 | 124168 |
| grep | zlg_grep | fixed-lines64k | src_ip | 3 | 0.141802 | 0.141077 | 0.176656 | 0.047763 | 9218316 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | alternation_error_failed_denied | 3 | 0.091121 | 0.089186 | 0.097248 | 0.046771 | 175364 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | branch_suffix | 3 | 0.094035 | 0.092376 | 0.096203 | 0.049158 | 111409 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | literal_failed_password | 3 | 0.090884 | 0.090849 | 0.091459 | 0.049428 | 63955 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | lookbehind_key | 3 | 0.012531 | 0.011774 | 0.012602 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | no_match_literal | 3 | 0.011120 | 0.010744 | 0.012049 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | quoted_key | 3 | 0.094703 | 0.094692 | 0.098265 | 0.052284 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | src_ip | 3 | 0.148188 | 0.140299 | 0.154726 | 0.050603 | 9218316 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | alternation_error_failed_denied | 3 | 0.098872 | 0.091295 | 0.100075 | 0.050096 | 175364 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | branch_suffix | 3 | 0.097754 | 0.096509 | 0.108350 | 0.051101 | 111409 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | literal_failed_password | 3 | 0.093351 | 0.092819 | 0.104929 | 0.050862 | 63955 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | lookbehind_key | 3 | 0.012448 | 0.011762 | 0.013716 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | no_match_literal | 3 | 0.009899 | 0.009787 | 0.011271 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | quoted_key | 3 | 0.093521 | 0.089295 | 0.098579 | 0.051326 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | src_ip | 3 | 0.148054 | 0.147380 | 0.153489 | 0.051895 | 9218316 |
| grep | zlg_grep | hybrid-progressive-cap16m | alternation_error_failed_denied | 3 | 0.122345 | 0.117424 | 0.124472 | 0.018862 | 175364 |
| grep | zlg_grep | hybrid-progressive-cap16m | branch_suffix | 3 | 0.115996 | 0.112655 | 0.118722 | 0.019567 | 111409 |
| grep | zlg_grep | hybrid-progressive-cap16m | literal_failed_password | 3 | 0.121828 | 0.113386 | 0.128251 | 0.027371 | 63955 |
| grep | zlg_grep | hybrid-progressive-cap16m | lookbehind_key | 3 | 0.012187 | 0.010802 | 0.012203 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap16m | no_match_literal | 3 | 0.010414 | 0.009632 | 0.011440 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap16m | quoted_key | 3 | 0.121464 | 0.117032 | 0.130917 | 0.019644 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap16m | src_ip | 3 | 0.172603 | 0.172014 | 0.176676 | 0.013510 | 9218316 |
| grep | zlg_grep | hybrid-progressive-cap8m | alternation_error_failed_denied | 3 | 0.120644 | 0.118663 | 0.120712 | 0.019335 | 175364 |
| grep | zlg_grep | hybrid-progressive-cap8m | branch_suffix | 3 | 0.116508 | 0.113837 | 0.118871 | 0.019412 | 111409 |
| grep | zlg_grep | hybrid-progressive-cap8m | literal_failed_password | 3 | 0.115302 | 0.111716 | 0.119134 | 0.026081 | 63955 |
| grep | zlg_grep | hybrid-progressive-cap8m | lookbehind_key | 3 | 0.012467 | 0.011892 | 0.013705 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap8m | no_match_literal | 3 | 0.010170 | 0.010130 | 0.012828 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap8m | quoted_key | 3 | 0.120771 | 0.118150 | 0.127036 | 0.020532 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap8m | src_ip | 3 | 0.172630 | 0.166428 | 0.173983 | 0.014210 | 9218316 |
| grep | zlg_grep | progressive-lines | alternation_error_failed_denied | 3 | 0.119207 | 0.117908 | 0.119262 | 0.018283 | 175364 |
| grep | zlg_grep | progressive-lines | branch_suffix | 3 | 0.117024 | 0.110773 | 0.122377 | 0.019503 | 111409 |
| grep | zlg_grep | progressive-lines | literal_failed_password | 3 | 0.112401 | 0.111854 | 0.126128 | 0.025317 | 63955 |
| grep | zlg_grep | progressive-lines | lookbehind_key | 3 | 0.011933 | 0.011104 | 0.012113 |  | 0 |
| grep | zlg_grep | progressive-lines | no_match_literal | 3 | 0.010261 | 0.009919 | 0.010277 |  | 0 |
| grep | zlg_grep | progressive-lines | quoted_key | 3 | 0.114849 | 0.114842 | 0.115881 | 0.018784 | 124168 |
| grep | zlg_grep | progressive-lines | src_ip | 3 | 0.166674 | 0.164217 | 0.195440 | 0.013425 | 9218316 |
| grep_baseline | grep_plain |  | alternation_error_failed_denied | 3 | 0.023799 | 0.022567 | 0.024413 | 0.006651 | 175364 |
| grep_baseline | grep_plain |  | branch_suffix | 3 | 0.015063 | 0.014602 | 0.015917 | 0.006947 | 34486 |
| grep_baseline | grep_plain |  | literal_failed_password | 3 | 0.013277 | 0.013016 | 0.013540 | 0.006573 | 63955 |
| grep_baseline | grep_plain |  | no_match_literal | 3 | 0.011152 | 0.010775 | 0.011821 |  | 0 |
| grep_baseline | grep_plain |  | quoted_key | 3 | 0.012919 | 0.012236 | 0.014789 | 0.006569 | 124168 |
| grep_baseline | grep_plain |  | src_ip | 3 | 0.077620 | 0.075246 | 0.081816 | 0.005652 | 9218316 |
| grep_baseline | rg_plain |  | alternation_error_failed_denied | 3 | 0.024274 | 0.020608 | 0.024976 | 0.010656 | 175364 |
| grep_baseline | rg_plain |  | branch_suffix | 3 | 0.022407 | 0.020218 | 0.023157 | 0.011165 | 111409 |
| grep_baseline | rg_plain |  | literal_failed_password | 3 | 0.021015 | 0.020341 | 0.025467 | 0.012056 | 63955 |
| grep_baseline | rg_plain |  | no_match_literal | 3 | 0.022155 | 0.020475 | 0.025150 |  | 0 |
| grep_baseline | rg_plain |  | quoted_key | 3 | 0.023039 | 0.022965 | 0.026172 | 0.013316 | 124168 |
| grep_baseline | rg_plain |  | src_ip | 3 | 0.109644 | 0.096206 | 0.110192 | 0.010900 | 9218316 |
| grep_baseline | zgrep_gzip6 |  | alternation_error_failed_denied | 3 | 0.076252 | 0.072901 | 0.077010 | 0.028561 | 175364 |
| grep_baseline | zgrep_gzip6 |  | branch_suffix | 3 | 0.076487 | 0.072419 | 0.077583 | 0.034115 | 34486 |
| grep_baseline | zgrep_gzip6 |  | literal_failed_password | 3 | 0.078519 | 0.077661 | 0.084057 | 0.032302 | 63955 |
| grep_baseline | zgrep_gzip6 |  | no_match_literal | 3 | 0.074971 | 0.074405 | 0.081654 |  | 0 |
| grep_baseline | zgrep_gzip6 |  | quoted_key | 3 | 0.075672 | 0.075124 | 0.089025 | 0.028702 | 124168 |
| grep_baseline | zgrep_gzip6 |  | src_ip | 3 | 0.115430 | 0.114413 | 0.120985 | 0.027007 | 9218316 |

## zlg grep counter medians

| policy | pattern | repeats | chunks_total | chunks_skipped | chunks_decoded | decoded_bytes | matching_lines |
|---|---|---:|---:|---:|---:|---:|---:|
| fixed-lines64k | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 |
| fixed-lines64k | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 |
| fixed-lines64k | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 |
| fixed-lines64k | lookbehind_key | 3 | 2 | 2 | 0 | 0 | 0 |
| fixed-lines64k | no_match_literal | 3 | 2 | 2 | 0 | 0 | 0 |
| fixed-lines64k | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 |
| fixed-lines64k | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 |
| hybrid-fixed64k-cap16m | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 |
| hybrid-fixed64k-cap16m | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 |
| hybrid-fixed64k-cap16m | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 |
| hybrid-fixed64k-cap16m | lookbehind_key | 3 | 2 | 2 | 0 | 0 | 0 |
| hybrid-fixed64k-cap16m | no_match_literal | 3 | 2 | 2 | 0 | 0 | 0 |
| hybrid-fixed64k-cap16m | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 |
| hybrid-fixed64k-cap16m | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 |
| hybrid-fixed64k-cap8m | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 |
| hybrid-fixed64k-cap8m | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 |
| hybrid-fixed64k-cap8m | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 |
| hybrid-fixed64k-cap8m | lookbehind_key | 3 | 2 | 2 | 0 | 0 | 0 |
| hybrid-fixed64k-cap8m | no_match_literal | 3 | 2 | 2 | 0 | 0 | 0 |
| hybrid-fixed64k-cap8m | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 |
| hybrid-fixed64k-cap8m | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 |
| hybrid-progressive-cap16m | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 |
| hybrid-progressive-cap16m | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 |
| hybrid-progressive-cap16m | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 |
| hybrid-progressive-cap16m | lookbehind_key | 3 | 5 | 5 | 0 | 0 | 0 |
| hybrid-progressive-cap16m | no_match_literal | 3 | 5 | 5 | 0 | 0 | 0 |
| hybrid-progressive-cap16m | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 |
| hybrid-progressive-cap16m | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 |
| hybrid-progressive-cap8m | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 |
| hybrid-progressive-cap8m | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 |
| hybrid-progressive-cap8m | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 |
| hybrid-progressive-cap8m | lookbehind_key | 3 | 5 | 5 | 0 | 0 | 0 |
| hybrid-progressive-cap8m | no_match_literal | 3 | 5 | 5 | 0 | 0 | 0 |
| hybrid-progressive-cap8m | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 |
| hybrid-progressive-cap8m | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 |
| progressive-lines | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 |
| progressive-lines | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 |
| progressive-lines | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 |
| progressive-lines | lookbehind_key | 3 | 5 | 5 | 0 | 0 | 0 |
| progressive-lines | no_match_literal | 3 | 5 | 5 | 0 | 0 | 0 |
| progressive-lines | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 |
| progressive-lines | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 |
