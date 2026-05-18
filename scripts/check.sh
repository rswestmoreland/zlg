#!/usr/bin/env bash
set -euo pipefail

cargo fmt --check
cargo check
cargo test
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
bash scripts/smoke.sh
bash scripts/convert_check.sh
bash scripts/release_readiness_check.sh
