#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

input="$repo_root/fixtures/smoke.txt"
zlg_file="$tmp_dir/smoke.zlg"

cargo run --quiet -- compress "$input" -o "$zlg_file"

compare() {
    local name="$1"
    shift
    local expected_cmd="$1"
    shift
    local actual_cmd="$1"
    shift

    local expected="$tmp_dir/${name}.expected"
    local actual="$tmp_dir/${name}.actual"

    bash -c "$expected_cmd" > "$expected"
    bash -c "$actual_cmd" > "$actual"

    if ! diff -u "$expected" "$actual"; then
        echo "phase0h correctness failed: $name" >&2
        exit 1
    fi

    echo "phase0h correctness ok: $name"
}

compare \
    regex_alternation \
    "grep -E 'error|failed' '$input'" \
    "cargo run --quiet -- grep 'error|failed' '$zlg_file'"

compare \
    fixed_string \
    "grep -F 'alpha' '$input'" \
    "cargo run --quiet -- grep -f 'alpha' '$zlg_file'"

compare \
    only_matching \
    "grep -oE 'key=\"[^\"]+\"' '$input'" \
    "cargo run --quiet -- grep -o 'key=\"[^\"]+\"' '$zlg_file'"

compare \
    line_numbers \
    "grep -nE 'failed password' '$input'" \
    "cargo run --quiet -- grep -n 'failed password' '$zlg_file'"

compare \
    ignore_case \
    "grep -iE 'info' '$input'" \
    "cargo run --quiet -- grep -i 'info' '$zlg_file'"

compare \
    count \
    "grep -cE 'warning' '$input'" \
    "cargo run --quiet -- grep -c 'warning' '$zlg_file'"

compare \
    invert_match \
    "grep -vE 'warning' '$input'" \
    "cargo run --quiet -- grep -v 'warning' '$zlg_file'"

fancy_actual="$tmp_dir/fancy.actual"
cargo run --quiet -- grep -oP '(?<=key=")[^"]+' "$zlg_file" > "$fancy_actual"
if [[ "$(cat "$fancy_actual")" != 'abc' ]]; then
    echo "phase0h correctness failed: fancy lookbehind extraction" >&2
    cat "$fancy_actual" >&2
    exit 1
fi
echo "phase0h correctness ok: fancy_lookbehind_only_matching"

printf 'phase0h correctness: pass\n'
