# Phase 1c-fix - Summary Scratch Clear and Non-Bitset Ranking

## Purpose

Phase 1c found a promising duplicate-control result, especially
`combined-bitset-seen`, but the restored ZBM1 encoder missed a required
`out.clear()` call. Because summary buffers are reused across chunks, this caused
summary bytes to accumulate across chunks and made Phase 1c storage numbers
invalid.

This phase fixes that regression and reruns the same case/duplicate-control
shootout.

## Fix

`encode_bigram_mesh_edges_into` now clears the reusable output buffer before
writing the ZBM1 header and delta-varint edge stream.

## Additional reporting

The benchmark markdown now includes:

- ranked build profiles by wall time and total build time
- best non-bitset profile

The non-bitset ranking matters because `combined-bitset-seen` uses a reusable
2 MiB u24 presence table. That may be acceptable, but it should not be adopted
without comparing the second-best strategy.
