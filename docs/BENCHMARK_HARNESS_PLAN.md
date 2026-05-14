# Benchmark Harness Plan

## Project gates

`zlg` must eventually prove that it can:

```text
compress plaintext logs faster than gzip
produce total .zlg files smaller than gzip output
search compressed logs faster than zgrep
avoid temp files
avoid memory exhaustion
preserve pipe behavior
```

## Phase 0h benchmark-prep stance

Phase 0h adds a lightweight benchmark-prep harness only.

It is not the final benchmark proof.

## Measurements to capture

For compression:

```text
input_name
input_bytes
policy
command
wall_seconds
output_bytes
exit_code
```

For decompression/cat:

```text
input_name
policy
command
wall_seconds
stdout_bytes_or_output_bytes
exit_code
```

For search:

```text
input_name
policy
pattern_name
pattern
engine
command
wall_seconds
match_output_bytes
exit_code
```

## Candidate chunk policies

Initial `zlg compress --chunk-policy` candidates:

```text
fixed-lines64k
progressive-lines
byte1m
byte4m
byte8m
hybrid-progressive-cap4m
hybrid-progressive-cap8m
hybrid-progressive-cap16m
hybrid-progressive-cap32m
hybrid-fixed64k-cap8m
hybrid-fixed64k-cap16m
hybrid-fixed64k-cap32m
```

## Initial pattern set

```text
literal_failed_password: failed password
alternation_error_failed_denied: error|failed|denied
quoted_key: key="[^"]+"
branch_suffix: (?:foo|bar)[0-9]
src_ip: src_ip=[0-9.]+
lookbehind_key: (?<=key=")[^"]+
no_match_literal: no_such_token_zzzz
```

## Baseline comparisons

Required when available:

```text
gzip -6
gzip -9
zgrep
plain grep against original input
```

Optional when available:

```text
rg
zstd
zstdcat
```

## Artifact policy

Benchmark scripts may write small CSV/text reports under:

```text
validation_results/
```

Do not commit:

```text
target/
compressed binaries
.zlg outputs
.gz outputs
large generated corpora
large logs
```

## Later benchmark additions

Later phases should add:

```text
peak RSS tracking
first-result latency
chunk skip counters
chunks decompressed
zstd decoded bytes
metadata overhead by chunk policy
false-positive candidate chunk rate
pipe-mode benchmarks
```
