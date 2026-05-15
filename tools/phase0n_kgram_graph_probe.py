#!/usr/bin/env python3
"""Phase 0n k-gram graph/postings probe.

This is an offline design probe. It does not change the .zlg format. It builds
block-level bigram, trigram, and bigram-edge graph summaries over the
same deterministic corpus used by the prebench harness. The purpose is to
estimate whether a future graph/postings index can reduce selected blocks and
decoded bytes enough to justify metadata cost.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from phase0h_bench import PATTERNS, make_corpus, sha256  # noqa: E402
from phase0m_postings_probe import selector  # noqa: E402


@dataclass(frozen=True)
class BlockStats:
    block_id: int
    first_line: int
    line_count: int
    byte_count: int
    bigrams: frozenset[int]
    trigrams: frozenset[int]
    edges: frozenset[tuple[int, int]]


def grams2(value: bytes) -> set[int]:
    if len(value) < 2:
        return set()
    return {value[idx] << 8 | value[idx + 1] for idx in range(len(value) - 1)}


def grams3(value: bytes) -> set[int]:
    if len(value) < 3:
        return set()
    return {
        value[idx] << 16 | value[idx + 1] << 8 | value[idx + 2]
        for idx in range(len(value) - 2)
    }


def bigram_edges(value: bytes) -> set[tuple[int, int]]:
    if len(value) < 3:
        return set()
    out: set[tuple[int, int]] = set()
    for idx in range(len(value) - 2):
        left = value[idx] << 8 | value[idx + 1]
        right = value[idx + 1] << 8 | value[idx + 2]
        out.add((left, right))
    return out


def literal_edge_path(value: bytes) -> set[tuple[int, int]]:
    return bigram_edges(value)


def build_blocks(lines: list[bytes], block_lines: int) -> list[BlockStats]:
    blocks: list[BlockStats] = []
    for block_id, offset in enumerate(range(0, len(lines), block_lines)):
        block_lines_data = lines[offset:offset + block_lines]
        data = b"".join(block_lines_data)
        blocks.append(
            BlockStats(
                block_id=block_id,
                first_line=offset + 1,
                line_count=len(block_lines_data),
                byte_count=len(data),
                bigrams=frozenset(grams2(data)),
                trigrams=frozenset(grams3(data)),
                edges=frozenset(bigram_edges(data)),
            )
        )
    return blocks


def frequency_counter(blocks: list[BlockStats], attr: str) -> Counter[int]:
    counter: Counter[int] = Counter()
    for block in blocks:
        values = getattr(block, attr)
        counter.update(values)
    return counter


def select_bigram(blocks: list[BlockStats], mode: str, literals: list[bytes]) -> set[int]:
    if mode == "none" or not literals:
        return {block.block_id for block in blocks}
    literal_sets = [grams2(literal) for literal in literals]
    selected: set[int] = set()
    for block in blocks:
        if mode == "all":
            if all(gs and gs.issubset(block.bigrams) for gs in literal_sets):
                selected.add(block.block_id)
        elif mode == "any":
            if any(gs and gs.issubset(block.bigrams) for gs in literal_sets):
                selected.add(block.block_id)
    return selected


def select_trigram(blocks: list[BlockStats], mode: str, literals: list[bytes]) -> set[int]:
    if mode == "none" or not literals:
        return {block.block_id for block in blocks}
    literal_sets = [grams3(literal) for literal in literals if len(literal) >= 3]
    if not literal_sets:
        return select_bigram(blocks, mode, literals)
    selected: set[int] = set()
    for block in blocks:
        if mode == "all":
            if all(gs and gs.issubset(block.trigrams) for gs in literal_sets):
                selected.add(block.block_id)
        elif mode == "any":
            if any(gs and gs.issubset(block.trigrams) for gs in literal_sets):
                selected.add(block.block_id)
    return selected


def select_graph_edges(blocks: list[BlockStats], mode: str, literals: list[bytes]) -> set[int]:
    if mode == "none" or not literals:
        return {block.block_id for block in blocks}
    literal_paths = [literal_edge_path(literal) for literal in literals if len(literal) >= 3]
    if not literal_paths:
        return select_bigram(blocks, mode, literals)
    selected: set[int] = set()
    for block in blocks:
        if mode == "all":
            if all(path and path.issubset(block.edges) for path in literal_paths):
                selected.add(block.block_id)
        elif mode == "any":
            if any(path and path.issubset(block.edges) for path in literal_paths):
                selected.add(block.block_id)
    return selected


def select_rarest_kgram(
    blocks: list[BlockStats],
    mode: str,
    literals: list[bytes],
    bigram_freq: Counter[int],
    trigram_freq: Counter[int],
    rarest_count: int,
) -> set[int]:
    if mode == "none" or not literals:
        return {block.block_id for block in blocks}

    literal_selected: list[set[int]] = []
    for literal in literals:
        candidates: list[tuple[int, str, int]] = []
        for gram in grams2(literal):
            candidates.append((bigram_freq.get(gram, 0), "bigram", gram))
        for gram in grams3(literal):
            candidates.append((trigram_freq.get(gram, 0), "trigram", gram))
        # Keep zero-frequency grams. If a required literal contains a gram that
        # is absent globally, the selected block set should be empty, not all
        # blocks. Phase 0n filtered zero-frequency grams and therefore made the
        # no-match rarest-kgram path look worse than it should.
        candidates.sort(key=lambda item: (item[0], item[1], item[2]))
        chosen = candidates[:max(1, rarest_count)]
        if not chosen:
            # Literal too short to produce grams; no safe pruning.
            literal_selected.append({block.block_id for block in blocks})
            continue

        selected_for_literal: set[int] = set()
        for block in blocks:
            ok = True
            for _freq, kind, gram in chosen:
                if kind == "bigram" and gram not in block.bigrams:
                    ok = False
                    break
                if kind == "trigram" and gram not in block.trigrams:
                    ok = False
                    break
            if ok:
                selected_for_literal.add(block.block_id)
        literal_selected.append(selected_for_literal)

    if not literal_selected:
        return {block.block_id for block in blocks}

    if mode == "all":
        out = set(literal_selected[0])
        for item in literal_selected[1:]:
            out &= item
        return out

    if mode == "any":
        out: set[int] = set()
        for item in literal_selected:
            out |= item
        return out

    return {block.block_id for block in blocks}


def estimated_index_bytes(blocks: list[BlockStats]) -> dict[str, int]:
    # These are intentionally simple lower-bound estimates for comparison only.
    # A real format would delta-code, varint-code, section, and compress metadata.
    bigram_postings = sum(len(block.bigrams) for block in blocks)
    trigram_postings = sum(len(block.trigrams) for block in blocks)
    edge_postings = sum(len(block.edges) for block in blocks)
    return {
        "bigram_postings_est_bytes": bigram_postings * 6,
        "trigram_postings_est_bytes": trigram_postings * 7,
        "graph_edge_est_bytes": edge_postings * 8,
    }


def summarize_selection(blocks: list[BlockStats], selected: set[int]) -> tuple[int, int, float, float]:
    total_blocks = len(blocks)
    selected_blocks = len(selected)
    selected_bytes = sum(block.byte_count for block in blocks if block.block_id in selected)
    total_bytes = sum(block.byte_count for block in blocks)
    selected_ratio = selected_blocks / total_blocks if total_blocks else 0.0
    decoded_ratio = selected_bytes / total_bytes if total_bytes else 0.0
    return selected_blocks, selected_bytes, selected_ratio, decoded_ratio


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "pattern_name",
        "engine",
        "pattern",
        "selector_mode",
        "selector_count",
        "strategy",
        "block_lines",
        "total_blocks",
        "selected_blocks",
        "selected_ratio",
        "estimated_decoded_bytes",
        "estimated_decoded_ratio",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_markdown(
    path: Path,
    rows: list[dict[str, object]],
    *,
    lines: int,
    input_bytes: int,
    digest: str,
    block_lines: int,
    blocks: list[BlockStats],
    index_bytes: dict[str, int],
) -> None:
    best_by_pattern: dict[str, dict[str, object]] = {}
    for row in rows:
        name = str(row["pattern_name"])
        ratio = float(row["estimated_decoded_ratio"])
        if name not in best_by_pattern or ratio < float(best_by_pattern[name]["estimated_decoded_ratio"]):
            best_by_pattern[name] = row

    doc = [
        "# zlg Phase 0n k-gram graph probe",
        "",
        "This is an offline design probe. It does not change the .zlg format.",
        "",
        "## Corpus",
        "",
        f"- Lines: {lines}",
        f"- Input bytes: {input_bytes}",
        f"- Input sha256: {digest}",
        f"- Block lines: {block_lines}",
        f"- Blocks: {len(blocks)}",
        "",
        "## Estimated raw index sizes",
        "",
        "These are lower-bound comparison estimates before delta/varint coding or compression.",
        "",
        "| index | estimated bytes |",
        "|---|---:|",
    ]
    for key, value in index_bytes.items():
        doc.append(f"| {key} | {value} |")

    doc.extend([
        "",
        "## Best strategy by pattern",
        "",
        "| pattern | selector | best_strategy | selected_blocks | decoded_ratio |",
        "|---|---|---|---:|---:|",
    ])
    for name in sorted(best_by_pattern):
        row = best_by_pattern[name]
        doc.append(
            f"| {name} | {row['selector_mode']}:{row['selector_count']} | "
            f"{row['strategy']} | {row['selected_blocks']} | "
            f"{float(row['estimated_decoded_ratio']):.3f} |"
        )

    doc.extend([
        "",
        "## Full strategy table",
        "",
        "| pattern | selector | strategy | selected_blocks | selected_ratio | decoded_ratio |",
        "|---|---|---|---:|---:|---:|",
    ])
    for row in rows:
        doc.append(
            f"| {row['pattern_name']} | {row['selector_mode']}:{row['selector_count']} | "
            f"{row['strategy']} | {row['selected_blocks']} | "
            f"{float(row['selected_ratio']):.3f} | "
            f"{float(row['estimated_decoded_ratio']):.3f} |"
        )

    doc.extend([
        "",
        "## Interpretation",
        "",
        "- bigram_block models current block-level bigram presence.",
        "- trigram_sparse models sparse trigram postings.",
        "- bigram_graph_edges models overlapping bigram edges, equivalent to observed trigrams.",
        "- rarest_kgram_2 chooses the two rarest bigrams/trigrams from each selector literal.",
        "",
        "A strategy is promising only if it materially reduces estimated decoded bytes while keeping estimated index bytes low enough that total .zlg size can still beat gzip.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lines", type=int, default=125000)
    parser.add_argument("--block-lines", type=int, default=4096)
    parser.add_argument("--output", default="validation_results/phase0n_kgram_graph_probe.md")
    parser.add_argument("--csv", default="validation_results/phase0n_kgram_graph_probe.csv")
    args = parser.parse_args()

    tmp = REPO / "validation_results" / "phase0n_kgram_graph_probe_corpus.tmp"
    make_corpus(tmp, args.lines)
    raw = tmp.read_bytes()
    raw_lines = raw.splitlines(keepends=True)
    digest = sha256(tmp)
    input_bytes = tmp.stat().st_size
    tmp.unlink()

    blocks = build_blocks(raw_lines, args.block_lines)
    bigram_freq = frequency_counter(blocks, "bigrams")
    trigram_freq = frequency_counter(blocks, "trigrams")
    index_bytes = estimated_index_bytes(blocks)

    rows: list[dict[str, object]] = []
    for name, engine, pattern in PATTERNS:
        mode, literals = selector(pattern, engine)
        strategies = {
            "bigram_block": select_bigram(blocks, mode, literals),
            "trigram_sparse": select_trigram(blocks, mode, literals),
            "bigram_graph_edges": select_graph_edges(blocks, mode, literals),
            "rarest_kgram_2": select_rarest_kgram(
                blocks, mode, literals, bigram_freq, trigram_freq, 2
            ),
        }
        for strategy, selected in strategies.items():
            selected_blocks, selected_bytes, selected_ratio, decoded_ratio = summarize_selection(
                blocks, selected
            )
            rows.append({
                "pattern_name": name,
                "engine": engine,
                "pattern": pattern,
                "selector_mode": mode,
                "selector_count": len(literals),
                "strategy": strategy,
                "block_lines": args.block_lines,
                "total_blocks": len(blocks),
                "selected_blocks": selected_blocks,
                "selected_ratio": f"{selected_ratio:.6f}",
                "estimated_decoded_bytes": selected_bytes,
                "estimated_decoded_ratio": f"{decoded_ratio:.6f}",
            })

    csv_path = REPO / args.csv
    md_path = REPO / args.output
    write_csv(csv_path, rows)
    write_markdown(
        md_path,
        rows,
        lines=args.lines,
        input_bytes=input_bytes,
        digest=digest,
        block_lines=args.block_lines,
        blocks=blocks,
        index_bytes=index_bytes,
    )

    print(f"wrote {md_path}")
    print(f"wrote {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
