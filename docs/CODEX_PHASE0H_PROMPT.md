# Minimal Codex Prompt for Phase 0h

```text
You are continuing zlg from the validated Phase 0g baseline.

Authoritative input bundle:

zlg-main.zip

Goal:

Run Phase 0h correctness and benchmark-prep validation. Start with review and validation. Make only bounded fixes required for fmt/check/test/clippy/build/script failures. Do not broaden scope.

Required validation flow:

cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release

Then run:

scripts/phase0h_smoke.sh
scripts/phase0h_correctness_check.sh
python3 tools/phase0h_bench.py --quick

Guardrails:

- Do not add async/concurrency yet.
- Do not freeze or redesign the file format.
- Do not add PCRE2.
- Do not add multiline regex.
- Do not add unsafe Rust.
- Do not add large fixtures or generated corpora.
- Do not commit target/, build artifacts, temp files, .zlg files, .gz files, binaries, or large outputs.
- Keep comments and docs ASCII-only.
- Keep fixes minimal and explain each one.
- Cargo.lock may remain committed if Cargo updates it legitimately.
- Small text reports under validation_results/ are allowed.

Final response should include:

1. Files reviewed.
2. Exact commands run and pass/fail status.
3. Script outputs or summarized results.
4. Files changed.
5. Any remaining issues.
6. Artifact hygiene confirmation.
```
