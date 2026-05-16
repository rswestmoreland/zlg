# Phase 1g Size Overhead Pass

This benchmark compares the carried-forward builders against gzip build speed, CPU, RSS, output size, and zlg component overhead.

RSS and CPU capture are fail-closed. Blank max_rss_kb or total_cpu_seconds fails the run.

## Compression ranking by corpus

### binaryish

| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | gzip | gzip-6 | 0.017196 | 0.011885 | 1856 | 126894 |  |  |  |  |  |  |
| 2 | zlg | combined | 0.032626 | 0.029644 | 6044 | 327042 | 1512642 | 0 | 0 | 277888 | 155248 | 0.441329 |
| 3 | zlg | combined-bitset-seen | 0.038638 | 0.033644 | 6748 | 327042 | 3470848 | 2097152 | 0 | 155248 | 155248 | 0.000000 |
| 4 | zlg | combined-bitset-paged-seen | 0.044807 | 0.040474 | 7364 | 327042 | 3470848 | 2097152 | 2097152 | 155248 | 155248 | 0.000000 |
| 5 | zlg | combined-sparse-first-bitset | 0.044827 | 0.042932 | 7276 | 327042 | 3470848 | 0 | 2097152 | 155248 | 155248 | 0.000000 |

### high_cardinality

| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | zlg | combined-bitset-seen | 0.153624 | 0.150338 | 8556 | 2386482 | 23488784 | 2097152 | 0 | 56887 | 56887 | 0.000000 |
| 2 | zlg | combined-bitset-paged-seen | 0.196994 | 0.193057 | 8552 | 2386482 | 23488784 | 2097152 | 2097152 | 56887 | 56887 | 0.000000 |
| 3 | zlg | combined-sparse-first-bitset | 0.197085 | 0.193414 | 6904 | 2386482 | 21743888 | 0 | 352256 | 56887 | 56887 | 0.000000 |
| 4 | gzip | gzip-6 | 0.350113 | 0.346107 | 1960 | 2474031 |  |  |  |  |  |  |
| 5 | zlg | combined | 0.478966 | 0.474005 | 18220 | 2386482 | 24064566 | 0 | 0 | 26102428 | 56887 | 0.997821 |

### high_dup

| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | zlg | combined-bitset-seen | 0.144171 | 0.142567 | 9112 | 1345279 | 21554736 | 2097152 | 0 | 53826 | 53826 | 0.000000 |
| 2 | zlg | combined-sparse-first-bitset | 0.191188 | 0.187286 | 7432 | 1345279 | 19818032 | 0 | 360448 | 53826 | 53826 | 0.000000 |
| 3 | zlg | combined-bitset-paged-seen | 0.196201 | 0.194135 | 9116 | 1345279 | 21554736 | 2097152 | 2097152 | 53826 | 53826 | 0.000000 |
| 4 | gzip | gzip-6 | 0.200528 | 0.197489 | 2036 | 1455414 |  |  |  |  |  |  |
| 5 | zlg | combined | 0.401229 | 0.397561 | 17712 | 1345279 | 21888762 | 0 | 0 | 23742116 | 53826 | 0.997733 |

### long_line_log

| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | zlg | combined-bitset-seen | 0.371073 | 0.367817 | 31312 | 1572192 | 191647912 | 2097152 | 0 | 11994 | 11994 | 0.000000 |
| 2 | zlg | combined-bitset-paged-seen | 0.460158 | 0.456997 | 31168 | 1572192 | 191647912 | 2097152 | 2097152 | 11994 | 11994 | 0.000000 |
| 3 | zlg | combined-sparse-first-bitset | 0.461285 | 0.460262 | 29496 | 1572192 | 189894824 | 0 | 344064 | 11994 | 11994 | 0.000000 |
| 4 | gzip | gzip-6 | 1.165133 | 1.159739 | 2096 | 2925542 |  |  |  |  |  |  |
| 5 | zlg | combined | 2.107071 | 2.099591 | 237444 | 1572192 | 213243583 | 0 | 0 | 57845056 | 11994 | 0.999793 |

### realistic_mixed_log

| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | zlg | combined-bitset-seen | 0.171254 | 0.170257 | 8652 | 2403573 | 24047968 | 2097152 | 0 | 62619 | 62619 | 0.000000 |
| 2 | zlg | combined-sparse-first-bitset | 0.224534 | 0.219919 | 7028 | 2403573 | 22393184 | 0 | 442368 | 62619 | 62619 | 0.000000 |
| 3 | zlg | combined-bitset-paged-seen | 0.244804 | 0.237904 | 8600 | 2403573 | 24047968 | 2097152 | 2097152 | 62619 | 62619 | 0.000000 |
| 4 | gzip | gzip-6 | 0.371610 | 0.367370 | 2016 | 2152918 |  |  |  |  |  |  |
| 5 | zlg | combined | 0.499798 | 0.498638 | 18632 | 2403573 | 24693648 | 0 | 0 | 26776766 | 62619 | 0.997661 |

### short_line_log

| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | zlg | combined-bitset-seen | 0.101723 | 0.098007 | 7312 | 1380881 | 8280160 | 2097152 | 0 | 35051 | 35051 | 0.000000 |
| 2 | zlg | combined-bitset-paged-seen | 0.127969 | 0.122945 | 7324 | 1380881 | 8280160 | 2097152 | 2097152 | 35051 | 35051 | 0.000000 |
| 3 | zlg | combined-sparse-first-bitset | 0.139096 | 0.136254 | 5504 | 1380881 | 6436960 | 0 | 253952 | 35051 | 35051 | 0.000000 |
| 4 | zlg | combined | 0.149469 | 0.146832 | 6848 | 1380881 | 3092528 | 0 | 0 | 7547166 | 35051 | 0.995356 |
| 5 | gzip | gzip-6 | 0.256581 | 0.255369 | 1988 | 1195190 |  |  |  |  |  |  |

### unicode

| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | gzip | gzip-6 | 0.027937 | 0.023385 | 1904 | 99957 |  |  |  |  |  |  |
| 2 | zlg | combined-bitset-seen | 0.049410 | 0.046704 | 7660 | 70312 | 9722104 | 2097152 | 0 | 4332 | 4332 | 0.000000 |
| 3 | zlg | combined-sparse-first-bitset | 0.055343 | 0.049371 | 6232 | 70312 | 8247544 | 0 | 622592 | 4332 | 4332 | 0.000000 |
| 4 | zlg | combined-bitset-paged-seen | 0.058859 | 0.054657 | 7624 | 70312 | 9722104 | 2097152 | 2097152 | 4332 | 4332 | 0.000000 |
| 5 | zlg | combined | 0.126240 | 0.121550 | 14028 | 70312 | 8577817 | 0 | 0 | 4652500 | 4332 | 0.999069 |

## Size component comparison

This section compares zlg component sizes against gzip output size. The zlg component fields are parsed from the .zlg archive and help identify whether size losses come from compressed payload, mesh summary, chunk headers, or directory/footer overhead.

### binaryish

| profile | zlg_bytes | gzip_bytes | delta_vs_gzip | summary | payload | headers | dir_footer |
|---|---:|---:|---:|---:|---:|---:|---:|
| combined | 327042 | 126894 | 200148 | 200626 | 126192 | 64 | 128 |
| combined-bitset-paged-seen | 327042 | 126894 | 200148 | 200626 | 126192 | 64 | 128 |
| combined-bitset-seen | 327042 | 126894 | 200148 | 200626 | 126192 | 64 | 128 |
| combined-sparse-first-bitset | 327042 | 126894 | 200148 | 200626 | 126192 | 64 | 128 |

### high_cardinality

| profile | zlg_bytes | gzip_bytes | delta_vs_gzip | summary | payload | headers | dir_footer |
|---|---:|---:|---:|---:|---:|---:|---:|
| combined | 2386482 | 2474031 | -87549 | 61817 | 2323289 | 640 | 704 |
| combined-bitset-paged-seen | 2386482 | 2474031 | -87549 | 61817 | 2323289 | 640 | 704 |
| combined-bitset-seen | 2386482 | 2474031 | -87549 | 61817 | 2323289 | 640 | 704 |
| combined-sparse-first-bitset | 2386482 | 2474031 | -87549 | 61817 | 2323289 | 640 | 704 |

### high_dup

