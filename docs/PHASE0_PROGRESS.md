# zlg Phase 0 Progress

## Current baseline

Phase 0g validated source prototype is the current baseline.

Validated in Codex:

```text
cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
```

Smoke-tested in Codex:

```text
compress
cat
grep regex
grep -o extraction
grep -n line numbers
grep -P fancy-regex path
```

## Phase 0g result

Status: complete.

Bounded fixes made during validation:

```text
fixed_find_all offset slicing corrected
DIRECTORY_ENTRY_LEN corrected to 64
clippy identity-op cleanup
conflicting -h short flag removed from --no-filename
Cargo.lock generated and committed
```

## Phase 0h scope

Phase 0h is correctness and benchmark harness preparation.

It should add repeatable scripts and documentation that prepare the project for proof work without changing runtime behavior.

## Phase 0h guardrails

Do not add:

```text
async worker pool
format freeze
PCRE2 backend
multiline regex
timestamp sidecar
dictionary training
append/update mode
large fixtures
binary artifacts
```

Allowed:

```text
small text fixtures
smoke scripts
correctness scripts
benchmark-prep scripts
small validation reports
documentation updates
minimal source fixes only if validation fails
```

## Next phase after Phase 0h

Phase 0i should run the first benchmark/correctness proof and capture results.

Phase 0i should decide which areas need implementation before serious benchmarks:

```text
better selector extraction
chunk policy instrumentation
benchmark CSV fields
memory/RSS capture
zgrep/gzip comparison matrix
```
## Phase 0i - Pre-bench readiness

Status: prepared for Codex validation.

Added:

```text
one-command prebench script
all-policy correctness matrix
artifact hygiene check
stronger benchmark-prep harness
environment report output
CSV and Markdown summary output
Codex prebench prompt
```

Phase 0i does not add runtime features and does not freeze the format.

## Phase 0j - Instrumentation and full-bench prep

Status: prepared for Codex validation.

Added:

```text
zlg grep --stats-json instrumentation
first-output latency capture in benchmark harness
zlg chunk count and payload/summary/overhead accounting
CSV preservation and column checks
instrumented one-command prebench flow
Codex Phase 0j prompt
```

Phase 0j does not add async/concurrency and does not freeze the format.

## Phase 0l - Index strategy comparison prep

Status: prepared in ChatGPT, pending Codex validation.

Purpose:

- Compare current bitmap summaries against no-index `.zlg` files.
- Preserve compact CSV evidence.
- Clarify whether bitmap metadata helps enough to keep, replace, or make optional.
- Defer async/parallel work until decoded-byte and metadata-cost evidence is clearer.

Added:

- `zlg compress --summary-mode none` experimental no-index mode.
- `selector_kind` and `selector_len` fields in grep stats JSON.
- `tools/phase0l_analyze_index_strategy.py`.
- `scripts/phase0l_index_strategy_once.sh`.
- `scripts/phase0l_no_index_smoke.sh`.
- `docs/PHASE0L_INDEX_STRATEGY_COMPARISON.md`.

Required result CSV:

- `validation_results/phase0l_index_strategy_bench.csv`

## Phase 0m - Selector extraction and postings prep

Status: prepared in ChatGPT, pending Codex validation.

Purpose:

- Improve safe literal selector extraction for common regex patterns.
- Record selector plan details in grep stats and benchmark CSV output.
- Run an offline block-level postings probe before changing the `.zlg` format.

Added:

- selector plans: `literal_all`, `literal_any`, and `none`.
- selector count in grep stats and benchmark CSV output.
- top-level alternation selectors such as `error|failed|denied`.
- noncapturing branch selectors such as `(?:foo|bar)[0-9]`.
- positive lookbehind literal hints such as `(?<=key=")[^"]+`.
- `tools/phase0m_postings_probe.py`.
- `scripts/phase0m_selector_postings_once.sh`.
- `scripts/phase0m_selector_smoke.sh`.

## Phase 0n - K-gram graph/postings experiment

Status: prepared in ChatGPT, pending Codex validation.

Purpose:

- Test whether graph/postings-style k-gram selectors can reduce estimated decoded bytes.
- Compare bigram block presence, sparse trigram postings, overlapping bigram graph edges, and rarest-kgram selection.
- Preserve compact CSV evidence for both the prebench run and the offline graph probe.
- Avoid changing or freezing the `.zlg` format until the experiment shows a clear benefit.

Added:

- `tools/phase0n_kgram_graph_probe.py`.
- `scripts/phase0n_kgram_graph_once.sh`.
- `docs/PHASE0N_KGRAM_GRAPH_EXPERIMENT.md`.

Required result CSVs:

- `validation_results/phase0n_kgram_graph_bench.csv`.
- `validation_results/phase0n_kgram_graph_probe.csv`.
