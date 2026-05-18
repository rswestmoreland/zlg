# zlg Release Checklist

This checklist is for a pre-1.0 Linux release candidate.

## Metadata

- [ ] Confirm final repository URL in Cargo.toml.
- [ ] Confirm version string.
- [ ] Confirm author: Richard S. Westmoreland.
- [ ] Confirm contact: dev@rswestmore.land.
- [ ] Confirm license: MIT OR Apache-2.0.
- [ ] Confirm README.md is current.
- [ ] Confirm file format is still described as experimental.

## Validation

Run:

```bash
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
bash scripts/phase3_release_readiness_once.sh
```

## Packaging dry run

Run:

```bash
bash scripts/phase3_release_artifact_dry_run.sh
```

Confirm generated artifacts stay outside committed source or remain ignored.

## Documentation

- [ ] README command examples are current.
- [ ] docs/COMMAND_REFERENCE.md is current.
- [ ] docs/INSTALL.md is current.
- [ ] docs/man/zlg.1 is current.
- [ ] docs/ROADMAP.md is current.
- [ ] docs/SHELL_COMPLETIONS.md accurately reflects current status.
- [ ] Historical Phase 0/1 docs are treated as traceability, not active guidance.

## CLI audit

- [ ] No public `--preset`.
- [ ] No public numeric `--level`.
- [ ] No public `-P` or `-F`.
- [ ] No public `--max-count`.
- [ ] No public `--verify-before-output`.
- [ ] `grep -e --top` is documented.
- [ ] `convert` helper behavior is documented.

## Release notes

- [ ] Summarize search/compression goals.
- [ ] Summarize command set.
- [ ] Summarize benchmark headline without overclaiming.
- [ ] Note that timings vary by system.
- [ ] Note that the format remains experimental.
