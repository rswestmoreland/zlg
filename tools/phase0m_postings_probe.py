#!/usr/bin/env python3
"""Phase 0m positional bigram postings probe.

This is an offline design probe. It does not change the .zlg format. It builds
block-level bigram postings over a deterministic corpus and estimates how many
independently-decodable search blocks a future postings index would select.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from phase0h_bench import PATTERNS, make_corpus, sha256  # noqa: E402


def literal_runs(pattern: str) -> list[bytes]:
    out: list[bytes] = []
    current = bytearray()
    in_class = False
    escaped = False
    meta = set(b"(){}*+?^$.|")
    literal_escapes = set(b"\\\"'/. _-=:")

    for byte in pattern.encode("utf-8"):
        if escaped:
            if byte in literal_escapes:
                current.append(byte)
            else:
                if len(current) >= 2:
                    out.append(bytes(current))
                current.clear()
            escaped = False
            continue

        if byte == ord("\\"):
            escaped = True
        elif byte == ord("["):
            if len(current) >= 2:
                out.append(bytes(current))
            current.clear()
            in_class = True
        elif byte == ord("]"):
            in_class = False
        elif not in_class and byte in meta:
            if len(current) >= 2:
                out.append(bytes(current))
            current.clear()
        elif not in_class:
            current.append(byte)

    if len(current) >= 2:
        out.append(bytes(current))
    return sorted(set(out))


def split_top_level_or(pattern: str) -> list[str] | None:
    parts: list[str] = []
    escaped = False
    in_class = False
    depth = 0
    last = 0
    for idx, char in enumerate(pattern):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
        elif char == "[" and not in_class:
            in_class = True
        elif char == "]" and in_class:
            in_class = False
        elif char == "(" and not in_class:
            depth += 1
        elif char == ")" and not in_class and depth > 0:
            depth -= 1
        elif char == "|" and not in_class and depth == 0:
            parts.append(pattern[last:idx])
            last = idx + 1
    if not parts:
        return None
    parts.append(pattern[last:])
    return parts


def noncapturing_alt(pattern: str) -> list[bytes] | None:
    if not pattern.startswith("(?:"):
        return None
    end = pattern.find(")")
    if end < 0:
        return None
    body = pattern[3:end]
    if not body or any(ch in body for ch in "[](){}*+?^$.\\"):
        return None
    branches = [part.encode("utf-8") for part in body.split("|") if len(part) >= 2]
    if len(branches) != len(body.split("|")):
        return None
    return sorted(set(branches))


def positive_lookbehind(pattern: str) -> bytes | None:
    prefix = "(?<="
    start = pattern.find(prefix)
    if start < 0:
        return None
    after = start + len(prefix)
    end = pattern.find(")", after)
    if end < 0:
        return None
    literal = pattern[after:end]
    if literal and not any(ch in literal for ch in "[](){}*+?|^$.\\"):
        return literal.encode("utf-8")
    return None


def selector(pattern: str, engine: str) -> tuple[str, list[bytes]]:
    if engine == "fixed":
        return "all", [pattern.encode("utf-8")]
    look = positive_lookbehind(pattern)
    if look:
        return "all", [look]
    branches = split_top_level_or(pattern)
    if branches:
        literals = []
        for branch in branches:
            runs = literal_runs(branch)
            if not runs:
                return "none", []
            literals.append(max(runs, key=len))
        return "any", sorted(set(literals))
    alt = noncapturing_alt(pattern)
    if alt:
        return "any", alt
    if "(" in pattern or ")" in pattern or "|" in pattern:
        return "none", []
    runs = literal_runs(pattern)
    if runs:
        return "all", runs
    return "none", []


def bigrams(value: bytes) -> set[int]:
    if len(value) < 2:
        return set()
    return {value[idx] << 8 | value[idx + 1] for idx in range(len(value) - 1)}


def block_bigrams(lines: list[bytes], block_lines: int) -> list[set[int]]:
    blocks: list[set[int]] = []
    for offset in range(0, len(lines), block_lines):
        data = b"".join(lines[offset:offset + block_lines])
        blocks.append(bigrams(data))
    return blocks


def select_blocks(blocks: list[set[int]], mode: str, literals: list[bytes]) -> list[int]:
    if mode == "none" or not literals:
        return list(range(len(blocks)))
    literal_bigrams = [bigrams(literal) for literal in literals]
    selected = []
    for idx, block in enumerate(blocks):
        if mode == "all":
            if all(bg and bg.issubset(block) for bg in literal_bigrams):
                selected.append(idx)
        elif mode == "any":
            if any(bg and bg.issubset(block) for bg in literal_bigrams):
                selected.append(idx)
    return selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lines", type=int, default=125000)
    parser.add_argument("--block-lines", type=int, default=4096)
    parser.add_argument("--output", default="validation_results/phase0m_postings_probe.md")
    args = parser.parse_args()

    out = REPO / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = REPO / "validation_results" / "phase0m_postings_probe_corpus.tmp"
    make_corpus(tmp, args.lines)
    raw_lines = tmp.read_bytes().splitlines(keepends=True)
    blocks = block_bigrams(raw_lines, args.block_lines)
    input_bytes = tmp.stat().st_size
    digest = sha256(tmp)
    tmp.unlink()

    doc = [
        "# zlg Phase 0m postings probe",
        "",
        "This is an offline design probe, not the final .zlg format.",
        "",
        f"- Lines: {args.lines}",
        f"- Input bytes: {input_bytes}",
        f"- Input sha256: {digest}",
        f"- Block lines: {args.block_lines}",
        f"- Blocks: {len(blocks)}",
        "",
        "| pattern | selector_mode | selector_count | selected_blocks | selected_ratio | estimated_lines |",
        "|---|---|---:|---:|---:|---:|",
    ]

    for name, engine, pattern in PATTERNS:
        mode, literals = selector(pattern, engine)
        selected = select_blocks(blocks, mode, literals)
        ratio = len(selected) / len(blocks) if blocks else 0.0
        estimated_lines = len(selected) * args.block_lines
        doc.append(
            f"| {name} | {mode} | {len(literals)} | {len(selected)} | {ratio:.3f} | {estimated_lines} |"
        )

    doc.extend([
        "",
        "## Interpretation",
        "",
        "If selected_ratio is much lower than 1.0, a future block-level or postings index may reduce decoded bytes.",
        "If selected_ratio remains 1.0 for common patterns, selector extraction or the index representation still needs work.",
    ])
    out.write_text("\n".join(doc) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
