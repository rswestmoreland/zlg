#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <csv-path>" >&2
  exit 2
fi

csv_path="$1"

if [[ ! -s "$csv_path" ]]; then
  echo "phase0k guard: missing or empty CSV: $csv_path" >&2
  exit 1
fi

if git check-ignore "$csv_path" >/dev/null 2>&1; then
  echo "phase0k guard: CSV is ignored by git: $csv_path" >&2
  exit 1
fi

status_line="$(git status --short -- "$csv_path" || true)"
if [[ -z "$status_line" ]]; then
  echo "phase0k guard: CSV exists and is not ignored, and is already tracked clean: $csv_path"
else
  echo "phase0k guard: CSV exists and is not ignored, status: $status_line"
fi
