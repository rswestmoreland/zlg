# zlg Phase 0h/0i prebench benchmark summary

This is pre-bench evidence only, not the final performance proof.

## Corpus

- Lines: 125000
- Input bytes: 9218316
- Input sha256: 942cac75a8319eae9acbcbfe97bd52d5dc1b161175ee6f9c5908c71f2edc48c2

## Median timings

| kind | name | policy | pattern | repeats | median_s | min_s | max_s | first_output_s | output_bytes |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| cat | zlg_cat | fixed-lines64k | bitmap |  | 3 | 0.121405 | 0.120361 | 0.122934 |  | 9218316 |
| cat | zlg_cat | hybrid-fixed64k-cap16m | bitmap |  | 3 | 0.123388 | 0.118505 | 0.129477 |  | 9218316 |
| cat | zlg_cat | hybrid-fixed64k-cap8m | bitmap |  | 3 | 0.115511 | 0.113207 | 0.121503 |  | 9218316 |
| cat | zlg_cat | hybrid-progressive-cap16m | bitmap |  | 3 | 0.161292 | 0.154283 | 0.161478 |  | 9218316 |
| cat | zlg_cat | hybrid-progressive-cap8m | bitmap |  | 3 | 0.152747 | 0.151119 | 0.162846 |  | 9218316 |
| cat | zlg_cat | progressive-lines | bitmap |  | 3 | 0.152289 | 0.137228 | 0.160974 |  | 9218316 |
| cat | zlg_cat_no_index | fixed-lines64k | none |  | 3 | 0.126485 | 0.125028 | 0.154352 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-fixed64k-cap16m | none |  | 3 | 0.130831 | 0.123802 | 0.148044 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-fixed64k-cap8m | none |  | 3 | 0.125628 | 0.116905 | 0.128041 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-progressive-cap16m | none |  | 3 | 0.148804 | 0.144455 | 0.160974 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-progressive-cap8m | none |  | 3 | 0.162607 | 0.158099 | 0.178706 |  | 9218316 |
| cat | zlg_cat_no_index | progressive-lines | none |  | 3 | 0.152088 | 0.151882 | 0.154106 |  | 9218316 |
| compress | gzip_6 |  |  |  | 3 | 0.168507 | 0.168378 | 0.174662 |  | 849250 |
| compress | gzip_9 |  |  |  | 3 | 0.835940 | 0.813487 | 0.862328 |  | 746531 |
| compress | zlg | fixed-lines64k | bitmap |  | 3 | 0.237546 | 0.229414 | 0.252602 |  | 623250 |
| compress | zlg | hybrid-fixed64k-cap16m | bitmap |  | 3 | 0.230839 | 0.218056 | 0.232256 |  | 623250 |
| compress | zlg | hybrid-fixed64k-cap8m | bitmap |  | 3 | 0.237188 | 0.218900 | 0.244912 |  | 623250 |
| compress | zlg | hybrid-progressive-cap16m | bitmap |  | 3 | 0.192119 | 0.177534 | 0.193715 |  | 672627 |
| compress | zlg | hybrid-progressive-cap8m | bitmap |  | 3 | 0.193923 | 0.183693 | 0.197867 |  | 672627 |
| compress | zlg | progressive-lines | bitmap |  | 3 | 0.193204 | 0.180174 | 0.194824 |  | 672627 |
| compress | zlg_no_index | fixed-lines64k | none |  | 3 | 0.157817 | 0.146377 | 0.158829 |  | 590338 |
| compress | zlg_no_index | hybrid-fixed64k-cap16m | none |  | 3 | 0.168027 | 0.156688 | 0.178395 |  | 590338 |
| compress | zlg_no_index | hybrid-fixed64k-cap8m | none |  | 3 | 0.147526 | 0.146317 | 0.160557 |  | 590338 |
| compress | zlg_no_index | hybrid-progressive-cap16m | none |  | 3 | 0.110016 | 0.104029 | 0.121353 |  | 590347 |
| compress | zlg_no_index | hybrid-progressive-cap8m | none |  | 3 | 0.112471 | 0.108588 | 0.116816 |  | 590347 |
| compress | zlg_no_index | progressive-lines | none |  | 3 | 0.110943 | 0.108917 | 0.112084 |  | 590347 |
| grep | zlg_grep | fixed-lines64k | bitmap | alternation_error_failed_denied | 3 | 0.136723 | 0.134055 | 0.137049 | 0.067895 | 175364 |
| grep | zlg_grep | fixed-lines64k | bitmap | branch_suffix | 3 | 0.129839 | 0.128138 | 0.135392 | 0.067425 | 111409 |
| grep | zlg_grep | fixed-lines64k | bitmap | literal_failed_password | 3 | 0.141874 | 0.138637 | 0.144395 | 0.078847 | 63955 |
| grep | zlg_grep | fixed-lines64k | bitmap | lookbehind_key | 3 | 0.016653 | 0.015975 | 0.017006 |  | 0 |
| grep | zlg_grep | fixed-lines64k | bitmap | no_match_literal | 3 | 0.015090 | 0.015083 | 0.017962 |  | 0 |
| grep | zlg_grep | fixed-lines64k | bitmap | quoted_key | 3 | 0.131100 | 0.130406 | 0.132300 | 0.072179 | 124168 |
| grep | zlg_grep | fixed-lines64k | bitmap | src_ip | 3 | 0.215605 | 0.208268 | 0.259972 | 0.064698 | 9218316 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | alternation_error_failed_denied | 3 | 0.127574 | 0.120499 | 0.139321 | 0.066584 | 175364 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | branch_suffix | 3 | 0.128313 | 0.125576 | 0.133648 | 0.069548 | 111409 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | literal_failed_password | 3 | 0.129671 | 0.125404 | 0.133658 | 0.068781 | 63955 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | lookbehind_key | 3 | 0.016482 | 0.016405 | 0.017939 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | no_match_literal | 3 | 0.015635 | 0.013682 | 0.015711 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | quoted_key | 3 | 0.132672 | 0.123450 | 0.134574 | 0.073688 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | src_ip | 3 | 0.197367 | 0.192887 | 0.203375 | 0.065048 | 9218316 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | alternation_error_failed_denied | 3 | 0.127375 | 0.126697 | 0.138870 | 0.064844 | 175364 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | branch_suffix | 3 | 0.137363 | 0.116340 | 0.141056 | 0.072282 | 111409 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | literal_failed_password | 3 | 0.124971 | 0.120808 | 0.134825 | 0.068819 | 63955 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | lookbehind_key | 3 | 0.017057 | 0.015233 | 0.017544 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | no_match_literal | 3 | 0.013825 | 0.013770 | 0.014629 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | quoted_key | 3 | 0.130159 | 0.129019 | 0.131064 | 0.069578 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | src_ip | 3 | 0.208034 | 0.195355 | 0.209051 | 0.067756 | 9218316 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | alternation_error_failed_denied | 3 | 0.162151 | 0.161166 | 0.172042 | 0.026025 | 175364 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | branch_suffix | 3 | 0.162200 | 0.157770 | 0.169515 | 0.026874 | 111409 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | literal_failed_password | 3 | 0.165292 | 0.162220 | 0.166585 | 0.036461 | 63955 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | lookbehind_key | 3 | 0.016717 | 0.016374 | 0.017162 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | no_match_literal | 3 | 0.014631 | 0.013941 | 0.018260 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | quoted_key | 3 | 0.174986 | 0.166647 | 0.196223 | 0.028192 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | src_ip | 3 | 0.228949 | 0.227542 | 0.243982 | 0.016992 | 9218316 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | alternation_error_failed_denied | 3 | 0.165929 | 0.148140 | 0.187295 | 0.025912 | 175364 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | branch_suffix | 3 | 0.166408 | 0.153781 | 0.193407 | 0.025296 | 111409 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | literal_failed_password | 3 | 0.159296 | 0.156619 | 0.166326 | 0.036385 | 63955 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | lookbehind_key | 3 | 0.017777 | 0.015453 | 0.022718 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | no_match_literal | 3 | 0.013250 | 0.012738 | 0.016003 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | quoted_key | 3 | 0.173606 | 0.166722 | 0.183080 | 0.028934 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | src_ip | 3 | 0.246020 | 0.217990 | 0.266157 | 0.019583 | 9218316 |
| grep | zlg_grep | progressive-lines | bitmap | alternation_error_failed_denied | 3 | 0.168850 | 0.156854 | 0.170558 | 0.025952 | 175364 |
| grep | zlg_grep | progressive-lines | bitmap | branch_suffix | 3 | 0.169985 | 0.165825 | 0.173925 | 0.027543 | 111409 |
| grep | zlg_grep | progressive-lines | bitmap | literal_failed_password | 3 | 0.165310 | 0.163353 | 0.174279 | 0.041230 | 63955 |
| grep | zlg_grep | progressive-lines | bitmap | lookbehind_key | 3 | 0.016543 | 0.014933 | 0.016718 |  | 0 |
| grep | zlg_grep | progressive-lines | bitmap | no_match_literal | 3 | 0.014785 | 0.013058 | 0.015080 |  | 0 |
| grep | zlg_grep | progressive-lines | bitmap | quoted_key | 3 | 0.162212 | 0.159020 | 0.177328 | 0.026023 | 124168 |
| grep | zlg_grep | progressive-lines | bitmap | src_ip | 3 | 0.252437 | 0.222755 | 0.262276 | 0.018754 | 9218316 |
| grep | zlg_grep_no_index | fixed-lines64k | none | alternation_error_failed_denied | 3 | 0.136270 | 0.129139 | 0.153359 | 0.072219 | 175364 |
| grep | zlg_grep_no_index | fixed-lines64k | none | branch_suffix | 3 | 0.122616 | 0.118858 | 0.143933 | 0.065344 | 111409 |
| grep | zlg_grep_no_index | fixed-lines64k | none | literal_failed_password | 3 | 0.133879 | 0.126109 | 0.135336 | 0.072634 | 63955 |
| grep | zlg_grep_no_index | fixed-lines64k | none | lookbehind_key | 3 | 0.668581 | 0.648737 | 0.712955 | 0.107359 | 124168 |
| grep | zlg_grep_no_index | fixed-lines64k | none | no_match_literal | 3 | 0.139586 | 0.132692 | 0.140791 |  | 0 |
| grep | zlg_grep_no_index | fixed-lines64k | none | quoted_key | 3 | 0.144004 | 0.129470 | 0.191006 | 0.077531 | 124168 |
| grep | zlg_grep_no_index | fixed-lines64k | none | src_ip | 3 | 0.219173 | 0.191451 | 0.228612 | 0.063328 | 9218316 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | alternation_error_failed_denied | 3 | 0.132890 | 0.130602 | 0.140968 | 0.069216 | 175364 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | branch_suffix | 3 | 0.134152 | 0.126713 | 0.134554 | 0.070097 | 111409 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | literal_failed_password | 3 | 0.133021 | 0.129838 | 0.141916 | 0.073163 | 63955 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | lookbehind_key | 3 | 0.704264 | 0.664986 | 0.712641 | 0.113601 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | no_match_literal | 3 | 0.140585 | 0.124997 | 0.156145 |  | 0 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | quoted_key | 3 | 0.128308 | 0.123711 | 0.141690 | 0.068067 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | src_ip | 3 | 0.199376 | 0.195266 | 0.221425 | 0.068271 | 9218316 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | alternation_error_failed_denied | 3 | 0.127861 | 0.122575 | 0.133763 | 0.065947 | 175364 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | branch_suffix | 3 | 0.131010 | 0.129842 | 0.135103 | 0.067968 | 111409 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | literal_failed_password | 3 | 0.129327 | 0.122327 | 0.129859 | 0.068573 | 63955 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | lookbehind_key | 3 | 0.673565 | 0.661051 | 0.683675 | 0.106318 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | no_match_literal | 3 | 0.136782 | 0.136063 | 0.139825 |  | 0 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | quoted_key | 3 | 0.129181 | 0.128031 | 0.129432 | 0.071782 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | src_ip | 3 | 0.198268 | 0.196165 | 0.203064 | 0.066962 | 9218316 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | alternation_error_failed_denied | 3 | 0.160389 | 0.159803 | 0.167655 | 0.024730 | 175364 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | branch_suffix | 3 | 0.164273 | 0.164009 | 0.182881 | 0.025617 | 111409 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | literal_failed_password | 3 | 0.164667 | 0.154758 | 0.170266 | 0.036257 | 63955 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | lookbehind_key | 3 | 0.704852 | 0.702579 | 0.730980 | 0.062828 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | no_match_literal | 3 | 0.170659 | 0.158237 | 0.174090 |  | 0 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | quoted_key | 3 | 0.167535 | 0.167252 | 0.169551 | 0.029418 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | src_ip | 3 | 0.248157 | 0.234857 | 0.260733 | 0.020188 | 9218316 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | alternation_error_failed_denied | 3 | 0.165583 | 0.164623 | 0.177051 | 0.026609 | 175364 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | branch_suffix | 3 | 0.165167 | 0.156723 | 0.179515 | 0.026257 | 111409 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | literal_failed_password | 3 | 0.163370 | 0.163186 | 0.188949 | 0.035250 | 63955 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | lookbehind_key | 3 | 0.730833 | 0.730164 | 0.783130 | 0.065148 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | no_match_literal | 3 | 0.175360 | 0.170751 | 0.177182 |  | 0 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | quoted_key | 3 | 0.163015 | 0.149810 | 0.180014 | 0.026989 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | src_ip | 3 | 0.231413 | 0.222215 | 0.255458 | 0.017660 | 9218316 |
| grep | zlg_grep_no_index | progressive-lines | none | alternation_error_failed_denied | 3 | 0.160281 | 0.158154 | 0.180322 | 0.026013 | 175364 |
| grep | zlg_grep_no_index | progressive-lines | none | branch_suffix | 3 | 0.172967 | 0.171553 | 0.189882 | 0.027172 | 111409 |
| grep | zlg_grep_no_index | progressive-lines | none | literal_failed_password | 3 | 0.157757 | 0.152164 | 0.160745 | 0.034992 | 63955 |
| grep | zlg_grep_no_index | progressive-lines | none | lookbehind_key | 3 | 0.716066 | 0.711770 | 0.719925 | 0.064608 | 124168 |
| grep | zlg_grep_no_index | progressive-lines | none | no_match_literal | 3 | 0.176277 | 0.174227 | 0.206400 |  | 0 |
| grep | zlg_grep_no_index | progressive-lines | none | quoted_key | 3 | 0.160632 | 0.158584 | 0.171260 | 0.026345 | 124168 |
| grep | zlg_grep_no_index | progressive-lines | none | src_ip | 3 | 0.235051 | 0.226185 | 0.238552 | 0.018708 | 9218316 |
| grep_baseline | grep_plain |  |  | alternation_error_failed_denied | 3 | 0.034647 | 0.031864 | 0.034858 | 0.010413 | 175364 |
| grep_baseline | grep_plain |  |  | branch_suffix | 3 | 0.022431 | 0.021408 | 0.024764 | 0.010549 | 34486 |
| grep_baseline | grep_plain |  |  | literal_failed_password | 3 | 0.019752 | 0.018709 | 0.020862 | 0.009926 | 63955 |
| grep_baseline | grep_plain |  |  | no_match_literal | 3 | 0.015473 | 0.014813 | 0.020593 |  | 0 |
| grep_baseline | grep_plain |  |  | quoted_key | 3 | 0.018552 | 0.018228 | 0.019400 | 0.008650 | 124168 |
| grep_baseline | grep_plain |  |  | src_ip | 3 | 0.104967 | 0.096393 | 0.121897 | 0.007663 | 9218316 |
| grep_baseline | rg_plain |  |  | alternation_error_failed_denied | 3 | 0.036161 | 0.031292 | 0.071166 | 0.016378 | 175364 |
| grep_baseline | rg_plain |  |  | branch_suffix | 3 | 0.043288 | 0.034055 | 0.043638 | 0.020705 | 111409 |
| grep_baseline | rg_plain |  |  | literal_failed_password | 3 | 0.033725 | 0.030022 | 0.043320 | 0.017020 | 63955 |
| grep_baseline | rg_plain |  |  | no_match_literal | 3 | 0.030281 | 0.028758 | 0.031502 |  | 0 |
| grep_baseline | rg_plain |  |  | quoted_key | 3 | 0.032915 | 0.032457 | 0.040340 | 0.017775 | 124168 |
| grep_baseline | rg_plain |  |  | src_ip | 3 | 0.141075 | 0.137722 | 0.143198 | 0.016371 | 9218316 |
| grep_baseline | zgrep_gzip6 |  |  | alternation_error_failed_denied | 3 | 0.096914 | 0.094922 | 0.099850 | 0.041133 | 175364 |
| grep_baseline | zgrep_gzip6 |  |  | branch_suffix | 3 | 0.104258 | 0.100623 | 0.107724 | 0.050973 | 34486 |
| grep_baseline | zgrep_gzip6 |  |  | literal_failed_password | 3 | 0.096595 | 0.096391 | 0.099914 | 0.043849 | 63955 |
| grep_baseline | zgrep_gzip6 |  |  | no_match_literal | 3 | 0.105741 | 0.100611 | 0.112398 |  | 0 |
| grep_baseline | zgrep_gzip6 |  |  | quoted_key | 3 | 0.097721 | 0.096186 | 0.106085 | 0.041998 | 124168 |
| grep_baseline | zgrep_gzip6 |  |  | src_ip | 3 | 0.153006 | 0.150643 | 0.175812 | 0.046084 | 9218316 |

