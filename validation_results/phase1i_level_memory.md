# Phase 1i Zstd Level and Memory Diagnosis

This is a diagnostic confirmation pass. It keeps the locked zlg stack fixed and varies only zstd level for the locked builder. It also runs a no-summary diagnostic path to estimate how much RSS belongs to chunking/zstd/writer behavior versus mesh-summary construction.

## Locked stack

```text
fixed-lines8192
+ mesh-bigram ZBM1 v2
+ zstd::bulk::Compressor
+ combined-bitset-seen
+ streaming grep
+ Rust regex default
+ PCRE2 for -P
+ literal prefiltering
+ positive-lookbehind fast path
+ --head / --max-count early stop
```

## Zstd level comparison for locked mesh profile

| corpus | gzip_bytes | level | zlg_bytes | delta_vs_gzip | payload_bytes | summary_bytes | wall_s | cpu_s | rss_kb |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| binaryish | 126894 | 3 | 327042 | 200148 | 126192 | 200626 | 0.027168 | 0.023262 | 7484 |
| binaryish | 126894 | 4 | 327027 | 200133 | 126177 | 200626 | 0.031896 | 0.028005 | 7492 |
| binaryish | 126894 | 5 | 327023 | 200129 | 126173 | 200626 | 0.031836 | 0.026933 | 8000 |
| binaryish | 126894 | 6 | 327013 | 200119 | 126163 | 200626 | 0.033097 | 0.032541 | 9396 |
| high_cardinality | 2474031 | 3 | 2386482 | -87549 | 2323289 | 61817 | 0.121689 | 0.114987 | 8604 |
| high_cardinality | 2474031 | 4 | 2413986 | -60045 | 2350793 | 61817 | 0.127218 | 0.125974 | 9884 |
| high_cardinality | 2474031 | 5 | 2404068 | -69963 | 2340875 | 61817 | 0.173260 | 0.172483 | 10464 |
| high_cardinality | 2474031 | 6 | 2386917 | -87114 | 2323724 | 61817 | 0.189615 | 0.184110 | 10496 |
| high_dup | 1455414 | 3 | 1345279 | -110135 | 1285051 | 58852 | 0.110949 | 0.102867 | 9140 |
| high_dup | 1455414 | 4 | 1345163 | -110251 | 1284935 | 58852 | 0.111267 | 0.109643 | 10348 |
| high_dup | 1455414 | 5 | 1213788 | -241626 | 1153560 | 58852 | 0.147226 | 0.145742 | 11020 |
| high_dup | 1455414 | 6 | 1187752 | -267662 | 1127524 | 58852 | 0.173819 | 0.170343 | 11056 |
| long_line_log | 2925542 | 3 | 1572192 | -1353350 | 1558796 | 13044 | 0.277620 | 0.274307 | 31256 |
| long_line_log | 2925542 | 4 | 1582039 | -1343503 | 1568643 | 13044 | 0.279053 | 0.274110 | 32548 |
| long_line_log | 2925542 | 5 | 1538602 | -1386940 | 1525206 | 13044 | 0.286535 | 0.284134 | 33180 |
| long_line_log | 2925542 | 6 | 1165501 | -1760041 | 1152105 | 13044 | 0.302287 | 0.301609 | 32816 |
| realistic_mixed_log | 2152918 | 3 | 2403573 | 250655 | 2332908 | 69289 | 0.131431 | 0.127520 | 8632 |
| realistic_mixed_log | 2152918 | 4 | 2400799 | 247881 | 2330134 | 69289 | 0.143733 | 0.138468 | 9852 |
| realistic_mixed_log | 2152918 | 5 | 2185317 | 32399 | 2114652 | 69289 | 0.183846 | 0.181127 | 10444 |
| realistic_mixed_log | 2152918 | 6 | 2071996 | -80922 | 2001331 | 69289 | 0.209248 | 0.205557 | 10460 |
| short_line_log | 1195190 | 3 | 1380881 | 185691 | 1338234 | 39991 | 0.074113 | 0.072604 | 7316 |
| short_line_log | 1195190 | 4 | 1378611 | 183421 | 1335964 | 39991 | 0.079581 | 0.077867 | 8600 |
| short_line_log | 1195190 | 5 | 1352575 | 157385 | 1309928 | 39991 | 0.109793 | 0.107102 | 9252 |
| short_line_log | 1195190 | 6 | 1254069 | 58879 | 1211422 | 39991 | 0.136482 | 0.131667 | 9140 |
| unicode | 99957 | 3 | 70312 | -29645 | 64396 | 5436 | 0.037067 | 0.034690 | 7608 |
| unicode | 99957 | 4 | 70312 | -29645 | 64396 | 5436 | 0.041580 | 0.040831 | 8928 |
| unicode | 99957 | 5 | 51214 | -48743 | 45298 | 5436 | 0.042579 | 0.038716 | 9516 |
| unicode | 99957 | 6 | 53173 | -46784 | 47257 | 5436 | 0.048292 | 0.045708 | 9688 |

