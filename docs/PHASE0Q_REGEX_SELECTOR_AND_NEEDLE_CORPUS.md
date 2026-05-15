# Phase 0q - Regex Selector Gap and Needle Corpus

## Purpose

Phase 0q fixes the offline regex selector gap for positive lookbehind patterns
and adds a deterministic needle-in-haystack sample-data probe.

## Compression block-size tradeoff

Smaller independently compressed blocks, such as 512-line blocks, can improve
search selectivity because the index can point to a smaller decompression unit.
The tradeoff is that compression ratio may get worse because zstd has less
history per independent block and more frame/header overhead.

This is not a reason to stop the experiment. It means the next runtime design
should compare:

- 512-line independently decodable search blocks
- 1024-line independently decodable search blocks
- larger logical groups for directory/index organization
- optional zstd dictionaries for small independent blocks
- total indexed `.zlg` size versus gzip, not only versus no-index `.zlg`

The failure criterion remains whether indexed `.zlg` loses against equivalent
gzip/zgrep baselines without enough search benefit.

## Regex selector fix

The offline selector now accepts escaped literal characters inside positive
lookbehind selectors. This lets a pattern such as:

```text
(?<=key=\")[^\"]+
```

use this safe selector:

```text
key="
```

The real matcher must still verify results after decode.

## Needle corpus

The new probe creates deterministic sample data where this IP appears exactly
once, around 80 percent into the log volume:

```text
198.18.99.123
```

The generated corpus is not committed. Only compact result artifacts are saved.

## Output artifacts

Phase 0q should produce:

- `validation_results/phase0q_needle_probe.csv`
- `validation_results/phase0q_needle_probe.md`
- `validation_results/phase0q_selector_needle_once.txt`

The CSV must be present, non-empty, not ignored by Git, and included in the
final commit/package.
