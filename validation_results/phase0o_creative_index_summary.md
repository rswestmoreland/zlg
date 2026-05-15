# zlg Phase 0h/0i prebench benchmark summary

This is pre-bench evidence only, not the final performance proof.

## Corpus

- Lines: 125000
- Input bytes: 9218316
- Input sha256: 942cac75a8319eae9acbcbfe97bd52d5dc1b161175ee6f9c5908c71f2edc48c2

## Median timings

| kind | name | policy | pattern | repeats | median_s | min_s | max_s | first_output_s | output_bytes |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| cat | zlg_cat | fixed-lines64k | bitmap |  | 3 | 0.095117 | 0.085875 | 0.101460 |  | 9218316 |
| cat | zlg_cat | hybrid-fixed64k-cap16m | bitmap |  | 3 | 0.087977 | 0.085639 | 0.092238 |  | 9218316 |
| cat | zlg_cat | hybrid-fixed64k-cap8m | bitmap |  | 3 | 0.086573 | 0.084913 | 0.086582 |  | 9218316 |
| cat | zlg_cat | hybrid-progressive-cap16m | bitmap |  | 3 | 0.109768 | 0.107893 | 0.121169 |  | 9218316 |
| cat | zlg_cat | hybrid-progressive-cap8m | bitmap |  | 3 | 0.110595 | 0.109252 | 0.114659 |  | 9218316 |
| cat | zlg_cat | progressive-lines | bitmap |  | 3 | 0.111930 | 0.109018 | 0.125674 |  | 9218316 |
| cat | zlg_cat_no_index | fixed-lines64k | none |  | 3 | 0.091975 | 0.090766 | 0.107715 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-fixed64k-cap16m | none |  | 3 | 0.095035 | 0.089858 | 0.100657 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-fixed64k-cap8m | none |  | 3 | 0.089356 | 0.089073 | 0.089391 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-progressive-cap16m | none |  | 3 | 0.114113 | 0.112522 | 0.123195 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-progressive-cap8m | none |  | 3 | 0.110741 | 0.106519 | 0.116367 |  | 9218316 |
| cat | zlg_cat_no_index | progressive-lines | none |  | 3 | 0.115237 | 0.109744 | 0.118834 |  | 9218316 |
| compress | gzip_6 |  |  |  | 3 | 0.139019 | 0.137621 | 0.141225 |  | 849250 |
| compress | gzip_9 |  |  |  | 3 | 0.695139 | 0.693328 | 0.698833 |  | 746531 |
| compress | zlg | fixed-lines64k | bitmap |  | 3 | 0.166746 | 0.165591 | 0.173875 |  | 623250 |
| compress | zlg | hybrid-fixed64k-cap16m | bitmap |  | 3 | 0.176527 | 0.168882 | 0.176790 |  | 623250 |
| compress | zlg | hybrid-fixed64k-cap8m | bitmap |  | 3 | 0.166607 | 0.164429 | 0.173458 |  | 623250 |
| compress | zlg | hybrid-progressive-cap16m | bitmap |  | 3 | 0.136306 | 0.133943 | 0.139617 |  | 672627 |
| compress | zlg | hybrid-progressive-cap8m | bitmap |  | 3 | 0.136285 | 0.135021 | 0.139990 |  | 672627 |
| compress | zlg | progressive-lines | bitmap |  | 3 | 0.137377 | 0.134033 | 0.142614 |  | 672627 |
| compress | zlg_no_index | fixed-lines64k | none |  | 3 | 0.108381 | 0.108166 | 0.109898 |  | 590338 |
| compress | zlg_no_index | hybrid-fixed64k-cap16m | none |  | 3 | 0.111908 | 0.109529 | 0.115703 |  | 590338 |
| compress | zlg_no_index | hybrid-fixed64k-cap8m | none |  | 3 | 0.110732 | 0.107642 | 0.122966 |  | 590338 |
| compress | zlg_no_index | hybrid-progressive-cap16m | none |  | 3 | 0.079276 | 0.075740 | 0.084424 |  | 590347 |
| compress | zlg_no_index | hybrid-progressive-cap8m | none |  | 3 | 0.077187 | 0.072240 | 0.078475 |  | 590347 |
| compress | zlg_no_index | progressive-lines | none |  | 3 | 0.081343 | 0.078723 | 0.081414 |  | 590347 |
| grep | zlg_grep | fixed-lines64k | bitmap | alternation_error_failed_denied | 3 | 0.095567 | 0.095294 | 0.096495 | 0.049456 | 175364 |
| grep | zlg_grep | fixed-lines64k | bitmap | branch_suffix | 3 | 0.096801 | 0.095368 | 0.099906 | 0.051820 | 111409 |
| grep | zlg_grep | fixed-lines64k | bitmap | literal_failed_password | 3 | 0.091345 | 0.090597 | 0.095574 | 0.049255 | 63955 |
| grep | zlg_grep | fixed-lines64k | bitmap | lookbehind_key | 3 | 0.498845 | 0.497504 | 0.503183 | 0.080317 | 124168 |
| grep | zlg_grep | fixed-lines64k | bitmap | no_match_literal | 3 | 0.011186 | 0.010870 | 0.012025 |  | 0 |
| grep | zlg_grep | fixed-lines64k | bitmap | quoted_key | 3 | 0.095358 | 0.094644 | 0.107893 | 0.051879 | 124168 |
| grep | zlg_grep | fixed-lines64k | bitmap | src_ip | 3 | 0.150825 | 0.144800 | 0.187375 | 0.049168 | 9218316 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | alternation_error_failed_denied | 3 | 0.096902 | 0.094460 | 0.098780 | 0.048316 | 175364 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | branch_suffix | 3 | 0.096474 | 0.096057 | 0.096690 | 0.049951 | 111409 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | literal_failed_password | 3 | 0.092860 | 0.092068 | 0.098832 | 0.051815 | 63955 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | lookbehind_key | 3 | 0.506160 | 0.500285 | 0.512398 | 0.080148 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | no_match_literal | 3 | 0.011811 | 0.010235 | 0.012067 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | quoted_key | 3 | 0.095349 | 0.091286 | 0.097687 | 0.052149 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | src_ip | 3 | 0.144725 | 0.144046 | 0.145922 | 0.049974 | 9218316 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | alternation_error_failed_denied | 3 | 0.097793 | 0.096723 | 0.100413 | 0.049382 | 175364 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | branch_suffix | 3 | 0.095792 | 0.093966 | 0.096439 | 0.049619 | 111409 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | literal_failed_password | 3 | 0.093887 | 0.090910 | 0.097080 | 0.050494 | 63955 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | lookbehind_key | 3 | 0.500268 | 0.494549 | 0.504913 | 0.079113 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | no_match_literal | 3 | 0.010574 | 0.010076 | 0.011086 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | quoted_key | 3 | 0.094984 | 0.091405 | 0.096544 | 0.051856 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | src_ip | 3 | 0.143095 | 0.140740 | 0.143253 | 0.047948 | 9218316 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | alternation_error_failed_denied | 3 | 0.120755 | 0.120250 | 0.129920 | 0.019616 | 175364 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | branch_suffix | 3 | 0.118071 | 0.116556 | 0.136069 | 0.018625 | 111409 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | literal_failed_password | 3 | 0.123064 | 0.115236 | 0.123765 | 0.027120 | 63955 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | lookbehind_key | 3 | 0.532965 | 0.514053 | 0.548086 | 0.045435 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | no_match_literal | 3 | 0.012685 | 0.011707 | 0.013665 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | quoted_key | 3 | 0.123777 | 0.119158 | 0.141667 | 0.019929 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | src_ip | 3 | 0.164791 | 0.163245 | 0.178845 | 0.012446 | 9218316 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | alternation_error_failed_denied | 3 | 0.122808 | 0.119145 | 0.128601 | 0.018285 | 175364 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | branch_suffix | 3 | 0.124762 | 0.123917 | 0.135526 | 0.023393 | 111409 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | literal_failed_password | 3 | 0.120221 | 0.116993 | 0.120558 | 0.025911 | 63955 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | lookbehind_key | 3 | 0.526263 | 0.518038 | 0.545955 | 0.045945 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | no_match_literal | 3 | 0.010262 | 0.010072 | 0.010634 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | quoted_key | 3 | 0.127568 | 0.120963 | 0.128249 | 0.021829 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | src_ip | 3 | 0.176458 | 0.165816 | 0.186141 | 0.014530 | 9218316 |
| grep | zlg_grep | progressive-lines | bitmap | alternation_error_failed_denied | 3 | 0.123708 | 0.117041 | 0.124487 | 0.020993 | 175364 |
| grep | zlg_grep | progressive-lines | bitmap | branch_suffix | 3 | 0.119883 | 0.117620 | 0.134482 | 0.019659 | 111409 |
| grep | zlg_grep | progressive-lines | bitmap | literal_failed_password | 3 | 0.121094 | 0.119056 | 0.125226 | 0.027390 | 63955 |
| grep | zlg_grep | progressive-lines | bitmap | lookbehind_key | 3 | 0.521567 | 0.519874 | 0.528796 | 0.047006 | 124168 |
| grep | zlg_grep | progressive-lines | bitmap | no_match_literal | 3 | 0.010924 | 0.010862 | 0.012691 |  | 0 |
| grep | zlg_grep | progressive-lines | bitmap | quoted_key | 3 | 0.124015 | 0.121639 | 0.126377 | 0.020655 | 124168 |
| grep | zlg_grep | progressive-lines | bitmap | src_ip | 3 | 0.184172 | 0.172301 | 0.191426 | 0.013297 | 9218316 |
| grep | zlg_grep_no_index | fixed-lines64k | none | alternation_error_failed_denied | 3 | 0.100772 | 0.095036 | 0.112053 | 0.053038 | 175364 |
| grep | zlg_grep_no_index | fixed-lines64k | none | branch_suffix | 3 | 0.097966 | 0.094214 | 0.100170 | 0.052523 | 111409 |
| grep | zlg_grep_no_index | fixed-lines64k | none | literal_failed_password | 3 | 0.097399 | 0.089025 | 0.107854 | 0.052433 | 63955 |
| grep | zlg_grep_no_index | fixed-lines64k | none | lookbehind_key | 3 | 0.509002 | 0.499314 | 0.509031 | 0.076965 | 124168 |
| grep | zlg_grep_no_index | fixed-lines64k | none | no_match_literal | 3 | 0.103048 | 0.102952 | 0.109869 |  | 0 |
| grep | zlg_grep_no_index | fixed-lines64k | none | quoted_key | 3 | 0.101612 | 0.093901 | 0.102867 | 0.056303 | 124168 |
| grep | zlg_grep_no_index | fixed-lines64k | none | src_ip | 3 | 0.152258 | 0.144489 | 0.169256 | 0.049097 | 9218316 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | alternation_error_failed_denied | 3 | 0.097838 | 0.094319 | 0.101688 | 0.050145 | 175364 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | branch_suffix | 3 | 0.095508 | 0.094640 | 0.097808 | 0.050594 | 111409 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | literal_failed_password | 3 | 0.096032 | 0.093153 | 0.101930 | 0.050709 | 63955 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | lookbehind_key | 3 | 0.501761 | 0.490556 | 0.503874 | 0.077222 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | no_match_literal | 3 | 0.100239 | 0.100146 | 0.101347 |  | 0 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | quoted_key | 3 | 0.093895 | 0.092396 | 0.095478 | 0.050648 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | src_ip | 3 | 0.145924 | 0.142136 | 0.149366 | 0.049884 | 9218316 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | alternation_error_failed_denied | 3 | 0.096049 | 0.096024 | 0.097266 | 0.050458 | 175364 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | branch_suffix | 3 | 0.096192 | 0.092498 | 0.112252 | 0.050701 | 111409 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | literal_failed_password | 3 | 0.096318 | 0.091764 | 0.097654 | 0.051501 | 63955 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | lookbehind_key | 3 | 0.498796 | 0.493207 | 0.503803 | 0.079340 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | no_match_literal | 3 | 0.103502 | 0.101426 | 0.104687 |  | 0 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | quoted_key | 3 | 0.095897 | 0.092957 | 0.097069 | 0.052195 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | src_ip | 3 | 0.142092 | 0.141062 | 0.147096 | 0.048806 | 9218316 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | alternation_error_failed_denied | 3 | 0.122376 | 0.121468 | 0.124441 | 0.019702 | 175364 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | branch_suffix | 3 | 0.123035 | 0.118852 | 0.125157 | 0.021820 | 111409 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | literal_failed_password | 3 | 0.118684 | 0.116657 | 0.125275 | 0.026879 | 63955 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | lookbehind_key | 3 | 0.526462 | 0.516161 | 0.533488 | 0.046834 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | no_match_literal | 3 | 0.130311 | 0.121889 | 0.162266 |  | 0 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | quoted_key | 3 | 0.127069 | 0.125604 | 0.142819 | 0.020227 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | src_ip | 3 | 0.173116 | 0.170792 | 0.174609 | 0.013552 | 9218316 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | alternation_error_failed_denied | 3 | 0.119339 | 0.116757 | 0.125094 | 0.018805 | 175364 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | branch_suffix | 3 | 0.117951 | 0.113469 | 0.149829 | 0.019385 | 111409 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | literal_failed_password | 3 | 0.116061 | 0.111742 | 0.116202 | 0.025040 | 63955 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | lookbehind_key | 3 | 0.523331 | 0.521443 | 0.528111 | 0.045603 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | no_match_literal | 3 | 0.126683 | 0.125564 | 0.137776 |  | 0 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | quoted_key | 3 | 0.117660 | 0.117360 | 0.121427 | 0.019000 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | src_ip | 3 | 0.166428 | 0.164089 | 0.166814 | 0.012609 | 9218316 |
| grep | zlg_grep_no_index | progressive-lines | none | alternation_error_failed_denied | 3 | 0.120985 | 0.117689 | 0.121253 | 0.018366 | 175364 |
| grep | zlg_grep_no_index | progressive-lines | none | branch_suffix | 3 | 0.120757 | 0.116976 | 0.121574 | 0.019547 | 111409 |
| grep | zlg_grep_no_index | progressive-lines | none | literal_failed_password | 3 | 0.119295 | 0.116103 | 0.120876 | 0.025563 | 63955 |
| grep | zlg_grep_no_index | progressive-lines | none | lookbehind_key | 3 | 0.522221 | 0.522142 | 0.526237 | 0.045963 | 124168 |
| grep | zlg_grep_no_index | progressive-lines | none | no_match_literal | 3 | 0.123696 | 0.123516 | 0.125073 |  | 0 |
| grep | zlg_grep_no_index | progressive-lines | none | quoted_key | 3 | 0.120225 | 0.119602 | 0.120249 | 0.019796 | 124168 |
| grep | zlg_grep_no_index | progressive-lines | none | src_ip | 3 | 0.166367 | 0.161731 | 0.191997 | 0.012899 | 9218316 |
| grep_baseline | grep_plain |  |  | alternation_error_failed_denied | 3 | 0.022453 | 0.022246 | 0.023476 | 0.006178 | 175364 |
| grep_baseline | grep_plain |  |  | branch_suffix | 3 | 0.014094 | 0.014002 | 0.014365 | 0.006318 | 34486 |
| grep_baseline | grep_plain |  |  | literal_failed_password | 3 | 0.013249 | 0.012859 | 0.013465 | 0.006266 | 63955 |
| grep_baseline | grep_plain |  |  | no_match_literal | 3 | 0.011072 | 0.010494 | 0.011169 |  | 0 |
| grep_baseline | grep_plain |  |  | quoted_key | 3 | 0.012157 | 0.011510 | 0.012360 | 0.006184 | 124168 |
| grep_baseline | grep_plain |  |  | src_ip | 3 | 0.080897 | 0.075604 | 0.087332 | 0.006079 | 9218316 |
| grep_baseline | rg_plain |  |  | alternation_error_failed_denied | 3 | 0.024864 | 0.021937 | 0.025982 | 0.011439 | 175364 |
| grep_baseline | rg_plain |  |  | branch_suffix | 3 | 0.022811 | 0.022313 | 0.023092 | 0.010771 | 111409 |
| grep_baseline | rg_plain |  |  | literal_failed_password | 3 | 0.021545 | 0.021087 | 0.022932 | 0.011335 | 63955 |
| grep_baseline | rg_plain |  |  | no_match_literal | 3 | 0.021414 | 0.019334 | 0.021576 |  | 0 |
| grep_baseline | rg_plain |  |  | quoted_key | 3 | 0.022508 | 0.022000 | 0.025249 | 0.012651 | 124168 |
| grep_baseline | rg_plain |  |  | src_ip | 3 | 0.098299 | 0.097736 | 0.102314 | 0.011626 | 9218316 |
| grep_baseline | zgrep_gzip6 |  |  | alternation_error_failed_denied | 3 | 0.075267 | 0.074437 | 0.084393 | 0.027873 | 175364 |
| grep_baseline | zgrep_gzip6 |  |  | branch_suffix | 3 | 0.077961 | 0.075248 | 0.083136 | 0.037750 | 34486 |
| grep_baseline | zgrep_gzip6 |  |  | literal_failed_password | 3 | 0.080496 | 0.078971 | 0.080534 | 0.035462 | 63955 |
| grep_baseline | zgrep_gzip6 |  |  | no_match_literal | 3 | 0.079772 | 0.076592 | 0.098313 |  | 0 |
| grep_baseline | zgrep_gzip6 |  |  | quoted_key | 3 | 0.078348 | 0.077885 | 0.090994 | 0.031782 | 124168 |
| grep_baseline | zgrep_gzip6 |  |  | src_ip | 3 | 0.122464 | 0.117094 | 0.146579 | 0.027718 | 9218316 |

