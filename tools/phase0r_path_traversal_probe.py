#!/usr/bin/env python3
"""Phase 0r path-aware k-gram traversal probe.

This offline experiment tests a stronger index idea than independent k-gram
membership. It models path traversal for bigram, trigram, 4-gram, and literal
window variants.

The key question is whether a future index can prove that selector grams occur
as a contiguous path, not merely somewhere in the same block.

This does not change the .zlg file format.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from phase0h_bench import PATTERNS, make_corpus  # noqa: E402
from phase0m_postings_probe import selector  # noqa: E402
from phase0o_creative_index_probe import EXTRA_PATTERNS  # noqa: E402
from phase0q_needle_corpus_probe import NEEDLE_IP, make_needle_corpus  # noqa: E402


@dataclass
class Block:
    block_id: int
    first_line: int
    line_count: int
    byte_count: int
    data: bytes


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_blocks(lines: list[bytes], block_lines: int) -> list[Block]:
    blocks: list[Block] = []
    for block_id, offset in enumerate(range(0, len(lines), block_lines)):
        block_lines_data = lines[offset:offset + block_lines]
        data = b"".join(block_lines_data)
        blocks.append(
            Block(
                block_id=block_id,
                first_line=offset + 1,
                line_count=len(block_lines_data),
                byte_count=len(data),
                data=data,
            )
        )
    return blocks


def kgrams(value: bytes, k: int) -> list[bytes]:
    if k <= 0 or len(value) < k:
        return []
    return [value[idx:idx + k] for idx in range(len(value) - k + 1)]


def literal_windows(value: bytes, width: int) -> list[bytes]:
    return kgrams(value, width)


def positions_for(data: bytes, needle: bytes) -> list[int]:
    if not needle:
        return []
    out: list[int] = []
    start = 0
    while True:
        idx = data.find(needle, start)
        if idx < 0:
            return out
        out.append(idx)
        start = idx + 1


def path_exists(data: bytes, literal: bytes, k: int) -> bool:
    """Return true if the k-gram path reconstructs the literal in this block.

    For k=2 and literal=abcd, the path is ab -> bc -> cd. This is equivalent to
    checking that the literal occurs contiguously in the block, but it is written
    as a path model to match the proposed index traversal behavior.
    """
    if len(literal) < k:
        return literal in data

    first = literal[:k]
    starts = positions_for(data, first)
    if not starts:
        return False

    grams = kgrams(literal, k)
    for pos in starts:
        ok = True
        for offset, gram in enumerate(grams[1:], start=1):
            if data[pos + offset:pos + offset + k] != gram:
                ok = False
                break
        if ok:
            return True
    return False


def path_count(data: bytes, literal: bytes) -> int:
    if not literal:
        return 0
    return len(positions_for(data, literal))


def blocks_for_literal(blocks: list[Block], literal: bytes) -> set[int]:
    return {block.block_id for block in blocks if literal in block.data}


def blocks_for_kgram_all(blocks: list[Block], literal: bytes, k: int) -> set[int]:
    grams = set(kgrams(literal, k))
    if not grams:
        return blocks_for_literal(blocks, literal)
    out: set[int] = set()
    for block in blocks:
        if all(gram in block.data for gram in grams):
            out.add(block.block_id)
    return out


def blocks_for_path(blocks: list[Block], literal: bytes, k: int) -> set[int]:
    return {block.block_id for block in blocks if path_exists(block.data, literal, k)}


def blocks_for_rarest_window(blocks: list[Block], literal: bytes, width: int) -> tuple[set[int], bytes | None]:
    windows = literal_windows(literal, width)
    if not windows:
        selected = blocks_for_literal(blocks, literal)
        return selected, literal if literal else None

    df: Counter[bytes] = Counter()
    for block in blocks:
        seen = set()
        for window in windows:
            if window in block.data:
                seen.add(window)
        df.update(seen)

    # If a required window is absent globally, the literal cannot be present.
    absent = [window for window in windows if df.get(window, 0) == 0]
    if absent:
        return set(), absent[0]

    rarest = min(windows, key=lambda item: (df[item], item))
    return {block.block_id for block in blocks if rarest in block.data}, rarest


def feature_stats(blocks: list[Block], feature: bytes) -> tuple[int, int, int, int, int, float]:
    first_seen = -1
    last_seen = -1
    block_df = 0
    occurrence_count = 0

    for block in blocks:
        count = path_count(block.data, feature)
        if count > 0:
            block_df += 1
            occurrence_count += count
            if first_seen < 0:
                first_seen = block.block_id
            last_seen = block.block_id

    span = 0 if first_seen < 0 else last_seen - first_seen + 1
    density = occurrence_count / block_df if block_df else 0.0
    return first_seen, last_seen, span, block_df, occurrence_count, density


def summarize_selection(blocks: list[Block], selected: set[int]) -> tuple[int, int, float, float, int, int, int]:
    total_blocks = len(blocks)
    total_bytes = sum(block.byte_count for block in blocks)
    selected_blocks = len(selected)
    selected_bytes = sum(block.byte_count for block in blocks if block.block_id in selected)
    selected_ratio = selected_blocks / total_blocks if total_blocks else 0.0
    decoded_ratio = selected_bytes / total_bytes if total_bytes else 0.0

    if selected:
        first_selected = min(selected)
        last_selected = max(selected)
        selected_span = last_selected - first_selected + 1
    else:
        first_selected = -1
        last_selected = -1
        selected_span = 0

    return (
        selected_blocks,
        selected_bytes,
        selected_ratio,
        decoded_ratio,
        first_selected,
        last_selected,
        selected_span,
    )


def estimate_storage(blocks: list[Block], strategy: str, literal: bytes, selected: set[int]) -> tuple[int, int, int]:
    """Return raw, delta-varint, and compressed-estimate index bytes.

    This is a heuristic storage model, not a final format size.
    """
    total_blocks = len(blocks)

    if strategy == "full_scan":
        raw = 0
    elif strategy.endswith("_all_membership"):
        # Store gram -> block postings for all grams in the literal.
        if strategy.startswith("bigram"):
            gram_count = max(0, len(set(kgrams(literal, 2))))
        elif strategy.startswith("trigram"):
            gram_count = max(0, len(set(kgrams(literal, 3))))
        else:
            gram_count = max(0, len(set(kgrams(literal, 4))))
        raw = gram_count * 4 + len(selected) * 4
    elif "path" in strategy:
        # Store first gram postings plus compact path-transition hints.
        raw = 8 + len(selected) * 6 + max(0, len(literal) - 1)
    elif "window" in strategy:
        raw = len(literal) + len(selected) * 4
    elif strategy == "literal_exact_scan":
        raw = len(literal) + len(selected) * 4
    else:
        raw = len(selected) * 4

    # Block IDs delta-code well when selected sets are sparse and sorted.
    if selected:
        sorted_ids = sorted(selected)
        deltas = [sorted_ids[0]] + [
            sorted_ids[idx] - sorted_ids[idx - 1]
            for idx in range(1, len(sorted_ids))
        ]
        delta_bytes = sum(varint_len(delta) for delta in deltas)
    else:
        delta_bytes = 0

    encoded = min(raw, len(literal) + 8 + delta_bytes + max(0, len(literal) // 2))

    if raw == 0:
        compressed = 0
    else:
        # Crude compressed estimate for metadata. Real footer compression must
        # be benchmarked later.
        compressed = max(8, int(encoded * 0.65))

    return raw, encoded, compressed


def varint_len(value: int) -> int:
    if value < 0:
        return 10
    length = 1
    value >>= 7
    while value:
        length += 1
        value >>= 7
    return length


def info_bits(selected_ratio: float) -> float:
    if selected_ratio <= 0:
        return 64.0
    return -math.log2(selected_ratio)


def all_patterns() -> list[tuple[str, str, str]]:
    return list(PATTERNS) + EXTRA_PATTERNS + [
        ("needle_exact_ip", "regex", f"src_ip={NEEDLE_IP}"),
        ("needle_ip_value", "fixed", NEEDLE_IP),
        ("needle_request_id_prefix", "fixed", "NEEDLE-001000"),
    ]


def make_combined_corpus(lines: int, needle_ratio: float) -> tuple[Path, int]:
    path = REPO / "validation_results" / "phase0r_path_corpus.tmp"
    needle_line = make_needle_corpus(path, lines, needle_ratio)
    return path, needle_line


def run_probe(lines: int, needle_ratio: float, block_sizes: list[int]) -> tuple[list[dict[str, object]], dict[str, object]]:
    corpus, needle_line = make_combined_corpus(lines, needle_ratio)
    raw = corpus.read_bytes()
    raw_lines = raw.splitlines(keepends=True)
    digest = sha256(corpus)
    input_bytes = corpus.stat().st_size
    corpus.unlink()

    rows: list[dict[str, object]] = []
    for block_lines in block_sizes:
        blocks = build_blocks(raw_lines, block_lines)
        total_blocks = len(blocks)

        for pattern_name, engine, pattern in all_patterns():
            mode, literals = selector(pattern, engine)
            if mode == "none" or not literals:
                literal_items: list[tuple[str, bytes]] = []
            else:
                literal_items = [(mode, item) for item in literals]

            if not literal_items:
                selected = set(range(total_blocks))
                rows.append(row_for(
                    blocks,
                    pattern_name,
                    engine,
                    pattern,
                    "none",
                    0,
                    b"",
                    block_lines,
                    "full_scan_no_selector",
                    selected,
                    b"",
                    needle_line,
                ))
                continue

            for selector_index, (_, literal) in enumerate(literal_items):
                strategy_selections: list[tuple[str, set[int], bytes]] = []

                strategy_selections.append(("full_scan", set(range(total_blocks)), b""))
                strategy_selections.append(("bigram_all_membership", blocks_for_kgram_all(blocks, literal, 2), literal[:2]))
                strategy_selections.append(("trigram_all_membership", blocks_for_kgram_all(blocks, literal, 3), literal[:3]))
                strategy_selections.append(("fourgram_all_membership", blocks_for_kgram_all(blocks, literal, 4), literal[:4]))
                strategy_selections.append(("bigram_path_traversal", blocks_for_path(blocks, literal, 2), literal[:2]))
                strategy_selections.append(("trigram_path_traversal", blocks_for_path(blocks, literal, 3), literal[:3]))
                strategy_selections.append(("fourgram_path_traversal", blocks_for_path(blocks, literal, 4), literal[:4]))
                strategy_selections.append(("literal_exact_scan", blocks_for_literal(blocks, literal), literal))

                for width in (4, 6, 8, 12):
                    selected, feature = blocks_for_rarest_window(blocks, literal, width)
                    strategy_selections.append((f"rarest_window_{width}", selected, feature or b""))

                for strategy, selected, feature in strategy_selections:
                    rows.append(row_for(
                        blocks,
                        pattern_name,
                        engine,
                        pattern,
                        mode,
                        selector_index + 1,
                        literal,
                        block_lines,
                        strategy,
                        selected,
                        feature,
                        needle_line,
                    ))

    meta = {
        "lines": lines,
        "input_bytes": input_bytes,
        "sha256": digest,
        "needle_ip": NEEDLE_IP,
        "needle_line": needle_line,
        "needle_line_ratio": needle_line / lines,
    }
    return rows, meta


def row_for(
    blocks: list[Block],
    pattern_name: str,
    engine: str,
    pattern: str,
    selector_mode: str,
    selector_index: int,
    literal: bytes,
    block_lines: int,
    strategy: str,
    selected: set[int],
    feature: bytes,
    needle_line: int,
) -> dict[str, object]:
    (
        selected_blocks,
        selected_bytes,
        selected_ratio,
        decoded_ratio,
        first_selected,
        last_selected,
        selected_span,
    ) = summarize_selection(blocks, selected)

    first_seen, last_seen, feature_span, feature_df, feature_count, feature_density = (
        feature_stats(blocks, feature) if feature else (-1, -1, 0, 0, 0, 0.0)
    )
    raw_bytes, encoded_bytes, compressed_bytes = estimate_storage(blocks, strategy, literal, selected)

    needle_block = (needle_line - 1) // block_lines
    contains_needle = "yes" if needle_block in selected else "no"

    return {
        "pattern_name": pattern_name,
        "engine": engine,
        "pattern": pattern,
        "selector_mode": selector_mode,
        "selector_index": selector_index,
        "literal": literal.decode("utf-8", "replace"),
        "literal_len": len(literal),
        "block_lines": block_lines,
        "total_blocks": len(blocks),
        "strategy": strategy,
        "selected_blocks": selected_blocks,
        "selected_bytes": selected_bytes,
        "selected_ratio": f"{selected_ratio:.6f}",
        "decoded_ratio": f"{decoded_ratio:.6f}",
        "first_selected_block": first_selected,
        "last_selected_block": last_selected,
        "selected_block_span": selected_span,
        "feature": feature.decode("utf-8", "replace") if feature else "",
        "feature_len": len(feature),
        "feature_first_seen_block": first_seen,
        "feature_last_seen_block": last_seen,
        "feature_block_span": feature_span,
        "feature_block_df": feature_df,
        "feature_occurrence_count": feature_count,
        "feature_density": f"{feature_density:.6f}",
        "feature_info_bits": f"{info_bits(selected_ratio):.6f}",
        "estimated_raw_index_bytes": raw_bytes,
        "estimated_delta_varint_bytes": encoded_bytes,
        "estimated_compressed_index_bytes": compressed_bytes,
        "needle_block": needle_block,
        "contains_needle_block": contains_needle,
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "pattern_name",
        "engine",
        "pattern",
        "selector_mode",
        "selector_index",
        "literal",
        "literal_len",
        "block_lines",
        "total_blocks",
        "strategy",
        "selected_blocks",
        "selected_bytes",
        "selected_ratio",
        "decoded_ratio",
        "first_selected_block",
        "last_selected_block",
        "selected_block_span",
        "feature",
        "feature_len",
        "feature_first_seen_block",
        "feature_last_seen_block",
        "feature_block_span",
        "feature_block_df",
        "feature_occurrence_count",
        "feature_density",
        "feature_info_bits",
        "estimated_raw_index_bytes",
        "estimated_delta_varint_bytes",
        "estimated_compressed_index_bytes",
        "needle_block",
        "contains_needle_block",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, object]], meta: dict[str, object]) -> None:
    needle_rows = [row for row in rows if str(row["pattern_name"]).startswith("needle")]
    best_needle = sorted(
        needle_rows,
        key=lambda row: (
            row["contains_needle_block"] != "yes",
            float(row["decoded_ratio"]),
            int(row["estimated_compressed_index_bytes"]),
            row["strategy"],
        ),
    )[:12]

    by_strategy: defaultdict[str, list[float]] = defaultdict(list)
    for row in rows:
        by_strategy[str(row["strategy"])].append(float(row["decoded_ratio"]))

    strategy_summary = [
        (strategy, sum(values) / len(values), min(values), max(values), len(values))
        for strategy, values in by_strategy.items()
    ]
    strategy_summary.sort(key=lambda item: (item[1], item[0]))

    doc = [
        "# zlg Phase 0r path-aware traversal probe",
        "",
        "This offline probe tests path-aware literal traversal over bigram, trigram,",
        "4-gram, and longer window variants. It also tracks first-seen, span, count,",
        "density, information, and estimated storage overhead per strategy.",
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
        "## Best needle strategies",
        "",
        "| pattern | block_lines | strategy | selected_blocks | decoded_ratio | feature | first_seen | count | compressed_index_est |",
        "|---|---:|---|---:|---:|---|---:|---:|---:|",
    ]
    for row in best_needle:
        doc.append(
            f"| {row['pattern_name']} | {row['block_lines']} | {row['strategy']} | "
            f"{row['selected_blocks']} | {float(row['decoded_ratio']):.6f} | "
            f"{row['feature']} | {row['feature_first_seen_block']} | "
            f"{row['feature_occurrence_count']} | {row['estimated_compressed_index_bytes']} |"
        )

    doc.extend([
        "",
        "## Strategy decoded-ratio summary",
        "",
        "| strategy | mean_decoded_ratio | min | max | rows |",
        "|---|---:|---:|---:|---:|",
    ])
    for strategy, mean_value, min_value, max_value, count in strategy_summary:
        doc.append(f"| {strategy} | {mean_value:.6f} | {min_value:.6f} | {max_value:.6f} | {count} |")

    doc.extend([
        "",
        "## Interpretation",
        "",
        "- Membership strategies ask whether all grams exist somewhere in the block.",
        "- Path traversal asks whether the grams reconstruct the selector literal contiguously.",
        "- Rarest windows use longer contiguous byte windows as selective features.",
        "- `feature_first_seen_block`, `feature_occurrence_count`, and `feature_block_span`",
        "  are the first step toward a weighted planner with locality awareness.",
        "- Storage estimates are heuristic and must be replaced by real encoded footer",
        "  measurements before format freeze.",
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
    parser.add_argument("--output", default="validation_results/phase0r_path_traversal_probe.md")
    parser.add_argument("--csv", default="validation_results/phase0r_path_traversal_probe.csv")
    args = parser.parse_args()

    rows, meta = run_probe(args.lines, args.needle_ratio, parse_block_lines(args.block_lines))
    write_csv(REPO / args.csv, rows)
    write_markdown(REPO / args.output, rows, meta)
    print(f"wrote {REPO / args.output}")
    print(f"wrote {REPO / args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