## zlg grep counter medians

| policy | pattern | repeats | chunks_total | chunks_skipped | chunks_decoded | decoded_bytes | matching_lines |
|---|---|---:|---:|---:|---:|---:|---:|
| zlg_grep | fixed-lines64k | bitmap | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 | none | 0 |
| zlg_grep | fixed-lines64k | bitmap | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 | none | 0 |
| zlg_grep | fixed-lines64k | bitmap | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 | literal | 15 |
| zlg_grep | fixed-lines64k | bitmap | lookbehind_key | 3 | 2 | 2 | 0 | 0 | 0 | literal | 6 |
| zlg_grep | fixed-lines64k | bitmap | no_match_literal | 3 | 2 | 2 | 0 | 0 | 0 | literal | 18 |
| zlg_grep | fixed-lines64k | bitmap | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal | 5 |
| zlg_grep | fixed-lines64k | bitmap | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 | literal | 7 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 | none | 0 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 | none | 0 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 | literal | 15 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | lookbehind_key | 3 | 2 | 2 | 0 | 0 | 0 | literal | 6 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | no_match_literal | 3 | 2 | 2 | 0 | 0 | 0 | literal | 18 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal | 5 |
| zlg_grep | hybrid-fixed64k-cap16m | bitmap | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 | literal | 7 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 | none | 0 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 | none | 0 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 | literal | 15 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | lookbehind_key | 3 | 2 | 2 | 0 | 0 | 0 | literal | 6 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | no_match_literal | 3 | 2 | 2 | 0 | 0 | 0 | literal | 18 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal | 5 |
| zlg_grep | hybrid-fixed64k-cap8m | bitmap | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 | literal | 7 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 | none | 0 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 | none | 0 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 | literal | 15 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | lookbehind_key | 3 | 5 | 5 | 0 | 0 | 0 | literal | 6 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | no_match_literal | 3 | 5 | 5 | 0 | 0 | 0 | literal | 18 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal | 5 |
| zlg_grep | hybrid-progressive-cap16m | bitmap | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 | literal | 7 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 | none | 0 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 | none | 0 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 | literal | 15 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | lookbehind_key | 3 | 5 | 5 | 0 | 0 | 0 | literal | 6 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | no_match_literal | 3 | 5 | 5 | 0 | 0 | 0 | literal | 18 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal | 5 |
| zlg_grep | hybrid-progressive-cap8m | bitmap | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 | literal | 7 |
| zlg_grep | progressive-lines | bitmap | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 | none | 0 |
| zlg_grep | progressive-lines | bitmap | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 | none | 0 |
| zlg_grep | progressive-lines | bitmap | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 | literal | 15 |
| zlg_grep | progressive-lines | bitmap | lookbehind_key | 3 | 5 | 5 | 0 | 0 | 0 | literal | 6 |
| zlg_grep | progressive-lines | bitmap | no_match_literal | 3 | 5 | 5 | 0 | 0 | 0 | literal | 18 |
| zlg_grep | progressive-lines | bitmap | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal | 5 |
| zlg_grep | progressive-lines | bitmap | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 | literal | 7 |
| zlg_grep_no_index | fixed-lines64k | none | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 | none | 0 |
| zlg_grep_no_index | fixed-lines64k | none | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 | none | 0 |
| zlg_grep_no_index | fixed-lines64k | none | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 | literal | 15 |
| zlg_grep_no_index | fixed-lines64k | none | lookbehind_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal | 6 |
| zlg_grep_no_index | fixed-lines64k | none | no_match_literal | 3 | 2 | 0 | 2 | 9218316 | 0 | literal | 18 |
| zlg_grep_no_index | fixed-lines64k | none | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal | 5 |
| zlg_grep_no_index | fixed-lines64k | none | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 | literal | 7 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 | none | 0 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 | none | 0 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 | literal | 15 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | lookbehind_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal | 6 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | no_match_literal | 3 | 2 | 0 | 2 | 9218316 | 0 | literal | 18 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal | 5 |
| zlg_grep_no_index | hybrid-fixed64k-cap16m | none | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 | literal | 7 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | alternation_error_failed_denied | 3 | 2 | 0 | 2 | 9218316 | 2816 | none | 0 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | branch_suffix | 3 | 2 | 0 | 2 | 9218316 | 1871 | none | 0 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | literal_failed_password | 3 | 2 | 0 | 2 | 9218316 | 945 | literal | 15 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | lookbehind_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal | 6 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | no_match_literal | 3 | 2 | 0 | 2 | 9218316 | 0 | literal | 18 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | quoted_key | 3 | 2 | 0 | 2 | 9218316 | 2115 | literal | 5 |
| zlg_grep_no_index | hybrid-fixed64k-cap8m | none | src_ip | 3 | 2 | 0 | 2 | 9218316 | 125000 | literal | 7 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 | none | 0 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 | none | 0 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 | literal | 15 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | lookbehind_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal | 6 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | no_match_literal | 3 | 5 | 0 | 5 | 9218316 | 0 | literal | 18 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal | 5 |
| zlg_grep_no_index | hybrid-progressive-cap16m | none | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 | literal | 7 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 | none | 0 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 | none | 0 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 | literal | 15 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | lookbehind_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal | 6 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | no_match_literal | 3 | 5 | 0 | 5 | 9218316 | 0 | literal | 18 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal | 5 |
| zlg_grep_no_index | hybrid-progressive-cap8m | none | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 | literal | 7 |
| zlg_grep_no_index | progressive-lines | none | alternation_error_failed_denied | 3 | 5 | 0 | 5 | 9218316 | 2816 | none | 0 |
| zlg_grep_no_index | progressive-lines | none | branch_suffix | 3 | 5 | 0 | 5 | 9218316 | 1871 | none | 0 |
| zlg_grep_no_index | progressive-lines | none | literal_failed_password | 3 | 5 | 0 | 5 | 9218316 | 945 | literal | 15 |
| zlg_grep_no_index | progressive-lines | none | lookbehind_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal | 6 |
| zlg_grep_no_index | progressive-lines | none | no_match_literal | 3 | 5 | 0 | 5 | 9218316 | 0 | literal | 18 |
| zlg_grep_no_index | progressive-lines | none | quoted_key | 3 | 5 | 0 | 5 | 9218316 | 2115 | literal | 5 |
| zlg_grep_no_index | progressive-lines | none | src_ip | 3 | 5 | 0 | 5 | 9218316 | 125000 | literal | 7 |
