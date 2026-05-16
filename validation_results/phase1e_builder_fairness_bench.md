# Phase 1e Builder Fairness Benchmark

RSS capture is fail-closed in this benchmark. Blank max_rss_kb fails the run.

## Compression ranking by corpus

### binaryish

| rank | profile | wall_s | rss_kb | scratch | bitset | first/trie bitset | grouped | pushed | unique | dup_ratio | bytes |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | combined-lower-only | 0.022446 | 4280 | 817920 | 0 | 0 | 0 | 138944 | 122053 | 0.121567 | 285564 |
| 2 | combined | 0.031834 | 5068 | 1512642 | 0 | 0 | 0 | 277888 | 155248 | 0.441329 | 327042 |
| 3 | combined-rdst | 0.031936 | 5860 | 1512642 | 0 | 0 | 0 | 277888 | 155248 | 0.441329 | 327042 |
| 4 | combined-rdxsort | 0.032350 | 5112 | 1512642 | 0 | 0 | 0 | 277888 | 155248 | 0.441329 | 327042 |
| 5 | combined-grouped-buckets | 0.032499 | 5640 | 2368384 | 0 | 0 | 1171456 | 177217 | 155248 | 0.123967 | 327042 |
| 6 | combined-case-raw | 0.032561 | 4240 | 817920 | 0 | 0 | 0 | 138944 | 122714 | 0.116810 | 297135 |
| 7 | combined-radix | 0.032605 | 6136 | 2624194 | 0 | 0 | 0 | 277888 | 155248 | 0.441329 | 327042 |
| 8 | combined-inline-lower-delta | 0.032682 | 5652 | 1373696 | 0 | 0 | 0 | 177217 | 155248 | 0.123967 | 327042 |
| 9 | combined-lower-only-bitset-seen | 0.032913 | 6240 | 2915072 | 2097152 | 0 | 0 | 122053 | 122053 | 0.000000 | 285564 |
| 10 | combined-bucket256 | 0.042063 | 6048 | 2624194 | 0 | 0 | 0 | 277888 | 155248 | 0.441329 | 327042 |
| 11 | combined-bitset-seen | 0.042598 | 6376 | 3470848 | 2097152 | 0 | 0 | 155248 | 155248 | 0.000000 | 327042 |
| 12 | combined-trie-pair-bitset | 0.042711 | 7868 | 3601920 | 0 | 2228224 | 0 | 155248 | 155248 | 0.000000 | 327042 |
| 13 | combined-identity-hash | 0.042843 | 5816 | 1449666 | 0 | 0 | 0 | 155248 | 155248 | 0.000000 | 327042 |
| 14 | combined-hash | 0.042954 | 5740 | 1449666 | 0 | 0 | 0 | 155248 | 155248 | 0.000000 | 327042 |
| 15 | combined-sparse-first-bitset | 0.043529 | 7680 | 3470848 | 0 | 2097152 | 0 | 155248 | 155248 | 0.000000 | 327042 |

### high_cardinality

