# Phase 1k final-stack memory and level diagnostic

Diagnostic-only pass for the final stack defaults, zstd level 8, gzip level 8, and memory accounting.

## Gzip rows

| corpus | gzip level | wall_s | cpu_s | rss_kb | output_bytes |
|---|---:|---:|---:|---:|---:|
| high_dup | 6 | 0.32405472599930363 | 0.317819 | 2132 | 2274038 |
| high_dup | 8 | 0.9338909440011776 | 0.929269 | 1972 | 2118695 |
| high_dup | 9 | 0.9798652870013029 | 0.974760 | 2044 | 2118695 |
| high_cardinality | 6 | 0.5648755439979141 | 0.561305 | 1960 | 3865575 |
| high_cardinality | 8 | 1.013280286002555 | 1.008245 | 1988 | 3857694 |
| high_cardinality | 9 | 1.0102076920011314 | 1.007315 | 2020 | 3857694 |
| unicode | 6 | 0.03285430899995845 | 0.031425 | 1920 | 155938 |
| unicode | 8 | 0.07132956900022691 | 0.068063 | 1820 | 102506 |
| unicode | 9 | 0.07711496699994314 | 0.071475 | 1804 | 102506 |
| binaryish | 6 | 0.01768105199880665 | 0.015804 | 1908 | 198261 |
| binaryish | 8 | 0.022414499002479715 | 0.018045 | 1928 | 198230 |
| binaryish | 9 | 0.0223015170013241 | 0.017660 | 1940 | 198230 |
| realistic_mixed_log | 6 | 0.5611735249985941 | 0.559965 | 1984 | 3363528 |
| realistic_mixed_log | 8 | 1.1274733200007176 | 1.124774 | 1984 | 3220603 |
| realistic_mixed_log | 9 | 1.1122388469993894 | 1.111002 | 2016 | 3220603 |
| long_line_log | 6 | 1.7974225409998326 | 1.791603 | 2080 | 4571481 |
| long_line_log | 8 | 5.683923081996909 | 5.679249 | 1904 | 4101596 |
| long_line_log | 9 | 9.074387200998899 | 9.069271 | 1936 | 4101208 |
| short_line_log | 6 | 0.3837288470022031 | 0.378768 | 2064 | 1866285 |
| short_line_log | 8 | 2.588148569000623 | 2.583172 | 2084 | 1832909 |
| short_line_log | 9 | 2.688630180000473 | 2.687038 | 2052 | 1832903 |

## ZLG mode summary

