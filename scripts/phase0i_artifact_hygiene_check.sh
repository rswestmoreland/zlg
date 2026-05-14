#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bad=0

check_path() {
    local path="$1"
    if [[ -e "$path" ]]; then
        echo "artifact hygiene failure: unexpected path exists: $path" >&2
        bad=1
    fi
}

# Build outputs may exist during local validation, but must not be committed.
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if git status --porcelain | grep -E 'target/|\.zlg$|\.gz$|\.zst$' >/dev/null; then
        echo "artifact hygiene failure: git status shows build/compressed artifacts" >&2
        git status --porcelain | grep -E 'target/|\.zlg$|\.zst$|\.gz$' >&2 || true
        bad=1
    fi
fi

# Check the working tree for accidental committed-location binary/compressed artifacts.
while IFS= read -r -d '' path; do
    case "$path" in
        ./target/*) continue ;;
        ./.git/*) continue ;;
    esac
    echo "artifact hygiene failure: compressed/binary artifact in repo path: $path" >&2
    bad=1
done < <(find . -type f \( -name '*.zlg' -o -name '*.gz' -o -name '*.zst' -o -name '*.tmp' \) -print0)

if [[ "$bad" -ne 0 ]]; then
    exit 1
fi

printf 'phase0i artifact hygiene: pass\n'
