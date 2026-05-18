# Phase 3 - Release Readiness and Installability

Status: prep package, not yet Rust-validated.

Phase 3 moves zlg from a validated Phase 2 CLI into a release-ready Linux tool. The goal is not to add new compression/search features. The goal is to make the existing command set easier to install, document, audit, package, and explain.

## Scope

- Keep the locked production core unchanged.
- Keep the Phase 2 command behavior unchanged.
- Prepare user-facing docs and release artifacts.
- Add release-readiness checks that can be run before packaging.
- Keep generated binaries, tarballs, corpora, compressed fixtures, and logs out of the repository.

## Locked core carried forward

```text
fixed-lines8192-cap8m
+ mesh-bigram ZBM1 v2
+ combined-bitset-seen
+ current reserve behavior
+ zstd::bulk::Compressor
+ streaming grep by default
+ summary-first skip
+ memchr line splitting
+ Rust regex default
+ PCRE2 mode
+ literal prefiltering
+ positive-lookbehind fast path
+ head-style early stop
```

## Phase 3 checklist

### Release metadata

- [x] Confirm author and contact are documented.
- [x] Confirm license is documented as MIT OR Apache-2.0.
- [x] Add package readme metadata in Cargo.toml.
- [x] Confirm final repository URL before release.
- [ ] Decide final version for first public release.
- [ ] Decide whether the first release is tagged as experimental/pre-1.0.

### User documentation

- [x] Add command reference.
- [x] Add install and uninstall guide.
- [x] Add release checklist.
- [x] Add active roadmap.
- [x] Add man-page draft.
- [x] Add shell completion notes.
- [x] Update README with Phase 3 status and doc links.
- [ ] Add terminal screenshots later if desired.

### Packaging and installability

- [x] Add release artifact dry-run script.
- [x] Add release-readiness audit script.
- [x] Add package contents checklist.
- [ ] Validate release artifact script in Codex/local Rust environment.
- [ ] Decide whether man page is packaged in release tarball.
- [ ] Decide whether shell completions are generated now or deferred.

### Validation

- [ ] Run full Cargo validation at end of Phase 3.
- [ ] Run Phase 2 smoke/hardening/benchmark scripts as needed.
- [ ] Run Phase 3 release-readiness script.
- [ ] Confirm no generated artifacts are committed.

## Not in Phase 3

- No file format freeze.
- No default compression mode change.
- No compression mode renaming.
- No embedded gzip/bzip2/xz decoder crates.
- No standalone zlg top.
- No parser-like top lines/tokens/fields.
- No async worker pool.
- No package-manager integration such as deb/rpm/homebrew yet.

## Known release blockers or warnings

- The Phase 2o reconciliation package should still be Rust-validated together with this Phase 3 package.
- The file format remains experimental and should be described that way in release materials.
