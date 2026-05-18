# Command reference

## Global commands

```text
zlg help [command]
zlg version [-l|--long]
```

## compress

```text
zlg compress [options] <input.log> <output.zlg>
```

Common options:

```text
-m, --mode <none|fast|standard|best>
-y, --force
```

Examples:

```bash
zlg compress app.log app.log.zlg
zlg compress -m fast app.log app.log.zlg
zlg compress --mode standard app.log app.log.zlg --force
```

## cat and decompress

```text
zlg cat [options] <input.zlg>
zlg decompress [options] <input.zlg>
```

Common options:

```text
-o, --output <path>
-y, --force
```

Examples:

```bash
zlg cat app.log.zlg
zlg cat app.log.zlg -o app.log
zlg decompress app.log.zlg --output app.log --force
```

## grep

```text
zlg grep [options] <pattern> <input.zlg>...
```

Search options:

```text
-r, --regex                  regex search, default matcher
-f, --fixed                  fixed-string search
-p, --pcre2                  PCRE2 regex mode
-i, --ignore-case
-v, --invert-match
-c, --count
-n, --line-number
-g, --paths                  print only matching input paths
-m, --head <n>               stop after n matching lines
-s, --strict                 verify candidate chunks before output
```

Extraction and top options:

```text
-e, --extract
-t, --top
-l, --limit <n>
-a, --cap <n>
-b, --truncate <bytes>
-j, --json
```

Examples:

```bash
zlg grep -r 'error|warn|fail' app.log.zlg
zlg grep -f 'literal needle' app.log.zlg
zlg grep -p '(?<=status=)[a-z]+' app.log.zlg
zlg grep --extract --top 'status=[a-z]+' app.log.zlg
zlg grep --pcre2 --extract --top --json '(?<=src_ip=)[0-9.]+' firewall.zlg
```

`--top` requires `--extract`. If `--cap` is exceeded, zlg exits with an error and emits no top results.

## head and tail

```text
zlg head [-n|--lines <n>] <input.zlg>
zlg tail [-n|--lines <n>] <input.zlg>
```

Examples:

```bash
zlg head -n 20 app.log.zlg
zlg tail -n 100 app.log.zlg
```

## test

```text
zlg test [options] <input.zlg>
```

Options:

```text
-j, --json
-q, --quiet
```

## info and stats

```text
zlg info [-j|--json] <input.zlg>
zlg stats [-j|--json] <input.zlg>
```

`info` focuses on archive layout. `stats` focuses on content and storage ratios.

## convert

```text
zlg convert [options] <compressed-input> [output.zlg]
```

Options:

```text
-m, --mode <none|fast|standard|best>
-y, --force
```

Supported inputs:

```text
.zst  internal zstd support
.gz   gzip -dc helper
.bz2  bzip2 -dc helper
.xz   xz -dc helper
```

Examples:

```bash
zlg convert app.log.zst
zlg convert app.log.gz
zlg convert app.log.bz2
zlg convert app.log.xz
zlg convert app.log.gz app-archive.zlg -m fast
```

Plain logs should use `zlg compress`.
