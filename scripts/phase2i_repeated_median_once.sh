#!/usr/bin/env bash
set -euo pipefail

zlg="${ZLG_BIN:-target/release/zlg}"
if [ ! -x "$zlg" ]; then
  zlg="cargo run --quiet --"
fi

mkdir -p validation_results
python3 tools/phase2i_repeated_median_bench.py \
  --zlg-bin "$zlg" \
  --out-csv validation_results/phase2i_repeated_median_smoke.csv \
  --out-md validation_results/phase2i_repeated_median_smoke.md \
  --repeats "${ZLG_PHASE2I_REPEATS:-3}"

python3 - <<'PY'
import csv
from pathlib import Path
path = Path('validation_results/phase2i_repeated_median_smoke.csv')
rows = list(csv.DictReader(path.open()))
if not rows:
    raise SystemExit('no phase2i rows written')
missing = []
median_rows = 0
for idx, row in enumerate(rows, start=2):
    if row.get('aggregate') == 'median':
        median_rows += 1
    for field in ('wall_seconds', 'user_seconds', 'system_seconds', 'cpu_percent', 'max_rss_kb'):
        value = row.get(field, '')
        if value == '' or value.lower() == 'n/a':
            missing.append((idx, field))
    if row.get('parity') not in ('ok', 'n/a'):
        raise SystemExit(f'bad parity on row {idx}: {row.get("parity")}')
if missing:
    raise SystemExit(f'missing metrics: {missing[:5]}')
if median_rows == 0:
    raise SystemExit('no median rows written')
print(f'phase2i repeated median rows={len(rows)} median_rows={median_rows}')
PY
