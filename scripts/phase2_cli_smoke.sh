#!/usr/bin/env bash
set -euo pipefail

workdir="${TMPDIR:-/tmp}/zlg_phase2_cli_smoke.$$"
trap 'rm -rf "$workdir"' EXIT
mkdir -p "$workdir"

input="$workdir/input.log"
cat > "$input" <<'LOG'
alpha one
beta two
alpha three
error four
LOG

zlg="target/release/zlg"
if [ ! -x "$zlg" ]; then
  zlg="cargo run --quiet --"
fi

$zlg version >/dev/null
$zlg version --long >/dev/null
$zlg help >/dev/null
$zlg help grep >/dev/null

for mode in none fast standard best; do
  archive="$workdir/$mode.zlg"
  $zlg compress "$input" -o "$archive" --mode "$mode"
  cmp "$input" <($zlg cat "$archive")
  $zlg test "$archive" >/dev/null
  $zlg info "$archive" >/dev/null
  $zlg info "$archive" --json >/dev/null
  $zlg stats "$archive" >/dev/null
  $zlg stats "$archive" --json >/dev/null
  $zlg grep -f alpha "$archive" >/dev/null
  $zlg grep --head 1 alpha "$archive" >/dev/null
  $zlg head -n 2 "$archive" >/dev/null
  $zlg tail -n 2 "$archive" >/dev/null
  $zlg grep -p '(?<=alpha )[a-z]+' "$archive" >/dev/null
  $zlg grep -o -p '(?<=alpha )[a-z]+' "$archive" >/dev/null
  if $zlg grep -f alpha -p alpha "$archive" >/dev/null 2>&1; then
    echo "expected -f and -p conflict to fail" >&2
    exit 1
  fi
done

echo "phase2 cli smoke passed"
