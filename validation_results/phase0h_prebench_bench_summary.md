# zlg Phase 0h/0i prebench benchmark summary

This is pre-bench evidence only, not the final performance proof.

## Corpus

- Lines: 125000
- Input bytes: 9218316
- Input sha256: 942cac75a8319eae9acbcbfe97bd52d5dc1b161175ee6f9c5908c71f2edc48c2

## Median timings

| kind | name | policy | pattern | repeats | median_s | min_s | max_s | output_bytes |
|---|---|---|---|---:|---:|---:|---:|---:|
| cat | zlg_cat | fixed-lines64k |  | 3 | 0.093153 | 0.090154 | 0.114361 | 9218316 |
| cat | zlg_cat | hybrid-fixed64k-cap16m |  | 3 | 0.093834 | 0.093708 | 0.106061 | 9218316 |
| cat | zlg_cat | hybrid-fixed64k-cap8m |  | 3 | 0.097531 | 0.096793 | 0.118874 | 9218316 |
| cat | zlg_cat | hybrid-progressive-cap16m |  | 3 | 0.118054 | 0.116695 | 0.123883 | 9218316 |
| cat | zlg_cat | hybrid-progressive-cap8m |  | 3 | 0.114517 | 0.110628 | 0.126047 | 9218316 |
| cat | zlg_cat | progressive-lines |  | 3 | 0.126480 | 0.116517 | 0.147580 | 9218316 |
| compress | gzip_6 |  |  | 3 | 0.147099 | 0.146949 | 0.149125 | 849250 |
| compress | gzip_9 |  |  | 3 | 0.714519 | 0.711648 | 0.721133 | 746531 |
| compress | zlg | fixed-lines64k |  | 3 | 0.178339 | 0.171691 | 0.181557 | 623250 |
| compress | zlg | hybrid-fixed64k-cap16m |  | 3 | 0.170593 | 0.170329 | 0.172790 | 623250 |
| compress | zlg | hybrid-fixed64k-cap8m |  | 3 | 0.186617 | 0.177127 | 0.187106 | 623250 |
| compress | zlg | hybrid-progressive-cap16m |  | 3 | 0.143787 | 0.139708 | 0.157239 | 672627 |
| compress | zlg | hybrid-progressive-cap8m |  | 3 | 0.142473 | 0.140055 | 0.149171 | 672627 |
| compress | zlg | progressive-lines |  | 3 | 0.149937 | 0.148119 | 0.172685 | 672627 |
| grep | zlg_grep | fixed-lines64k | alternation_error_failed_denied | 3 | 0.102819 | 0.097156 | 0.106333 | 175364 |
| grep | zlg_grep | fixed-lines64k | branch_suffix | 3 | 0.104703 | 0.094903 | 0.110850 | 111409 |
| grep | zlg_grep | fixed-lines64k | literal_failed_password | 3 | 0.098045 | 0.096816 | 0.100742 | 63955 |
| grep | zlg_grep | fixed-lines64k | lookbehind_key | 3 | 0.013688 | 0.012929 | 0.015776 | 0 |
| grep | zlg_grep | fixed-lines64k | no_match_literal | 3 | 0.015223 | 0.012039 | 0.015382 | 0 |
| grep | zlg_grep | fixed-lines64k | quoted_key | 3 | 0.099963 | 0.098159 | 0.104056 | 124168 |
| grep | zlg_grep | fixed-lines64k | src_ip | 3 | 0.116040 | 0.108324 | 0.176061 | 9218316 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | alternation_error_failed_denied | 3 | 0.103097 | 0.101951 | 0.111552 | 175364 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | branch_suffix | 3 | 0.106524 | 0.102941 | 0.111254 | 111409 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | literal_failed_password | 3 | 0.107042 | 0.100925 | 0.108040 | 63955 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | lookbehind_key | 3 | 0.014014 | 0.012379 | 0.014402 | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | no_match_literal | 3 | 0.011096 | 0.010189 | 0.012017 | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | quoted_key | 3 | 0.104853 | 0.098796 | 0.105299 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap16m | src_ip | 3 | 0.123515 | 0.120019 | 0.125783 | 9218316 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | alternation_error_failed_denied | 3 | 0.101870 | 0.100284 | 0.106336 | 175364 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | branch_suffix | 3 | 0.100345 | 0.096383 | 0.101066 | 111409 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | literal_failed_password | 3 | 0.098531 | 0.093302 | 0.105316 | 63955 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | lookbehind_key | 3 | 0.013327 | 0.012549 | 0.016666 | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | no_match_literal | 3 | 0.011487 | 0.011430 | 0.011605 | 0 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | quoted_key | 3 | 0.107447 | 0.101527 | 0.133402 | 124168 |
| grep | zlg_grep | hybrid-fixed64k-cap8m | src_ip | 3 | 0.114453 | 0.110718 | 0.144245 | 9218316 |
| grep | zlg_grep | hybrid-progressive-cap16m | alternation_error_failed_denied | 3 | 0.133100 | 0.127153 | 0.134100 | 175364 |
| grep | zlg_grep | hybrid-progressive-cap16m | branch_suffix | 3 | 0.129218 | 0.124822 | 0.138245 | 111409 |
| grep | zlg_grep | hybrid-progressive-cap16m | literal_failed_password | 3 | 0.129743 | 0.123537 | 0.144739 | 63955 |
| grep | zlg_grep | hybrid-progressive-cap16m | lookbehind_key | 3 | 0.013551 | 0.013369 | 0.017090 | 0 |
| grep | zlg_grep | hybrid-progressive-cap16m | no_match_literal | 3 | 0.014740 | 0.011898 | 0.014914 | 0 |
| grep | zlg_grep | hybrid-progressive-cap16m | quoted_key | 3 | 0.128693 | 0.127305 | 0.129038 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap16m | src_ip | 3 | 0.156519 | 0.143582 | 0.186262 | 9218316 |
| grep | zlg_grep | hybrid-progressive-cap8m | alternation_error_failed_denied | 3 | 0.126204 | 0.121119 | 0.127770 | 175364 |
| grep | zlg_grep | hybrid-progressive-cap8m | branch_suffix | 3 | 0.123987 | 0.123803 | 0.132977 | 111409 |
| grep | zlg_grep | hybrid-progressive-cap8m | literal_failed_password | 3 | 0.120470 | 0.114134 | 0.125849 | 63955 |
| grep | zlg_grep | hybrid-progressive-cap8m | lookbehind_key | 3 | 0.013857 | 0.013265 | 0.014691 | 0 |
| grep | zlg_grep | hybrid-progressive-cap8m | no_match_literal | 3 | 0.015245 | 0.011678 | 0.016763 | 0 |
| grep | zlg_grep | hybrid-progressive-cap8m | quoted_key | 3 | 0.128664 | 0.127580 | 0.134512 | 124168 |
| grep | zlg_grep | hybrid-progressive-cap8m | src_ip | 3 | 0.141722 | 0.134714 | 0.147864 | 9218316 |
| grep | zlg_grep | progressive-lines | alternation_error_failed_denied | 3 | 0.128323 | 0.122748 | 0.129600 | 175364 |
| grep | zlg_grep | progressive-lines | branch_suffix | 3 | 0.138842 | 0.124108 | 0.139784 | 111409 |
| grep | zlg_grep | progressive-lines | literal_failed_password | 3 | 0.121541 | 0.120358 | 0.129451 | 63955 |
| grep | zlg_grep | progressive-lines | lookbehind_key | 3 | 0.013444 | 0.013114 | 0.016618 | 0 |
| grep | zlg_grep | progressive-lines | no_match_literal | 3 | 0.012233 | 0.011213 | 0.012308 | 0 |
| grep | zlg_grep | progressive-lines | quoted_key | 3 | 0.126187 | 0.124221 | 0.136618 | 124168 |
| grep | zlg_grep | progressive-lines | src_ip | 3 | 0.138084 | 0.132210 | 0.168421 | 9218316 |
| grep_baseline | grep_plain |  | alternation_error_failed_denied | 3 | 0.028835 | 0.024666 | 0.033867 | 175364 |
| grep_baseline | grep_plain |  | branch_suffix | 3 | 0.017397 | 0.015892 | 0.020244 | 34486 |
| grep_baseline | grep_plain |  | literal_failed_password | 3 | 0.013706 | 0.013237 | 0.015973 | 63955 |
| grep_baseline | grep_plain |  | no_match_literal | 3 | 0.012356 | 0.011577 | 0.014696 | 0 |
| grep_baseline | grep_plain |  | quoted_key | 3 | 0.013805 | 0.013166 | 0.015319 | 124168 |
| grep_baseline | grep_plain |  | src_ip | 3 | 0.040380 | 0.037074 | 0.042331 | 9218316 |
| grep_baseline | rg_plain |  | alternation_error_failed_denied | 3 | 0.023539 | 0.023151 | 0.024086 | 175364 |
| grep_baseline | rg_plain |  | branch_suffix | 3 | 0.024890 | 0.023840 | 0.029465 | 111409 |
| grep_baseline | rg_plain |  | literal_failed_password | 3 | 0.025411 | 0.023556 | 0.026598 | 63955 |
| grep_baseline | rg_plain |  | no_match_literal | 3 | 0.023916 | 0.022033 | 0.024626 | 0 |
| grep_baseline | rg_plain |  | quoted_key | 3 | 0.024391 | 0.023544 | 0.026099 | 124168 |
| grep_baseline | rg_plain |  | src_ip | 3 | 0.069469 | 0.064983 | 0.074475 | 9218316 |
| grep_baseline | zgrep_gzip6 |  | alternation_error_failed_denied | 3 | 0.080885 | 0.080764 | 0.084672 | 175364 |
| grep_baseline | zgrep_gzip6 |  | branch_suffix | 3 | 0.080048 | 0.079562 | 0.084474 | 34486 |
| grep_baseline | zgrep_gzip6 |  | literal_failed_password | 3 | 0.088296 | 0.086010 | 0.091259 | 63955 |
| grep_baseline | zgrep_gzip6 |  | no_match_literal | 3 | 0.082317 | 0.075171 | 0.084165 | 0 |
| grep_baseline | zgrep_gzip6 |  | quoted_key | 3 | 0.085669 | 0.079044 | 0.087735 | 124168 |
| grep_baseline | zgrep_gzip6 |  | src_ip | 3 | 0.090109 | 0.085015 | 0.095239 | 9218316 |