| rank | profile | wall_s | rss_kb | scratch | bitset | first/trie bitset | grouped | pushed | unique | dup_ratio | bytes |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | combined-lower-only-bitset-seen | 0.149045 | 8504 | 12797064 | 2097152 | 0 | 0 | 56827 | 56827 | 0.000000 | 2386372 |
| 2 | combined-bitset-seen | 0.165247 | 8644 | 23488784 | 2097152 | 0 | 0 | 56887 | 56887 | 0.000000 | 2386482 |
| 3 | combined-sparse-first-bitset | 0.197520 | 6888 | 21743888 | 0 | 352256 | 0 | 56887 | 56887 | 0.000000 | 2386482 |
| 4 | combined-trie-pair-bitset | 0.220191 | 6664 | 21545616 | 0 | 153984 | 0 | 56887 | 56887 | 0.000000 | 2386482 |
| 5 | combined-case-raw | 0.291504 | 11712 | 10699912 | 0 | 0 | 0 | 13051214 | 56827 | 0.995646 | 2386382 |
| 6 | combined-identity-hash | 0.300313 | 15596 | 2713894 | 0 | 0 | 0 | 56887 | 56887 | 0.000000 | 2386482 |
| 7 | combined-lower-only | 0.311628 | 11768 | 10699912 | 0 | 0 | 0 | 13051214 | 56827 | 0.995646 | 2386372 |
| 8 | combined-inline-lower-delta | 0.313515 | 11900 | 21391632 | 0 | 0 | 0 | 13531214 | 56887 | 0.995796 | 2386482 |
| 9 | combined-grouped-buckets | 0.321161 | 12496 | 9213472 | 0 | 0 | 9175040 | 13531214 | 56887 | 0.995796 | 2386482 |
| 10 | combined-rdxsort | 0.497211 | 18236 | 24064566 | 0 | 0 | 0 | 26102428 | 56887 | 0.997821 | 2386482 |
| 11 | combined | 0.500551 | 18396 | 24064566 | 0 | 0 | 0 | 26102428 | 56887 | 0.997821 | 2386482 |
| 12 | combined-bucket256 | 0.537795 | 28768 | 45448006 | 0 | 0 | 0 | 26102428 | 56887 | 0.997821 | 2386482 |
| 13 | combined-radix | 0.543784 | 28836 | 45448006 | 0 | 0 | 0 | 26102428 | 56887 | 0.997821 | 2386482 |
| 14 | combined-rdst | 0.584400 | 18932 | 24064566 | 0 | 0 | 0 | 26102428 | 56887 | 0.997821 | 2386482 |
| 15 | combined-hash | 0.600037 | 20220 | 2713894 | 0 | 0 | 0 | 56887 | 56887 | 0.000000 | 2386482 |

### high_dup

| rank | profile | wall_s | rss_kb | scratch | bitset | first/trie bitset | grouped | pushed | unique | dup_ratio | bytes |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | combined-lower-only-bitset-seen | 0.136226 | 9160 | 11830040 | 2097152 | 0 | 0 | 53586 | 53586 | 0.000000 | 1344969 |
| 2 | combined-bitset-seen | 0.156783 | 9136 | 21554736 | 2097152 | 0 | 0 | 53826 | 53826 | 0.000000 | 1345279 |
| 3 | combined-sparse-first-bitset | 0.198515 | 7500 | 19818032 | 0 | 360448 | 0 | 53826 | 53826 | 0.000000 | 1345279 |
| 4 | combined-trie-pair-bitset | 0.219595 | 7292 | 19611696 | 0 | 154112 | 0 | 53826 | 53826 | 0.000000 | 1345279 |
| 5 | combined-case-raw | 0.238555 | 11756 | 9732888 | 0 | 0 | 0 | 11871058 | 53596 | 0.995485 | 1344989 |
| 6 | combined-identity-hash | 0.249105 | 15184 | 2472138 | 0 | 0 | 0 | 53826 | 53826 | 0.000000 | 1345279 |
| 7 | combined-lower-only | 0.269025 | 11848 | 9732888 | 0 | 0 | 0 | 11871058 | 53586 | 0.995486 | 1344969 |
| 8 | combined-grouped-buckets | 0.270772 | 12400 | 7186520 | 0 | 0 | 7151616 | 12591058 | 53826 | 0.995725 | 1345279 |
| 9 | combined-inline-lower-delta | 0.301888 | 12068 | 19457584 | 0 | 0 | 0 | 12591058 | 53826 | 0.995725 | 1345279 |
| 10 | combined-rdxsort | 0.403129 | 17796 | 21888762 | 0 | 0 | 0 | 23742116 | 53826 | 0.997733 | 1345279 |
| 11 | combined-bucket256 | 0.413442 | 27312 | 41338154 | 0 | 0 | 0 | 23742116 | 53826 | 0.997733 | 1345279 |
| 12 | combined | 0.416053 | 17728 | 21888762 | 0 | 0 | 0 | 23742116 | 53826 | 0.997733 | 1345279 |
| 13 | combined-radix | 0.510628 | 27348 | 41338154 | 0 | 0 | 0 | 23742116 | 53826 | 0.997733 | 1345279 |
| 14 | combined-rdst | 0.561816 | 18188 | 21888762 | 0 | 0 | 0 | 23742116 | 53826 | 0.997733 | 1345279 |
| 15 | combined-hash | 0.568287 | 19652 | 2472138 | 0 | 0 | 0 | 53826 | 53826 | 0.000000 | 1345279 |

