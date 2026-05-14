# zlg Phase 0h/0i prebench benchmark summary

This is pre-bench evidence only, not the final performance proof.

## Corpus

- Lines: 125000
- Input bytes: 9218316
- Input sha256: 942cac75a8319eae9acbcbfe97bd52d5dc1b161175ee6f9c5908c71f2edc48c2

## Median timings

| kind | name | policy | pattern | repeats | median_s | min_s | max_s | first_output_s | output_bytes |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| cat | zlg_cat | fixed-lines64k | bitmap |  | 3 | 0.090445 | 0.088505 | 0.094532 |  | 9218316 |
| cat | zlg_cat | hybrid-fixed64k-cap16m | bitmap |  | 3 | 0.093505 | 0.092615 | 0.097822 |  | 9218316 |
| cat | zlg_cat | hybrid-fixed64k-cap8m | bitmap |  | 3 | 0.086176 | 0.083493 | 0.090308 |  | 9218316 |
| cat | zlg_cat | hybrid-progressive-cap16m | bitmap |  | 3 | 0.114109 | 0.110499 | 0.121526 |  | 9218316 |
| cat | zlg_cat | hybrid-progressive-cap8m | bitmap |  | 3 | 0.114069 | 0.110834 | 0.120954 |  | 9218316 |
| cat | zlg_cat | progressive-lines | bitmap |  | 3 | 0.110387 | 0.107205 | 0.111636 |  | 9218316 |
| cat | zlg_cat_no_index | fixed-lines64k | none |  | 3 | 0.091449 | 0.088916 | 0.093208 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-fixed64k-cap16m | none |  | 3 | 0.086863 | 0.086303 | 0.100254 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-fixed64k-cap8m | none |  | 3 | 0.090424 | 0.083851 | 0.099960 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-progressive-cap16m | none |  | 3 | 0.117264 | 0.110303 | 0.132761 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-progressive-cap8m | none |  | 3 | 0.115282 | 0.113059 | 0.116581 |  | 9218316 |
| cat | zlg_cat_no_index | progressive-lines | none |  | 3 | 0.112652 | 0.108654 | 0.125325 |  | 9218316 |
| compress | gzip_6 |  |  |  | 3 | 0.137555 | 0.136540 | 0.138790 |  | 849250 |
| compress | gzip_9 |  |  |  | 3 | 0.695652 | 0.689602 | 0.696304 |  | 746531 |
| compress | zlg | fixed-lines64k | bitmap |  | 3 | 0.166138 | 0.165505 | 0.171610 |  | 623250 |
| compress | zlg | hybrid-fixed64k-cap16m | bitmap |  | 3 | 0.165116 | 0.164625 | 0.171848 |  | 623250 |
| compress | zlg | hybrid-fixed64k-cap8m | bitmap |  | 3 | 0.171003 | 0.160083 | 0.177582 |  | 623250 |
| compress | zlg | hybrid-progressive-cap16m | bitmap |  | 3 | 0.135864 | 0.130532 | 0.139263 |  | 672627 |
| compress | zlg | hybrid-progressive-cap8m | bitmap |  | 3 | 0.138661 | 0.133958 | 0.157923 |  | 672627 |
| compress | zlg | progressive-lines | bitmap |  | 3 | 0.131796 | 0.130758 | 0.140773 |  | 672627 |
| compress | zlg_no_index | fixed-lines64k | none |  | 3 | 0.107886 | 0.105329 | 0.109460 |  | 590338 |
| compress | zlg_no_index | hybrid-fixed64k-cap16m | none |  | 3 | 0.117851 | 0.108823 | 0.120833 |  | 590338 |
| compress | zlg_no_index | hybrid-fixed64k-cap8m | none |  | 3 | 0.107910 | 0.104969 | 0.112549 |  | 590338 |
| compress | zlg_no_index | hybrid-progressive-cap16m | none |  | 3 | 0.078497 | 0.077066 | 0.084573 |  | 590347 |
| compress | zlg_no_index | hybrid-progressive-cap8m | none |  | 3 | 0.082132 | 0.077214 | 0.083996 |  | 590347 |
| compress | zlg_no_index | progressive-lines | none |  | 3 | 0.082378 | 0.079234 | 0.082517 |  | 590347 |
| grep | zlg_grep | fixed-lines64k | bitmap | alternation_error_failed_denied | 3 | 0.098536 | 0.094414 | 0.103363 | 0.051668 | 175364 |
| grep | zlg_grep | fixed-lines64k | bitmap | branch_suffix | 3 | 0.101538 | 0.096239 | 0.102370 | 0.054816 | 111409 |
| grep | zlg_grep | fixed-lines64k | bitmap | literal_failed_password | 3 | 0.091907 | 0.091619 | 0.098769 | 0.050025 | 63955 |
| grep | zlg_grep | fixed-lines64k | bitmap | lookbehind_key | 3 | 0.514199 | 0.499107 | 0.544515 | 0.080905 | 124168 |
| grep | zlg_grep | fixed-lines64k | bitmap | no_match_literal | 3 | 0.011686 | 0.010633 | 0.011694 |  | 0 |
| grep | zlg_grep | fixed-lines64k | bitmap | quoted_key | 3 | 0.096943 | 0.093520 | 0.102916 | 0.053554 | 124168 |
| grep | zlg_grep | fixed-lines64k | bitmap | src_ip | 3 | 0.152982 | 0.152440 | 0.183117 | 0.050406 | 9218316 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | alternation_error_failed_denied | 3 | 0.101648 | 0.098993 | 0.105324 | 0.052456 | 175364 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | branch_suffix | 3 | 0.097955 | 0.093566 | 0.100859 | 0.052585 | 111409 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | literal_failed_password | 3 | 0.094033 | 0.093993 | 0.104741 | 0.050900 | 63955 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | lookbehind_key | 3 | 0.513363 | 0.506364 | 0.531949 | 0.084631 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | no_match_literal | 3 | 0.012070 | 0.011300 | 0.012847 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | quoted_key | 3 | 0.099182 | 0.097361 | 0.110863 | 0.056241 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | src_ip | 3 | 0.151485 | 0.148231 | 0.177600 | 0.050014 | 9218316 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | alternation_error_failed_denied | 3 | 0.094858 | 0.094320 | 0.096130 | 0.048962 | 175364 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | branch_suffix | 3 | 0.096455 | 0.093379 | 0.101455 | 0.051580 | 111409 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | literal_failed_password | 3 | 0.093854 | 0.093348 | 0.095988 | 0.051332 | 63955 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | lookbehind_key | 3 | 0.512473 | 0.501152 | 0.517039 | 0.082586 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | no_match_literal | 3 | 0.011589 | 0.011420 | 0.012013 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | quoted_key | 3 | 0.099594 | 0.091736 | 0.106234 | 0.054176 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | src_ip | 3 | 0.145995 | 0.145686 | 0.155178 | 0.050357 | 9218316 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | alternation_error_failed_denied | 3 | 0.123709 | 0.118580 | 0.131941 | 0.020125 | 175364 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | branch_suffix | 3 | 0.128170 | 0.123860 | 0.133351 | 0.020161 | 111409 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | literal_failed_password | 3 | 0.122619 | 0.113334 | 0.123473 | 0.026373 | 63955 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | lookbehind_key | 3 | 0.538573 | 0.524360 | 0.558560 | 0.046697 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | no_match_literal | 3 | 0.011271 | 0.011106 | 0.014364 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | quoted_key | 3 | 0.122762 | 0.120577 | 0.125878 | 0.019821 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | src_ip | 3 | 0.181936 | 0.175490 | 0.241074 | 0.014328 | 9218316 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | alternation_error_failed_denied | 3 | 0.119744 | 0.118696 | 0.124833 | 0.019108 | 175364 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | branch_suffix | 3 | 0.122469 | 0.120036 | 0.124317 | 0.020169 | 111409 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | literal_failed_password | 3 | 0.115675 | 0.114134 | 0.119478 | 0.026254 | 63955 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | lookbehind_key | 3 | 0.515275 | 0.509723 | 0.519900 | 0.046253 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | no_match_literal | 3 | 0.011969 | 0.010989 | 0.013273 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | quoted_key | 3 | 0.118652 | 0.116440 | 0.122356 | 0.020274 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | src_ip | 3 | 0.166553 | 0.163754 | 0.167949 | 0.012947 | 9218316 |
| grep | zlg_grep | progressive-lines | bitmap | alternation_error_failed_denied | 3 | 0.118430 | 0.116994 | 0.140358 | 0.019634 | 175364 |
| grep | zlg_grep | progressive-lines | bitmap | branch_suffix | 3 | 0.122908 | 0.118076 | 0.123313 | 0.020251 | 111409 |
| grep | zlg_grep | progressive-lines | bitmap | literal_failed_password | 3 | 0.115912 | 0.115411 | 0.124452 | 0.025956 | 63955 |
| grep | zlg_grep | progressive-lines | bitmap | lookbehind_key | 3 | 0.531297 | 0.512874 | 0.533067 | 0.047699 | 124168 |
| grep | zlg_grep | progressive-lines | bitmap | no_match_literal | 3 | 0.011953 | 0.010820 | 0.012283 |  | 0 |
| grep | zlg_grep | progressive-lines | bitmap | quoted_key | 3 | 0.126460 | 0.113086 | 0.131077 | 0.019981 | 124168 |
| grep | zlg_grep | progressive-lines | bitmap | src_ip | 3 | 0.170332 | 0.166518 | 0.175708 | 0.013236 | 9218316 |
| grep | zlg_grep_no_index | fixed-lines64k | none | alternation_error_failed_denied | 3 | 0.098840 | 0.098221 | 0.104253 | 0.050729 | 175364 |
| grep | zlg_grep_no_index | fixed-lines64k | none | branch_suffix | 3 | 0.100487 | 0.096600 | 0.100945 | 0.053208 | 111409 |
| grep | zlg_grep_no_index | fixed-lines64k | none | literal_failed_password | 3 | 0.098327 | 0.092534 | 0.099194 | 0.052579 | 63955 |
| grep | zlg_grep_no_index | fixed-lines64k | none | lookbehind_key | 3 | 0.506698 | 0.490400 | 0.550289 | 0.083273 | 124168 |
| grep | zlg_grep_no_index | fixed-lines64k | none | no_match_literal | 3 | 0.102332 | 0.100819 | 0.108954 |  | 0 |
| grep | zlg_grep_no_index | fixed-lines64k | none | quoted_key | 3 | 0.097082 | 0.092009 | 0.100588 | 0.053048 | 124168 |
| grep | zlg_grep_no_index | fixed-lines64k | none | src_ip | 3 | 0.152410 | 0.139420 | 0.167558 | 0.050841 | 9218316 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | alternation_error_failed_denied | 3 | 0.096060 | 0.095908 | 0.102316 | 0.050357 | 175364 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | branch_suffix | 3 | 0.098348 | 0.097136 | 0.101250 | 0.051645 | 111409 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | literal_failed_password | 3 | 0.098978 | 0.091897 | 0.102095 | 0.053151 | 63955 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | lookbehind_key | 3 | 0.512637 | 0.497606 | 0.575473 | 0.082076 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | no_match_literal | 3 | 0.104480 | 0.102821 | 0.120071 |  | 0 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | quoted_key | 3 | 0.101321 | 0.097069 | 0.117630 | 0.054981 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | src_ip | 3 | 0.148214 | 0.147123 | 0.164637 | 0.052487 | 9218316 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | alternation_error_failed_denied | 3 | 0.103130 | 0.098931 | 0.104152 | 0.052230 | 175364 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | branch_suffix | 3 | 0.098638 | 0.093879 | 0.108907 | 0.051795 | 111409 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | literal_failed_password | 3 | 0.099380 | 0.096419 | 0.103592 | 0.052724 | 63955 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | lookbehind_key | 3 | 0.518739 | 0.491789 | 0.574095 | 0.081203 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | no_match_literal | 3 | 0.109893 | 0.103463 | 0.111771 |  | 0 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | quoted_key | 3 | 0.099807 | 0.096436 | 0.103561 | 0.053872 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | src_ip | 3 | 0.152999 | 0.152172 | 0.158998 | 0.050622 | 9218316 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | alternation_error_failed_denied | 3 | 0.122032 | 0.117004 | 0.128786 | 0.019209 | 175364 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | branch_suffix | 3 | 0.120788 | 0.113979 | 0.129231 | 0.018998 | 111409 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | literal_failed_password | 3 | 0.114516 | 0.114445 | 0.122630 | 0.026319 | 63955 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | lookbehind_key | 3 | 0.515580 | 0.510258 | 0.532251 | 0.045769 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | no_match_literal | 3 | 0.126662 | 0.117512 | 0.133195 |  | 0 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | quoted_key | 3 | 0.120799 | 0.114288 | 0.125291 | 0.019897 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | src_ip | 3 | 0.167387 | 0.166841 | 0.178398 | 0.013883 | 9218316 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | alternation_error_failed_denied | 3 | 0.130428 | 0.121611 | 0.140048 | 0.021030 | 175364 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | branch_suffix | 3 | 0.118967 | 0.118687 | 0.139075 | 0.019238 | 111409 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | literal_failed_password | 3 | 0.119198 | 0.117369 | 0.126585 | 0.025683 | 63955 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | lookbehind_key | 3 | 0.532724 | 0.507484 | 0.551313 | 0.048460 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | no_match_literal | 3 | 0.129840 | 0.122336 | 0.130178 |  | 0 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | quoted_key | 3 | 0.124522 | 0.119328 | 0.137525 | 0.020788 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | src_ip | 3 | 0.181857 | 0.176066 | 0.185545 | 0.014851 | 9218316 |
| grep | zlg_grep_no_index | progressive-lines | none | alternation_error_failed_denied | 3 | 0.122121 | 0.121720 | 0.124566 | 0.019335 | 175364 |
| grep | zlg_grep_no_index | progressive-lines | none | branch_suffix | 3 | 0.125633 | 0.118381 | 0.129544 | 0.021375 | 111409 |
| grep | zlg_grep_no_index | progressive-lines | none | literal_failed_password | 3 | 0.121488 | 0.119659 | 0.122160 | 0.026492 | 63955 |
| grep | zlg_grep_no_index | progressive-lines | none | lookbehind_key | 3 | 0.532711 | 0.529455 | 0.552336 | 0.050448 | 124168 |
| grep | zlg_grep_no_index | progressive-lines | none | no_match_literal | 3 | 0.126251 | 0.120950 | 0.130063 |  | 0 |
| grep | zlg_grep_no_index | progressive-lines | none | quoted_key | 3 | 0.124000 | 0.117106 | 0.137966 | 0.021024 | 124168 |
| grep | zlg_grep_no_index | progressive-lines | none | src_ip | 3 | 0.181331 | 0.172827 | 0.186623 | 0.014250 | 9218316 |
| grep_baseline | grep_plain |  |  | alternation_error_failed_denied | 3 | 0.024408 | 0.023837 | 0.025803 | 0.007158 | 175364 |
| grep_baseline | grep_plain |  |  | branch_suffix | 3 | 0.019601 | 0.015497 | 0.021318 | 0.008138 | 34486 |
| grep_baseline | grep_plain |  |  | literal_failed_password | 3 | 0.014796 | 0.013592 | 0.015207 | 0.007655 | 63955 |
| grep_baseline | grep_plain |  |  | no_match_literal | 3 | 0.011733 | 0.011677 | 0.013918 |  | 0 |
| grep_baseline | grep_plain |  |  | quoted_key | 3 | 0.013553 | 0.012090 | 0.017335 | 0.006301 | 124168 |
| grep_baseline | grep_plain |  |  | src_ip | 3 | 0.089867 | 0.077681 | 0.096852 | 0.006666 | 9218316 |
| grep_baseline | rg_plain |  |  | alternation_error_failed_denied | 3 | 0.024871 | 0.023879 | 0.030590 | 0.012853 | 175364 |
| grep_baseline | rg_plain |  |  | branch_suffix | 3 | 0.025400 | 0.022565 | 0.027997 | 0.012513 | 111409 |
| grep_baseline | rg_plain |  |  | literal_failed_password | 3 | 0.023077 | 0.021909 | 0.026221 | 0.012066 | 63955 |
| grep_baseline | rg_plain |  |  | no_match_literal | 3 | 0.021096 | 0.020027 | 0.027765 |  | 0 |
| grep_baseline | rg_plain |  |  | quoted_key | 3 | 0.024849 | 0.022286 | 0.036414 | 0.013827 | 124168 |
| grep_baseline | rg_plain |  |  | src_ip | 3 | 0.102446 | 0.100428 | 0.120560 | 0.010483 | 9218316 |
| grep_baseline | zgrep_gzip6 |  |  | alternation_error_failed_denied | 3 | 0.079533 | 0.078871 | 0.086162 | 0.030296 | 175364 |
| grep_baseline | zgrep_gzip6 |  |  | branch_suffix | 3 | 0.080155 | 0.074811 | 0.081704 | 0.036229 | 34486 |
| grep_baseline | zgrep_gzip6 |  |  | literal_failed_password | 3 | 0.082093 | 0.080644 | 0.085762 | 0.033218 | 63955 |
| grep_baseline | zgrep_gzip6 |  |  | no_match_literal | 3 | 0.081488 | 0.078561 | 0.083358 |  | 0 |
| grep_baseline | zgrep_gzip6 |  |  | quoted_key | 3 | 0.077409 | 0.074341 | 0.077890 | 0.030148 | 124168 |
| grep_baseline | zgrep_gzip6 |  |  | src_ip | 3 | 0.121543 | 0.119326 | 0.125039 | 0.030420 | 9218316 |

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
