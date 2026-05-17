# Benchmark Measurement Reliability

This document records the required approach for zlg benchmark resource measurement so future sessions do not repeatedly lose CPU and RSS data.

## Required metrics

Every benchmark row that runs a real command must include:

```text
wall_seconds
user_seconds
system_seconds
cpu_percent
max_rss_kb
exit_code
```

Rows with blank CPU or RSS fields are invalid unless the script is explicitly run with an allow-missing option and the validation log says why metrics were unavailable.

## Preferred Linux measurement path

Use Python `os.wait4()` for benchmark scripts on Linux and POSIX systems where it is available.

The preferred sequence is:

1. Start the command with `subprocess.Popen`.
2. Redirect stdout to the expected output file.
3. Redirect stderr to a sidecar text file.
4. Wait with `os.wait4(pid, 0)`.
5. Capture wall time with `time.perf_counter()` around the process lifetime.
6. Use the returned `rusage` object for:
   - `ru_utime` as user CPU seconds
   - `ru_stime` as system CPU seconds
   - `ru_maxrss` as maximum resident set size in KB on Linux
7. Compute CPU percent as:

```text
(user_seconds + system_seconds) / wall_seconds * 100
```

This avoids depending only on parsing `/usr/bin/time -v`, which has varied across prior environments and has repeatedly produced blank CPU/RSS fields.

## GNU time role

`/usr/bin/time -v` may still be used as an optional cross-check artifact, but it must not be the only source for required metrics.

Reasons:

- Some environments use shell built-in `time` instead of GNU time.
- Output labels can vary.
- Parsing can fail silently.
- Pipeline commands can complicate which process is measured.
- Prior zlg sessions repeatedly produced blank `user_seconds`, `system_seconds`, `cpu_percent`, and `max_rss_kb` fields when relying on parsing alone.

## Pipelines

For gzip head/tail comparisons, scripts may use a shell pipeline such as:

```text
gzip -dc file.gz | tail -n 10
```

When the shell is launched as the direct child and waited with `os.wait4()`, Linux resource accounting covers the waited child. This is sufficient for smoke-bench comparison. For deeper profiling, avoid shell pipelines and build an explicit process tree with separate accounting.

## Validation policy

Benchmark scripts should validate CSV rows before exiting successfully:

- no blank wall/user/system/CPU/RSS fields for real command rows
- exit code is zero
- output hashes match across equivalent backends
- generated logs, `.gz`, `.zlg`, and command outputs remain in a temporary directory
- only compact CSV/Markdown/text summaries are written under `validation_results/`

If required tools such as `gzip`, `zgrep`, `head`, or `tail` are missing, the script should fail clearly or the validation log should state that the comparison could not run. It must not report a successful three-way comparison with missing dependencies.

## Recommended output fields

Use this core CSV shape for performance smoke benches:

```text
scenario,backend,operation,pattern_type,storage_bytes,wall_seconds,user_seconds,system_seconds,cpu_percent,max_rss_kb,exit_code,output_bytes,output_sha256,match_count,parity,measurement_source,command
```

The `measurement_source` field should be `os.wait4` when the required resource metrics were captured by the preferred path.
