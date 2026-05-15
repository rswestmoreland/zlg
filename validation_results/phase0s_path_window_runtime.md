# zlg Phase 0s path-window runtime probe

This probe exercises an experimental runtime summary mode:

```text
zlg compress --summary-mode path-window --chunk-policy fixed-lines512
```

The generated corpus and .zlg files are temporary. Only this compact report
and CSV should be committed.

## Corpus

- Lines: 125000
- Input bytes: 9223684
- Input sha256: fea507e974d3f1bd542665e11e2d93e07c155b670f53b9d5874dce74a3c50c5e
- Needle IP: 198.18.99.123
- Needle line: 100001
- Needle line ratio: 0.800

## Results

| policy | summary_mode | zlg_bytes | compress_s | grep_s | chunks_total | chunks_decoded | decoded_ratio | gzip6_bytes |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fixed-lines512 | path-window | 35670345 | 0.865311 | 0.185386 | 245 | 1 | 0.004134 | 839949 |
| fixed-lines1024 | path-window | 29049485 | 0.812577 | 0.173263 | 123 | 1 | 0.008222 | 839949 |
| fixed-lines512 | bitmap | 4809053 | 0.153036 | 0.022966 | 245 | 57 | 0.233427 | 839949 |
| fixed-lines1024 | bitmap | 2738625 | 0.141914 | 0.029493 | 123 | 57 | 0.466813 | 839949 |
| fixed-lines1024 | none | 714537 | 0.066866 | 0.046189 | 123 | 123 | 1.000000 | 839949 |
| fixed-lines512 | none | 777333 | 0.070216 | 0.046961 | 245 | 245 | 1.000000 | 839949 |
