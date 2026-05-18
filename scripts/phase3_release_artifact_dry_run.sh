#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VERSION="$(grep '^version = ' Cargo.toml | head -1 | sed 's/version = //; s/\"//g')"
TARGET_DIR="target/phase3-release-dry-run"
PKG="zlg-${VERSION}-linux-x86_64"
PKG_DIR="${TARGET_DIR}/${PKG}"

cargo build --release
rm -rf "$TARGET_DIR"
mkdir -p "$PKG_DIR/docs/man"

cp target/release/zlg "$PKG_DIR/zlg"
cp README.md LICENSE LICENSE-MIT LICENSE-APACHE "$PKG_DIR/"
cp docs/COMMAND_REFERENCE.md docs/INSTALL.md docs/RELEASE_CHECKLIST.md docs/ROADMAP.md "$PKG_DIR/docs/"
cp docs/man/zlg.1 "$PKG_DIR/docs/man/"

(
  cd "$TARGET_DIR"
  tar -czf "${PKG}.tar.gz" "$PKG"
  sha256sum "${PKG}.tar.gz" > "${PKG}.tar.gz.sha256"
)

echo "created ${TARGET_DIR}/${PKG}.tar.gz"
echo "created ${TARGET_DIR}/${PKG}.tar.gz.sha256"
echo "dry-run artifacts are under target/ and must not be committed"
