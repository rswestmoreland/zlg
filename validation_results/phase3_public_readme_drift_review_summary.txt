Phase 3 public README and drift review prep summary

Scope:
- Reviewed Cargo metadata, README, active release docs, command reference, install docs, roadmap, scripts, source layout, and benchmark artifacts.
- Replaced the internal phase-heavy README with a public-facing README focused on what zlg is, how it works, how to use it, and current benchmark signals.
- Kept historical Phase 0/1/2 files as traceability records rather than rewriting old benchmark history.

Changes:
- Cargo.toml repository now points to https://github.com/rswestmoreland/zlg.
- README now includes:
  - naming note: zlg is pronounced z-log and comes from zstd log
  - quick usage examples
  - zlg file layout diagram
  - explanation of chunks, ZBM1 mesh-bigram summaries, directory, and footer
  - compression mode summary
  - grep extract/top examples and safety behavior
  - stats example suitable for screenshots
  - repeated-median benchmark snapshot tables for build/storage/search/head/tail
  - convert helper behavior for .zst/.gz/.bz2/.xz
  - install-from-source notes
- Added docs/PHASE3_PUBLIC_README_AND_DRIFT_REVIEW.md.
- Updated tools/phase3_doc_audit.py:
  - repository URL is now an exact required check
  - README is checked for internal process terms such as Codex, phase history, handoff, or prep package wording
- Updated docs/PHASE3_RELEASE_READINESS.md to mark repository URL confirmation complete.
- Regenerated validation_results/phase3_release_readiness.csv and .md.

Review findings:
- Active public command docs are aligned with current command names: --mode, --extract, --top, --strict, --force, and convert.
- Active public command docs do not contain stale public names: --preset, --max-count, --verify-before-output, or --only-matching.
- Historical Phase 0/1/2 docs and Codex prompt files still contain old terms by design; they remain traceability records.
- No generated binary artifacts were found outside ignored/temporary paths.
- Path-length audit passed.
- ASCII scan passed after removing Python __pycache__ output.

Sandbox checks run:
- python3 -B -m py_compile tools/phase3_doc_audit.py
- bash -n scripts/phase3_release_readiness_once.sh
- bash -n scripts/phase3_release_artifact_dry_run.sh
- bash -n scripts/phase2_cli_smoke.sh
- bash -n scripts/phase2m_convert_once.sh
- python3 tools/phase3_doc_audit.py
- ASCII scan
- path-length scan
- zip integrity check

Rust/Cargo validation was not run in this sandbox.
