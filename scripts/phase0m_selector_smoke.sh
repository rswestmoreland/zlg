#!/usr/bin/env bash
set -euo pipefail

tmpdir="${TMPDIR:-/tmp}/zlg-phase0m-selector-smoke-$$"
mkdir -p "$tmpdir"
trap 'rm -rf "$tmpdir"' EXIT

input="$tmpdir/input.log"
zlg_file="$tmpdir/input.zlg"
stats="$tmpdir/stats.json"

cat > "$input" <<'EOF'
alpha
error key="abc" src_ip=10.0.0.1
failed password for user bob from 192.0.2.10
firewall action=drop bar7 key="deny7" src_ip=10.0.7.49
EOF

cargo run --quiet -- compress "$input" --summary-mode bitmap -o "$zlg_file"

cargo run --quiet -- grep --stats-json "$stats" 'error|failed|denied' "$zlg_file" >/dev/null
python3 - "$stats" <<'PY'
import json
import sys
path = sys.argv[1]
data = json.load(open(path, 'r', encoding='utf-8'))
assert data['selector_kind'] == 'literal_any', data
assert data['selector_count'] == 3, data
PY

cargo run --quiet -- grep --stats-json "$stats" '(?:foo|bar)[0-9]' "$zlg_file" >/dev/null
python3 - "$stats" <<'PY'
import json
import sys
path = sys.argv[1]
data = json.load(open(path, 'r', encoding='utf-8'))
assert data['selector_kind'] == 'literal_any', data
assert data['selector_count'] == 2, data
PY

cargo run --quiet -- grep --stats-json "$stats" 'key="[^"]+"' "$zlg_file" >/dev/null
python3 - "$stats" <<'PY'
import json
import sys
path = sys.argv[1]
data = json.load(open(path, 'r', encoding='utf-8'))
assert data['selector_kind'] == 'literal_all', data
assert data['selector_count'] >= 1, data
PY

cargo run --quiet -- grep --stats-json "$stats" -p '(?<=key=")[^"]+' "$zlg_file" >/dev/null
python3 - "$stats" <<'PY'
import json
import sys
path = sys.argv[1]
data = json.load(open(path, 'r', encoding='utf-8'))
assert data['selector_kind'] == 'literal_all', data
assert data['selector_count'] == 1, data
PY

echo "phase0m selector smoke: pass"