| corpus | mode | policy | level | profile | summary | wall_s | cpu_s | rss_kb | output_bytes | max_chunk_bytes | delta_gzip6 | delta_gzip8 | delta_gzip9 | roundtrip |
|---|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| high_dup | final-cap8m-l3 | fixed-lines8192-cap8m | 3 | combined-bitset-seen | mesh-bigram | 0.1962740919989301 | 0.193233 | 9180 | 2103529 | 1215685 | -170509 | -15166 | -15166 | true |
| high_dup | final-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | mesh-bigram | 0.334491445999447 | 0.328885 | 10952 | 1857474 | 1215685 | -416564 | -261221 | -261221 | true |
| high_dup | final-cap8m-l8 | fixed-lines8192-cap8m | 8 | combined-bitset-seen | mesh-bigram | 0.42231312500007334 | 0.421267 | 13576 | 1713897 | 1215685 | -560141 | -404798 | -404798 | true |
| high_dup | final-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | mesh-bigram | 0.5082273209991399 | 0.504352 | 18736 | 1711261 | 1215685 | -562777 | -407434 | -407434 | true |
| high_dup | no-summary-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | none | 0.25582951300020795 | 0.250687 | 9056 | 1765170 | 1215685 | -508868 | -353525 | -353525 | true |
| high_dup | no-summary-cap8m-l8 | fixed-lines8192-cap8m | 8 | combined-bitset-seen | none | 0.33239090200004284 | 0.327276 | 11384 | 1621593 | 1215685 | -652445 | -497102 | -497102 | true |
| high_dup | no-summary-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | none | 0.3856063620005443 | 0.384438 | 16644 | 1618957 | 1215685 | -655081 | -499738 | -499738 | true |
| high_dup | default-cli | default | 0 | default | default | 0.34020523599974695 | 0.338476 | 11024 | 1857474 | 1215685 | -416564 | -261221 | -261221 | true |
| high_cardinality | final-cap8m-l3 | fixed-lines8192-cap8m | 3 | combined-bitset-seen | mesh-bigram | 0.22740850500122178 | 0.223359 | 9424 | 3730311 | 1336598 | -135264 | -127383 | -127383 | true |
| high_cardinality | final-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | mesh-bigram | 0.38311271499696886 | 0.378924 | 11260 | 3731403 | 1336598 | -134172 | -126291 | -126291 | true |
| high_cardinality | final-cap8m-l8 | fixed-lines8192-cap8m | 8 | combined-bitset-seen | mesh-bigram | 0.4866109200011124 | 0.485387 | 13800 | 3636834 | 1336598 | -228741 | -220860 | -220860 | true |
| high_cardinality | final-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | mesh-bigram | 0.5328432230016915 | 0.527887 | 19104 | 3637043 | 1336598 | -228532 | -220651 | -220651 | true |
| high_cardinality | no-summary-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | none | 0.28616990400041686 | 0.280631 | 9212 | 3632505 | 1336598 | -233070 | -225189 | -225189 | true |
| high_cardinality | no-summary-cap8m-l8 | fixed-lines8192-cap8m | 8 | combined-bitset-seen | none | 0.3627934029973403 | 0.359476 | 11752 | 3537936 | 1336598 | -327639 | -319758 | -319758 | true |
| high_cardinality | no-summary-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | none | 0.4436492989989347 | 0.443163 | 17020 | 3538145 | 1336598 | -327430 | -319549 | -319549 | true |
| high_cardinality | default-cli | default | 0 | default | default | 0.4170178849999502 | 0.407278 | 11212 | 3731403 | 1336598 | -134172 | -126291 | -126291 | true |
| unicode | final-cap8m-l3 | fixed-lines8192-cap8m | 3 | combined-bitset-seen | mesh-bigram | 0.06985863400041126 | 0.065784 | 7924 | 99360 | 952862 | -56578 | -3146 | -3146 | true |
| unicode | final-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | mesh-bigram | 0.12277685699882568 | 0.119154 | 9816 | 81685 | 952862 | -74253 | -20821 | -20821 | true |
| unicode | final-cap8m-l8 | fixed-lines8192-cap8m | 8 | combined-bitset-seen | mesh-bigram | 0.11870374499994796 | 0.113701 | 12336 | 69285 | 952862 | -86653 | -33221 | -33221 | true |
| unicode | final-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | mesh-bigram | 0.14521374700052547 | 0.139760 | 17508 | 69285 | 952862 | -86653 | -33221 | -33221 | true |
| unicode | no-summary-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | none | 0.06146774399894639 | 0.060169 | 7844 | 74437 | 952862 | -81501 | -28069 | -28069 | true |
| unicode | no-summary-cap8m-l8 | fixed-lines8192-cap8m | 8 | combined-bitset-seen | none | 0.0800953739999386 | 0.076657 | 10424 | 62037 | 952862 | -93901 | -40469 | -40469 | true |
| unicode | no-summary-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | none | 0.12154824199751602 | 0.116539 | 15532 | 62037 | 952862 | -93901 | -40469 | -40469 | true |
| unicode | default-cli | default | 0 | default | default | 0.09236251200127299 | 0.091660 | 9796 | 81685 | 952862 | -74253 | -20821 | -20821 | true |
| binaryish | final-cap8m-l3 | fixed-lines8192-cap8m | 3 | combined-bitset-seen | mesh-bigram | 0.04335644800084992 | 0.038617 | 7468 | 477893 | 217070 | 279632 | 279663 | 279663 | true |
| binaryish | final-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | mesh-bigram | 0.05900702500002808 | 0.058375 | 10280 | 477802 | 217070 | 279541 | 279572 | 279572 | true |
| binaryish | final-cap8m-l8 | fixed-lines8192-cap8m | 8 | combined-bitset-seen | mesh-bigram | 0.048737391000031494 | 0.047437 | 10220 | 477686 | 217070 | 279425 | 279456 | 279456 | true |
| binaryish | final-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | mesh-bigram | 0.05323016499824007 | 0.049856 | 10420 | 477682 | 217070 | 279421 | 279452 | 279452 | true |
| binaryish | no-summary-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | none | 0.027838091999001335 | 0.024947 | 6936 | 197309 | 217070 | -952 | -921 | -921 | true |
| binaryish | no-summary-cap8m-l8 | fixed-lines8192-cap8m | 8 | combined-bitset-seen | none | 0.027487053001095774 | 0.024796 | 6984 | 197193 | 217070 | -1068 | -1037 | -1037 | true |
| binaryish | no-summary-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | none | 0.027497699000377906 | 0.025435 | 6980 | 197189 | 217070 | -1072 | -1041 | -1041 | true |
| binaryish | default-cli | default | 0 | default | default | 0.05358791799881146 | 0.051788 | 10324 | 477802 | 217070 | 279541 | 279572 | 279572 | true |
| realistic_mixed_log | final-cap8m-l3 | fixed-lines8192-cap8m | 3 | combined-bitset-seen | mesh-bigram | 0.28029152100134525 | 0.274894 | 8676 | 3757978 | 1371227 | 394450 | 537375 | 537375 | true |
| realistic_mixed_log | final-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | mesh-bigram | 0.4457490489985503 | 0.440243 | 10512 | 3240403 | 1371227 | -123125 | 19800 | 19800 | true |
| realistic_mixed_log | final-cap8m-l8 | fixed-lines8192-cap8m | 8 | combined-bitset-seen | mesh-bigram | 0.58733998200114 | 0.586374 | 13076 | 2942287 | 1371227 | -421241 | -278316 | -278316 | true |
| realistic_mixed_log | final-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | mesh-bigram | 0.6446790170011809 | 0.642313 | 18224 | 2940919 | 1371227 | -422609 | -279684 | -279684 | true |
| realistic_mixed_log | no-summary-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | none | 0.3356167810015904 | 0.332847 | 8500 | 3129723 | 1371227 | -233805 | -90880 | -90880 | true |
| realistic_mixed_log | no-summary-cap8m-l8 | fixed-lines8192-cap8m | 8 | combined-bitset-seen | none | 0.48494687600032194 | 0.482713 | 10844 | 2831607 | 1371227 | -531921 | -388996 | -388996 | true |
| realistic_mixed_log | no-summary-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | none | 0.5143184990010923 | 0.511770 | 15892 | 2830239 | 1371227 | -533289 | -390364 | -390364 | true |
| realistic_mixed_log | default-cli | default | 0 | default | default | 0.44637376299942844 | 0.441741 | 10508 | 3240403 | 1371227 | -123125 | 19800 | 19800 | true |
| long_line_log | final-cap8m-l3 | fixed-lines8192-cap8m | 3 | combined-bitset-seen | mesh-bigram | 0.49627085800239 | 0.493977 | 20872 | 2445380 | 8388464 | -2126101 | -1656216 | -1655828 | true |
| long_line_log | final-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | mesh-bigram | 0.5835394259993336 | 0.578869 | 22708 | 1834252 | 8388464 | -2737229 | -2267344 | -2266956 | true |
| long_line_log | final-cap8m-l8 | fixed-lines8192-cap8m | 8 | combined-bitset-seen | mesh-bigram | 0.7087311989998852 | 0.704577 | 25240 | 2024502 | 8388464 | -2546979 | -2077094 | -2076706 | true |
| long_line_log | final-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | mesh-bigram | 0.8181473069998901 | 0.813167 | 30436 | 2111101 | 8388464 | -2460380 | -1990495 | -1990107 | true |
| long_line_log | no-summary-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | none | 0.35009111700128415 | 0.346396 | 20540 | 1795139 | 8388464 | -2776342 | -2306457 | -2306069 | true |
| long_line_log | no-summary-cap8m-l8 | fixed-lines8192-cap8m | 8 | combined-bitset-seen | none | 0.4884843740001088 | 0.487355 | 23108 | 1985389 | 8388464 | -2586092 | -2116207 | -2115819 | true |
| long_line_log | no-summary-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | none | 0.5461636929976521 | 0.541179 | 28332 | 2071988 | 8388464 | -2499493 | -2029608 | -2029220 | true |
| long_line_log | default-cli | default | 0 | default | default | 0.5341427860003023 | 0.532064 | 22704 | 1834252 | 8388464 | -2737229 | -2267344 | -2266956 | true |
| long_line_log | uncapped-reference-l6 | fixed-lines8192 | 6 | combined-bitset-seen | mesh-bigram | 0.6252048939968518 | 0.621359 | 32832 | 1814579 | 23692823 | -2756902 | -2287017 | -2286629 | true |
| long_line_log | uncapped-reference-l8 | fixed-lines8192 | 8 | combined-bitset-seen | mesh-bigram | 0.7630342310003471 | 0.757887 | 35396 | 1998526 | 23692823 | -2572955 | -2103070 | -2102682 | true |
| long_line_log | uncapped-reference-l9 | fixed-lines8192 | 9 | combined-bitset-seen | mesh-bigram | 0.8516533649999474 | 0.847548 | 40724 | 2118360 | 23692823 | -2453121 | -1983236 | -1982848 | true |
| short_line_log | final-cap8m-l3 | fixed-lines8192-cap8m | 3 | combined-bitset-seen | mesh-bigram | 0.18490508000104455 | 0.181380 | 7320 | 2156049 | 386574 | 289764 | 323140 | 323146 | true |
| short_line_log | final-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | mesh-bigram | 0.3002840820008714 | 0.298327 | 9136 | 1959223 | 386574 | 92938 | 126314 | 126320 | true |
| short_line_log | final-cap8m-l8 | fixed-lines8192-cap8m | 8 | combined-bitset-seen | mesh-bigram | 0.43088168900067103 | 0.427111 | 11680 | 1905913 | 386574 | 39628 | 73004 | 73010 | true |
| short_line_log | final-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | mesh-bigram | 0.3899045219986874 | 0.384648 | 11880 | 1906010 | 386574 | 39725 | 73101 | 73107 | true |
| short_line_log | no-summary-cap8m-l6 | fixed-lines8192-cap8m | 6 | combined-bitset-seen | none | 0.23750984499929473 | 0.234799 | 7184 | 1897219 | 386574 | 30934 | 64310 | 64316 | true |
| short_line_log | no-summary-cap8m-l8 | fixed-lines8192-cap8m | 8 | combined-bitset-seen | none | 0.35764465300235315 | 0.356918 | 9652 | 1843909 | 386574 | -22376 | 11000 | 11006 | true |
| short_line_log | no-summary-cap8m-l9 | fixed-lines8192-cap8m | 9 | combined-bitset-seen | none | 0.3644834789993183 | 0.359660 | 9644 | 1844006 | 386574 | -22279 | 11097 | 11103 | true |
| short_line_log | default-cli | default | 0 | default | default | 0.3713832969988289 | 0.370023 | 9140 | 1959223 | 386574 | 92938 | 126314 | 126320 | true |

## Best size per corpus among locked/capped zlg rows

| corpus | best_mode | level | policy | output_bytes | gzip6 | gzip8 | gzip9 |
|---|---|---:|---|---:|---:|---:|---:|
| binaryish | final-cap8m-l9 | 9 | fixed-lines8192-cap8m | 477682 | 198261 | 198230 | 198230 |
| high_cardinality | final-cap8m-l8 | 8 | fixed-lines8192-cap8m | 3636834 | 3865575 | 3857694 | 3857694 |
| high_dup | final-cap8m-l9 | 9 | fixed-lines8192-cap8m | 1711261 | 2274038 | 2118695 | 2118695 |
| long_line_log | final-cap8m-l6 | 6 | fixed-lines8192-cap8m | 1834252 | 4571481 | 4101596 | 4101208 |
| realistic_mixed_log | final-cap8m-l9 | 9 | fixed-lines8192-cap8m | 2940919 | 3363528 | 3220603 | 3220603 |
| short_line_log | final-cap8m-l8 | 8 | fixed-lines8192-cap8m | 1905913 | 1866285 | 1832909 | 1832903 |
| unicode | final-cap8m-l8 | 8 | fixed-lines8192-cap8m | 69285 | 155938 | 102506 | 102506 |