### unicode

| rank | profile | wall_s | rss_kb | scratch | bitset | first/trie bitset | grouped | pushed | unique | dup_ratio | bytes |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | combined-bitset-seen | 0.052452 | 7600 | 9722104 | 2097152 | 0 | 0 | 4332 | 4332 | 0.000000 | 70312 |
| 2 | combined-sparse-first-bitset | 0.052831 | 6192 | 8247544 | 0 | 622592 | 0 | 4332 | 4332 | 0.000000 | 70312 |
| 3 | combined-lower-only-bitset-seen | 0.053134 | 7308 | 5910652 | 2097152 | 0 | 0 | 4314 | 4314 | 0.000000 | 70279 |
| 4 | combined-trie-pair-bitset | 0.063978 | 5692 | 7770488 | 0 | 145536 | 0 | 4332 | 4332 | 0.000000 | 70312 |
| 5 | combined-case-raw | 0.064187 | 9276 | 3813500 | 0 | 0 | 0 | 2326250 | 4314 | 0.998146 | 70276 |
| 6 | combined-lower-only | 0.074191 | 9344 | 3813500 | 0 | 0 | 0 | 2326250 | 4314 | 0.998146 | 70279 |
| 7 | combined-inline-lower-delta | 0.084172 | 9440 | 7624952 | 0 | 0 | 0 | 2446250 | 4332 | 0.998229 | 70312 |
| 8 | combined-identity-hash | 0.084260 | 10044 | 963105 | 0 | 0 | 0 | 4332 | 4332 | 0.000000 | 70312 |
| 9 | combined-grouped-buckets | 0.085145 | 9972 | 4370152 | 0 | 0 | 4358144 | 2446250 | 4332 | 0.998229 | 70312 |
| 10 | combined-rdxsort | 0.115502 | 13924 | 8577817 | 0 | 0 | 0 | 4652500 | 4332 | 0.999069 | 70312 |
| 11 | combined | 0.118858 | 14076 | 8577817 | 0 | 0 | 0 | 4652500 | 4332 | 0.999069 | 70312 |
| 12 | combined-bucket256 | 0.136010 | 21496 | 16200721 | 0 | 0 | 0 | 4652500 | 4332 | 0.999069 | 70312 |
| 13 | combined-rdst | 0.146509 | 14352 | 8577817 | 0 | 0 | 0 | 4652500 | 4332 | 0.999069 | 70312 |
| 14 | combined-hash | 0.157046 | 13872 | 963105 | 0 | 0 | 0 | 4332 | 4332 | 0.000000 | 70312 |
| 15 | combined-radix | 0.180330 | 21400 | 16200721 | 0 | 0 | 0 | 4652500 | 4332 | 0.999069 | 70312 |

## Profile groups

- Full bitset: combined-bitset-seen.
- Sparse bitset compromise: combined-sparse-first-bitset.
- Trie-pair bitset: combined-trie-pair-bitset.
- True non-bitset grouped arrays: combined-grouped-buckets.
- Identity-hash experiment: combined-identity-hash.
- External radix sort experiments: combined-rdxsort and combined-rdst.
- Control-only profiles: combined-case-raw, combined-lower-only, combined-lower-only-bitset-seen.

## Success criteria

- Full validation script completes.
- No CSV row has blank max_rss_kb.
- Serious profile search output matches combined on line-oriented corpora.
- Combined round trip is byte-exact for every corpus, including unicode and binaryish.
- No on-disk format change is introduced.