| profile | zlg_bytes | gzip_bytes | delta_vs_gzip | summary | payload | headers | dir_footer |
|---|---:|---:|---:|---:|---:|---:|---:|
| combined | 1345279 | 1455414 | -110135 | 58852 | 1285051 | 640 | 704 |
| combined-bitset-paged-seen | 1345279 | 1455414 | -110135 | 58852 | 1285051 | 640 | 704 |
| combined-bitset-seen | 1345279 | 1455414 | -110135 | 58852 | 1285051 | 640 | 704 |
| combined-sparse-first-bitset | 1345279 | 1455414 | -110135 | 58852 | 1285051 | 640 | 704 |

### long_line_log

| profile | zlg_bytes | gzip_bytes | delta_vs_gzip | summary | payload | headers | dir_footer |
|---|---:|---:|---:|---:|---:|---:|---:|
| combined | 1572192 | 2925542 | -1353350 | 13044 | 1558796 | 128 | 192 |
| combined-bitset-paged-seen | 1572192 | 2925542 | -1353350 | 13044 | 1558796 | 128 | 192 |
| combined-bitset-seen | 1572192 | 2925542 | -1353350 | 13044 | 1558796 | 128 | 192 |
| combined-sparse-first-bitset | 1572192 | 2925542 | -1353350 | 13044 | 1558796 | 128 | 192 |

### realistic_mixed_log

| profile | zlg_bytes | gzip_bytes | delta_vs_gzip | summary | payload | headers | dir_footer |
|---|---:|---:|---:|---:|---:|---:|---:|
| combined | 2403573 | 2152918 | 250655 | 69289 | 2332908 | 640 | 704 |
| combined-bitset-paged-seen | 2403573 | 2152918 | 250655 | 69289 | 2332908 | 640 | 704 |
| combined-bitset-seen | 2403573 | 2152918 | 250655 | 69289 | 2332908 | 640 | 704 |
| combined-sparse-first-bitset | 2403573 | 2152918 | 250655 | 69289 | 2332908 | 640 | 704 |

### short_line_log

| profile | zlg_bytes | gzip_bytes | delta_vs_gzip | summary | payload | headers | dir_footer |
|---|---:|---:|---:|---:|---:|---:|---:|
| combined | 1380881 | 1195190 | 185691 | 39991 | 1338234 | 1280 | 1344 |
| combined-bitset-paged-seen | 1380881 | 1195190 | 185691 | 39991 | 1338234 | 1280 | 1344 |
| combined-bitset-seen | 1380881 | 1195190 | 185691 | 39991 | 1338234 | 1280 | 1344 |
| combined-sparse-first-bitset | 1380881 | 1195190 | 185691 | 39991 | 1338234 | 1280 | 1344 |

### unicode

| profile | zlg_bytes | gzip_bytes | delta_vs_gzip | summary | payload | headers | dir_footer |
|---|---:|---:|---:|---:|---:|---:|---:|
| combined | 70312 | 99957 | -29645 | 5436 | 64396 | 192 | 256 |
| combined-bitset-paged-seen | 70312 | 99957 | -29645 | 5436 | 64396 | 192 | 256 |
| combined-bitset-seen | 70312 | 99957 | -29645 | 5436 | 64396 | 192 | 256 |
| combined-sparse-first-bitset | 70312 | 99957 | -29645 | 5436 | 64396 | 192 | 256 |

## Candidates

- combined: current safe baseline and reference builder.
- combined-bitset-seen: full contiguous u24 bitset production candidate.
- combined-bitset-paged-seen: full u24 bitset stored as 256 first-byte pages.
- combined-sparse-first-bitset: sparse first-byte bitset second candidate.
- gzip -6: external build speed, CPU, RSS, and size baseline.

## Success criteria

- Full validation script completes.
- No CSV row has blank max_rss_kb.
- No CSV row has blank total_cpu_seconds.
- Search output for candidate profiles matches combined on line-oriented corpora.
- Combined round trip is byte-exact for every corpus, including unicode and binaryish.
- gzip compression speed, CPU, RSS, and output size are recorded for every corpus.
- zlg summary, compressed payload, chunk header, and directory/footer bytes are recorded.
- No on-disk format change is introduced.
