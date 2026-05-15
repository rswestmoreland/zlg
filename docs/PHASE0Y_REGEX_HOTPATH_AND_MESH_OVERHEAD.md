# Phase 0y - Regex Hot Path and Mesh Overhead Audit

## Purpose

Phase 0y keeps the narrowed strategy stack fixed:

- fixed-lines8192
- mesh-bigram
- Rust regex for default regex
- PCRE2 for `-P`
- streaming decode available for grep

The phase focuses on two optimization questions:

1. How do we reduce regex cost, especially PCRE2 cost?
2. Where exactly is the 8192 mesh-bigram storage overhead coming from?

## Source changes

Phase 0y adds hot-path counters and lightweight regex prefiltering:

- line count scanned
- fixed matcher calls
- Rust regex calls
- PCRE2 calls
- fast-path calls
- prefilter rejects

For Rust regex and PCRE2, selector literals are checked before invoking the full
regex engine. This is intended to make zlg behave more like grep/ripgrep, where
literal prefilters avoid expensive regex execution when possible.

A narrow fast path is also added for simple positive lookbehind extraction:

```text
(?<=literal)[^X]+
```

For example:

```text
(?<=key=")[^"]+
```

can be handled by finding `key="` and scanning until the next quote, avoiding
PCRE2 for that common form.

## Mesh overhead accounting

The benchmark parses the generated `.zlg` file and splits size into:

- total zlg bytes
- compressed payload bytes
- mesh summary bytes
- chunk header bytes
- directory/footer bytes
- chunk count

This helps determine whether the next storage work should target summary bytes,
headers, compressed payload, or footer/directory layout.

## Benchmark scope

Only this zlg candidate is benchmarked:

```text
fixed-lines8192 mesh-bigram
```

Baselines:

- original/plain grep
- gzip -6
- gzip -dc
- zgrep

The report should show whether literal prefiltering and the lookbehind fast path
reduce PCRE2 calls and wall time.
