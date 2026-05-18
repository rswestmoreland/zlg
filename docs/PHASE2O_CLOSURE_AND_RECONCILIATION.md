# Phase 2o - Closure and reconciliation prep

Phase 2o reconciles the validated Phase 2n extract/top work with the Phase 2m convert follow-up items that were prepared separately.

## Scope

- Keep the locked compression/search core unchanged.
- Reapply the Phase 2m `.zst` validation cleanup on top of the Phase 2n validated tree.
- Keep helper-based `.gz`, `.bz2`, and `.xz` conversion.
- Keep standalone `zlg top` deferred. The current top workflow is `zlg grep -e --top`.
- Add an explicit future cleanup item for the grep pipeline helper argument lists.

## Convert reconciliation

The validated Phase 2m helper convert pass supports:

```text
zlg convert <compressed-input> [output.zlg]
```

Input behavior:

| Input | Strategy | External helper required |
|---|---|---:|
| `.zst` | internal zstd crate decoder | no |
| `.gz` | `gzip -dc` helper | yes |
| `.bz2` | `bzip2 -dc` helper | yes |
| `.xz` | `xz -dc` helper | yes |

Phase 2o removes the validation-script dependency on the external `zstd` command. `.zst` conversion is covered by a Rust unit test that creates a `.zst` fixture with the existing zstd crate and then converts it through `zlg convert`.

Phase 2o also hardens external helper cleanup: if writing the `.zlg` output fails while reading a helper stream, zlg kills/waits for the helper and removes the temporary output path.

## Extract/top status

Phase 2n validated the grep-integrated top workflow:

```text
zlg grep -e -t PATTERN file.zlg
zlg grep -pte PATTERN file.zlg
```

This remains the only top-style behavior for now. zlg does not implement parser-like top lines, top tokens, or top fields.

## Future cleanup item

Codex validation for Phase 2n used scoped `#[allow(clippy::too_many_arguments)]` on the grep pipeline helpers:

```text
grep_one
grep_streaming_chunk
grep_decoded_chunk
```

This is acceptable for the current validated milestone, but it should not grow indefinitely. A future cleanup should introduce a small `GrepContext` or pipeline context struct that groups stable grep runtime state and reduces function argument lists. The existing `GrepOptions` struct already covers user-selected search behavior; the new context should be a pipeline/runtime context rather than another options object.

Suggested future item:

```text
Refactor grep pipeline helpers to use a GrepContext/GrepPipelineContext struct so helper signatures stay small as extract/top/strict/search modes evolve.
```

This cleanup should be behavior-preserving and should happen after Phase 2 closure, not as part of the functional command work.

## Validation expected later

This prep has not been Rust/Cargo validated in ChatGPT. Later validation should run:

```text
cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
bash scripts/phase0h_smoke.sh
bash scripts/phase0h_correctness_check.sh
bash scripts/phase0i_policy_matrix_check.sh
bash scripts/phase0m_selector_smoke.sh
bash scripts/phase0i_artifact_hygiene_check.sh
bash scripts/phase2_cli_smoke.sh
bash scripts/phase2g_archive_hardening_once.sh
bash scripts/phase2i_repeated_median_once.sh
bash scripts/phase2m_convert_once.sh
```

Expected result:

- `.zst` convert test passes without requiring the external `zstd` CLI.
- `.gz`, `.bz2`, and `.xz` convert paths remain helper-based.
- Phase 2n extract/top behavior remains intact.
- No new Cargo dependencies are added.
