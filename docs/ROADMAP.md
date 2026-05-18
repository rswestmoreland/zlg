# Roadmap

## Current focus

zlg currently has the core command surface in place:

```text
compress, decompress, cat, grep, head, tail, test, info, stats, convert
```

`grep --extract --top` provides the first extraction aggregation workflow without making zlg a parser or a general log analytics engine.

## Near-term work

- Validate release packaging on a clean Linux environment.
- Improve command error messages and exit-code consistency.
- Keep benchmark snapshots reproducible and easy to refresh.
- Add man-page packaging if release artifacts include manuals.
- Review whether shell completions are worth adding.

## Later work

- Larger benchmark corpora and multi-GB validation.
- More realistic logs: auth, web, firewall, JSON, high-cardinality, and Unicode-heavy logs.
- Optional parallel compression pipeline exploration.
- Optional embedded decoder measurement for gzip, bzip2, and xz.
- Possible standalone `zlg top` only if there is a narrow, non-parser use case.
- Possible default compression-mode change if `fast` remains the best operational default.

## Explicitly out of scope for now

- Full log parsing.
- Field-aware analytics.
- Top tokens, top fields, or semantic log understanding.
- Broad Unix-clone behavior.
- Async worker pools.
- Embedded gzip/bzip2/xz decoders in the default binary.
