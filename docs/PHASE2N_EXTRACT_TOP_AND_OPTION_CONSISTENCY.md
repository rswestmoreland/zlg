# Phase 2n - Extract/top aggregation and option consistency

Phase 2n adds a grep-integrated top aggregation workflow and cleans up the public option shape before release.

## Design intent

`zlg` should not become a parser, a field engine, or a general log analytics system. The first top-style feature is limited to extracted search matches:

```text
zlg grep -e -t PATTERN file.zlg
zlg grep --extract --top PATTERN file.zlg
```

This replaces the shell pipeline shape:

```text
zlg grep -e PATTERN file.zlg | sort | uniq -c | sort -nr | head
```

The zlg implementation keeps the optimized grep path, including summary-first chunk skipping, then counts extracted values internally.

## Public option convention

Every public option should have a lowercase short form and a lowercase long form where practical. Uppercase short options remain disallowed.

Core grep options:

```text
-f, --fixed
-p, --pcre2
-e, --extract
-t, --top
-l, --limit <n>
-a, --cap <n>
-r, --truncate <bytes>
-j, --json
-s, --strict
-m, --head <n>
-n, --line-number
-i, --ignore-case
-c, --count
-v, --invert-match
-g, --paths
-u, --no-filename
-w, --with-filename
```

`-h` is reserved by the CLI help system, so grep uses `-m, --head` for the head-style early stop option.

Stacked short flags should work for boolean flags, for example:

```text
zlg grep -te 'status=[a-z]+' app.zlg
zlg grep -pte '(?<=status=)[a-z]+' app.zlg
zlg grep -se 'status=[a-z]+' app.zlg
```

## Extract mode

`-e, --extract` replaces the earlier pre-release `-o, --only-matching` spelling.

Examples:

```text
zlg grep -e 'status=[a-z]+' app.zlg
zlg grep --extract 'src_ip=[0-9.]+' firewall.zlg
```

## Top aggregation

`-t, --top` aggregates extracted matches.

Rules:

- `--top` requires `-e, --extract`.
- `--top` emits aggregate output only, not normal grep lines.
- `--top` rejects incompatible output modes such as count, paths, line-number, and invert-match.
- Default grep remains streaming and low-latency.
- `--strict` still verifies candidate chunks before output or aggregation.
- Sorting is deterministic: count descending, then value ascending.

Defaults:

```text
--limit 20
--cap 100000
--truncate 1000
```

If `--cap` is exceeded, zlg exits with an error and emits no top results because the aggregate would be incomplete.

Values longer than `--truncate` bytes are truncated before counting/display and are marked as truncated. This bounds memory usage and avoids huge accidental captures.

## Text output

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

## JSON output

```json
{
  "pattern": "status=[a-z]+",
  "total_matches": 80000,
  "unique_values": 3,
  "limit": 20,
  "cap": 100000,
  "truncate": 1000,
  "items": [
    {
      "rank": 1,
      "count": 40000,
      "percent": 50.0,
      "value": "status=failed",
      "truncated": false
    }
  ]
}
```

## Shell quoting guidance

zlg receives the pattern after the shell has processed quotes. Use single quotes for static patterns and double quotes when shell variable interpolation is intended.

```bash
zlg grep -te 'status=[a-z]+' app.zlg
STATUS='failed|denied'
zlg grep -pte "status=(${STATUS})" app.zlg
```

## Out of scope for this phase

Do not implement:

- standalone `zlg top`
- top lines
- top tokens
- top fields
- parser behavior
- field extraction semantics
- `--left`, `--right`, or `--trim`


## Future cleanup

Phase 2n increased grep pipeline complexity. The current code has scoped clippy allows on a few grep helper functions for argument count. A later cleanup should introduce a `GrepContext` or `GrepPipelineContext` to group runtime pipeline state and keep helper signatures small. This should be a behavior-preserving refactor after Phase 2 closure.
