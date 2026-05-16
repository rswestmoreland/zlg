# Phase 1f Final Builder Bakeoff

This benchmark narrows the production-facing builder candidates and compares zlg against gzip build speed, CPU, RSS, and output size.

RSS and CPU capture are fail-closed. Blank max_rss_kb or total_cpu_seconds fails the run.

## Compression ranking by corpus

### binaryish

| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | gzip | gzip-6 | 0.018661 | 0.014475 | 1804 | 126894 |  |  |  |  |  |  |
| 2 | zlg | combined | 0.045867 | 0.039971 | 5936 | 327042 | 1512642 | 0 | 0 | 277888 | 155248 | 0.441329 |
| 3 | zlg | combined-bitset-seen | 0.046209 | 0.042994 | 7360 | 327042 | 3470848 | 2097152 | 0 | 155248 | 155248 | 0.000000 |
| 4 | zlg | combined-sparse-first-bitset | 0.057310 | 0.052957 | 7384 | 327042 | 3470848 | 0 | 2097152 | 155248 | 155248 | 0.000000 |
| 5 | zlg | combined-trie-pair-bitset | 0.059255 | 0.056458 | 7760 | 327042 | 3601920 | 0 | 2228224 | 155248 | 155248 | 0.000000 |

### high_cardinality

| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | zlg | combined-bitset-seen | 0.235937 | 0.234075 | 8516 | 2386482 | 23488784 | 2097152 | 0 | 56887 | 56887 | 0.000000 |
| 2 | zlg | combined-sparse-first-bitset | 0.300643 | 0.295383 | 6968 | 2386482 | 21743888 | 0 | 352256 | 56887 | 56887 | 0.000000 |
| 3 | zlg | combined-trie-pair-bitset | 0.310306 | 0.307046 | 6632 | 2386482 | 21545616 | 0 | 153984 | 56887 | 56887 | 0.000000 |
| 4 | gzip | gzip-6 | 0.432107 | 0.429509 | 1940 | 2474031 |  |  |  |  |  |  |
| 5 | zlg | combined | 0.668805 | 0.665675 | 18260 | 2386482 | 24064566 | 0 | 0 | 26102428 | 56887 | 0.997821 |

### high_dup

| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | zlg | combined-bitset-seen | 0.225693 | 0.219563 | 8952 | 1345279 | 21554736 | 2097152 | 0 | 53826 | 53826 | 0.000000 |
| 2 | gzip | gzip-6 | 0.258276 | 0.256844 | 2008 | 1455414 |  |  |  |  |  |  |
| 3 | zlg | combined-sparse-first-bitset | 0.267919 | 0.261152 | 7420 | 1345279 | 19818032 | 0 | 360448 | 53826 | 53826 | 0.000000 |
| 4 | zlg | combined-trie-pair-bitset | 0.290156 | 0.287961 | 7348 | 1345279 | 19611696 | 0 | 154112 | 53826 | 53826 | 0.000000 |
| 5 | zlg | combined | 0.555014 | 0.548872 | 17688 | 1345279 | 21888762 | 0 | 0 | 23742116 | 53826 | 0.997733 |

### long_line_log

| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | zlg | combined-bitset-seen | 0.534131 | 0.528328 | 31324 | 1572192 | 191647912 | 2097152 | 0 | 11994 | 11994 | 0.000000 |
| 2 | zlg | combined-sparse-first-bitset | 0.651927 | 0.647832 | 29396 | 1572192 | 189894824 | 0 | 344064 | 11994 | 11994 | 0.000000 |
| 3 | zlg | combined-trie-pair-bitset | 0.717913 | 0.711988 | 29256 | 1572192 | 189704360 | 0 | 153600 | 11994 | 11994 | 0.000000 |
| 4 | gzip | gzip-6 | 1.509196 | 1.503383 | 2064 | 2925542 |  |  |  |  |  |  |
| 5 | zlg | combined | 2.808021 | 2.798885 | 237400 | 1572192 | 213243583 | 0 | 0 | 57845056 | 11994 | 0.999793 |

### realistic_mixed_log

| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | zlg | combined-bitset-seen | 0.257632 | 0.255405 | 8652 | 2403573 | 24047968 | 2097152 | 0 | 62619 | 62619 | 0.000000 |
| 2 | zlg | combined-sparse-first-bitset | 0.306941 | 0.301738 | 6996 | 2403573 | 22393184 | 0 | 442368 | 62619 | 62619 | 0.000000 |
| 3 | zlg | combined-trie-pair-bitset | 0.339899 | 0.334288 | 6932 | 2403573 | 22110944 | 0 | 160128 | 62619 | 62619 | 0.000000 |
| 4 | gzip | gzip-6 | 0.440451 | 0.426769 | 1980 | 2152918 |  |  |  |  |  |  |
| 5 | zlg | combined | 0.690522 | 0.685954 | 18584 | 2403573 | 24693648 | 0 | 0 | 26776766 | 62619 | 0.997661 |

### short_line_log

| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | zlg | combined-bitset-seen | 0.141203 | 0.136015 | 7356 | 1380881 | 8280160 | 2097152 | 0 | 35051 | 35051 | 0.000000 |
| 2 | zlg | combined-sparse-first-bitset | 0.176197 | 0.170311 | 5484 | 1380881 | 6436960 | 0 | 253952 | 35051 | 35051 | 0.000000 |
| 3 | zlg | combined-trie-pair-bitset | 0.190486 | 0.188275 | 5384 | 1380881 | 6323168 | 0 | 140160 | 35051 | 35051 | 0.000000 |
| 4 | zlg | combined | 0.209370 | 0.204907 | 6728 | 1380881 | 3092528 | 0 | 0 | 7547166 | 35051 | 0.995356 |
| 5 | gzip | gzip-6 | 0.295891 | 0.292137 | 2016 | 1195190 |  |  |  |  |  |  |

### unicode

| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | gzip | gzip-6 | 0.035271 | 0.030418 | 1848 | 99957 |  |  |  |  |  |  |
| 2 | zlg | combined-bitset-seen | 0.068683 | 0.065732 | 7572 | 70312 | 9722104 | 2097152 | 0 | 4332 | 4332 | 0.000000 |
| 3 | zlg | combined-trie-pair-bitset | 0.073376 | 0.067999 | 5644 | 70312 | 7770488 | 0 | 145536 | 4332 | 4332 | 0.000000 |
| 4 | zlg | combined-sparse-first-bitset | 0.077777 | 0.072606 | 6104 | 70312 | 8247544 | 0 | 622592 | 4332 | 4332 | 0.000000 |
| 5 | zlg | combined | 0.174740 | 0.170698 | 14016 | 70312 | 8577817 | 0 | 0 | 4652500 | 4332 | 0.999069 |

## Candidates

- combined: current safe baseline.
- combined-bitset-seen: full u24 bitset candidate.
- combined-sparse-first-bitset: sparse first-byte bitset candidate.
- combined-trie-pair-bitset: trie-pair bitset candidate.
- gzip -6: external build speed, CPU, RSS, and size baseline.

## Success criteria

- Full validation script completes.
- No CSV row has blank max_rss_kb.
- No CSV row has blank total_cpu_seconds.
- Search output for candidate profiles matches combined on line-oriented corpora.
- Combined round trip is byte-exact for every corpus, including unicode and binaryish.
- gzip compression speed, CPU, RSS, and output size are recorded for every corpus.
- No on-disk format change is introduced.