## Payload-only diagnostic versus gzip

| corpus | level | payload_delta_vs_gzip | total_delta_vs_gzip | summary_pct | payload_pct |
|---|---:|---:|---:|---:|---:|
| binaryish | 3 | -702 | 200148 | 61.345638 | 38.585870 |
| binaryish | 4 | -717 | 200133 | 61.348451 | 38.583053 |
| binaryish | 5 | -721 | 200129 | 61.349202 | 38.582302 |
| binaryish | 6 | -731 | 200119 | 61.351078 | 38.580423 |
| high_cardinality | 3 | -150742 | -87549 | 2.590298 | 97.352044 |
| high_cardinality | 4 | -123238 | -60045 | 2.560785 | 97.382213 |
| high_cardinality | 5 | -133156 | -69963 | 2.571350 | 97.371414 |
| high_cardinality | 6 | -150307 | -87114 | 2.589826 | 97.352526 |
| high_dup | 3 | -170363 | -110135 | 4.374706 | 95.523010 |
| high_dup | 4 | -170479 | -110251 | 4.375083 | 95.522624 |
| high_dup | 5 | -301854 | -241626 | 4.848623 | 95.038013 |
| high_dup | 6 | -327890 | -267662 | 4.954906 | 94.929244 |
| long_line_log | 3 | -1366746 | -1353350 | 0.829670 | 99.147941 |
| long_line_log | 4 | -1356899 | -1343503 | 0.824506 | 99.153245 |
| long_line_log | 5 | -1400336 | -1386940 | 0.847783 | 99.129339 |
| long_line_log | 6 | -1773437 | -1760041 | 1.119175 | 98.850623 |
| realistic_mixed_log | 3 | 179990 | 250655 | 2.882750 | 97.060002 |
| realistic_mixed_log | 4 | 177216 | 247881 | 2.886081 | 97.056605 |
| realistic_mixed_log | 5 | -38266 | 32399 | 3.170661 | 96.766373 |
| realistic_mixed_log | 6 | -151587 | -80922 | 3.344070 | 96.589520 |
| short_line_log | 3 | 143044 | 185691 | 2.896050 | 96.911609 |
| short_line_log | 4 | 140774 | 183421 | 2.900818 | 96.906524 |
| short_line_log | 5 | 114738 | 157385 | 2.956657 | 96.846977 |
| short_line_log | 6 | 16232 | 58879 | 3.188899 | 96.599310 |
| unicode | 3 | -35561 | -29645 | 7.731255 | 91.586074 |
| unicode | 4 | -35561 | -29645 | 7.731255 | 91.586074 |
| unicode | 5 | -54659 | -48743 | 10.614285 | 88.448471 |
| unicode | 6 | -52700 | -46784 | 10.223234 | 88.874053 |

## Memory isolation: mesh profile versus no-summary diagnostic

