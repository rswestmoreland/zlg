# Codex Prompt - Phase 0m

Run Phase 0m selector and postings validation only.

Primary command:

```bash
bash scripts/phase0m_selector_postings_once.sh
```

Do not add async, PCRE2, multiline regex, timestamp sidecars, dictionary
training, append mode, or final format freeze. Make only bounded fixes required
for validation, selector correctness, CSV preservation, scripts, docs, or the
postings probe.

Required output artifacts:

- validation_results/phase0m_selector_postings_bench.csv
- validation_results/phase0m_selector_postings_summary.md
- validation_results/phase0m_selector_postings_env.txt
- validation_results/phase0m_selector_postings_analysis.md
- validation_results/phase0m_postings_probe.md
- validation_results/phase0m_selector_postings_once.txt

The CSV must be present, non-empty, not ignored, and committed.
