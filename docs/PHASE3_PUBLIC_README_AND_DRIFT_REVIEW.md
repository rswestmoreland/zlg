# Phase 3 Public README and Drift Review

This review cleaned the public-facing repository presentation without changing the compression/search core.

## Scope

- Review Cargo metadata, README, active docs, scripts, validation artifacts, source layout, and benchmark outputs.
- Replace the internal phase-heavy README with a public-facing README.
- Keep historical Phase 0/1/2 documents as traceability records.
- Avoid changing runtime behavior in this pass.

## Drift addressed

- Replaced the placeholder Cargo repository URL with `https://github.com/rswestmoreland/zlg`.
- Removed internal validation/phase narrative from README.
- Added a short naming note: `zlg` is pronounced `z-log` and comes from `zstd log`.
- Added public explanations for the `.zlg` file layout, chunk summaries, footer directory, stats, extract/top, and convert helper behavior.
- Added benchmark snapshot tables sourced from repeated-median validation artifacts.
- Updated the release-readiness audit so the repository URL is now a required exact match instead of a warning.
- Added an audit check to warn if README reintroduces internal process terms.

## Review notes

- Historical Phase 0/1/2 design and Codex prompt files still contain old option names such as `-P`, `-F`, `--preset`, and `--max-count`. They are retained as traceability records.
- Active public command docs are `README.md`, `docs/COMMAND_REFERENCE.md`, `docs/INSTALL.md`, and `docs/man/zlg.1`.
- The current README intentionally does not discuss internal phase validation history or handoff workflow.
- The file format remains experimental and not frozen.

## Validation performed in the ChatGPT sandbox

- Python syntax check for `tools/phase3_doc_audit.py`.
- Bash syntax checks for Phase 2/3 scripts.
- Phase 3 release-readiness audit.
- ASCII scan.
- Path-length scan.
- Zip integrity check for the produced package.

Rust/Cargo validation was not run in the ChatGPT sandbox.
