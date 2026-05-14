#!/usr/bin/env bash
set -euo pipefail

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

cat > "$tmpdir/input.log" <<'EOF'
alpha
error key="abc"
failed password
EOF

cargo run --quiet -- compress --summary-mode none "$tmpdir/input.log" -o "$tmpdir/no-index.zlg"
cargo run --quiet -- cat "$tmpdir/no-index.zlg" > "$tmpdir/out.log"
diff -u "$tmpdir/input.log" "$tmpdir/out.log"

cargo run --quiet -- grep 'error|failed' "$tmpdir/no-index.zlg" > "$tmpdir/grep.out"
grep -q 'error key="abc"' "$tmpdir/grep.out"
grep -q 'failed password' "$tmpdir/grep.out"

echo "phase0l no-index smoke: pass"
