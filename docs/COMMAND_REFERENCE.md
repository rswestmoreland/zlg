# zlg Command Reference

This reference documents the current pre-1.0 command surface.

## Global shape

```text
zlg <command> [options]
```

Commands:

```text
help
version
compress
decompress
cat
grep
head
tail
test
info
stats
convert
```

Standalone `zlg top` is deferred. Top aggregation is currently available through `zlg grep -e -t`.

## Compression modes

```text
none      store payloads uncompressed inside .zlg chunks
fast      zstd level 3
standard  zstd level 6, current default
best      zstd level 8
```

Use `-m, --mode` where compression mode is supported.

## zlg version

```text
zlg version
zlg version -l
zlg version --long
```

Shows concise or long version/build/default information.

Options:

```text
-l, --long
```

## zlg compress

```text
zlg compress [input.log] -o output.zlg
zlg compress [input.log] -o output.zlg -m fast
zlg compress [input.log] -o output.zlg -y
```

Options:

```text
-o, --output <path>
-m, --mode <none|fast|standard|best>
-y, --force
```

Behavior:

- Reads stdin when input is omitted.
- Refuses to overwrite output unless `-y, --force` is used.
- Keeps the locked default chunking and summary stack.

## zlg decompress

```text
zlg decompress input.zlg -o output.log
zlg decompress input.zlg -o output.log -y
```

Options:

```text
-o, --output <path>
-y, --force
```

Alias behavior:

- `decompress` and `cat` share the same core output path.

## zlg cat

```text
zlg cat input.zlg
zlg cat input.zlg -o output.log
zlg cat input.zlg -o output.log -y
```

Options:

```text
-o, --output <path>
-y, --force
```

## zlg grep

```text
zlg grep 'pattern' input.zlg
zlg grep -f 'literal' input.zlg
zlg grep -p '(?<=status=)[a-z]+' input.zlg
zlg grep -e 'status=[a-z]+' input.zlg
zlg grep -te 'status=[a-z]+' input.zlg
zlg grep -pte '(?<=status=)[a-z]+' input.zlg
zlg grep -g 'error' input.zlg
zlg grep -s 'pattern' input.zlg
```

Options:

```text
-f, --fixed                  fixed-string search
-p, --pcre2                  PCRE2 regex mode
-e, --extract                print extracted matches
-t, --top                    aggregate extracted matches
-l, --limit <n>              top output rows, default 20
-a, --cap <n>                distinct extracted-value cap, default 100000
-r, --truncate <bytes>       truncate extracted values before counting/display
-j, --json                   JSON output for top aggregation
-n, --line-number            print line numbers
-i, --ignore-case            case-insensitive search
-c, --count                  print match count
-g, --paths                  print only input paths with at least one match
-v, --invert-match           invert line match
-u, --no-filename            suppress filename prefix
-w, --with-filename          force filename prefix
-m, --head <n>               stop after n matching lines
-s, --strict                 verify candidate chunk before emitting output
```

Rules:

- `-f, --fixed` and `-p, --pcre2` are mutually exclusive.
- `-t, --top` requires `-e, --extract`.
- `--top` emits aggregate output only, not normal match lines.
- If `--cap` is exceeded, zlg exits with an error and emits no trusted top results.
- `--strict` is opt-in. Default grep remains streaming and low-latency.
- Stacked boolean flags such as `-te`, `-pte`, and `-se` are supported by the CLI parser.

Shell quoting examples:

```bash
zlg grep -te 'status=[a-z]+' app.zlg
STATUS='failed|denied'
zlg grep -pte "status=(${STATUS})" app.zlg
```

Use single quotes for static shell patterns and double quotes when shell variable interpolation is intended.

## zlg head

```text
zlg head input.zlg
zlg head -n 25 input.zlg
```

Options:

```text
-n, --lines <n>
```

## zlg tail

```text
zlg tail input.zlg
zlg tail -n 100 input.zlg
```

Options:

```text
-n, --lines <n>
```

File-backed `tail` uses archive metadata to decode only selected trailing chunks.

## zlg test

```text
zlg test input.zlg
zlg test -j input.zlg
zlg test -q input.zlg
```

Options:

```text
-j, --json
-q, --quiet
```

Behavior:

- Validates archive structure and chunk integrity.
- File-backed input checks metadata totals against decoded totals.
- `--json` and `--quiet` are mutually exclusive.

## zlg info

```text
zlg info input.zlg
zlg info -j input.zlg
```

Options:

```text
-j, --json
```

Shows format, archive, and layout metadata.

## zlg stats

```text
zlg stats input.zlg
zlg stats -j input.zlg
```

Options:

```text
-j, --json
```

Shows content, storage, and format stats. JSON output is intended for scripts.

## zlg convert

```text
zlg convert input.log.zst
zlg convert input.log.gz
zlg convert input.log.bz2
zlg convert input.log.xz
zlg convert input.log.gz output.zlg
zlg convert input.log.xz output.zlg -m fast
zlg convert input.log.bz2 output.zlg -y
```

Options:

```text
-m, --mode <none|fast|standard|best>
-y, --force
```

Rules:

- `convert` is for already-compressed inputs only.
- Plain logs should use `zlg compress`.
- There is no `-o` or `--output` option.
- If output is omitted, the final extension is replaced with `.zlg`.
- `.zst` uses the existing internal zstd decoder.
- `.gz` uses `gzip -dc` from PATH.
- `.bz2` uses `bzip2 -dc` from PATH.
- `.xz` uses `xz -dc` from PATH.
- Helpers are invoked directly without a shell.
