# Phase 0k Search Bottleneck Analysis

## Compression highlights
- Input size: 8.79 MiB
- Output size: 0.59 MiB
- Compression ratio (output/input): 0.068
- Compression time: 0.1617s
- Compression throughput: 54.35 MiB/s

## Grep/search timing highlights
- Grep runs: 126
- Mean grep seconds: 0.0874s
- Min grep seconds: 0.0090s
- Max grep seconds: 0.1954s
- Mean first_output_seconds: 0.0352s
- Min first_output_seconds: 0.0119s
- Max first_output_seconds: 0.0612s

## Per-pattern chunk counters
| pattern | policy | wall_seconds | first_output_seconds | chunks_total | chunks_skipped | candidate_chunks | chunks_decoded | decoded_bytes | matching_lines | skip_ratio | decode_ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| no_match_literal | fixed-lines64k | 0.0090 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | hybrid-progressive-cap16m | 0.0096 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | hybrid-fixed64k-cap8m | 0.0098 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | hybrid-fixed64k-cap8m | 0.0099 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | progressive-lines | 0.0099 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | hybrid-progressive-cap8m | 0.0101 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | hybrid-progressive-cap8m | 0.0102 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | progressive-lines | 0.0103 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | progressive-lines | 0.0103 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | hybrid-progressive-cap16m | 0.0104 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | fixed-lines64k | 0.0104 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | hybrid-fixed64k-cap16m | 0.0107 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | hybrid-progressive-cap16m | 0.0108 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | fixed-lines64k | 0.0108 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | progressive-lines | 0.0111 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | hybrid-fixed64k-cap16m | 0.0111 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | fixed-lines64k | 0.0112 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | hybrid-fixed64k-cap8m | 0.0113 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | hybrid-progressive-cap16m | 0.0114 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | hybrid-fixed64k-cap8m | 0.0118 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | hybrid-fixed64k-cap16m | 0.0118 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | hybrid-progressive-cap8m | 0.0119 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | fixed-lines64k | 0.0119 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | progressive-lines | 0.0119 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | hybrid-fixed64k-cap16m | 0.0120 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | progressive-lines | 0.0121 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | fixed-lines64k | 0.0122 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | hybrid-progressive-cap16m | 0.0122 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | hybrid-progressive-cap16m | 0.0122 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | hybrid-fixed64k-cap8m | 0.0124 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | hybrid-progressive-cap8m | 0.0125 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | hybrid-fixed64k-cap16m | 0.0125 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | hybrid-fixed64k-cap16m | 0.0126 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| no_match_literal | hybrid-progressive-cap8m | 0.0128 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | hybrid-progressive-cap8m | 0.0137 | n/a | 5 | 5 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| lookbehind_key | hybrid-fixed64k-cap8m | 0.0137 | n/a | 2 | 2 | 0 | 0 | 0 | 0 | 1.000 | 0.000 |
| literal_failed_password | fixed-lines64k | 0.0887 | 0.0476 | 2 | 0 | 2 | 2 | 9218316 | 945 | 0.000 | 1.000 |
| alternation_error_failed_denied | hybrid-fixed64k-cap16m | 0.0892 | 0.0458 | 2 | 0 | 2 | 2 | 9218316 | 2816 | 0.000 | 1.000 |
| branch_suffix | fixed-lines64k | 0.0893 | 0.0467 | 2 | 0 | 2 | 2 | 9218316 | 1871 | 0.000 | 1.000 |
| quoted_key | hybrid-fixed64k-cap8m | 0.0893 | 0.0482 | 2 | 0 | 2 | 2 | 9218316 | 2115 | 0.000 | 1.000 |
| literal_failed_password | hybrid-fixed64k-cap16m | 0.0908 | 0.0485 | 2 | 0 | 2 | 2 | 9218316 | 945 | 0.000 | 1.000 |
| literal_failed_password | hybrid-fixed64k-cap16m | 0.0909 | 0.0494 | 2 | 0 | 2 | 2 | 9218316 | 945 | 0.000 | 1.000 |
| alternation_error_failed_denied | hybrid-fixed64k-cap16m | 0.0911 | 0.0468 | 2 | 0 | 2 | 2 | 9218316 | 2816 | 0.000 | 1.000 |
| quoted_key | fixed-lines64k | 0.0912 | 0.0508 | 2 | 0 | 2 | 2 | 9218316 | 2115 | 0.000 | 1.000 |
| alternation_error_failed_denied | hybrid-fixed64k-cap8m | 0.0913 | 0.0471 | 2 | 0 | 2 | 2 | 9218316 | 2816 | 0.000 | 1.000 |
| quoted_key | fixed-lines64k | 0.0913 | 0.0508 | 2 | 0 | 2 | 2 | 9218316 | 2115 | 0.000 | 1.000 |
| literal_failed_password | hybrid-fixed64k-cap16m | 0.0915 | 0.0504 | 2 | 0 | 2 | 2 | 9218316 | 945 | 0.000 | 1.000 |
| alternation_error_failed_denied | fixed-lines64k | 0.0917 | 0.0474 | 2 | 0 | 2 | 2 | 9218316 | 2816 | 0.000 | 1.000 |
| branch_suffix | hybrid-fixed64k-cap16m | 0.0924 | 0.0495 | 2 | 0 | 2 | 2 | 9218316 | 1871 | 0.000 | 1.000 |
| literal_failed_password | fixed-lines64k | 0.0926 | 0.0503 | 2 | 0 | 2 | 2 | 9218316 | 945 | 0.000 | 1.000 |
| literal_failed_password | hybrid-fixed64k-cap8m | 0.0928 | 0.0490 | 2 | 0 | 2 | 2 | 9218316 | 945 | 0.000 | 1.000 |
| literal_failed_password | hybrid-fixed64k-cap8m | 0.0934 | 0.0509 | 2 | 0 | 2 | 2 | 9218316 | 945 | 0.000 | 1.000 |
| quoted_key | hybrid-fixed64k-cap8m | 0.0935 | 0.0513 | 2 | 0 | 2 | 2 | 9218316 | 2115 | 0.000 | 1.000 |
| branch_suffix | hybrid-fixed64k-cap16m | 0.0940 | 0.0492 | 2 | 0 | 2 | 2 | 9218316 | 1871 | 0.000 | 1.000 |
| quoted_key | hybrid-fixed64k-cap16m | 0.0947 | 0.0523 | 2 | 0 | 2 | 2 | 9218316 | 2115 | 0.000 | 1.000 |
| quoted_key | hybrid-fixed64k-cap16m | 0.0947 | 0.0518 | 2 | 0 | 2 | 2 | 9218316 | 2115 | 0.000 | 1.000 |
| branch_suffix | fixed-lines64k | 0.0955 | 0.0505 | 2 | 0 | 2 | 2 | 9218316 | 1871 | 0.000 | 1.000 |
| quoted_key | fixed-lines64k | 0.0959 | 0.0528 | 2 | 0 | 2 | 2 | 9218316 | 2115 | 0.000 | 1.000 |
| branch_suffix | hybrid-fixed64k-cap16m | 0.0962 | 0.0481 | 2 | 0 | 2 | 2 | 9218316 | 1871 | 0.000 | 1.000 |
| branch_suffix | hybrid-fixed64k-cap8m | 0.0965 | 0.0511 | 2 | 0 | 2 | 2 | 9218316 | 1871 | 0.000 | 1.000 |
| alternation_error_failed_denied | hybrid-fixed64k-cap16m | 0.0972 | 0.0506 | 2 | 0 | 2 | 2 | 9218316 | 2816 | 0.000 | 1.000 |
| branch_suffix | fixed-lines64k | 0.0977 | 0.0517 | 2 | 0 | 2 | 2 | 9218316 | 1871 | 0.000 | 1.000 |
| branch_suffix | hybrid-fixed64k-cap8m | 0.0978 | 0.0509 | 2 | 0 | 2 | 2 | 9218316 | 1871 | 0.000 | 1.000 |
| quoted_key | hybrid-fixed64k-cap16m | 0.0983 | 0.0551 | 2 | 0 | 2 | 2 | 9218316 | 2115 | 0.000 | 1.000 |
| quoted_key | hybrid-fixed64k-cap8m | 0.0986 | 0.0531 | 2 | 0 | 2 | 2 | 9218316 | 2115 | 0.000 | 1.000 |
| alternation_error_failed_denied | hybrid-fixed64k-cap8m | 0.0989 | 0.0501 | 2 | 0 | 2 | 2 | 9218316 | 2816 | 0.000 | 1.000 |
| literal_failed_password | fixed-lines64k | 0.0992 | 0.0595 | 2 | 0 | 2 | 2 | 9218316 | 945 | 0.000 | 1.000 |
| alternation_error_failed_denied | fixed-lines64k | 0.0999 | 0.0525 | 2 | 0 | 2 | 2 | 9218316 | 2816 | 0.000 | 1.000 |
| alternation_error_failed_denied | hybrid-fixed64k-cap8m | 0.1001 | 0.0544 | 2 | 0 | 2 | 2 | 9218316 | 2816 | 0.000 | 1.000 |
| alternation_error_failed_denied | fixed-lines64k | 0.1001 | 0.0522 | 2 | 0 | 2 | 2 | 9218316 | 2816 | 0.000 | 1.000 |
| literal_failed_password | hybrid-fixed64k-cap8m | 0.1049 | 0.0612 | 2 | 0 | 2 | 2 | 9218316 | 945 | 0.000 | 1.000 |
| branch_suffix | hybrid-fixed64k-cap8m | 0.1084 | 0.0578 | 2 | 0 | 2 | 2 | 9218316 | 1871 | 0.000 | 1.000 |
| branch_suffix | progressive-lines | 0.1108 | 0.0179 | 5 | 0 | 5 | 5 | 9218316 | 1871 | 0.000 | 1.000 |
| literal_failed_password | hybrid-progressive-cap8m | 0.1117 | 0.0248 | 5 | 0 | 5 | 5 | 9218316 | 945 | 0.000 | 1.000 |
| literal_failed_password | progressive-lines | 0.1119 | 0.0237 | 5 | 0 | 5 | 5 | 9218316 | 945 | 0.000 | 1.000 |
| literal_failed_password | progressive-lines | 0.1124 | 0.0253 | 5 | 0 | 5 | 5 | 9218316 | 945 | 0.000 | 1.000 |
| branch_suffix | hybrid-progressive-cap16m | 0.1127 | 0.0204 | 5 | 0 | 5 | 5 | 9218316 | 1871 | 0.000 | 1.000 |
| literal_failed_password | hybrid-progressive-cap16m | 0.1134 | 0.0243 | 5 | 0 | 5 | 5 | 9218316 | 945 | 0.000 | 1.000 |
| branch_suffix | hybrid-progressive-cap8m | 0.1138 | 0.0182 | 5 | 0 | 5 | 5 | 9218316 | 1871 | 0.000 | 1.000 |
| quoted_key | progressive-lines | 0.1148 | 0.0179 | 5 | 0 | 5 | 5 | 9218316 | 2115 | 0.000 | 1.000 |
| quoted_key | progressive-lines | 0.1148 | 0.0192 | 5 | 0 | 5 | 5 | 9218316 | 2115 | 0.000 | 1.000 |
| literal_failed_password | hybrid-progressive-cap8m | 0.1153 | 0.0261 | 5 | 0 | 5 | 5 | 9218316 | 945 | 0.000 | 1.000 |
| quoted_key | progressive-lines | 0.1159 | 0.0188 | 5 | 0 | 5 | 5 | 9218316 | 2115 | 0.000 | 1.000 |
| branch_suffix | hybrid-progressive-cap16m | 0.1160 | 0.0193 | 5 | 0 | 5 | 5 | 9218316 | 1871 | 0.000 | 1.000 |
| branch_suffix | hybrid-progressive-cap8m | 0.1165 | 0.0196 | 5 | 0 | 5 | 5 | 9218316 | 1871 | 0.000 | 1.000 |
| branch_suffix | progressive-lines | 0.1170 | 0.0198 | 5 | 0 | 5 | 5 | 9218316 | 1871 | 0.000 | 1.000 |
| quoted_key | hybrid-progressive-cap16m | 0.1170 | 0.0196 | 5 | 0 | 5 | 5 | 9218316 | 2115 | 0.000 | 1.000 |
| alternation_error_failed_denied | hybrid-progressive-cap16m | 0.1174 | 0.0190 | 5 | 0 | 5 | 5 | 9218316 | 2816 | 0.000 | 1.000 |
| alternation_error_failed_denied | progressive-lines | 0.1179 | 0.0183 | 5 | 0 | 5 | 5 | 9218316 | 2816 | 0.000 | 1.000 |
| quoted_key | hybrid-progressive-cap8m | 0.1182 | 0.0214 | 5 | 0 | 5 | 5 | 9218316 | 2115 | 0.000 | 1.000 |
| alternation_error_failed_denied | hybrid-progressive-cap8m | 0.1187 | 0.0189 | 5 | 0 | 5 | 5 | 9218316 | 2816 | 0.000 | 1.000 |
| branch_suffix | hybrid-progressive-cap16m | 0.1187 | 0.0196 | 5 | 0 | 5 | 5 | 9218316 | 1871 | 0.000 | 1.000 |
| branch_suffix | hybrid-progressive-cap8m | 0.1189 | 0.0194 | 5 | 0 | 5 | 5 | 9218316 | 1871 | 0.000 | 1.000 |
| literal_failed_password | hybrid-progressive-cap8m | 0.1191 | 0.0265 | 5 | 0 | 5 | 5 | 9218316 | 945 | 0.000 | 1.000 |
| alternation_error_failed_denied | progressive-lines | 0.1192 | 0.0202 | 5 | 0 | 5 | 5 | 9218316 | 2816 | 0.000 | 1.000 |
| alternation_error_failed_denied | progressive-lines | 0.1193 | 0.0182 | 5 | 0 | 5 | 5 | 9218316 | 2816 | 0.000 | 1.000 |
| alternation_error_failed_denied | hybrid-progressive-cap8m | 0.1206 | 0.0193 | 5 | 0 | 5 | 5 | 9218316 | 2816 | 0.000 | 1.000 |
| alternation_error_failed_denied | hybrid-progressive-cap8m | 0.1207 | 0.0217 | 5 | 0 | 5 | 5 | 9218316 | 2816 | 0.000 | 1.000 |
| quoted_key | hybrid-progressive-cap8m | 0.1208 | 0.0205 | 5 | 0 | 5 | 5 | 9218316 | 2115 | 0.000 | 1.000 |
| quoted_key | hybrid-progressive-cap16m | 0.1215 | 0.0194 | 5 | 0 | 5 | 5 | 9218316 | 2115 | 0.000 | 1.000 |
| literal_failed_password | hybrid-progressive-cap16m | 0.1218 | 0.0274 | 5 | 0 | 5 | 5 | 9218316 | 945 | 0.000 | 1.000 |
| alternation_error_failed_denied | hybrid-progressive-cap16m | 0.1223 | 0.0185 | 5 | 0 | 5 | 5 | 9218316 | 2816 | 0.000 | 1.000 |
| branch_suffix | progressive-lines | 0.1224 | 0.0195 | 5 | 0 | 5 | 5 | 9218316 | 1871 | 0.000 | 1.000 |
| alternation_error_failed_denied | hybrid-progressive-cap16m | 0.1245 | 0.0189 | 5 | 0 | 5 | 5 | 9218316 | 2816 | 0.000 | 1.000 |
| literal_failed_password | progressive-lines | 0.1261 | 0.0287 | 5 | 0 | 5 | 5 | 9218316 | 945 | 0.000 | 1.000 |
| quoted_key | hybrid-progressive-cap8m | 0.1270 | 0.0189 | 5 | 0 | 5 | 5 | 9218316 | 2115 | 0.000 | 1.000 |
| literal_failed_password | hybrid-progressive-cap16m | 0.1283 | 0.0278 | 5 | 0 | 5 | 5 | 9218316 | 945 | 0.000 | 1.000 |
| quoted_key | hybrid-progressive-cap16m | 0.1309 | 0.0203 | 5 | 0 | 5 | 5 | 9218316 | 2115 | 0.000 | 1.000 |
| src_ip | hybrid-fixed64k-cap16m | 0.1403 | 0.0494 | 2 | 0 | 2 | 2 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | fixed-lines64k | 0.1411 | 0.0498 | 2 | 0 | 2 | 2 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | fixed-lines64k | 0.1418 | 0.0478 | 2 | 0 | 2 | 2 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | hybrid-fixed64k-cap8m | 0.1474 | 0.0519 | 2 | 0 | 2 | 2 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | hybrid-fixed64k-cap8m | 0.1481 | 0.0527 | 2 | 0 | 2 | 2 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | hybrid-fixed64k-cap16m | 0.1482 | 0.0506 | 2 | 0 | 2 | 2 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | hybrid-fixed64k-cap8m | 0.1535 | 0.0490 | 2 | 0 | 2 | 2 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | hybrid-fixed64k-cap16m | 0.1547 | 0.0508 | 2 | 0 | 2 | 2 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | progressive-lines | 0.1642 | 0.0134 | 5 | 0 | 5 | 5 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | hybrid-progressive-cap8m | 0.1664 | 0.0142 | 5 | 0 | 5 | 5 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | progressive-lines | 0.1667 | 0.0134 | 5 | 0 | 5 | 5 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | hybrid-progressive-cap16m | 0.1720 | 0.0123 | 5 | 0 | 5 | 5 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | hybrid-progressive-cap16m | 0.1726 | 0.0135 | 5 | 0 | 5 | 5 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | hybrid-progressive-cap8m | 0.1726 | 0.0119 | 5 | 0 | 5 | 5 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | hybrid-progressive-cap8m | 0.1740 | 0.0179 | 5 | 0 | 5 | 5 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | fixed-lines64k | 0.1767 | 0.0457 | 2 | 0 | 2 | 2 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | hybrid-progressive-cap16m | 0.1767 | 0.0139 | 5 | 0 | 5 | 5 | 9218316 | 125000 | 0.000 | 1.000 |
| src_ip | progressive-lines | 0.1954 | 0.0135 | 5 | 0 | 5 | 5 | 9218316 | 125000 | 0.000 | 1.000 |

