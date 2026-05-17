You are continuing work on the zlg Rust project.

Start with REVIEW ONLY. Do not write code until the review is complete, drift is identified, and the exact implementation plan is clear.

Use the uploaded bundle as the authoritative baseline. Treat older Phase 0/1 zips and historical benchmark artifacts as traceability only; do not let them override the current locked decisions.

Project summary:

zlg is a single-binary Linux CLI utility and experimental `.zlg` file format for compressing, decompressing/catting, and searching plaintext logs. It uses zstd internally with independent chunks and a mesh-bigram search summary to accelerate compressed search.

Current locked production core:

fixed-lines8192-cap8m
+ mesh-bigram ZBM1 v2
+ combined-bitset-seen
+ current reserve behavior
+ zstd::bulk::Compressor
+ streaming grep
+ summary-first skip
+ memchr line splitting
+ Rust regex default
+ PCRE2 mode
+ literal prefiltering
+ positive-lookbehind fast path
+ head-style early stop

Compression modes:

none     = store payloads uncompressed inside .zlg chunks
fast     = zstd level 3
standard = zstd level 6
best     = zstd level 8

Use the term "compression mode", not "preset".

License and author decision:

MIT OR Apache-2.0
Richard S. Westmoreland
 dev@rswestmore.land

Important CLI design decisions:

- Use subcommands.
- Use lowercase short options only.
- Use lowercase long options only.
- Avoid aliases.
- Do not use uppercase options such as -P or -F.
- Use -p/--pcre2 instead of -P.
- Use -f/--fixed instead of -F.
- Use --mode, not --preset.
- Do not expose the full numeric compression-level range in the normal CLI.
- Include help and version commands.
- Include head and tail commands now.
- Store line-count and byte-count metadata for efficient stats and tail.
- Put wc-style behavior under stats.
- Keep sort/uniq as design topics; do not implement broad Unix clones yet.
- Convert should start lean: plain and .zst first, .gz only after binary-size impact is measured; defer .bz2 and .xz by default.

Planned command set:

zlg help
zlg version
zlg compress
zlg decompress
zlg cat
zlg grep
zlg head
zlg tail
zlg test
zlg info
zlg stats
zlg top
zlg convert

Start by reviewing:

- Cargo.toml and license metadata
- README.md
- LICENSE, LICENSE-MIT, LICENSE-APACHE
- docs/PHASE2B_CLI_ROADMAP_AND_CHECKLIST.md
- docs/CLI_DESIGN_DECISIONS_PHASE2.md
- src/cli.rs
- src/chunk.rs
- src/format.rs
- src/search.rs
- scripts/
- tests embedded in source files
- validation_results/

Review goals:

1. Confirm the locked production core is still intact.
2. Identify CLI drift between current code and the Phase 2 CLI decisions.
3. Identify metadata gaps for head/tail/stats.
4. Identify docs drift, especially older references to preset, -P, -F, --level, and --max-count in active docs.
5. Identify any remaining experimental profile surface that should stay hidden or be removed.
6. Produce a narrow implementation plan before coding.

Guardrails:

- Do not change the locked production core.
- Do not change mesh-bigram ZBM1 v2 unless explicitly approved later.
- Do not freeze the file format.
- Do not reintroduce rdxsort or rdst.
- Do not add new experimental builder candidates.
- Do not implement async worker pools in this phase.
- Do not add .bz2 or .xz support in the default binary without discussion.
- Keep comments and docs ASCII-only.
- Keep path names short.
- Do not commit target/, temp dirs, generated .zlg/.gz/.zst files, corpora, logs, PNGs, or binary artifacts.

Initial implementation recommendation after review:

1. Replace user-facing preset terminology with compression mode.
2. Add mode enum with none/fast/standard/best.
3. Remove normal public numeric level option from CLI.
4. Add help and version commands.
5. Rename grep options to lowercase-only forms.
6. Remove --max-count in favor of --head.
7. Add metadata fields needed by head/tail/stats, with compatibility guards as needed.
8. Implement head and tail.
9. Implement initial info/stats output for line/byte counts and component accounting.
10. Defer top/convert implementation until command and metadata basics are stable.

Validation after changes:

cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
scripts/phase0h_smoke.sh
scripts/phase0h_correctness_check.sh
scripts/phase0i_policy_matrix_check.sh
scripts/phase0m_selector_smoke.sh
scripts/phase0i_artifact_hygiene_check.sh

Expected response after review:

- Current repo/package status.
- Drift found.
- Metadata gaps found.
- Recommended implementation order.
- Exact validation commands.
- Risks and fallback plan.
