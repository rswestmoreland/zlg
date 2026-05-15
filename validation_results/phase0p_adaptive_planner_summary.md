# zlg Phase 0h/0i prebench benchmark summary

This is pre-bench evidence only, not the final performance proof.

## Corpus

- Lines: 125000
- Input bytes: 9218316
- Input sha256: 942cac75a8319eae9acbcbfe97bd52d5dc1b161175ee6f9c5908c71f2edc48c2

## Median timings

| kind | name | policy | pattern | repeats | median_s | min_s | max_s | first_output_s | output_bytes |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| cat | zlg_cat | fixed-lines64k | bitmap |  | 3 | 0.087260 | 0.083982 | 0.093813 |  | 9218316 |
| cat | zlg_cat | hybrid-fixed64k-cap16m | bitmap |  | 3 | 0.082115 | 0.080991 | 0.088463 |  | 9218316 |
| cat | zlg_cat | hybrid-fixed64k-cap8m | bitmap |  | 3 | 0.094494 | 0.087326 | 0.096274 |  | 9218316 |
| cat | zlg_cat | hybrid-progressive-cap16m | bitmap |  | 3 | 0.114347 | 0.103836 | 0.115881 |  | 9218316 |
| cat | zlg_cat | hybrid-progressive-cap8m | bitmap |  | 3 | 0.105842 | 0.105731 | 0.115462 |  | 9218316 |
| cat | zlg_cat | progressive-lines | bitmap |  | 3 | 0.103319 | 0.102935 | 0.109039 |  | 9218316 |
| cat | zlg_cat_no_index | fixed-lines64k | none |  | 3 | 0.087242 | 0.085806 | 0.095629 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-fixed64k-cap16m | none |  | 3 | 0.094374 | 0.092627 | 0.103015 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-fixed64k-cap8m | none |  | 3 | 0.090844 | 0.086070 | 0.093239 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-progressive-cap16m | none |  | 3 | 0.116622 | 0.110751 | 0.120624 |  | 9218316 |
| cat | zlg_cat_no_index | hybrid-progressive-cap8m | none |  | 3 | 0.113137 | 0.111171 | 0.135721 |  | 9218316 |
| cat | zlg_cat_no_index | progressive-lines | none |  | 3 | 0.108541 | 0.105926 | 0.124655 |  | 9218316 |
| compress | gzip_6 |  |  |  | 3 | 0.140940 | 0.136602 | 0.141214 |  | 849250 |
| compress | gzip_9 |  |  |  | 3 | 0.694296 | 0.688872 | 0.712768 |  | 746531 |
| compress | zlg | fixed-lines64k | bitmap |  | 3 | 0.169842 | 0.162810 | 0.170819 |  | 623250 |
| compress | zlg | hybrid-fixed64k-cap16m | bitmap |  | 3 | 0.167333 | 0.160676 | 0.169836 |  | 623250 |
| compress | zlg | hybrid-fixed64k-cap8m | bitmap |  | 3 | 0.162812 | 0.158146 | 0.171710 |  | 623250 |
| compress | zlg | hybrid-progressive-cap16m | bitmap |  | 3 | 0.132309 | 0.128063 | 0.132431 |  | 672627 |
| compress | zlg | hybrid-progressive-cap8m | bitmap |  | 3 | 0.135584 | 0.130667 | 0.135711 |  | 672627 |
| compress | zlg | progressive-lines | bitmap |  | 3 | 0.139350 | 0.138320 | 0.143511 |  | 672627 |
| compress | zlg_no_index | fixed-lines64k | none |  | 3 | 0.120538 | 0.117295 | 0.123220 |  | 590338 |
| compress | zlg_no_index | hybrid-fixed64k-cap16m | none |  | 3 | 0.111587 | 0.100282 | 0.113923 |  | 590338 |
| compress | zlg_no_index | hybrid-fixed64k-cap8m | none |  | 3 | 0.113224 | 0.106217 | 0.118014 |  | 590338 |
| compress | zlg_no_index | hybrid-progressive-cap16m | none |  | 3 | 0.080446 | 0.071947 | 0.082597 |  | 590347 |
| compress | zlg_no_index | hybrid-progressive-cap8m | none |  | 3 | 0.080307 | 0.076259 | 0.080998 |  | 590347 |
| compress | zlg_no_index | progressive-lines | none |  | 3 | 0.082965 | 0.081732 | 0.083018 |  | 590347 |
| grep | zlg_grep | fixed-lines64k | bitmap | alternation_error_failed_denied | 3 | 0.096022 | 0.093765 | 0.103260 | 0.048793 | 175364 |
| grep | zlg_grep | fixed-lines64k | bitmap | branch_suffix | 3 | 0.096900 | 0.093305 | 0.099987 | 0.051454 | 111409 |
| grep | zlg_grep | fixed-lines64k | bitmap | literal_failed_password | 3 | 0.090851 | 0.088831 | 0.095013 | 0.049827 | 63955 |
| grep | zlg_grep | fixed-lines64k | bitmap | lookbehind_key | 3 | 0.490679 | 0.479097 | 0.495198 | 0.077676 | 124168 |
| grep | zlg_grep | fixed-lines64k | bitmap | no_match_literal | 3 | 0.011080 | 0.010764 | 0.011945 |  | 0 |
| grep | zlg_grep | fixed-lines64k | bitmap | quoted_key | 3 | 0.098288 | 0.096904 | 0.098569 | 0.052739 | 124168 |
| grep | zlg_grep | fixed-lines64k | bitmap | src_ip | 3 | 0.146914 | 0.143742 | 0.188048 | 0.050980 | 9218316 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | alternation_error_failed_denied | 3 | 0.104890 | 0.097813 | 0.110517 | 0.055467 | 175364 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | branch_suffix | 3 | 0.096450 | 0.096180 | 0.107419 | 0.051388 | 111409 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | literal_failed_password | 3 | 0.093874 | 0.090395 | 0.105678 | 0.051377 | 63955 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | lookbehind_key | 3 | 0.522290 | 0.503794 | 0.551913 | 0.084758 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | no_match_literal | 3 | 0.011659 | 0.010864 | 0.012398 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | quoted_key | 3 | 0.097664 | 0.094160 | 0.101422 | 0.053299 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | bitmap | src_ip | 3 | 0.154233 | 0.143042 | 0.161783 | 0.053469 | 9218316 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | alternation_error_failed_denied | 3 | 0.097455 | 0.097380 | 0.102398 | 0.050536 | 175364 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | branch_suffix | 3 | 0.101738 | 0.093491 | 0.121040 | 0.054438 | 111409 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | literal_failed_password | 3 | 0.094795 | 0.091095 | 0.101522 | 0.051909 | 63955 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | lookbehind_key | 3 | 0.504524 | 0.489344 | 0.508834 | 0.083893 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | no_match_literal | 3 | 0.011903 | 0.011483 | 0.013349 |  | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | quoted_key | 3 | 0.098474 | 0.090994 | 0.099873 | 0.052219 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | bitmap | src_ip | 3 | 0.143995 | 0.142225 | 0.147209 | 0.048513 | 9218316 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | alternation_error_failed_denied | 3 | 0.122569 | 0.121714 | 0.127345 | 0.020407 | 175364 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | branch_suffix | 3 | 0.120460 | 0.119277 | 0.124120 | 0.021063 | 111409 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | literal_failed_password | 3 | 0.124931 | 0.119765 | 0.127131 | 0.027968 | 63955 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | lookbehind_key | 3 | 0.531439 | 0.522061 | 0.567900 | 0.049157 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | no_match_literal | 3 | 0.011972 | 0.011526 | 0.012162 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | quoted_key | 3 | 0.128019 | 0.127649 | 0.130159 | 0.021636 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap16m | bitmap | src_ip | 3 | 0.181178 | 0.166696 | 0.182338 | 0.013388 | 9218316 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | alternation_error_failed_denied | 3 | 0.120669 | 0.120563 | 0.129979 | 0.019478 | 175364 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | branch_suffix | 3 | 0.123327 | 0.118484 | 0.124050 | 0.020621 | 111409 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | literal_failed_password | 3 | 0.113058 | 0.112695 | 0.117171 | 0.025390 | 63955 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | lookbehind_key | 3 | 0.526032 | 0.520962 | 0.530916 | 0.048780 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | no_match_literal | 3 | 0.012039 | 0.010302 | 0.020403 |  | 0 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | quoted_key | 3 | 0.115681 | 0.115413 | 0.122459 | 0.019312 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap8m | bitmap | src_ip | 3 | 0.173306 | 0.163848 | 0.175960 | 0.013641 | 9218316 |
| grep | zlg_grep | progressive-lines | bitmap | alternation_error_failed_denied | 3 | 0.113124 | 0.111715 | 0.121702 | 0.018118 | 175364 |
| grep | zlg_grep | progressive-lines | bitmap | branch_suffix | 3 | 0.118567 | 0.110772 | 0.121335 | 0.018114 | 111409 |
| grep | zlg_grep | progressive-lines | bitmap | literal_failed_password | 3 | 0.117103 | 0.109481 | 0.118159 | 0.025789 | 63955 |
| grep | zlg_grep | progressive-lines | bitmap | lookbehind_key | 3 | 0.526044 | 0.505956 | 0.556485 | 0.045083 | 124168 |
| grep | zlg_grep | progressive-lines | bitmap | no_match_literal | 3 | 0.011847 | 0.010338 | 0.012696 |  | 0 |
| grep | zlg_grep | progressive-lines | bitmap | quoted_key | 3 | 0.119103 | 0.113052 | 0.122437 | 0.019333 | 124168 |
| grep | zlg_grep | progressive-lines | bitmap | src_ip | 3 | 0.164850 | 0.164232 | 0.172401 | 0.013731 | 9218316 |
| grep | zlg_grep_no_index | fixed-lines64k | none | alternation_error_failed_denied | 3 | 0.093998 | 0.091452 | 0.104051 | 0.048486 | 175364 |
| grep | zlg_grep_no_index | fixed-lines64k | none | branch_suffix | 3 | 0.088899 | 0.087026 | 0.102705 | 0.047296 | 111409 |
| grep | zlg_grep_no_index | fixed-lines64k | none | literal_failed_password | 3 | 0.093143 | 0.092928 | 0.103136 | 0.051446 | 63955 |
| grep | zlg_grep_no_index | fixed-lines64k | none | lookbehind_key | 3 | 0.500475 | 0.486620 | 0.505158 | 0.078943 | 124168 |
| grep | zlg_grep_no_index | fixed-lines64k | none | no_match_literal | 3 | 0.096250 | 0.092812 | 0.103963 |  | 0 |
| grep | zlg_grep_no_index | fixed-lines64k | none | quoted_key | 3 | 0.093491 | 0.088370 | 0.101529 | 0.052201 | 124168 |
| grep | zlg_grep_no_index | fixed-lines64k | none | src_ip | 3 | 0.144515 | 0.142096 | 0.166108 | 0.049890 | 9218316 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | alternation_error_failed_denied | 3 | 0.104121 | 0.101374 | 0.106046 | 0.054063 | 175364 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | branch_suffix | 3 | 0.099035 | 0.098071 | 0.102307 | 0.053129 | 111409 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | literal_failed_password | 3 | 0.097633 | 0.092035 | 0.098361 | 0.051852 | 63955 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | lookbehind_key | 3 | 0.485175 | 0.480846 | 0.507093 | 0.079584 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | no_match_literal | 3 | 0.099174 | 0.097660 | 0.100302 |  | 0 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | quoted_key | 3 | 0.096886 | 0.093414 | 0.106949 | 0.052960 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap16m | none | src_ip | 3 | 0.145760 | 0.142442 | 0.164400 | 0.051943 | 9218316 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | alternation_error_failed_denied | 3 | 0.094298 | 0.089437 | 0.101512 | 0.049715 | 175364 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | branch_suffix | 3 | 0.099676 | 0.096959 | 0.104818 | 0.053025 | 111409 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | literal_failed_password | 3 | 0.097293 | 0.092543 | 0.098544 | 0.051785 | 63955 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | lookbehind_key | 3 | 0.507924 | 0.500750 | 0.526389 | 0.085027 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | no_match_literal | 3 | 0.111969 | 0.100511 | 0.133081 |  | 0 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | quoted_key | 3 | 0.100335 | 0.092422 | 0.102844 | 0.055978 | 124168 |
| grep | zlg_grep_no_index | hybrid-fixed64k-cap8m | none | src_ip | 3 | 0.147404 | 0.147022 | 0.160207 | 0.052525 | 9218316 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | alternation_error_failed_denied | 3 | 0.129471 | 0.120024 | 0.131610 | 0.021088 | 175364 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | branch_suffix | 3 | 0.123997 | 0.121211 | 0.130626 | 0.020753 | 111409 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | literal_failed_password | 3 | 0.129352 | 0.124388 | 0.129943 | 0.029675 | 63955 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | lookbehind_key | 3 | 0.529657 | 0.522712 | 0.532098 | 0.046877 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | no_match_literal | 3 | 0.121333 | 0.118020 | 0.132924 |  | 0 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | quoted_key | 3 | 0.125030 | 0.117240 | 0.129612 | 0.020157 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap16m | none | src_ip | 3 | 0.172228 | 0.169878 | 0.181094 | 0.014264 | 9218316 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | alternation_error_failed_denied | 3 | 0.123372 | 0.113589 | 0.126577 | 0.019236 | 175364 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | branch_suffix | 3 | 0.113427 | 0.112844 | 0.121288 | 0.019283 | 111409 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | literal_failed_password | 3 | 0.114175 | 0.110456 | 0.121600 | 0.027039 | 63955 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | lookbehind_key | 3 | 0.525967 | 0.519190 | 0.533775 | 0.044861 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | no_match_literal | 3 | 0.132040 | 0.120947 | 0.142234 |  | 0 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | quoted_key | 3 | 0.124892 | 0.117487 | 0.126571 | 0.020675 | 124168 |
| grep | zlg_grep_no_index | hybrid-progressive-cap8m | none | src_ip | 3 | 0.171300 | 0.168759 | 0.174718 | 0.012544 | 9218316 |
| grep | zlg_grep_no_index | progressive-lines | none | alternation_error_failed_denied | 3 | 0.117299 | 0.114576 | 0.120645 | 0.018441 | 175364 |
| grep | zlg_grep_no_index | progressive-lines | none | branch_suffix | 3 | 0.118399 | 0.113446 | 0.118853 | 0.019266 | 111409 |
| grep | zlg_grep_no_index | progressive-lines | none | literal_failed_password | 3 | 0.113199 | 0.110005 | 0.119157 | 0.026198 | 63955 |
| grep | zlg_grep_no_index | progressive-lines | none | lookbehind_key | 3 | 0.524307 | 0.511970 | 0.544968 | 0.045441 | 124168 |
| grep | zlg_grep_no_index | progressive-lines | none | no_match_literal | 3 | 0.123212 | 0.119966 | 0.129194 |  | 0 |
| grep | zlg_grep_no_index | progressive-lines | none | quoted_key | 3 | 0.111558 | 0.111182 | 0.123686 | 0.018297 | 124168 |
| grep | zlg_grep_no_index | progressive-lines | none | src_ip | 3 | 0.165666 | 0.159288 | 0.170465 | 0.012780 | 9218316 |
| grep_baseline | grep_plain |  |  | alternation_error_failed_denied | 3 | 0.022177 | 0.021669 | 0.023932 | 0.005793 | 175364 |
| grep_baseline | grep_plain |  |  | branch_suffix | 3 | 0.015873 | 0.013097 | 0.018491 | 0.007571 | 34486 |
| grep_baseline | grep_plain |  |  | literal_failed_password | 3 | 0.013296 | 0.012701 | 0.013700 | 0.006363 | 63955 |
| grep_baseline | grep_plain |  |  | no_match_literal | 3 | 0.011508 | 0.010622 | 0.011984 |  | 0 |
| grep_baseline | grep_plain |  |  | quoted_key | 3 | 0.013294 | 0.012442 | 0.014323 | 0.007036 | 124168 |
| grep_baseline | grep_plain |  |  | src_ip | 3 | 0.076260 | 0.073285 | 0.078586 | 0.005989 | 9218316 |
| grep_baseline | rg_plain |  |  | alternation_error_failed_denied | 3 | 0.021439 | 0.021076 | 0.025960 | 0.010678 | 175364 |
| grep_baseline | rg_plain |  |  | branch_suffix | 3 | 0.022286 | 0.019416 | 0.025043 | 0.012531 | 111409 |
| grep_baseline | rg_plain |  |  | literal_failed_password | 3 | 0.022762 | 0.019329 | 0.022806 | 0.012890 | 63955 |
| grep_baseline | rg_plain |  |  | no_match_literal | 3 | 0.019855 | 0.018524 | 0.022586 |  | 0 |
| grep_baseline | rg_plain |  |  | quoted_key | 3 | 0.020368 | 0.019335 | 0.025796 | 0.012472 | 124168 |
| grep_baseline | rg_plain |  |  | src_ip | 3 | 0.098343 | 0.091824 | 0.100559 | 0.010824 | 9218316 |
| grep_baseline | zgrep_gzip6 |  |  | alternation_error_failed_denied | 3 | 0.080517 | 0.073720 | 0.081188 | 0.028780 | 175364 |
| grep_baseline | zgrep_gzip6 |  |  | branch_suffix | 3 | 0.076778 | 0.074989 | 0.090779 | 0.033325 | 34486 |
| grep_baseline | zgrep_gzip6 |  |  | literal_failed_password | 3 | 0.078937 | 0.074719 | 0.082348 | 0.033607 | 63955 |
| grep_baseline | zgrep_gzip6 |  |  | no_match_literal | 3 | 0.078472 | 0.077960 | 0.078967 |  | 0 |
| grep_baseline | zgrep_gzip6 |  |  | quoted_key | 3 | 0.084127 | 0.074819 | 0.088204 | 0.029361 | 124168 |
| grep_baseline | zgrep_gzip6 |  |  | src_ip | 3 | 0.120237 | 0.115847 | 0.120252 | 0.029290 | 9218316 |

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