## Selector effectiveness summary
- Patterns decoding all chunks: fixed-lines64k:alternation_error_failed_denied, fixed-lines64k:branch_suffix, fixed-lines64k:literal_failed_password, fixed-lines64k:quoted_key, fixed-lines64k:src_ip, hybrid-fixed64k-cap16m:alternation_error_failed_denied, hybrid-fixed64k-cap16m:branch_suffix, hybrid-fixed64k-cap16m:literal_failed_password, hybrid-fixed64k-cap16m:quoted_key, hybrid-fixed64k-cap16m:src_ip, hybrid-fixed64k-cap8m:alternation_error_failed_denied, hybrid-fixed64k-cap8m:branch_suffix, hybrid-fixed64k-cap8m:literal_failed_password, hybrid-fixed64k-cap8m:quoted_key, hybrid-fixed64k-cap8m:src_ip, hybrid-progressive-cap16m:alternation_error_failed_denied, hybrid-progressive-cap16m:branch_suffix, hybrid-progressive-cap16m:literal_failed_password, hybrid-progressive-cap16m:quoted_key, hybrid-progressive-cap16m:src_ip, hybrid-progressive-cap8m:alternation_error_failed_denied, hybrid-progressive-cap8m:branch_suffix, hybrid-progressive-cap8m:literal_failed_password, hybrid-progressive-cap8m:quoted_key, hybrid-progressive-cap8m:src_ip, progressive-lines:alternation_error_failed_denied, progressive-lines:branch_suffix, progressive-lines:literal_failed_password, progressive-lines:quoted_key, progressive-lines:src_ip
- Patterns with effective skipping (skip_ratio >= 0.25): fixed-lines64k:lookbehind_key, fixed-lines64k:no_match_literal, hybrid-fixed64k-cap16m:lookbehind_key, hybrid-fixed64k-cap16m:no_match_literal, hybrid-fixed64k-cap8m:lookbehind_key, hybrid-fixed64k-cap8m:no_match_literal, hybrid-progressive-cap16m:lookbehind_key, hybrid-progressive-cap16m:no_match_literal, hybrid-progressive-cap8m:lookbehind_key, hybrid-progressive-cap8m:no_match_literal, progressive-lines:lookbehind_key, progressive-lines:no_match_literal

## Next likely optimization
- Most likely next step: summary refinement or selector extraction, because some patterns still force full decode.
