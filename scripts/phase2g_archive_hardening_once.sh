#!/usr/bin/env bash
set -euo pipefail

zlg="target/release/zlg"
if [ ! -x "$zlg" ]; then
  zlg="cargo run --quiet --"
fi

python3 tools/phase2g_archive_hardening_probe.py \
  --zlg "$zlg" \
  --out-dir validation_results
