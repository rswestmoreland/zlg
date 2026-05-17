#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

input="$repo_root/fixtures/smoke.txt"
zlg_file="$tmp_dir/smoke.zlg"
cat_out="$tmp_dir/cat.out"

cargo run --quiet -- compress "$input" -o "$zlg_file"
cargo run --quiet -- cat "$zlg_file" > "$cat_out"
diff -u "$input" "$cat_out"

regex_out="$(cargo run --quiet -- grep 'error|failed' "$zlg_file")"
expected_regex=$'error key="abc"\nfailed password'
[[ "$regex_out" == "$expected_regex" ]]

only_out="$(cargo run --quiet -- grep -o 'key="[^"]+"' "$zlg_file")"
[[ "$only_out" == 'key="abc"' ]]

line_out="$(cargo run --quiet -- grep -n 'failed password' "$zlg_file")"
[[ "$line_out" == '3:failed password' ]]

fancy_out="$(cargo run --quiet -- grep -oP '(?<=key=")[^"]+' "$zlg_file")"
[[ "$fancy_out" == 'abc' ]]

fixed_out="$(cargo run --quiet -- grep -f 'alpha' "$zlg_file")"
[[ "$fixed_out" == 'alpha' ]]

count_out="$(cargo run --quiet -- grep -c 'warning' "$zlg_file")"
[[ "$count_out" == '2' ]]

invert_out="$(cargo run --quiet -- grep -v 'warning' "$zlg_file" | wc -l | tr -d ' ')"
[[ "$invert_out" == '5' ]]

printf 'phase0h smoke: pass\n'
