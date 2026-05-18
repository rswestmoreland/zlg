# zlg Roadmap

This roadmap supersedes the short Phase 2-only checklists. Historical Phase 0 and Phase 1 files remain traceability records.

## Phase 0 - Format and search proof

Status: complete.

- Proved independent zstd-backed chunks.
- Proved line-aligned chunks.
- Proved mesh-bigram summary and summary-first skip.
- Benchmarked regex and fixed-search behavior.

## Phase 1 - Final stack selection

Status: complete.

- Selected the production stack.
- Optimized the build path.
- Validated compressed search speed and storage behavior.

## Phase 2 - CLI maturity

Status: functionally complete, pending final validation of Phase 2o reconciliation.

Completed:

- compress, decompress, cat, grep, head, tail, test, info, stats, convert
- extract/top through grep: `zlg grep -e -t`
- helper-based convert for `.gz`, `.bz2`, `.xz`
- internal `.zst` convert path
- archive hardening and repeated median benchmark scripts

Deferred from Phase 2:

- standalone `zlg top`
- parser-like top lines/tokens/fields
- embedded gzip/bzip2/xz decoders
- format freeze

## Phase 3 - Release readiness and installability

Status: in progress.

Goals:

- user-facing documentation
- command reference
- install/uninstall guidance
- man-page draft
- release checklist
- release artifact dry-run script
- package/audit script

## Phase 4 - Error quality and operational hardening

Planned:

- improve user-facing error categories
- strengthen helper failure messages
- document exit behavior
- add more malformed archive fixtures
- review temp-file cleanup on interrupted commands

## Phase 5 - Format specification and compatibility policy

Planned:

- formal `.zlg` format specification
- compatibility policy
- golden fixtures
- version negotiation rules
- checksum policy review

No format freeze until this phase is complete.

## Phase 6 - Large-scale performance validation

Planned:

- 500 MB and 1 GB corpora
- repeated medians by default
- fast vs standard default-mode decision support
- more realistic log shapes

## Phase 7 - Parallel pipeline exploration

Planned, design-first:

- parallel chunk building
- parallel summary building
- parallel zstd compression
- deterministic output preservation
- bounded memory queues

## Phase 8 - Search feature expansion

Planned, design-first:

- context lines
- count-only refinements
- JSONL output
- case/invert interactions
- explain/debug search mode

## Phase 9 - Embedded decoder decision

Planned:

- measure embedded gzip/bzip2/xz decoder overhead
- compare against helper-based convert
- decide whether helper-only remains the default design

## Phase 10 - Distribution and release polish

Planned:

- release tarballs
- checksums
- man page packaging
- shell completions if added
- GitHub release notes
- possible package manager exploration
