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
$zlg version --long > "$workdir/version_long.txt"
grep -q 'format-version:' "$workdir/version_long.txt"
grep -q 'default-compression-mode: standard' "$workdir/version_long.txt"
grep -q 'default-chunk-policy: fixed-lines8192-cap8m' "$workdir/version_long.txt"
grep -q 'default-summary-type: mesh-bigram ZBM1 v2' "$workdir/version_long.txt"
$zlg help >/dev/null
$zlg help grep >/dev/null

$zlg compress --help > "$workdir/compress_help.txt"
grep -q -- '--mode' "$workdir/compress_help.txt"
if grep -q -- '--preset\|--level\|--chunk-policy\|--summary-mode\|--build-profile\|--build-stats-json' "$workdir/compress_help.txt"; then
  echo "compress help exposed removed or hidden options" >&2
  exit 1
fi

$zlg grep --help > "$workdir/grep_help.txt"
grep -q -- '--head' "$workdir/grep_help.txt"
grep -q -- '--fixed' "$workdir/grep_help.txt"
grep -q -- '--pcre2' "$workdir/grep_help.txt"
if grep -q -- '--max-count\|-P,\|-F,\|--stats-json' "$workdir/grep_help.txt"; then
  echo "grep help exposed removed or hidden options" >&2
  exit 1
fi

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
  $zlg head -n 2 "$archive" > "$workdir/${mode}_head.txt"
  head -n 2 "$input" > "$workdir/${mode}_head_expected.txt"
  cmp "$workdir/${mode}_head_expected.txt" "$workdir/${mode}_head.txt"
  $zlg tail -n 2 "$archive" > "$workdir/${mode}_tail.txt"
  tail -n 2 "$input" > "$workdir/${mode}_tail_expected.txt"
  cmp "$workdir/${mode}_tail_expected.txt" "$workdir/${mode}_tail.txt"
  $zlg tail -n 99 "$archive" > "$workdir/${mode}_tail_all.txt"
  cmp "$input" "$workdir/${mode}_tail_all.txt"
  $zlg grep -p '(?<=alpha )[a-z]+' "$archive" >/dev/null
  $zlg grep -o -p '(?<=alpha )[a-z]+' "$archive" >/dev/null
  if $zlg grep -f alpha -p alpha "$archive" >/dev/null 2>&1; then
    echo "expected -f and -p conflict to fail" >&2
    exit 1
  fi
done

echo "phase2 cli smoke passed"
