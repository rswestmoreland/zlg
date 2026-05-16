# Phase 1h Locked-Stack Size Diagnosis

This is a diagnostic-only pass for the locked stack. It does not add new production candidates, change fixed-lines8192, change mesh-bigram ZBM1 v2, change the combined-bitset-seen builder, or change search behavior.

## Locked stack under diagnosis

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

## Locked profile versus gzip

| corpus | zlg_bytes | gzip_bytes | delta | payload_delta | summary_pct | payload_pct | wall_s | cpu_s | rss_kb | chunks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| binaryish | 327042 | 126894 | 200148 | -702 | 61.345638 | 38.585870 | 0.044809 | 0.040534 | 7084 | 1 |
| high_cardinality | 2386482 | 2474031 | -87549 | -150742 | 2.590298 | 97.352044 | 0.204952 | 0.203070 | 8496 | 10 |
| high_dup | 1345279 | 1455414 | -110135 | -170363 | 4.374706 | 95.523010 | 0.202541 | 0.200656 | 9112 | 10 |
| long_line_log | 1572192 | 2925542 | -1353350 | -1366746 | 0.829670 | 99.147941 | 0.490414 | 0.484899 | 31232 | 2 |
| realistic_mixed_log | 2403573 | 2152918 | 250655 | 179990 | 2.882750 | 97.060002 | 0.210170 | 0.206502 | 8608 | 10 |
| short_line_log | 1380881 | 1195190 | 185691 | 143044 | 2.896050 | 96.911609 | 0.122623 | 0.118052 | 7344 | 20 |
| unicode | 70312 | 99957 | -29645 | -35561 | 7.731255 | 91.586074 | 0.059939 | 0.055130 | 7652 | 3 |

## Component breakdown for locked profile

| corpus | total | payload | summary | chunk_headers | directory_footer | global_header |
|---|---:|---:|---:|---:|---:|---:|
| binaryish | 327042 | 126192 | 200626 | 64 | 128 | 32 |
| high_cardinality | 2386482 | 2323289 | 61817 | 640 | 704 | 32 |
| high_dup | 1345279 | 1285051 | 58852 | 640 | 704 | 32 |
| long_line_log | 1572192 | 1558796 | 13044 | 128 | 192 | 32 |
| realistic_mixed_log | 2403573 | 2332908 | 69289 | 640 | 704 | 32 |
| short_line_log | 1380881 | 1338234 | 39991 | 1280 | 1344 | 32 |
| unicode | 70312 | 64396 | 5436 | 192 | 256 | 32 |

## Worst locked-profile chunks by summary percent

| corpus | chunk | lines | uncomp | payload | summary | summary_pct | mesh_edges |
|---|---:|---:|---:|---:|---:|---:|---:|
| binaryish | 0 | 642 | 138946 | 126192 | 200626 | 61.375665 | 155248 |
| unicode | 2 | 3616 | 420532 | 11818 | 1812 | 13.232072 | 1444 |
| unicode | 0 | 8192 | 952865 | 25299 | 1812 | 6.667893 | 1444 |
| unicode | 1 | 8192 | 952859 | 27279 | 1812 | 6.215057 | 1444 |
| high_dup | 9 | 6272 | 930625 | 100828 | 5886 | 5.512371 | 5383 |
| short_line_log | 19 | 4352 | 205379 | 37163 | 1981 | 5.052540 | 1734 |
| high_dup | 1 | 8192 | 1215621 | 131446 | 5886 | 4.283968 | 5383 |
| high_dup | 3 | 8192 | 1215571 | 131517 | 5887 | 4.282451 | 5384 |
| high_dup | 7 | 8192 | 1215642 | 131394 | 5881 | 4.282105 | 5379 |
| high_dup | 5 | 8192 | 1215620 | 131510 | 5886 | 4.281973 | 5384 |

## Worst locked-profile chunks by payload ratio

| corpus | chunk | lines | uncomp | payload | summary | payload_ratio | avg_line_bytes |
|---|---:|---:|---:|---:|---:|---:|---:|
| binaryish | 0 | 642 | 138946 | 126192 | 200626 | 0.908209 | 216.426791 |
| short_line_log | 19 | 4352 | 205379 | 37163 | 1981 | 0.180948 | 47.191866 |
| high_cardinality | 4 | 8192 | 1336460 | 238206 | 6181 | 0.178237 | 163.142090 |
| high_cardinality | 6 | 8192 | 1336471 | 238190 | 6182 | 0.178223 | 163.143433 |
| high_cardinality | 3 | 8192 | 1336379 | 238055 | 6182 | 0.178134 | 163.132202 |
| high_cardinality | 8 | 8192 | 1336546 | 238075 | 6181 | 0.178127 | 163.152588 |
| high_cardinality | 0 | 8192 | 1336467 | 237954 | 6182 | 0.178047 | 163.142944 |
| high_cardinality | 2 | 8192 | 1336408 | 237878 | 6182 | 0.177998 | 163.135742 |
| high_cardinality | 5 | 8192 | 1336506 | 237873 | 6182 | 0.177981 | 163.147705 |
| high_cardinality | 7 | 8192 | 1336388 | 237825 | 6182 | 0.177961 | 163.133301 |

## Reference rows

The CSV also includes combined-sparse-first-bitset as the memory reference and combined as the historical reference baseline. These are not new production candidates in this phase.

## Success criteria

- RSS and CPU are captured for every archive row.
- gzip -6 is present for every corpus.
- Per-archive zlg component accounting is captured.
- Per-chunk payload and summary accounting is captured.
- The run does not change the active stack or on-disk format.
