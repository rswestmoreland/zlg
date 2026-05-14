# Phase 0m Selector and Postings Experiment

## Purpose

Phase 0m tests whether improved selector extraction and a future block-level
bigram postings design can reduce decoded bytes enough to justify search
metadata.

## Changes

- `zlg grep` now reports `selector_count` in stats JSON.
- Regex selector planning now distinguishes:
  - `literal_all` for required literals.
  - `literal_any` for safe alternation branches.
  - `none` when no safe selector is available.
- Common regex forms now have safer selectors:
  - `error|failed|denied` -> any of `error`, `failed`, `denied`.
  - `(?:foo|bar)[0-9]` -> any of `foo`, `bar`.
  - `key="[^"]+"` -> required `key="`.
  - `(?<=key=")[^"]+` -> required `key="`.
- `tools/phase0m_postings_probe.py` builds an offline block-level bigram
  postings probe over the deterministic corpus.

## Important limitation

The current `.zlg` runtime still uses chunk-level summary checks. The postings
probe is not yet the on-disk format. It estimates whether a future block-level
or postings index would reduce candidate decode regions.

## Compressed-domain search note

Searching compressed bytes directly is a known research topic called compressed
pattern matching. It is practical for some compression families and controlled
formats, but a general zstd bitstream is not laid out like a database btree or
inverted index. The safer product direction is to build an explicit queryable
sidecar/index during compression, then decompress only selected blocks for final
verification.

## Phase 0m gate

Phase 0m is accepted when:

- the validation flow passes;
- selector smoke tests prove the new selector kinds;
- the CSV artifact is committed;
- the postings probe report is produced;
- no generated binary/temp artifacts are committed.
