# Phase 0t-fix - Mesh Probe Cache Correctness

## Purpose

Phase 0t-fix is a narrow correction pass for the Phase 0t offline k-gram mesh
shootout.

The Phase 0t validation run completed, but the optimized probe cached block
edge data using only `(k, block_id)`. That is unsafe across different block
sizes because block 10 in a 512-line layout is not the same data as block 10 in
a 1024-line layout.

## Correction

The cache key now includes stable block identity fields:

```text
k
block_id
first_line
line_count
byte_count
```

The probe also clears block caches between each block-size/group-size
configuration.

## Correctness guard

The probe now fails if known-present needle patterns lose the true needle block.
This guards against cache contamination and selector regressions.

Guarded patterns:

```text
needle_exact_ip_regex_escaped
needle_ip_fixed
needle_src_ip_fixed
```

The request-id prefix is intentionally not in the hard guard because its exact
value depends on the generated line count used by small smoke runs.

## Outputs

Phase 0t-fix should produce:

```text
validation_results/phase0t_fix_mesh_shootout.csv
validation_results/phase0t_fix_mesh_shootout.md
validation_results/phase0t_fix_mesh_correctness_once.txt
```

The CSV must be present, non-empty, not ignored by Git, and included in the
final commit/package.