| corpus | level | gzip_rss | mesh_rss | no_summary_rss | mesh_minus_no_summary | mesh_minus_gzip | no_summary_minus_gzip | mesh_scratch | bitset_scratch |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| high_dup | 3 | 2032 | 9140 | 7024 | 2116 | 7108 | 4992 | 21554736 | 2097152 |
| high_dup | 4 | 2032 | 10348 | 8268 | 2080 | 8316 | 6236 | 21554736 | 2097152 |
| high_dup | 5 | 2032 | 11020 | 8972 | 2048 | 8988 | 6940 | 21554736 | 2097152 |
| high_dup | 6 | 2032 | 11056 | 8956 | 2100 | 9024 | 6924 | 21554736 | 2097152 |
| high_cardinality | 3 | 1980 | 8604 | 6448 | 2156 | 6624 | 4468 | 23488784 | 2097152 |
| high_cardinality | 4 | 1980 | 9884 | 7784 | 2100 | 7904 | 5804 | 23488784 | 2097152 |
| high_cardinality | 5 | 1980 | 10464 | 8412 | 2052 | 8484 | 6432 | 23488784 | 2097152 |
| high_cardinality | 6 | 1980 | 10496 | 8344 | 2152 | 8516 | 6364 | 23488784 | 2097152 |
| unicode | 3 | 1904 | 7608 | 5592 | 2016 | 5704 | 3688 | 9722104 | 2097152 |
| unicode | 4 | 1904 | 8928 | 6104 | 2824 | 7024 | 4200 | 9722104 | 2097152 |
| unicode | 5 | 1904 | 9516 | 7636 | 1880 | 7612 | 5732 | 9722104 | 2097152 |
| unicode | 6 | 1904 | 9688 | 7484 | 2204 | 7784 | 5580 | 9722104 | 2097152 |
| binaryish | 3 | 1780 | 7484 | 4080 | 3404 | 5704 | 2300 | 3470848 | 2097152 |
| binaryish | 4 | 1780 | 7492 | 3968 | 3524 | 5712 | 2188 | 3470848 | 2097152 |
| binaryish | 5 | 1780 | 8000 | 5372 | 2628 | 6220 | 3592 | 3470848 | 2097152 |
| binaryish | 6 | 1780 | 9396 | 6256 | 3140 | 7616 | 4476 | 3470848 | 2097152 |
| realistic_mixed_log | 3 | 1940 | 8632 | 6512 | 2120 | 6692 | 4572 | 24047968 | 2097152 |
| realistic_mixed_log | 4 | 1940 | 9852 | 7752 | 2100 | 7912 | 5812 | 24047968 | 2097152 |
| realistic_mixed_log | 5 | 1940 | 10444 | 8308 | 2136 | 8504 | 6368 | 24047968 | 2097152 |
| realistic_mixed_log | 6 | 1940 | 10460 | 8380 | 2080 | 8520 | 6440 | 24047968 | 2097152 |
| long_line_log | 3 | 2044 | 31256 | 29216 | 2040 | 29212 | 27172 | 191647912 | 2097152 |
| long_line_log | 4 | 2044 | 32548 | 30520 | 2028 | 30504 | 28476 | 191647912 | 2097152 |
| long_line_log | 5 | 2044 | 33180 | 31124 | 2056 | 31136 | 29080 | 191647912 | 2097152 |
| long_line_log | 6 | 2044 | 32816 | 30660 | 2156 | 30772 | 28616 | 191647912 | 2097152 |
| short_line_log | 3 | 2020 | 7316 | 5244 | 2072 | 5296 | 3224 | 8280160 | 2097152 |
| short_line_log | 4 | 2020 | 8600 | 6520 | 2080 | 6580 | 4500 | 8280160 | 2097152 |
| short_line_log | 5 | 2020 | 9252 | 7100 | 2152 | 7232 | 5080 | 8280160 | 2097152 |
| short_line_log | 6 | 2020 | 9140 | 7128 | 2012 | 7120 | 5108 | 8280160 | 2097152 |

## No-summary diagnostic size check

