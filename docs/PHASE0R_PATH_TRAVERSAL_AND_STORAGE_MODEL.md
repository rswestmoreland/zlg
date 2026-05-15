# Phase 0r - Path Traversal and Storage Model

## Purpose

Phase 0r tests a stronger index-planning idea than independent k-gram
membership.

Earlier probes showed that independent bigram/trigram evidence can be too weak
for IP-like needles because grams can be distributed across unrelated lines in
the same block. Phase 0r adds path-aware traversal variants.

## Variants

The offline probe compares:

- `bigram_all_membership`
- `trigram_all_membership`
- `fourgram_all_membership`
- `bigram_path_traversal`
- `trigram_path_traversal`
- `fourgram_path_traversal`
- `literal_exact_scan`
- `rarest_window_4`
- `rarest_window_6`
- `rarest_window_8`
- `rarest_window_12`

## What path traversal means

For a literal such as:

```text
198.18.99.123
```

A bigram path is:

```text
19 -> 98 -> 8. -> .1 -> 18 -> 8. -> .9 -> 99 -> 9. -> .1 -> 12 -> 23
```

The path must reconstruct the literal contiguously. This is stronger than asking
whether all bigrams exist somewhere in the block.

## Added planner fields

The probe records:

- first selected block
- last selected block
- selected block span
- feature first seen block
- feature last seen block
- feature block span
- feature block document frequency
- feature occurrence count
- feature density
- feature information bits
- estimated raw index bytes
- estimated delta-varint bytes
- estimated compressed index bytes

These fields are early ingredients for a future weighted query planner.

## Storage model

Storage estimates are heuristic. They are not final on-disk format sizes.

The goal is to compare the relative cost of variants and to identify which
features deserve a real serialized footer experiment later.

## Expected result

For the exact needle IP at 80 percent of the corpus, path/window strategies
should ideally select one or a small number of blocks while retaining the
needle block.
