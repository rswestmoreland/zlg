# Phase 1j memory and chunk-buffer diagnostic

Diagnostic-only pass for chunk buffering, zstd level, and gzip level comparison.

## Gzip rows

| corpus | gzip level | wall_s | cpu_s | rss_kb | output_bytes |
|---|---:|---:|---:|---:|---:|
| high_dup | 6 | 0.6867720699992788 | 0.665936 | 2048 | 2274038 |
| high_dup | 9 | 1.7675957760002348 | 1.761943 | 1972 | 2118695 |
| high_cardinality | 6 | 1.0797559639977408 | 1.077030 | 2068 | 3865575 |
| high_cardinality | 9 | 1.2893274640009622 | 1.285420 | 1964 | 3857694 |
| unicode | 6 | 0.07008191300337785 | 0.066156 | 1940 | 155938 |
| unicode | 9 | 0.17795643199860933 | 0.174733 | 1772 | 102506 |
| binaryish | 6 | 0.03439279600206646 | 0.031385 | 1900 | 198261 |
| binaryish | 9 | 0.040766350997728296 | 0.037744 | 1944 | 198230 |
| realistic_mixed_log | 6 | 1.0413299459978589 | 1.024984 | 1960 | 3363528 |
| realistic_mixed_log | 9 | 2.095879705000698 | 2.086979 | 1968 | 3220603 |
| long_line_log | 6 | 3.8851789139989705 | 3.883509 | 2100 | 4571481 |
| long_line_log | 9 | 17.821541573001014 | 17.816257 | 2068 | 4101208 |
| short_line_log | 6 | 0.8036699180011055 | 0.798257 | 2068 | 1866285 |
| short_line_log | 9 | 5.460589801001333 | 5.458984 | 2012 | 1832903 |

## ZLG mode summary