These rows are diagnostic only. They show the size and RSS of zlg chunking plus zstd payloads without mesh summaries. They are not production candidates.

| corpus | level | no_summary_bytes | no_summary_payload | mesh_payload | payload_delta_mesh_vs_no_summary | no_summary_rss | mesh_rss |
|---|---:|---:|---:|---:|---:|---:|---:|
| binaryish | 3 | 126416 | 126192 | 126192 | 0 | 4080 | 7484 |
| binaryish | 4 | 126401 | 126177 | 126177 | 0 | 3968 | 7492 |
| binaryish | 5 | 126397 | 126173 | 126173 | 0 | 5372 | 8000 |
| binaryish | 6 | 126387 | 126163 | 126163 | 0 | 6256 | 9396 |
| high_cardinality | 3 | 2324665 | 2323289 | 2323289 | 0 | 6448 | 8604 |
| high_cardinality | 4 | 2352169 | 2350793 | 2350793 | 0 | 7784 | 9884 |
| high_cardinality | 5 | 2342251 | 2340875 | 2340875 | 0 | 8412 | 10464 |
| high_cardinality | 6 | 2325100 | 2323724 | 2323724 | 0 | 8344 | 10496 |
| high_dup | 3 | 1286427 | 1285051 | 1285051 | 0 | 7024 | 9140 |
| high_dup | 4 | 1286311 | 1284935 | 1284935 | 0 | 8268 | 10348 |
| high_dup | 5 | 1154936 | 1153560 | 1153560 | 0 | 8972 | 11020 |
| high_dup | 6 | 1128900 | 1127524 | 1127524 | 0 | 8956 | 11056 |
| long_line_log | 3 | 1559148 | 1558796 | 1558796 | 0 | 29216 | 31256 |
| long_line_log | 4 | 1568995 | 1568643 | 1568643 | 0 | 30520 | 32548 |
| long_line_log | 5 | 1525558 | 1525206 | 1525206 | 0 | 31124 | 33180 |
| long_line_log | 6 | 1152457 | 1152105 | 1152105 | 0 | 30660 | 32816 |
| realistic_mixed_log | 3 | 2334284 | 2332908 | 2332908 | 0 | 6512 | 8632 |
| realistic_mixed_log | 4 | 2331510 | 2330134 | 2330134 | 0 | 7752 | 9852 |
| realistic_mixed_log | 5 | 2116028 | 2114652 | 2114652 | 0 | 8308 | 10444 |
| realistic_mixed_log | 6 | 2002707 | 2001331 | 2001331 | 0 | 8380 | 10460 |
| short_line_log | 3 | 1340890 | 1338234 | 1338234 | 0 | 5244 | 7316 |
| short_line_log | 4 | 1338620 | 1335964 | 1335964 | 0 | 6520 | 8600 |
| short_line_log | 5 | 1312584 | 1309928 | 1309928 | 0 | 7100 | 9252 |
| short_line_log | 6 | 1214078 | 1211422 | 1211422 | 0 | 7128 | 9140 |
| unicode | 3 | 64876 | 64396 | 64396 | 0 | 5592 | 7608 |
| unicode | 4 | 64876 | 64396 | 64396 | 0 | 6104 | 8928 |
| unicode | 5 | 45778 | 45298 | 45298 | 0 | 7636 | 9516 |
| unicode | 6 | 47737 | 47257 | 47257 | 0 | 7484 | 9688 |

## Diagnostic questions this run is intended to answer

1. Do zstd levels 4, 5, or 6 close the payload-size gap against gzip -6 for realistic_mixed_log and short_line_log?
2. Does the locked mesh profile remain faster than gzip -6 as zstd level increases?
3. How much RSS appears to come from zlg chunking/zstd/writer behavior before mesh-summary overhead is added?
4. How much RSS does mesh-summary construction add over the no-summary diagnostic path?

## Constraints

- This run must not change the locked stack or promote new candidates.
- No-summary rows are diagnostic only.
- No on-disk format change is introduced.
