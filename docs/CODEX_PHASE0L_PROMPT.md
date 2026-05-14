# Codex Phase 0l Prompt

Copy/paste prompt is provided in chat, but this file records the intended scope.

Start with Phase 0l index strategy comparison only. Validate the new no-index `.zlg` summary mode and run the one-command Phase 0l prebench.

Primary command:

```bash
bash scripts/phase0l_index_strategy_once.sh
```

Do not broaden scope into async, PCRE2, multiline regex, timestamp indexing, dictionary training, append mode, or file-format freeze.

Required hard gate:

```text
validation_results/phase0l_index_strategy_bench.csv
```

must be present, non-empty, not ignored by Git, and included in the final commit/package.
