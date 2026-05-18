#!/usr/bin/env bash
set -euo pipefail

workdir="${TMPDIR:-/tmp}/zlg_convert.$$"
trap 'rm -rf "$workdir"' EXIT
mkdir -p "$workdir"

zlg="target/release/zlg"
if [ ! -x "$zlg" ]; then
  zlg="cargo run --quiet --"
fi

input="$workdir/sample.log"
cat > "$input" <<'LOG'
alpha one
beta two
alpha three
error four
omega five
LOG

results_csv="validation_results/convert.csv"
results_md="validation_results/convert.md"
mkdir -p validation_results
printf 'format,helper,status,detail\n' > "$results_csv"
{
  echo '# Convert smoke'
  echo
  echo '| Format | Helper | Status | Detail |'
  echo '|---|---|---|---|'
} > "$results_md"

record() {
  local format="$1"
  local helper="$2"
  local status="$3"
  local detail="$4"
  printf '%s,%s,%s,%s\n' "$format" "$helper" "$status" "$detail" >> "$results_csv"
  printf '| %s | %s | %s | %s |\n' "$format" "$helper" "$status" "$detail" >> "$results_md"
}

run_case() {
  local format="$1"
  local helper="$2"
  local ext="$3"
  local fixture="$workdir/sample.log.$ext"
  local inferred="$workdir/sample.log.zlg"
  local explicit="$workdir/sample_${format}_explicit.zlg"
  rm -f "$fixture" "$inferred" "$explicit"

  if ! command -v "$helper" >/dev/null 2>&1; then
    if $zlg convert "$fixture" "$explicit" >/dev/null 2>&1; then
      echo "expected missing or absent $format input conversion to fail" >&2
      exit 1
    fi
    record "$format" "$helper" "skipped" "$helper not found in PATH"
    return
  fi

  case "$format" in
    zst) "$helper" -q -c "$input" > "$fixture" ;;
    gz) "$helper" -c "$input" > "$fixture" ;;
    bz2) "$helper" -c "$input" > "$fixture" ;;
    xz) "$helper" -c "$input" > "$fixture" ;;
    *) echo "unknown format $format" >&2; exit 1 ;;
  esac

  $zlg convert "$fixture"
  cmp "$input" <($zlg cat "$inferred")

  $zlg convert "$fixture" "$explicit" --mode fast
  cmp "$input" <($zlg cat "$explicit")

  if $zlg convert "$fixture" "$explicit" >/dev/null 2>&1; then
    echo "expected convert without --force to refuse overwrite for $format" >&2
    exit 1
  fi
  $zlg convert "$fixture" "$explicit" --force --mode standard
  cmp "$input" <($zlg cat "$explicit")

  record "$format" "$helper" "ok" "roundtrip and overwrite policy passed"
}

$zlg convert --help > "$workdir/convert_help.txt"
grep -q -- '--mode' "$workdir/convert_help.txt"
grep -q -- '--force' "$workdir/convert_help.txt"
if grep -q -- '--output\|-o,\|--preset\|--level' "$workdir/convert_help.txt"; then
  echo "convert help exposed disallowed options" >&2
  exit 1
fi

if $zlg convert "$input" "$workdir/plain.zlg" >/dev/null 2>&1; then
  echo "expected plain input convert to fail" >&2
  exit 1
fi
record "plain" "none" "ok" "plain input rejected; use compress"

record "zst" "internal" "ok" "covered by cargo test using internal zstd decoder"
run_case "gz" "gzip" "gz"
run_case "bz2" "bzip2" "bz2"
run_case "xz" "xz" "xz"

echo "convert smoke passed"
