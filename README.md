# zlg

`zlg` (pronounced "z-log") is a Linux command-line tool for compressed log archives that can still be searched quickly. It stores logs in `.zlg` files using zstd-backed chunks plus compact per-chunk search metadata, so common log workflows such as `grep`, `head`, `tail`, `stats`, and extraction-based top counts can work without fully decompressing the archive first.

The name comes from "zstd log" / "z-log". The command is `zlg`; the archive extension is `.zlg`.

> Status: pre-1.0. The CLI is usable, but the `.zlg` file format is still experimental and should not be treated as frozen yet.

## Why zlg?

Traditional compressed logs are small, but searching them often means streaming the whole compressed file through `zgrep` or `gzip -dc | grep`. `zlg` keeps the storage benefit of compression while adding chunk summaries and a footer directory so it can skip irrelevant chunks, seek efficiently for `tail`, and report archive layout stats quickly.

In the current benchmark snapshot, `zlg` showed three practical advantages:

- **Smaller than gzip** in tested log corpora.
- **Much faster than zgrep** for compressed search.
- **Fast head/tail on compressed archives** because zlg can seek by chunk metadata instead of streaming the entire gzip file.

## Quick examples

Compress a log:

```bash
zlg compress app.log -o app.log.zlg
zlg compress app.log -o app.log.zlg -m fast
```

Search an archive:

```bash
zlg grep 'status=failed' app.log.zlg
zlg grep -f 'literal needle' app.log.zlg
zlg grep -p '(?<=status=)[a-z]+' app.log.zlg
```

Extract and rank matching values without a shell pipeline:

```bash
zlg grep -te 'status=[a-z]+' app.log.zlg
zlg grep -pte '(?<=src_ip=)[0-9.]+' firewall.zlg
zlg grep -te --limit 10 --cap 100000 --truncate 1000 'user=[^ ]+' auth.zlg
zlg grep -te --json 'status=[a-z]+' app.log.zlg
```

Inspect an archive:

```bash
zlg stats app.log.zlg
zlg info app.log.zlg
zlg test app.log.zlg
```

Read the beginning or end of a compressed archive:

```bash
zlg head -n 20 app.log.zlg
zlg tail -n 100 app.log.zlg
```

Convert already-compressed logs into `.zlg`:

```bash
zlg convert app.log.zst
zlg convert app.log.gz
zlg convert app.log.bz2
zlg convert app.log.xz
zlg convert app.log.gz app-archive.zlg -m fast
```

Plain logs should use `zlg compress`; `zlg convert` is for already-compressed inputs.

## How the file format works

A `.zlg` file is a sequence of independent, line-aligned chunks followed by a seekable directory and footer.

```text
+------------------------------+
| Global header                |
+------------------------------+
| Chunk 0 header               |
|   line range and byte counts |
|   CRC of uncompressed bytes  |
|   compression mode           |
+------------------------------+
| Chunk 0 ZBM1 summary         |  compact mesh-bigram search summary
+------------------------------+
| Chunk 0 payload              |  zstd-compressed or stored bytes
+------------------------------+
| Chunk 1 header               |
| Chunk 1 ZBM1 summary         |
| Chunk 1 payload              |
+------------------------------+
| ...                          |
+------------------------------+
| Directory                    |  chunk offsets, lengths, line counts
+------------------------------+
| Footer                       |  totals and directory location
+------------------------------+
```

The default chunk policy is currently `fixed-lines8192-cap8m`: up to 8,192 lines per chunk, with an 8 MiB byte cap. Each chunk has an independent payload and a compact ZBM1 mesh-bigram summary. During search, zlg derives selectors from the pattern, checks chunk summaries first, and decodes only candidate chunks. This is what lets a deep "needle in a haystack" search skip most of the archive.

The footer directory stores chunk locations and counts, which makes commands like `tail`, `info`, and `stats` efficient on file-backed archives.

## Compression modes

```text
none      store payloads uncompressed inside .zlg chunks
fast      zstd level 3
standard  zstd level 6, current default
best      zstd level 8
```

Use `-m, --mode` on commands that create `.zlg` archives.

`fast` is a strong candidate for operational ingest workloads. `standard` remains the default for now because it gives better compression. The mode names and default may change before a stable format release.

## Search, extract, and top

`zlg grep` uses the same archive-aware search path for normal search, extraction, and top aggregation.

Useful grep options:

```text
-f, --fixed                  fixed-string search
-p, --pcre2                  PCRE2 regex mode
-e, --extract                print extracted matches
-t, --top                    count and rank extracted matches
-l, --limit <n>              top rows to show, default 20
-a, --cap <n>                distinct extracted-value cap, default 100000
-r, --truncate <bytes>       truncate extracted values before counting/display
-j, --json                   JSON output for top aggregation
-g, --paths                  print only matching input paths
-m, --head <n>               stop after n matching lines
-s, --strict                 verify candidate chunks before output
```

`--top` requires `--extract`. If `--cap` is exceeded, zlg exits with an error and emits no top results because the result would be incomplete. Extracted values are truncated to 1,000 bytes by default before counting and display.

