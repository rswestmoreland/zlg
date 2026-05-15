# Phase 0u - Sorted Bigram Mesh Runtime Prototype

## Purpose

Phase 0u drops the losing experimental candidates and focuses on the current
winner from the corrected mesh shootout: a compact bigram-edge mesh.

This phase validates storage efficiency and runtime behavior against existing
baselines:

- no-index zlg
- bitmap zlg
- gzip -6
- zgrep when available

## Runtime shape

This checkpoint adds an experimental summary mode:

```text
--summary-mode mesh-bigram
```

It serializes a sorted per-search-block table of unique bigram edges. A bigram
edge is equivalent to a contiguous 3-byte path:

```text
ab -> bc means abc exists
```

The summary stores packed 24-bit edge values in sorted order. Query planning
checks selector literals by requiring their contiguous 3-byte path edges to be
present before decompressing a candidate block. The real matcher still verifies
every candidate after decompression.

## Scope

This is still not a final format freeze. The index is stored as a compact
per-block summary first so we can validate size and runtime quickly. If this
wins, the next phase can move the same sorted-edge idea into a footer-oriented
layout with delta-varint postings.

## Tested search blocks

The probe tests:

- fixed-lines1024
- fixed-lines2048
- fixed-lines64k

## Metrics

The probe records:

- total output bytes
- overhead versus no-index zlg
- compression time
- grep time
- chunks total
- chunks skipped
- chunks decoded
- decoded bytes
- decoded ratio
- gzip -6 size/time when available
- zgrep time when available

## Expected interpretation

A good candidate should:

- remain smaller than gzip -6
- add far less overhead than bitmap and path-window
- decode fewer chunks than no-index
- beat zgrep for the needle query if possible
- avoid the huge storage blowup of Phase 0s path-window summaries
