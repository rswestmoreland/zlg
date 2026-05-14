# zlg Phase 0h/0i prebench benchmark summary

This is pre-bench evidence only, not the final performance proof.

## Corpus

- Lines: 125000
- Input bytes: 9218316
- Input sha256: 942cac75a8319eae9acbcbfe97bd52d5dc1b161175ee6f9c5908c71f2edc48c2

## Median timings

| kind | name | policy | pattern | repeats | median_s | min_s | max_s | first_output_s | output_bytes |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| cat | zlg_cat | fixed-lines64k |  | 3 | 0.089928 | 0.088668 | 0.097956 |  | 9218316 |
| cat | zlg_cat | hybrid-fixed64k-cap16m |  | 3 | 0.085713 | 0.082453 | 0.088637 |  | 9218316 |
| cat | zlg_cat | hybrid-fixed64k-cap8m |  | 3 | 0.091411 | 0.089275 | 0.093775 |  | 9218316 |
| cat | zlg_cat | hybrid-progressive-cap16m |  | 3 | 0.114068 | 0.108131 | 0.115520 |  | 9218316 |
| cat | zlg_cat | hybrid-progressive-cap8m |  | 3 | 0.113995 | 0.113264 | 0.115125 |  | 9218316 |
| cat | zlg_cat | progressive-lines |  | 3 | 0.116023 | 0.115024 | 0.116744 |  | 9218316 |
| compress | gzip_6 |  |  | 3 | 0.139964 | 0.139486 | 0.140867 |  | 849250 |
| compress | gzip_9 |  |  | 3 | 0.702627 | 0.699237 | 0.719387 |  | 746531 |
| compress | zlg | fixed-lines64k |  | 3 | 0.168061 | 0.165493 | 0.179079 |  | 623250 |
| compress | zlg | hybrid-fixed64k-cap16m |  | 3 | 0.166684 | 0.160654 | 0.168045 |  | 623250 |
| compress | zlg | hybrid-fixed64k-cap8m |  | 3 | 0.173536 | 0.171480 | 0.173716 |  | 623250 |
| compress | zlg | hybrid-progressive-cap16m |  | 3 | 0.133808 | 0.130495 | 0.140961 |  | 672627 |
| compress | zlg | hybrid-progressive-cap8m |  | 3 | 0.141673 | 0.140664 | 0.146252 |  | 672627 |
| compress | zlg | progressive-lines |  | 3 | 0.134663 | 0.134179 | 0.136345 |  | 672627 |
| grep | zlg_grep | fixed-lines64k | alternation_error_failed_denied | 3 | 0.100565 | 0.099950 | 0.102857 | 0.052475 | 175364 |
| grep | zlg_grep | fixed-lines64k | branch_suffix | 3 | 0.100411 | 0.097530 | 0.105368 | 0.054924 | 111409 |
| grep | zlg_grep | fixed-lines64k | literal_failed_password | 3 | 0.094581 | 0.093217 | 0.098656 | 0.052265 | 63955 |
| grep | zlg_grep | fixed-lines64k | lookbehind_key | 3 | 0.013019 | 0.012542 | 0.015031 |  | 0 |
| grep | zlg_grep | fixed-lines64k | no_match_literal | 3 | 0.012490 | 0.010542 | 0.012819 |  | 0 |
| grep | zlg_grep | fixed-lines64k | quoted_key | 3 | 0.097973 | 0.097360 | 0.100266 | 0.052961 | 124168 |
| grep | zlg_grep | fixed-lines64k | src_ip | 3 | 0.149042 | 0.146944 | 0.215070 | 0.051892 | 9218316 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | alternation_error_failed_denied | 3 | 0.093538 | 0.090732 | 0.099912 | 0.048512 | 175364 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | branch_suffix | 3 | 0.101717 | 0.093815 | 0.107186 | 0.054910 | 111409 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | literal_failed_password | 3 | 0.095778 | 0.094449 | 0.103944 | 0.051605 | 63955 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | lookbehind_key | 3 | 0.011928 | 0.011405 | 0.012802 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | no_match_literal | 3 | 0.011553 | 0.009766 | 0.011990 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | quoted_key | 3 | 0.097640 | 0.097622 | 0.103544 | 0.054758 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | src_ip | 3 | 0.151196 | 0.136147 | 0.151329 | 0.050560 | 9218316 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | alternation_error_failed_denied | 3 | 0.101073 | 0.096009 | 0.126904 | 0.055687 | 175364 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | branch_suffix | 3 | 0.098503 | 0.095877 | 0.103716 | 0.051414 | 111409 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | literal_failed_password | 3 | 0.096101 | 0.092463 | 0.100301 | 0.053888 | 63955 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | lookbehind_key | 3 | 0.011649 | 0.011490 | 0.012703 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | no_match_literal | 3 | 0.010260 | 0.009782 | 0.010645 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | quoted_key | 3 | 0.095123 | 0.093825 | 0.101139 | 0.051320 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | src_ip | 3 | 0.145650 | 0.141884 | 0.151542 | 0.050479 | 9218316 |
| grep | zlg_grep | hybrid-progressive-cap16m | alternation_error_failed_denied | 3 | 0.119579 | 0.118970 | 0.125028 | 0.018879 | 175364 |
| grep | zlg_grep | hybrid-progressive-cap16m | branch_suffix | 3 | 0.122679 | 0.116324 | 0.126469 | 0.019693 | 111409 |
| grep | zlg_grep | hybrid-progressive-cap16m | literal_failed_password | 3 | 0.122420 | 0.122179 | 0.125000 | 0.028332 | 63955 |
| grep | zlg_grep | hybrid-progressive-cap16m | lookbehind_key | 3 | 0.012319 | 0.011439 | 0.013860 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap16m | no_match_literal | 3 | 0.011131 | 0.010440 | 0.011607 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap16m | quoted_key | 3 | 0.122437 | 0.119163 | 0.125271 | 0.020596 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap16m | src_ip | 3 | 0.184875 | 0.173177 | 0.190121 | 0.013521 | 9218316 |
| grep | zlg_grep | hybrid-progressive-cap8m | alternation_error_failed_denied | 3 | 0.136084 | 0.115894 | 0.137509 | 0.018271 | 175364 |
| grep | zlg_grep | hybrid-progressive-cap8m | branch_suffix | 3 | 0.130742 | 0.125072 | 0.148088 | 0.020753 | 111409 |
| grep | zlg_grep | hybrid-progressive-cap8m | literal_failed_password | 3 | 0.122666 | 0.116132 | 0.122956 | 0.026095 | 63955 |
| grep | zlg_grep | hybrid-progressive-cap8m | lookbehind_key | 3 | 0.012263 | 0.010879 | 0.013042 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap8m | no_match_literal | 3 | 0.012011 | 0.011214 | 0.012588 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap8m | quoted_key | 3 | 0.129177 | 0.119466 | 0.155380 | 0.021507 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap8m | src_ip | 3 | 0.177247 | 0.163099 | 0.179007 | 0.012400 | 9218316 |
| grep | zlg_grep | progressive-lines | alternation_error_failed_denied | 3 | 0.126698 | 0.124375 | 0.138682 | 0.020318 | 175364 |
| grep | zlg_grep | progressive-lines | branch_suffix | 3 | 0.134107 | 0.121353 | 0.136093 | 0.022214 | 111409 |
| grep | zlg_grep | progressive-lines | literal_failed_password | 3 | 0.121789 | 0.119890 | 0.123443 | 0.028194 | 63955 |
| grep | zlg_grep | progressive-lines | lookbehind_key | 3 | 0.012307 | 0.012076 | 0.013477 |  | 0 |
| grep | zlg_grep | progressive-lines | no_match_literal | 3 | 0.011203 | 0.010502 | 0.011997 |  | 0 |
| grep | zlg_grep | progressive-lines | quoted_key | 3 | 0.128099 | 0.124209 | 0.150324 | 0.020268 | 124168 |
| grep | zlg_grep | progressive-lines | src_ip | 3 | 0.175320 | 0.161043 | 0.204554 | 0.013154 | 9218316 |
| grep_baseline | grep_plain |  | alternation_error_failed_denied | 3 | 0.023501 | 0.022633 | 0.029975 | 0.006811 | 175364 |
| grep_baseline | grep_plain |  | branch_suffix | 3 | 0.015479 | 0.014185 | 0.020600 | 0.006988 | 34486 |
| grep_baseline | grep_plain |  | literal_failed_password | 3 | 0.013628 | 0.012711 | 0.014077 | 0.006682 | 63955 |
| grep_baseline | grep_plain |  | no_match_literal | 3 | 0.011366 | 0.010545 | 0.011575 |  | 0 |
| grep_baseline | grep_plain |  | quoted_key | 3 | 0.012517 | 0.011750 | 0.015530 | 0.006231 | 124168 |
| grep_baseline | grep_plain |  | src_ip | 3 | 0.079376 | 0.075587 | 0.081016 | 0.005990 | 9218316 |
| grep_baseline | rg_plain |  | alternation_error_failed_denied | 3 | 0.024110 | 0.022127 | 0.027147 | 0.011742 | 175364 |
| grep_baseline | rg_plain |  | branch_suffix | 3 | 0.022355 | 0.022160 | 0.022896 | 0.011013 | 111409 |
| grep_baseline | rg_plain |  | literal_failed_password | 3 | 0.022737 | 0.021268 | 0.023447 | 0.012476 | 63955 |
| grep_baseline | rg_plain |  | no_match_literal | 3 | 0.023011 | 0.022917 | 0.025074 |  | 0 |
| grep_baseline | rg_plain |  | quoted_key | 3 | 0.023256 | 0.023105 | 0.026983 | 0.013072 | 124168 |
| grep_baseline | rg_plain |  | src_ip | 3 | 0.097510 | 0.097450 | 0.108790 | 0.011225 | 9218316 |
| grep_baseline | zgrep_gzip6 |  | alternation_error_failed_denied | 3 | 0.075414 | 0.074181 | 0.081195 | 0.027875 | 175364 |
| grep_baseline | zgrep_gzip6 |  | branch_suffix | 3 | 0.078927 | 0.077065 | 0.083089 | 0.035797 | 34486 |
| grep_baseline | zgrep_gzip6 |  | literal_failed_password | 3 | 0.078541 | 0.077013 | 0.083721 | 0.033304 | 63955 |
| grep_baseline | zgrep_gzip6 |  | no_match_literal | 3 | 0.080989 | 0.079143 | 0.085126 |  | 0 |
| grep_baseline | zgrep_gzip6 |  | quoted_key | 3 | 0.078610 | 0.077500 | 0.085372 | 0.029592 | 124168 |
| grep_baseline | zgrep_gzip6 |  | src_ip | 3 | 0.113097 | 0.110287 | 0.128176 | 0.028889 | 9218316 |

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