## zlg grep counter medians

| name | policy | summary_mode | pattern | repeats | chunks_total | chunks_skipped | chunks_decoded | decoded_bytes | matching_lines | selector_kind | selector_len | selector_count |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| zlg_grep | fixed-lines64k | bitmap | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 | literal_any | 17 | 3 |
| zlg_grep | fixed-lines64k | bitmap | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 | literal_any | 6 | 2 |
| zlg_grep | fixed-lines64k | bitmap | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 | literal_all | 15 | 1 |
| zlg_grep | fixed-lines64k | bitmap | lookbehind_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | none | 0 | 0 |
| zlg_grep | fixed-lines64k | bitmap | no_match_literal | 3 | 2 | 2 | 0 | 0 | 0 | literal_all | 18 | 1 |
| zlg_grep | fixed-lines64k | bitmap | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal_all | 5 | 1 |
| zlg_grep | fixed-lines64k | bitmap | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 | literal_all | 7 | 1 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 | literal_any | 17 | 3 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 | literal_any | 6 | 2 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 | literal_all | 15 | 1 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | lookbehind_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | none | 0 | 0 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | no_match_literal | 3 | 2 | 2 | 0 | 0 | 0 | literal_all | 18 | 1 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal_all | 5 | 1 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 | literal_all | 7 | 1 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 | literal_any | 17 | 3 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 | literal_any | 6 | 2 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 | literal_all | 15 | 1 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | lookbehind_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | none | 0 | 0 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | no_match_literal | 3 | 2 | 2 | 0 | 0 | 0 | literal_all | 18 | 1 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal_all | 5 | 1 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 | literal_all | 7 | 1 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 | literal_any | 17 | 3 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 | literal_any | 6 | 2 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 | literal_all | 15 | 1 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | lookbehind_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | none | 0 | 0 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | no_match_literal | 3 | 5 | 5 | 0 | 0 | 0 | literal_all | 18 | 1 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal_all | 5 | 1 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 | literal_all | 7 | 1 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 | literal_any | 17 | 3 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 | literal_any | 6 | 2 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 | literal_all | 15 | 1 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | lookbehind_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | none | 0 | 0 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | no_match_literal | 3 | 5 | 5 | 0 | 0 | 0 | literal_all | 18 | 1 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal_all | 5 | 1 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 | literal_all | 7 | 1 |
| zlg_grep | progressive-lines | bitmap | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 | literal_any | 17 | 3 |
| zlg_grep | progressive-lines | bitmap | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 | literal_any | 6 | 2 |
| zlg_grep | progressive-lines | bitmap | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 | literal_all | 15 | 1 |
| zlg_grep | progressive-lines | bitmap | lookbehind_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | none | 0 | 0 |
| zlg_grep | progressive-lines | bitmap | no_match_literal | 3 | 5 | 5 | 0 | 0 | 0 | literal_all | 18 | 1 |
| zlg_grep | progressive-lines | bitmap | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal_all | 5 | 1 |
| zlg_grep | progressive-lines | bitmap | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 | literal_all | 7 | 1 |
| zlg_grep_no_index | fixed-lines64k | none | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 | literal_any | 17 | 3 |
| zlg_grep_no_index | fixed-lines64k | none | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 | literal_any | 6 | 2 |
| zlg_grep_no_index | fixed-lines64k | none | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 | literal_all | 15 | 1 |
| zlg_grep_no_index | fixed-lines64k | none | lookbehind_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | none | 0 | 0 |
| zlg_grep_no_index | fixed-lines64k | none | no_match_literal | 3 | 2 | 0 | 2 | 9218316 | 0 | literal_all | 18 | 1 |
| zlg_grep_no_index | fixed-lines64k | none | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal_all | 5 | 1 |
| zlg_grep_no_index | fixed-lines64k | none | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 | literal_all | 7 | 1 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 | literal_any | 17 | 3 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 | literal_any | 6 | 2 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 | literal_all | 15 | 1 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | lookbehind_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | none | 0 | 0 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | no_match_literal | 3 | 2 | 0 | 2 | 9218316 | 0 | literal_all | 18 | 1 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal_all | 5 | 1 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 | literal_all | 7 | 1 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 | literal_any | 17 | 3 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 | literal_any | 6 | 2 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 | literal_all | 15 | 1 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | lookbehind_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | none | 0 | 0 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | no_match_literal | 3 | 2 | 0 | 2 | 9218316 | 0 | literal_all | 18 | 1 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal_all | 5 | 1 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 | literal_all | 7 | 1 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 | literal_any | 17 | 3 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 | literal_any | 6 | 2 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 | literal_all | 15 | 1 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | lookbehind_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | none | 0 | 0 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | no_match_literal | 3 | 5 | 0 | 5 | 9218316 | 0 | literal_all | 18 | 1 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal_all | 5 | 1 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 | literal_all | 7 | 1 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 | literal_any | 17 | 3 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 | literal_any | 6 | 2 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 | literal_all | 15 | 1 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | lookbehind_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | none | 0 | 0 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | no_match_literal | 3 | 5 | 0 | 5 | 9218316 | 0 | literal_all | 18 | 1 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal_all | 5 | 1 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 | literal_all | 7 | 1 |
| zlg_grep_no_index | progressive-lines | none | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 | literal_any | 17 | 3 |
| zlg_grep_no_index | progressive-lines | none | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 | literal_any | 6 | 2 |
| zlg_grep_no_index | progressive-lines | none | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 | literal_all | 15 | 1 |
| zlg_grep_no_index | progressive-lines | none | lookbehind_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | none | 0 | 0 |
| zlg_grep_no_index | progressive-lines | none | no_match_literal | 3 | 5 | 0 | 5 | 9218316 | 0 | literal_all | 18 | 1 |
| zlg_grep_no_index | progressive-lines | none | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal_all | 5 | 1 |
| zlg_grep_no_index | progressive-lines | none | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 | literal_all | 7 | 1 |
