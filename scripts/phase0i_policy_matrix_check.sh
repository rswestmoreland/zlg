#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

zlg="$repo_root/target/release/zlg"
input="$repo_root/fixtures/search_cases.txt"

if [[ ! -x "$zlg" ]]; then
    cargo build --release
fi

policies=(
    fixed-lines64k
    progressive-lines
    byte1m
    byte4m
    byte8m
    hybrid-progressive-cap4m
    hybrid-progressive-cap8m
    hybrid-progressive-cap16m
    hybrid-progressive-cap32m
    hybrid-fixed64k-cap8m
    hybrid-fixed64k-cap16m
    hybrid-fixed64k-cap32m
)

regex_patterns=(
    'error|failed|denied'
    'key="[^"]+"'
    '(foo|bar)[0-9]'
    'src_ip=[0-9.]+'
)

fixed_patterns=(
    'failed password'
    'no_such_token_zzzz'
)

for policy in "${policies[@]}"; do
    zlg_file="$tmp_dir/search_cases.${policy}.zlg"
    "$zlg" compress "$input" --chunk-policy "$policy" -o "$zlg_file"

    cat_actual="$tmp_dir/cat.${policy}.actual"
    "$zlg" cat "$zlg_file" > "$cat_actual"
    diff -u "$input" "$cat_actual"

    for pattern in "${regex_patterns[@]}"; do
        expected="$tmp_dir/${policy}.$(echo "$pattern" | tr -c 'A-Za-z0-9' '_').expected"
        actual="$tmp_dir/${policy}.$(echo "$pattern" | tr -c 'A-Za-z0-9' '_').actual"
        grep -E "$pattern" "$input" > "$expected" || true
        "$zlg" grep "$pattern" "$zlg_file" > "$actual" || true
        diff -u "$expected" "$actual"
    done

    for pattern in "${fixed_patterns[@]}"; do
        expected="$tmp_dir/${policy}.$(echo "$pattern" | tr -c 'A-Za-z0-9' '_').fixed.expected"
        actual="$tmp_dir/${policy}.$(echo "$pattern" | tr -c 'A-Za-z0-9' '_').fixed.actual"
        grep -F "$pattern" "$input" > "$expected" || true
        "$zlg" grep -F "$pattern" "$zlg_file" > "$actual" || true
        diff -u "$expected" "$actual"
    done

    fancy_expected="$tmp_dir/fancy.${policy}.expected"
    fancy_actual="$tmp_dir/fancy.${policy}.actual"
    grep -oP '(?<=key=")[^"]+' "$input" > "$fancy_expected" || true
    "$zlg" grep -oP '(?<=key=")[^"]+' "$zlg_file" > "$fancy_actual" || true
    diff -u "$fancy_expected" "$fancy_actual"

    echo "phase0i policy matrix ok: $policy"
done

printf 'phase0i policy matrix: pass\n'
