You are continuing work on the zlg Rust project.

Start by validating the Phase 1d checkpoint. Do not broaden runtime behavior or change the on-disk format.

Current goal:

Validate builder fairness and robustness changes after Phase 1c-fix. `combined-bitset-seen` is still experimental and must not be described as the locked build strategy.

Locked benchmark baseline:

```text
fixed-lines8192
+ mesh-bigram ZBM1 v2
+ zstd::bulk::Compressor
+ streaming grep
+ Rust regex default
+ PCRE2 for -P
+ literal prefiltering
+ positive-lookbehind fast path
+ --head / --max-count early stop
```

Changes to validate:

- CLI compression defaults now match the benchmark baseline: fixed-lines8192, mesh-bigram, combined.
- New build profile: combined-lower-only-bitset-seen.
- New build profile: combined-sparse-first-bitset.
- New build profile: combined-grouped-buckets.
- Build stats now include scratch and bitset accounting fields.
- README and Phase 1c semantics drift were corrected.
- Unicode and binary-like byte-exact round-trip tests were added.

Guardrails:

- Keep ZBM1 v2 on-disk format unchanged.
- Do not freeze the file format.
- Do not implement async worker pools.
- Do not reintroduce bitmap, trigram, path-window, rare-window, per-group mesh, fixed-lines1024, or fixed-lines2048 as active benchmark candidates.
- Do not add multiline regex or timestamp indexing.
- Do not add tail/sort/uniq runtime behavior.
- Do not add unsafe Rust.
- Keep comments and docs ASCII-only.
- Do not commit target/, generated .zlg/.gz/.zst files, generated logs, corpora, or binary artifacts.
- Any new dependencies must be justified and isolated to the experiment.

Validation flow:

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
python3 tools/phase1d_builder_fairness_bench.py \
  --binary target/release/zlg \
  --lines 125000 \
  --needle-ratio 0.80 \
  --repeats 3 \
  --output validation_results/phase1d_builder_fairness_bench.md \
  --csv validation_results/phase1d_builder_fairness_bench.csv
bash scripts/phase0k_csv_commit_guard.sh validation_results/phase1d_builder_fairness_bench.csv
bash scripts/phase0i_artifact_hygiene_check.sh
```

Preferred one-command run:

```bash
bash scripts/phase1d_builder_fairness_once.sh
```

Expected result:

Produce compact validation artifacts only:

- validation_results/phase1d_builder_fairness_once.txt
- validation_results/phase1d_builder_fairness_bench.md
- validation_results/phase1d_builder_fairness_bench.csv

If validation fails, make only bounded fixes required by the failure and preserve the phase scope.
