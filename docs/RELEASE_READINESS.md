# Release readiness

This document tracks public-release readiness for zlg.

## Current status

- The command name is `zlg`, pronounced "z-log".
- The archive extension is `.zlg`.
- The file format is versioned and frozen at format version 1.
- The repository URL is `https://github.com/rswestmoreland/zlg`.
- The license is `MIT OR Apache-2.0`.

## Public documentation

- [ ] README is current.
- [ ] Command reference is current.
- [ ] Format overview is current.
- [ ] Benchmark snapshot is current.
- [ ] Install notes are current.
- [ ] Release checklist is current.
- [ ] Man page draft is current.

## Validation

Before a release, run:

```bash
cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
bash scripts/release_readiness_check.sh
```

Then run the smoke, hardening, convert, and benchmark scripts used by the project validation workflow.

## Release artifact dry run

```bash
bash scripts/release_artifact_dry_run.sh
```

The dry run writes to `target/release-dry-run/`; those generated artifacts should not be committed.

## Open release decisions

- Confirm the public version string.
- Decide whether shell completions should be generated for the first release.
- Decide whether to include the man page in binary release tarballs.
- Decide whether the default compression mode should remain `standard` or later change to `fast`.
