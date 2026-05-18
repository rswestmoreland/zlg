You are continuing work on the zlg Rust project.

Start with REVIEW ONLY if a new validated package has been uploaded. Confirm the current baseline, validation status, docs, scripts, tests, and any drift before proposing implementation changes.

Current Phase 2m design:

- `zlg convert` is for already-compressed input only.
- Plain logs should use `zlg compress`.
- Command shape is `zlg convert <compressed-input> [output.zlg]`.
- There is no `-o` or `--output` option.
- If output is omitted, remove the last extension and add `.zlg`.
- Reuse `--mode <none|fast|standard|best>`.
- Reuse `-y`, `--force`.
- `.zst` uses the internal zstd decoder already present in zlg.
- `.gz` uses external `gzip -dc`.
- `.bz2` uses external `bzip2 -dc`.
- `.xz` uses external `xz -dc`.
- Helpers must be invoked directly, not through a shell.
- Missing helpers should produce clear unsupported-in-this-environment errors.
- No new Cargo dependencies should be added in the helper-based convert pass.

Guardrails:

- Do not change the locked production core.
- Do not change mesh-bigram ZBM1 v2.
- Do not freeze the file format.
- Do not change CRC scope from uncompressed chunk bytes.
- Do not change default grep to strict mode.
- Do not change default compression mode.
- Do not rename compression modes.
- Do not add embedded gzip/bzip2/xz decoder crates yet.
- Do not invoke helpers through a shell.
- Do not implement top.
- Keep comments and docs ASCII-only.
- Do not commit generated archives, compressed fixtures, corpora, target, temp dirs, or binary artifacts.