| corpus | mode | policy | level | profile | summary | wall_s | cpu_s | rss_kb | output_bytes | max_chunk_bytes | delta_gzip6 | delta_gzip9 | roundtrip |
|---|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| high_dup | locked-l3 | fixed-lines8192 | 3 | combined-bitset-seen | mesh-bigram | 0.41840469999806373 | 0.414122 | 9040 | 2103529 | 1215685 | -170509 | -15166 | true |
| high_dup | locked-l6 | fixed-lines8192 | 6 | combined-bitset-seen | mesh-bigram | 0.7546835149987601 | 0.751281 | 10944 | 1857474 | 1215685 | -416564 | -261221 | true |
| high_dup | locked-l9 | fixed-lines8192 | 9 | combined-bitset-seen | mesh-bigram | 1.0830580410001858 | 1.080258 | 18568 | 1711261 | 1215685 | -562777 | -407434 | true |
| high_dup | stream-zstd-l6 | fixed-lines8192 | 6 | combined-bitset-seen-stream-zstd | mesh-bigram | 0.6260136599994439 | 0.622816 | 12840 | 1857426 | 1215685 | -416612 | -261269 | true |
| high_dup | no-summary-l6 | fixed-lines8192 | 6 | combined-bitset-seen | none | 0.5755610779997369 | 0.570117 | 8840 | 1765170 | 1215685 | -508868 | -353525 | true |
| high_dup | stream-zstd-l9 | fixed-lines8192 | 9 | combined-bitset-seen-stream-zstd | mesh-bigram | 1.1591114130023925 | 1.155281 | 21976 | 1711188 | 1215685 | -562850 | -407507 | true |
| high_dup | no-summary-l9 | fixed-lines8192 | 9 | combined-bitset-seen | none | 0.8499442350002937 | 0.843497 | 16512 | 1618957 | 1215685 | -655081 | -499738 | true |
| high_dup | capped-fixed-lines8192-cap4m-l6 | fixed-lines8192-cap4m | 6 | combined-bitset-seen | mesh-bigram | 0.8432021540029382 | 0.836819 | 11000 | 1857474 | 1215685 | -416564 | -261221 | true |
| high_dup | capped-fixed-lines8192-cap4m-l9 | fixed-lines8192-cap4m | 9 | combined-bitset-seen | mesh-bigram | 0.7502734370027611 | 0.747045 | 18596 | 1711261 | 1215685 | -562777 | -407434 | true |
| high_dup | capped-fixed-lines8192-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | mesh-bigram | 0.5697674869988987 | 0.564130 | 10964 | 1857474 | 1215685 | -416564 | -261221 | true |
| high_dup | capped-fixed-lines8192-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | mesh-bigram | 1.0867594549999922 | 1.083737 | 18592 | 1711261 | 1215685 | -562777 | -407434 | true |
| high_dup | capped-fixed-lines8192-cap16m-l6 | fixed-lines8192-cap16m | 6 | combined-bitset-seen | mesh-bigram | 0.4936186999984784 | 0.490676 | 11136 | 1857474 | 1215685 | -416564 | -261221 | true |
| high_dup | capped-fixed-lines8192-cap16m-l9 | fixed-lines8192-cap16m | 9 | combined-bitset-seen | mesh-bigram | 1.1201727580009901 | 1.115147 | 18500 | 1711261 | 1215685 | -562777 | -407434 | true |
| high_cardinality | locked-l3 | fixed-lines8192 | 3 | combined-bitset-seen | mesh-bigram | 0.4521280230001139 | 0.444372 | 9396 | 3730311 | 1336598 | -135264 | -127383 | true |
| high_cardinality | locked-l6 | fixed-lines8192 | 6 | combined-bitset-seen | mesh-bigram | 0.8395951050006261 | 0.833978 | 11276 | 3731403 | 1336598 | -134172 | -126291 | true |
| high_cardinality | locked-l9 | fixed-lines8192 | 9 | combined-bitset-seen | mesh-bigram | 1.2454926969985536 | 1.241649 | 18728 | 3637043 | 1336598 | -228532 | -220651 | true |
| high_cardinality | stream-zstd-l6 | fixed-lines8192 | 6 | combined-bitset-seen-stream-zstd | mesh-bigram | 0.6317658100015251 | 0.629061 | 13864 | 3731355 | 1336598 | -134220 | -126339 | true |
| high_cardinality | no-summary-l6 | fixed-lines8192 | 6 | combined-bitset-seen | none | 0.6487359940001625 | 0.643403 | 9120 | 3632505 | 1336598 | -233070 | -225189 | true |
| high_cardinality | stream-zstd-l9 | fixed-lines8192 | 9 | combined-bitset-seen-stream-zstd | mesh-bigram | 1.4494454269988637 | 1.446063 | 22628 | 3636991 | 1336598 | -228584 | -220703 | true |
| high_cardinality | no-summary-l9 | fixed-lines8192 | 9 | combined-bitset-seen | none | 1.0784884620006778 | 1.076738 | 16696 | 3538145 | 1336598 | -327430 | -319549 | true |
| high_cardinality | capped-fixed-lines8192-cap4m-l6 | fixed-lines8192-cap4m | 6 | combined-bitset-seen | mesh-bigram | 0.8628429900018091 | 0.857226 | 11216 | 3731403 | 1336598 | -134172 | -126291 | true |
| high_cardinality | capped-fixed-lines8192-cap4m-l9 | fixed-lines8192-cap4m | 9 | combined-bitset-seen | mesh-bigram | 1.380827897999552 | 1.368333 | 18784 | 3637043 | 1336598 | -228532 | -220651 | true |
| high_cardinality | capped-fixed-lines8192-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | mesh-bigram | 0.8318993869979749 | 0.826186 | 11116 | 3731403 | 1336598 | -134172 | -126291 | true |
| high_cardinality | capped-fixed-lines8192-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | mesh-bigram | 1.1261727450000762 | 1.125042 | 18972 | 3637043 | 1336598 | -228532 | -220651 | true |
| high_cardinality | capped-fixed-lines8192-cap16m-l6 | fixed-lines8192-cap16m | 6 | combined-bitset-seen | mesh-bigram | 0.46870339599990984 | 0.465831 | 11356 | 3731403 | 1336598 | -134172 | -126291 | true |
| high_cardinality | capped-fixed-lines8192-cap16m-l9 | fixed-lines8192-cap16m | 9 | combined-bitset-seen | mesh-bigram | 1.0030849279974063 | 1.000818 | 18956 | 3637043 | 1336598 | -228532 | -220651 | true |
| unicode | locked-l3 | fixed-lines8192 | 3 | combined-bitset-seen | mesh-bigram | 0.06750698500036378 | 0.065873 | 7920 | 99360 | 952862 | -56578 | -3146 | true |
| unicode | locked-l6 | fixed-lines8192 | 6 | combined-bitset-seen | mesh-bigram | 0.177063138999074 | 0.173058 | 9860 | 81685 | 952862 | -74253 | -20821 | true |
| unicode | locked-l9 | fixed-lines8192 | 9 | combined-bitset-seen | mesh-bigram | 0.17149842100116075 | 0.170189 | 17540 | 69285 | 952862 | -86653 | -33221 | true |
| unicode | stream-zstd-l6 | fixed-lines8192 | 6 | combined-bitset-seen-stream-zstd | mesh-bigram | 0.20796398000311456 | 0.206318 | 10364 | 81673 | 952862 | -74265 | -20833 | true |
| unicode | no-summary-l6 | fixed-lines8192 | 6 | combined-bitset-seen | none | 0.06980062799993902 | 0.067830 | 7676 | 74437 | 952862 | -81501 | -28069 | true |
| unicode | stream-zstd-l9 | fixed-lines8192 | 9 | combined-bitset-seen-stream-zstd | mesh-bigram | 0.3218491269981314 | 0.317056 | 18220 | 69273 | 952862 | -86665 | -33233 | true |
| unicode | no-summary-l9 | fixed-lines8192 | 9 | combined-bitset-seen | none | 0.20537478100231965 | 0.202289 | 15212 | 62037 | 952862 | -93901 | -40469 | true |
| unicode | capped-fixed-lines8192-cap4m-l6 | fixed-lines8192-cap4m | 6 | combined-bitset-seen | mesh-bigram | 0.17957737300093868 | 0.177733 | 9884 | 81685 | 952862 | -74253 | -20821 | true |
| unicode | capped-fixed-lines8192-cap4m-l9 | fixed-lines8192-cap4m | 9 | combined-bitset-seen | mesh-bigram | 0.2697589059971506 | 0.266791 | 17488 | 69285 | 952862 | -86653 | -33221 | true |
| unicode | capped-fixed-lines8192-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | mesh-bigram | 0.21662131499761017 | 0.212529 | 9832 | 81685 | 952862 | -74253 | -20821 | true |
| unicode | capped-fixed-lines8192-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | mesh-bigram | 0.23883170699991751 | 0.237029 | 17384 | 69285 | 952862 | -86653 | -33221 | true |
| unicode | capped-fixed-lines8192-cap16m-l6 | fixed-lines8192-cap16m | 6 | combined-bitset-seen | mesh-bigram | 0.16932768799961195 | 0.164796 | 9832 | 81685 | 952862 | -74253 | -20821 | true |
| unicode | capped-fixed-lines8192-cap16m-l9 | fixed-lines8192-cap16m | 9 | combined-bitset-seen | mesh-bigram | 0.2646877670013055 | 0.260332 | 17556 | 69285 | 952862 | -86653 | -33221 | true |
| binaryish | locked-l3 | fixed-lines8192 | 3 | combined-bitset-seen | mesh-bigram | 0.07883874599792762 | 0.075226 | 8020 | 477893 | 217070 | 279632 | 279663 | true |
| binaryish | locked-l6 | fixed-lines8192 | 6 | combined-bitset-seen | mesh-bigram | 0.10140442800184246 | 0.096886 | 10240 | 477802 | 217070 | 279541 | 279572 | true |
| binaryish | locked-l9 | fixed-lines8192 | 9 | combined-bitset-seen | mesh-bigram | 0.06071147599868709 | 0.055636 | 9872 | 477682 | 217070 | 279421 | 279452 | true |
| binaryish | stream-zstd-l6 | fixed-lines8192 | 6 | combined-bitset-seen-stream-zstd | mesh-bigram | 0.10663843200018164 | 0.103132 | 10540 | 477799 | 217070 | 279538 | 279569 | true |
| binaryish | no-summary-l6 | fixed-lines8192 | 6 | combined-bitset-seen | none | 0.033248402000026545 | 0.029591 | 6928 | 197309 | 217070 | -952 | -921 | true |
| binaryish | stream-zstd-l9 | fixed-lines8192 | 9 | combined-bitset-seen-stream-zstd | mesh-bigram | 0.10604719999901135 | 0.100703 | 18092 | 477789 | 217070 | 279528 | 279559 | true |
| binaryish | no-summary-l9 | fixed-lines8192 | 9 | combined-bitset-seen | none | 0.032480519999808166 | 0.031340 | 6808 | 197189 | 217070 | -1072 | -1041 | true |
| binaryish | capped-fixed-lines8192-cap4m-l6 | fixed-lines8192-cap4m | 6 | combined-bitset-seen | mesh-bigram | 0.0632553059986094 | 0.057684 | 9920 | 477802 | 217070 | 279541 | 279572 | true |
| binaryish | capped-fixed-lines8192-cap4m-l9 | fixed-lines8192-cap4m | 9 | combined-bitset-seen | mesh-bigram | 0.0711806439976499 | 0.060765 | 10240 | 477682 | 217070 | 279421 | 279452 | true |
| binaryish | capped-fixed-lines8192-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | mesh-bigram | 0.06176228099866421 | 0.055643 | 10060 | 477802 | 217070 | 279541 | 279572 | true |
| binaryish | capped-fixed-lines8192-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | mesh-bigram | 0.10393468700203812 | 0.101581 | 10096 | 477682 | 217070 | 279421 | 279452 | true |
| binaryish | capped-fixed-lines8192-cap16m-l6 | fixed-lines8192-cap16m | 6 | combined-bitset-seen | mesh-bigram | 0.09422723800162203 | 0.090588 | 10204 | 477802 | 217070 | 279541 | 279572 | true |
| binaryish | capped-fixed-lines8192-cap16m-l9 | fixed-lines8192-cap16m | 9 | combined-bitset-seen | mesh-bigram | 0.09525089599992498 | 0.090514 | 10364 | 477682 | 217070 | 279421 | 279452 | true |
| realistic_mixed_log | locked-l3 | fixed-lines8192 | 3 | combined-bitset-seen | mesh-bigram | 0.5782674819965905 | 0.573129 | 8592 | 3757978 | 1371227 | 394450 | 537375 | true |
| realistic_mixed_log | locked-l6 | fixed-lines8192 | 6 | combined-bitset-seen | mesh-bigram | 1.0358077059972857 | 1.030972 | 10552 | 3240403 | 1371227 | -123125 | 19800 | true |
| realistic_mixed_log | locked-l9 | fixed-lines8192 | 9 | combined-bitset-seen | mesh-bigram | 1.4410379099972488 | 1.436398 | 18076 | 2940919 | 1371227 | -422609 | -279684 | true |
| realistic_mixed_log | stream-zstd-l6 | fixed-lines8192 | 6 | combined-bitset-seen-stream-zstd | mesh-bigram | 0.7066617250020499 | 0.701092 | 14028 | 3240355 | 1371227 | -123173 | 19752 | true |
| realistic_mixed_log | no-summary-l6 | fixed-lines8192 | 6 | combined-bitset-seen | none | 0.7292280019973987 | 0.709403 | 8320 | 3129723 | 1371227 | -233805 | -90880 | true |
| realistic_mixed_log | stream-zstd-l9 | fixed-lines8192 | 9 | combined-bitset-seen-stream-zstd | mesh-bigram | 1.6288079350015323 | 1.625103 | 22492 | 2940868 | 1371227 | -422660 | -279735 | true |
| realistic_mixed_log | no-summary-l9 | fixed-lines8192 | 9 | combined-bitset-seen | none | 1.2266171519986528 | 1.218740 | 16016 | 2830239 | 1371227 | -533289 | -390364 | true |
| realistic_mixed_log | capped-fixed-lines8192-cap4m-l6 | fixed-lines8192-cap4m | 6 | combined-bitset-seen | mesh-bigram | 1.102146682998864 | 1.099171 | 10696 | 3240403 | 1371227 | -123125 | 19800 | true |
| realistic_mixed_log | capped-fixed-lines8192-cap4m-l9 | fixed-lines8192-cap4m | 9 | combined-bitset-seen | mesh-bigram | 1.5508443340004305 | 1.546881 | 18252 | 2940919 | 1371227 | -422609 | -279684 | true |
| realistic_mixed_log | capped-fixed-lines8192-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | mesh-bigram | 0.9181303799996385 | 0.914484 | 10608 | 3240403 | 1371227 | -123125 | 19800 | true |
| realistic_mixed_log | capped-fixed-lines8192-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | mesh-bigram | 1.4122696689992154 | 1.409479 | 18308 | 2940919 | 1371227 | -422609 | -279684 | true |
| realistic_mixed_log | capped-fixed-lines8192-cap16m-l6 | fixed-lines8192-cap16m | 6 | combined-bitset-seen | mesh-bigram | 0.9198672659986187 | 0.915752 | 10712 | 3240403 | 1371227 | -123125 | 19800 | true |
| realistic_mixed_log | capped-fixed-lines8192-cap16m-l9 | fixed-lines8192-cap16m | 9 | combined-bitset-seen | mesh-bigram | 1.2897837689997687 | 1.287685 | 18176 | 2940919 | 1371227 | -422609 | -279684 | true |
| long_line_log | locked-l3 | fixed-lines8192 | 3 | combined-bitset-seen | mesh-bigram | 1.136488880001707 | 1.130427 | 31188 | 2451216 | 23692823 | -2120265 | -1649992 | true |
| long_line_log | locked-l6 | fixed-lines8192 | 6 | combined-bitset-seen | mesh-bigram | 1.3166780239989748 | 1.311924 | 32720 | 1814579 | 23692823 | -2756902 | -2286629 | true |
| long_line_log | locked-l9 | fixed-lines8192 | 9 | combined-bitset-seen | mesh-bigram | 1.809557983000559 | 1.805893 | 40808 | 2118360 | 23692823 | -2453121 | -1982848 | true |
| long_line_log | stream-zstd-l6 | fixed-lines8192 | 6 | combined-bitset-seen-stream-zstd | mesh-bigram | 1.372498317999998 | 1.368118 | 35024 | 1814625 | 23692823 | -2756856 | -2286583 | true |
| long_line_log | no-summary-l6 | fixed-lines8192 | 6 | combined-bitset-seen | none | 0.621124619996408 | 0.620223 | 30744 | 1801534 | 23692823 | -2769947 | -2299674 | true |
| long_line_log | stream-zstd-l9 | fixed-lines8192 | 9 | combined-bitset-seen-stream-zstd | mesh-bigram | 2.0405508240000927 | 2.039020 | 45056 | 2118409 | 23692823 | -2453072 | -1982799 | true |
| long_line_log | no-summary-l9 | fixed-lines8192 | 9 | combined-bitset-seen | none | 1.4846037520001119 | 1.482928 | 38564 | 2105315 | 23692823 | -2466166 | -1995893 | true |
| long_line_log | capped-fixed-lines8192-cap4m-l6 | fixed-lines8192-cap4m | 6 | combined-bitset-seen | mesh-bigram | 0.7870792619978602 | 0.784921 | 15656 | 1859742 | 4193966 | -2711739 | -2241466 | true |
| long_line_log | capped-fixed-lines8192-cap4m-l9 | fixed-lines8192-cap4m | 9 | combined-bitset-seen | mesh-bigram | 1.6745177880002302 | 1.671877 | 23336 | 2091127 | 4193966 | -2480354 | -2010081 | true |
| long_line_log | capped-fixed-lines8192-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | mesh-bigram | 0.6809520240021811 | 0.677961 | 22652 | 1834252 | 8388464 | -2737229 | -2266956 | true |
| long_line_log | capped-fixed-lines8192-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | mesh-bigram | 1.7045828500013158 | 1.695526 | 30196 | 2111101 | 8388464 | -2460380 | -1990107 | true |
| long_line_log | capped-fixed-lines8192-cap16m-l6 | fixed-lines8192-cap16m | 6 | combined-bitset-seen | mesh-bigram | 1.202026343002217 | 1.200355 | 36628 | 1820192 | 16776761 | -2751289 | -2281016 | true |
| long_line_log | capped-fixed-lines8192-cap16m-l9 | fixed-lines8192-cap16m | 9 | combined-bitset-seen | mesh-bigram | 1.8946582499993383 | 1.893421 | 44320 | 2119181 | 16776761 | -2452300 | -1982027 | true |
| short_line_log | locked-l3 | fixed-lines8192 | 3 | combined-bitset-seen | mesh-bigram | 0.2896518239977013 | 0.287816 | 7732 | 2156049 | 386574 | 289764 | 323146 | true |
| short_line_log | locked-l6 | fixed-lines8192 | 6 | combined-bitset-seen | mesh-bigram | 0.5779702360014198 | 0.572580 | 9800 | 1959223 | 386574 | 92938 | 126320 | true |
| short_line_log | locked-l9 | fixed-lines8192 | 9 | combined-bitset-seen | mesh-bigram | 0.7904070599979605 | 0.785753 | 12208 | 1906010 | 386574 | 39725 | 73107 | true |
| short_line_log | stream-zstd-l6 | fixed-lines8192 | 6 | combined-bitset-seen-stream-zstd | mesh-bigram | 0.38377564500115113 | 0.379314 | 10216 | 1959130 | 386574 | 92845 | 126227 | true |
| short_line_log | no-summary-l6 | fixed-lines8192 | 6 | combined-bitset-seen | none | 0.4343430660010199 | 0.431162 | 7124 | 1897219 | 386574 | 30934 | 64316 | true |
| short_line_log | stream-zstd-l9 | fixed-lines8192 | 9 | combined-bitset-seen-stream-zstd | mesh-bigram | 1.0000854009995237 | 0.993355 | 17708 | 1905733 | 386574 | 39448 | 72830 | true |
| short_line_log | no-summary-l9 | fixed-lines8192 | 9 | combined-bitset-seen | none | 0.6692404189998342 | 0.662887 | 9740 | 1844006 | 386574 | -22279 | 11103 | true |
| short_line_log | capped-fixed-lines8192-cap4m-l6 | fixed-lines8192-cap4m | 6 | combined-bitset-seen | mesh-bigram | 0.5842640709997795 | 0.578390 | 9608 | 1959223 | 386574 | 92938 | 126320 | true |
| short_line_log | capped-fixed-lines8192-cap4m-l9 | fixed-lines8192-cap4m | 9 | combined-bitset-seen | mesh-bigram | 0.8205808299971977 | 0.816344 | 12080 | 1906010 | 386574 | 39725 | 73107 | true |
| short_line_log | capped-fixed-lines8192-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | mesh-bigram | 0.5804829689986946 | 0.575893 | 9732 | 1959223 | 386574 | 92938 | 126320 | true |
| short_line_log | capped-fixed-lines8192-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | mesh-bigram | 0.8397403580020182 | 0.833737 | 12188 | 1906010 | 386574 | 39725 | 73107 | true |
| short_line_log | capped-fixed-lines8192-cap16m-l6 | fixed-lines8192-cap16m | 6 | combined-bitset-seen | mesh-bigram | 0.572386699001072 | 0.569659 | 9612 | 1959223 | 386574 | 92938 | 126320 | true |
| short_line_log | capped-fixed-lines8192-cap16m-l9 | fixed-lines8192-cap16m | 9 | combined-bitset-seen | mesh-bigram | 0.8044171929977892 | 0.799128 | 12236 | 1906010 | 386574 | 39725 | 73107 | true |

## Best size per corpus among locked/capped zlg rows

| corpus | best_mode | level | policy | output_bytes | gzip6 | gzip9 |
|---|---|---:|---|---:|---:|---:|
| binaryish | locked-l9 | 9 | fixed-lines8192 | 477682 | 198261 | 198230 |
| high_cardinality | stream-zstd-l9 | 9 | fixed-lines8192 | 3636991 | 3865575 | 3857694 |
| high_dup | stream-zstd-l9 | 9 | fixed-lines8192 | 1711188 | 2274038 | 2118695 |
| long_line_log | locked-l6 | 6 | fixed-lines8192 | 1814579 | 4571481 | 4101208 |
| realistic_mixed_log | stream-zstd-l9 | 9 | fixed-lines8192 | 2940868 | 3363528 | 3220603 |
| short_line_log | stream-zstd-l9 | 9 | fixed-lines8192 | 1905733 | 1866285 | 1832903 |
| unicode | stream-zstd-l9 | 9 | fixed-lines8192 | 69273 | 155938 | 102506 |
