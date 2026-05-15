# Phase 0s - Path/Window Runtime Prototype

## Purpose

Phase 0s moves the strongest Phase 0r idea into the runtime prototype without
freezing the final `.zlg` format.

It adds an experimental summary mode:

```text
--summary-mode path-window
```

and small fixed-line search block policies:

```text
--chunk-policy fixed-lines512
--chunk-policy fixed-lines1024
```

## Experimental runtime idea

During compression, each search block records hashed contiguous byte windows of
length 6, 8, and 12.

During grep, selector literals use their longest available window size:

- 12-byte windows for literals of length 12 or more
- 8-byte windows for literals of length 8 to 11
- 6-byte windows for literals of length 6 to 7
- no summary filtering for shorter literals

A block is a candidate only if all windows from the selector are present in the
block summary. Candidate blocks are still decompressed and verified by the real
matcher.

## Why this is not a final format

The path-window summary currently stores sorted hash values inline per block.
This is useful for proving runtime behavior, but it may not be the final storage
layout. Future variants may use:

- footer postings
- delta-varint block IDs
- compressed index sections
- rare-window-only indexes
- token/value-aware postings

## Expected result

For a fixed-string needle such as:

```text
198.18.99.123
```

with 512-line search blocks, path-window summaries should decode one or a small
number of blocks instead of the whole corpus.

## Tradeoff

Small independently compressed search blocks may hurt compression ratio. That is
acceptable in this phase if the indexed `.zlg` output remains competitive with
gzip and produces a search advantage for selective literals.