Top output uses `Rank`, `Count`, `Percent`, and `Value`:

```text
Top extracted matches
=====================

Pattern           status=[a-z]+
Total matches     80,000
Unique values          3
Limit                 20
Cap              100,000
Truncate bytes     1,000

Rank  Count       Percent  Value
1         40,000   50.00%  status=failed
2         30,000   37.50%  status=denied
3         10,000   12.50%  status=timeout
```

Shell quoting matters. Use single quotes for static patterns and double quotes when you want the shell to expand variables:

```bash
zlg grep -te 'status=[a-z]+' app.log.zlg
STATUS='failed|denied'
zlg grep -pte "status=(${STATUS})" app.log.zlg
```

## Stats example

`zlg stats` is intended to be readable in a terminal screenshot, while `zlg stats -j` is intended for scripts.

```text
zlg archive stats
=================

Content
  Lines                        120,000
  Uncompressed bytes           14.97 MiB
  Chunks                       15
  Avg lines/chunk              8000.0
  Avg raw bytes/chunk          1.00 MiB

Storage
  Archive bytes                945.14 KiB
  Payload bytes                802.27 KiB
  Payload share                84.88%
  Summary bytes                139.70 KiB
  Summary share                14.78%
  Directory bytes              1.02 KiB
  Directory share              0.11%
  Metadata share               14.89%
  Compression ratio            16.22:1
  Archive/raw size             6.17%

Format
  Compression mode             standard
  Chunk policy                 fixed-lines8192-cap8m
  Format version               1
  Metadata source              seekable
```

## Benchmark snapshot

These results come from the repeated-median benchmark artifacts in `validation_results/phase2i_repeated_median_smoke.md`. They are intended as a smoke-test snapshot, not a universal guarantee. Absolute timings vary by CPU, storage, kernel, and host load.

### Build and storage

| Scenario | Backend | Archive bytes | Median build time |
|---|---:|---:|---:|
| Repeated regex log | gzip -6 | 1,233,402 | 0.212365s |
| Repeated regex log | zlg fast | 1,185,857 | 0.131995s |
| Repeated regex log | zlg standard | 967,824 | 0.242521s |
| Large needle log | gzip -6 | 14,936,213 | 1.809784s |
| Large needle log | zlg fast | 14,807,773 | 1.567921s |
| Large needle log | zlg standard | 12,945,933 | 2.369447s |

### Search

| Scenario | Backend | Median search time | Matches |
|---|---:|---:|---:|
| Repeated regex log | plain grep | 0.047857s | 80,000 |
| Repeated regex log | zgrep | 0.112281s | 80,000 |
| Repeated regex log | zlg fast | 0.053496s | 80,000 |
| Repeated regex log | zlg standard | 0.054473s | 80,000 |
| Large needle log | plain grep | 0.073980s | 1 |
| Large needle log | zgrep | 0.664595s | 1 |
| Large needle log | zlg fast | 0.020609s | 1 |
| Large needle log | zlg standard | 0.019749s | 1 |

On the large needle test, zlg was faster than plain grep because the search metadata let it skip most chunks. On dense-match regex workloads, zlg stayed close to plain grep while searching compressed archives.

### Head and tail on compressed archives

| Scenario | Operation | gzip stream | zlg fast | zlg standard |
|---|---|---:|---:|---:|
| Repeated regex log | head | 1.874999s | 0.020026s | 0.020521s |
| Repeated regex log | tail | 2.066998s | 0.018484s | 0.017699s |
| Large needle log | head | 1.946713s | 0.020467s | 0.019655s |
| Large needle log | tail | 2.555441s | 0.010081s | 0.010744s |

## Convert helper behavior

`zlg convert` uses internal zstd support for `.zst` input. For common Linux compressed files, it uses helper programs from `PATH`:

```text
.gz   gzip -dc
.bz2  bzip2 -dc
.xz   xz -dc
```

Helpers are invoked directly, not through a shell. If a helper is missing, zlg reports that the format is unsupported in the current environment. This keeps the binary lean while covering common compressed log formats.

## Install from source

```bash
git clone https://github.com/rswestmoreland/zlg.git
cd zlg
cargo build --release
install -Dm755 target/release/zlg "$HOME/.local/bin/zlg"
```

Check the install:

```bash
zlg version
zlg version --long
```

More install and release notes are in `docs/INSTALL.md` and `docs/RELEASE_CHECKLIST.md`.

## Documentation

- `docs/COMMAND_REFERENCE.md` - command and option reference
- `docs/INSTALL.md` - install and uninstall notes
- `docs/ROADMAP.md` - current roadmap
- `docs/BENCHMARK_MEASUREMENT_RELIABILITY.md` - benchmark measurement notes
- `docs/man/zlg.1` - draft man page

## License

Dual licensed under MIT OR Apache-2.0.

See `LICENSE`, `LICENSE-MIT`, and `LICENSE-APACHE`.

## Author

Richard S. Westmoreland

`dev@rswestmore.land`
