#!/usr/bin/env python3
import csv
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "validation_results"
OUT_DIR.mkdir(exist_ok=True)

checks = []

def add(name, status, detail):
    checks.append({"check": name, "status": status, "detail": detail})

required_files = [
    "README.md",
    "Cargo.toml",
    "LICENSE",
    "LICENSE-MIT",
    "LICENSE-APACHE",
    "docs/COMMAND_REFERENCE.md",
    "docs/INSTALL.md",
    "docs/RELEASE_CHECKLIST.md",
    "docs/ROADMAP.md",
    "docs/PHASE3_RELEASE_READINESS.md",
    "docs/SHELL_COMPLETIONS.md",
    "docs/man/zlg.1",
]
for rel in required_files:
    add(f"required_file:{rel}", "ok" if (ROOT / rel).is_file() else "fail", rel)

cargo = (ROOT / "Cargo.toml").read_text(errors="replace")
add("cargo_license", "ok" if 'license = "MIT OR Apache-2.0"' in cargo else "fail", "MIT OR Apache-2.0")
add("cargo_author", "ok" if "Richard S. Westmoreland <dev@rswestmore.land>" in cargo else "fail", "author/contact")
add("cargo_readme", "ok" if 'readme = "README.md"' in cargo else "warn", "readme metadata")
add("cargo_repository", "ok" if 'repository = "https://github.com/rswestmoreland/zlg"' in cargo else "fail", "https://github.com/rswestmoreland/zlg")

active_files = [
    "README.md",
    "docs/COMMAND_REFERENCE.md",
    "docs/INSTALL.md",
    "docs/RELEASE_CHECKLIST.md",
    "docs/ROADMAP.md",
    "docs/PHASE3_RELEASE_READINESS.md",
    "docs/SHELL_COMPLETIONS.md",
    "docs/man/zlg.1",
]
# Stale option-name scans are limited to user command docs. The release
# checklist intentionally mentions removed options as negative assertions.
public_command_docs = [
    "docs/COMMAND_REFERENCE.md",
    "docs/INSTALL.md",
    "docs/man/zlg.1",
]
expected_terms = [
    "--mode",
    "--extract",
    "--top",
    "--strict",
    "--force",
    "convert",
]
for term in expected_terms:
    found = any(term in (ROOT / rel).read_text(errors="replace") for rel in active_files if (ROOT / rel).exists())
    add(f"active_docs_term:{term}", "ok" if found else "warn", term)

stale_public_terms = ["--preset", "--max-count", "--verify-before-output", "--only-matching"]
for term in stale_public_terms:
    hits = []
    for rel in public_command_docs:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(errors="replace")
        if term in text:
            hits.append(rel)
    add(f"active_docs_stale:{term}", "warn" if hits else "ok", ", ".join(hits) if hits else "no active hits")

readme = (ROOT / "README.md").read_text(errors="replace")
internal_readme_terms = ["Codex", "validated commit", "Phase 2", "Phase 3", "handoff", "prep package"]
readme_hits = [term for term in internal_readme_terms if term in readme]
add("readme_public_facing", "warn" if readme_hits else "ok", ", ".join(readme_hits) if readme_hits else "no internal process terms")

bad_suffixes = {".zlg", ".gz", ".zst", ".bz2", ".xz", ".png"}
bad_paths = []
for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT)
    parts = set(rel.parts)
    if "target" in parts:
        continue
    if path.suffix in bad_suffixes and "validation_results" not in parts:
        bad_paths.append(str(rel))
add("generated_binary_artifacts", "fail" if bad_paths else "ok", ", ".join(bad_paths[:20]) if bad_paths else "none")

long_paths = []
for path in ROOT.rglob("*"):
    rel = str(path.relative_to(ROOT))
    if len(rel) > 180:
        long_paths.append(f"{len(rel)}:{rel}")
add("path_length_under_180", "warn" if long_paths else "ok", ", ".join(long_paths[:10]) if long_paths else "ok")

csv_path = OUT_DIR / "phase3_release_readiness.csv"
with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["check", "status", "detail"])
    writer.writeheader()
    writer.writerows(checks)

md_path = OUT_DIR / "phase3_release_readiness.md"
failures = sum(1 for c in checks if c["status"] == "fail")
warnings = sum(1 for c in checks if c["status"] == "warn")
with md_path.open("w") as f:
    f.write("# Phase 3 Release Readiness Audit\n\n")
    f.write(f"Checks: {len(checks)}\n\n")
    f.write(f"Failures: {failures}\n\n")
    f.write(f"Warnings: {warnings}\n\n")
    f.write("| Check | Status | Detail |\n")
    f.write("|---|---:|---|\n")
    for c in checks:
        detail = c["detail"].replace("|", "\\|")
        f.write(f"| {c['check']} | {c['status']} | {detail} |\n")

print(f"wrote {csv_path.relative_to(ROOT)}")
print(f"wrote {md_path.relative_to(ROOT)}")
if failures:
    raise SystemExit(1)
