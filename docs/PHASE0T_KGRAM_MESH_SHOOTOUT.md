# Phase 0t - K-Gram Mesh Shootout

## Purpose

Phase 0t compares multiple implementation strategies for a k-gram graph mesh
before changing the `.zlg` format again.

The goal is to test several variants of the same strategy because the data
structure layout will strongly affect storage size, query cost, and runtime
performance.

## Variants

The offline probe compares:

- `edge_postings_bigram`
- `edge_postings_trigram`
- `sorted_edge_table_bigram`
- `sorted_edge_table_trigram`
- `path_exact_bigram`
- `path_exact_trigram`
- `rarest_edge_traversal_bigram`
- `rarest_edge_traversal_trigram`
- `hybrid_bigram_trigram`
- `per_group_mesh_bigram`
- `per_group_mesh_trigram`

## Block and group sizes

The probe tests block sizes:

- 512 lines
- 1024 lines
- 2048 lines
- 4096 lines

The probe tests group sizes:

- 16384 lines
- 65536 lines

Groups model a future layout where a larger logical group contains smaller
independently decodable search blocks plus a local mesh.

## Metrics

The probe records:

- selected blocks
- decoded byte ratio
- first selected block
- selected block span
- chosen edge count
- feature first seen block
- feature block span
- feature document frequency
- feature occurrence count
- feature density
- feature information bits
- mesh edge count
- mesh postings entries
- estimated raw index bytes
- estimated delta-varint bytes
- estimated compressed index bytes

## Status

This is still offline. It does not freeze the `.zlg` format.
The next runtime phase should serialize only the top one or two variants.
