# Phase 0z - Mesh-Bigram Summary Optimization

## Purpose

Phase 0z keeps the current winning strategy and optimizes only the mesh-bigram
summary representation and build path.

Current winning stack:

```text
fixed-lines8192
mesh-bigram
streaming grep
Rust regex by default
PCRE2 for -P
literal prefiltering
positive-lookbehind fast path
--head / --max-count early stop
```

Phase 0y-fix showed the fixed-lines8192 `.zlg` component split:

```text
total:              617291 bytes
compressed payload: 514915 bytes
mesh summary:       100232 bytes
chunk headers:        1024 bytes
directory/footer:     1088 bytes
chunk count:             16
```

The largest non-payload component is the mesh summary, so this phase targets
summary bytes and compression/build time.

## Optimization

The previous `ZBM1` mesh-bigram summary stored every sorted unique packed
24-bit edge in a 32-bit little-endian slot:

```text
edge bytes per entry: 4
```

Phase 0z changes newly written `ZBM1` summaries to version 2:

```text
magic:   ZBM1
version: 2
count:   number of sorted unique edges
payload: delta-varint encoded u24 edge values
```

The decoder keeps support for version 1 summaries so older local test artifacts
can still be read during development.

## Build-path cleanup

The edge collector now uses indexed byte access for 3-byte edge packing instead
of the generic window iterator.

## Expected result

Success is measured by the same benchmark matrix as Phase 0y-fix:

- total `.zlg` size
- compressed payload bytes
- mesh summary bytes
- chunk headers
- directory/footer
- compression time
- decompression time
- stream/full grep times
- hot-path counters

Desired result:

```text
mesh summary bytes below 100232
total .zlg size still below gzip -6
search wins over zgrep preserved
compression/build time no worse, ideally improved
```

## Scope

This phase does not add async, new candidates, trigram, bitmap, path-window,
rare-window, per-group mesh, or a format freeze.
