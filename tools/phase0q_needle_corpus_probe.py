#!/usr/bin/env python3
"""Phase 0q needle-in-haystack probe.

This offline probe generates deterministic sample data where one specific IP
address appears exactly once, around 80 percent into the log volume. It then
estimates how different block sizes and k-gram strategies narrow the candidate
blocks for that exact needle query.

No generated corpus is committed. Only compact CSV/Markdown results are saved.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
from pathlib import Path
import sys
from collections import Counter

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from phase0m_postings_probe import selector  # noqa: E402


NEEDLE_IP = "198.18.99.123"


def make_needle_corpus(path: Path, lines: int, needle_ratio: float) -> int:
    needle_index = max(0, min(lines - 1, int(lines * needle_ratio)))
    with path.open("w", encoding="utf-8") as handle:
        for i in range(lines):
            if i == needle_index:
                handle.write(
                    f"warn event_id={i} src_ip={NEEDLE_IP} "
                    f"request_id=NEEDLE-{i:08d} user=needle_user "
                    f"msg=find-the-needle marker=unique_ip\n"
                )
            elif i % 97 == 0:
                handle.write(
                    f"error key=\"abc{i}\" src_ip=192.0.2.{i % 255} "
                    f"foo{i % 10} component=auth\n"
                )
            elif i % 131 == 0:
                handle.write(
                    f"failed password user=test{i} "
                    f"src_ip=198.51.100.{i % 255} component=sshd\n"
                )
            elif i % 211 == 0:
                handle.write(
                    f"denied action=drop bar{i % 10} key=\"deny{i}\" "
                    f"src_ip=10.0.{i % 255}.{(i * 7) % 255}\n"
                )
            else:
                handle.write(
                    f"info event_id={i} src_ip=203.0.113.{i % 255} "
                    f"msg=normal component=app shard={i % 16}\n"
                )
    return needle_index + 1


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def grams2(data: bytes) -> set[int]:
    return {data[idx] << 8 | data[idx + 1] for idx in range(max(0, len(data) - 1))}


def grams3(data: bytes) -> set[int]:
    return {
        data[idx] << 16 | data[idx + 1] << 8 | data[idx + 2]
        for idx in range(max(0, len(data) - 2))
    }


def edges(data: bytes) -> set[tuple[int, int]]:
    out: set[tuple[int, int]] = set()
    for idx in range(max(0, len(data) - 2)):
        left = data[idx] << 8 | data[idx + 1]
        right = data[idx + 1] << 8 | data[idx + 2]
        out.add((left, right))
    return out


def build_blocks(lines: list[bytes], block_lines: int) -> list[dict[str, object]]:
    blocks = []
    for block_id, offset in enumerate(range(0, len(lines), block_lines)):
        block_lines_data = lines[offset:offset + block_lines]
        data = b"".join(block_lines_data)
        blocks.append({
            "block_id": block_id,
            "first_line": offset + 1,
            "line_count": len(block_lines_data),
            "byte_count": len(data),
            "bigrams": grams2(data),
            "trigrams": grams3(data),
            "edges": edges(data),
        })
    return blocks


def df(blocks: list[dict[str, object]], key: str) -> Counter:
    out: Counter = Counter()
    for block in blocks:
        out.update(block[key])
    return out


def block_ids(blocks: list[dict[str, object]]) -> set[int]:
    return {int(block["block_id"]) for block in blocks}


def with_all(blocks: list[dict[str, object]], key: str, wanted: set) -> set[int]:
    if not wanted:
        return set(block_ids(blocks))
    return {
        int(block["block_id"])
        for block in blocks
        if wanted.issubset(block[key])
    }


def rarest_features(
    literal: bytes,
    bigram_df: Counter,
    trigram_df: Counter,
    edge_df: Counter,
    count: int,
) -> tuple[str, set]:
    candidates: list[tuple[int, str, object]] = []
    for gram in grams2(literal):
        candidates.append((bigram_df.get(gram, 0), "bigram", gram))
    for gram in grams3(literal):
        candidates.append((trigram_df.get(gram, 0), "trigram", gram))
    for edge in edges(literal):
        candidates.append((edge_df.get(edge, 0), "edge", edge))
    candidates.sort(key=lambda item: (item[0], item[1], str(item[2])))

    if not candidates:
        return "none", set()

    chosen = candidates[:count]
    kind = "mixed"
    if all(item[1] == "bigram" for item in chosen):
        kind = "bigram"
    elif all(item[1] == "trigram" for item in chosen):
        kind = "trigram"
    elif all(item[1] == "edge" for item in chosen):
        kind = "edge"
    return kind, {item[2] for item in chosen}


def estimate(
    blocks: list[dict[str, object]],
    selected: set[int],
) -> tuple[int, int, float, float]:
    total_blocks = len(blocks)
    total_bytes = sum(int(block["byte_count"]) for block in blocks)
    selected_bytes = sum(
        int(block["byte_count"])
        for block in blocks
        if int(block["block_id"]) in selected
    )
    return (
        len(selected),
        selected_bytes,
        len(selected) / total_blocks if total_blocks else 0.0,
        selected_bytes / total_bytes if total_bytes else 0.0,
    )


def info_bits(selected_ratio: float) -> float:
    if selected_ratio <= 0.0:
        return 64.0
    return -math.log2(selected_ratio)


def run_probe(lines: int, needle_ratio: float, block_sizes: list[int]) -> tuple[list[dict[str, object]], dict[str, object]]:
    tmp = REPO / "validation_results" / "phase0q_needle_corpus.tmp"
    needle_line = make_needle_corpus(tmp, lines, needle_ratio)
    raw = tmp.read_bytes()
    raw_lines = raw.splitlines(keepends=True)
    digest = sha256(tmp)
    input_bytes = tmp.stat().st_size
    tmp.unlink()

    pattern = f"src_ip={NEEDLE_IP}"
    mode, literals = selector(pattern, "regex")
    if mode == "none" or not literals:
        raise SystemExit("needle selector extraction failed")

    literal = literals[0]
    rows: list[dict[str, object]] = []

    for block_lines in block_sizes:
        blocks = build_blocks(raw_lines, block_lines)
        needle_block = (needle_line - 1) // block_lines
        total_blocks = len(blocks)
        bigram_df = df(blocks, "bigrams")
        trigram_df = df(blocks, "trigrams")
        edge_df = df(blocks, "edges")

        strategies: list[tuple[str, set[int]]] = [
            ("full_scan", block_ids(blocks)),
            ("bigram_all", with_all(blocks, "bigrams", grams2(literal))),
            ("trigram_all", with_all(blocks, "trigrams", grams3(literal))),
            ("edge_all", with_all(blocks, "edges", edges(literal))),
        ]

        for count in (1, 2, 4):
            kind, wanted = rarest_features(literal, bigram_df, trigram_df, edge_df, count)
            key = {
                "bigram": "bigrams",
                "trigram": "trigrams",
                "edge": "edges",
                "mixed": "mixed",
                "none": "none",
            }[kind]
            if key == "mixed":
                selected = block_ids(blocks)
                for feature in wanted:
                    if isinstance(feature, tuple):
                        selected &= with_all(blocks, "edges", {feature})
                    elif isinstance(feature, int) and feature > 0xFFFF:
                        selected &= with_all(blocks, "trigrams", {feature})
                    else:
                        selected &= with_all(blocks, "bigrams", {feature})
            elif key == "none":
                selected = block_ids(blocks)
            else:
                selected = with_all(blocks, key, wanted)
            strategies.append((f"rarest_{count}_{kind}", selected))

        for strategy, selected in strategies:
            selected_blocks, selected_bytes, selected_ratio, decoded_ratio = estimate(blocks, selected)
            rows.append({
                "pattern_name": "needle_exact_ip",
                "pattern": pattern,
                "needle_ip": NEEDLE_IP,
                "needle_line": needle_line,
                "needle_line_ratio": f"{needle_line / lines:.6f}",
                "block_lines": block_lines,
                "total_blocks": total_blocks,
                "needle_block": needle_block,
                "strategy": strategy,
                "selected_blocks": selected_blocks,
                "selected_bytes": selected_bytes,
                "selected_ratio": f"{selected_ratio:.6f}",
                "decoded_ratio": f"{decoded_ratio:.6f}",
                "contains_needle_block": "yes" if needle_block in selected else "no",
                "info_bits": f"{info_bits(selected_ratio):.6f}",
            })

    meta = {
        "lines": lines,
        "input_bytes": input_bytes,
        "sha256": digest,
        "needle_ip": NEEDLE_IP,
        "needle_line": needle_line,
        "needle_line_ratio": needle_line / lines,
    }
    return rows, meta


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "pattern_name",
        "pattern",
        "needle_ip",
        "needle_line",
        "needle_line_ratio",
        "block_lines",
        "total_blocks",
        "needle_block",
        "strategy",
        "selected_blocks",
        "selected_bytes",
        "selected_ratio",
        "decoded_ratio",
        "contains_needle_block",
        "info_bits",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, object]], meta: dict[str, object]) -> None:
    best = sorted(
        rows,
        key=lambda row: (
            row["contains_needle_block"] != "yes",
            float(row["decoded_ratio"]),
            int(row["selected_blocks"]),
            row["strategy"],
        ),
    )[:8]

    doc = [
        "# zlg Phase 0q needle-in-haystack probe",
        "",
        "This offline probe creates deterministic sample data where one specific IP",
        "appears exactly once, about 80 percent into the log volume.",
        "",
        "The generated corpus is not committed. Only compact CSV/Markdown results are saved.",
        "",
        "## Corpus",
        "",
        f"- Lines: {meta['lines']}",
        f"- Input bytes: {meta['input_bytes']}",
        f"- Input sha256: {meta['sha256']}",
        f"- Needle IP: {meta['needle_ip']}",
        f"- Needle line: {meta['needle_line']}",
        f"- Needle line ratio: {float(meta['needle_line_ratio']):.3f}",
        "",
        "## Best candidate selections",
        "",
        "| block_lines | strategy | selected_blocks | decoded_ratio | contains_needle | info_bits |",
        "|---:|---|---:|---:|---|---:|",
    ]
    for row in best:
        doc.append(
            f"| {row['block_lines']} | {row['strategy']} | {row['selected_blocks']} | "
            f"{float(row['decoded_ratio']):.6f} | {row['contains_needle_block']} | "
            f"{float(row['info_bits']):.2f} |"
        )

    doc.extend([
        "",
        "## Full table",
        "",
        "| block_lines | total_blocks | needle_block | strategy | selected_blocks | selected_ratio | decoded_ratio | contains_needle |",
        "|---:|---:|---:|---|---:|---:|---:|---|",
    ])
    for row in rows:
        doc.append(
            f"| {row['block_lines']} | {row['total_blocks']} | {row['needle_block']} | "
            f"{row['strategy']} | {row['selected_blocks']} | {float(row['selected_ratio']):.6f} | "
            f"{float(row['decoded_ratio']):.6f} | {row['contains_needle_block']} |"
        )

    doc.extend([
        "",
        "## Interpretation",
        "",
        "If a strategy selects one block and contains the needle block, the offline index",
        "has enough selectivity to support a real sparse search-block prototype.",
        "",
        "The next runtime experiment should test whether the same decoded-ratio gain",
        "turns into wall-clock speedup after adding independently decodable search blocks.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")


def parse_block_lines(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lines", type=int, default=125000)
    parser.add_argument("--needle-ratio", type=float, default=0.80)
    parser.add_argument("--block-lines", default="512,1024,2048,4096")
    parser.add_argument("--output", default="validation_results/phase0q_needle_probe.md")
    parser.add_argument("--csv", default="validation_results/phase0q_needle_probe.csv")
    args = parser.parse_args()

    rows, meta = run_probe(args.lines, args.needle_ratio, parse_block_lines(args.block_lines))
    write_csv(REPO / args.csv, rows)
    write_markdown(REPO / args.output, rows, meta)
    print(f"wrote {REPO / args.output}")
    print(f"wrote {REPO / args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
