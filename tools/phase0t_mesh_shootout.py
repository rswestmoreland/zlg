#!/usr/bin/env python3
"""Phase 0t offline k-gram mesh shootout.

This experiment compares multiple implementation strategies for a k-gram mesh
before changing the .zlg format again.

It models candidate block selection, graph/path traversal behavior, group-local
indexes, and heuristic storage overhead for bigram and trigram mesh variants.
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

from phase0h_bench import PATTERNS  # noqa: E402
from phase0m_postings_probe import selector  # noqa: E402
from phase0o_creative_index_probe import EXTRA_PATTERNS  # noqa: E402
from phase0q_needle_corpus_probe import NEEDLE_IP, make_needle_corpus  # noqa: E402


@dataclass
class Block:
    block_id: int
    group_id: int
    first_line: int
    line_count: int
    byte_count: int
    data: bytes


@dataclass
class EdgeStats:
    edge_count: int
    edge_occurrences: int
    postings_entries: int
    raw_index_bytes: int
    delta_varint_bytes: int
    compressed_estimate_bytes: int


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_corpus(lines: int, needle_ratio: float) -> tuple[list[bytes], dict[str, object]]:
    tmp = REPO / "validation_results" / "phase0t_mesh_corpus.tmp"
    needle_line = make_needle_corpus(tmp, lines, needle_ratio)
    raw = tmp.read_bytes()
    digest = sha256(tmp)
    input_bytes = tmp.stat().st_size
    raw_lines = raw.splitlines(keepends=True)
    tmp.unlink()
    return raw_lines, {
        "lines": lines,
        "input_bytes": input_bytes,
        "sha256": digest,
        "needle_ip": NEEDLE_IP,
        "needle_line": needle_line,
        "needle_ratio": needle_line / lines,
    }


def make_blocks(lines: list[bytes], block_lines: int, group_lines: int) -> list[Block]:
    blocks: list[Block] = []
    for block_id, offset in enumerate(range(0, len(lines), block_lines)):
        line_slice = lines[offset:offset + block_lines]
        group_id = offset // group_lines
        data = b"".join(line_slice)
        blocks.append(Block(
            block_id=block_id,
            group_id=group_id,
            first_line=offset + 1,
            line_count=len(line_slice),
            byte_count=len(data),
            data=data,
        ))
    return blocks


def grams(value: bytes, k: int) -> list[bytes]:
    if k <= 0 or len(value) < k:
        return []
    return [value[idx:idx + k] for idx in range(len(value) - k + 1)]


def edges(value: bytes, k: int) -> list[tuple[bytes, bytes]]:
    path = grams(value, k)
    return list(zip(path, path[1:]))


def positions(data: bytes, needle: bytes) -> list[int]:
    if not needle:
        return []
    out: list[int] = []
    start = 0
    while True:
        found = data.find(needle, start)
        if found < 0:
            return out
        out.append(found)
        start = found + 1


def path_exists(data: bytes, literal: bytes, k: int) -> bool:
    if len(literal) < k:
        return literal in data
    first = literal[:k]
    starts = positions(data, first)
    if not starts:
        return False
    literal_grams = grams(literal, k)
    for start in starts:
        ok = True
        for offset, gram in enumerate(literal_grams[1:], start=1):
            if data[start + offset:start + offset + k] != gram:
                ok = False
                break
        if ok:
            return True
    return False


def block_edges(block: Block, k: int) -> set[tuple[bytes, bytes]]:
    return set(edges(block.data, k))


def block_grams(block: Block, k: int) -> set[bytes]:
    return set(grams(block.data, k))


def edge_frequency(blocks: list[Block], k: int) -> tuple[Counter, Counter]:
    df: Counter = Counter()
    occ: Counter = Counter()
    for block in blocks:
        edge_list = edges(block.data, k)
        occ.update(edge_list)
        df.update(set(edge_list))
    return df, occ


def group_edge_frequency(blocks: list[Block], k: int) -> dict[int, Counter]:
    out: dict[int, Counter] = defaultdict(Counter)
    for block in blocks:
        out[block.group_id].update(set(edges(block.data, k)))
    return dict(out)


def blocks_for_edge_all(blocks: list[Block], literal: bytes, k: int) -> set[int]:
    wanted = set(edges(literal, k))
    if not wanted:
        return {block.block_id for block in blocks if literal in block.data}
    selected: set[int] = set()
    for block in blocks:
        if wanted.issubset(block_edges(block, k)):
            selected.add(block.block_id)
    return selected


def blocks_for_path(blocks: list[Block], literal: bytes, k: int) -> set[int]:
    return {block.block_id for block in blocks if path_exists(block.data, literal, k)}


def blocks_for_rarest_edges(
    blocks: list[Block],
    literal: bytes,
    k: int,
    *,
    edge_df: Counter,
    target_ratio: float,
    max_edges: int,
) -> tuple[set[int], list[tuple[bytes, bytes]]]:
    literal_edges = list(dict.fromkeys(edges(literal, k)))
    if not literal_edges:
        return {block.block_id for block in blocks if literal in block.data}, []

    if any(edge_df.get(edge, 0) == 0 for edge in literal_edges):
        return set(), [edge for edge in literal_edges if edge_df.get(edge, 0) == 0][:1]

    sorted_edges = sorted(literal_edges, key=lambda edge: (edge_df.get(edge, 0), edge))
    selected = {block.block_id for block in blocks}
    chosen: list[tuple[bytes, bytes]] = []
    total = max(1, len(blocks))

    for edge in sorted_edges[:max_edges]:
        edge_blocks = {
            block.block_id
            for block in blocks
            if edge in block_edges(block, k)
        }
        selected &= edge_blocks
        chosen.append(edge)
        if len(selected) / total <= target_ratio:
            break

    return selected, chosen


def blocks_for_hybrid(
    blocks: list[Block],
    literal: bytes,
    edge_df2: Counter,
    edge_df3: Counter,
) -> tuple[set[int], str]:
    selected2, chosen2 = blocks_for_rarest_edges(
        blocks,
        literal,
        2,
        edge_df=edge_df2,
        target_ratio=0.10,
        max_edges=4,
    )
    selected3, chosen3 = blocks_for_rarest_edges(
        blocks,
        literal,
        3,
        edge_df=edge_df3,
        target_ratio=0.10,
        max_edges=4,
    )
    if len(selected3) <= len(selected2):
        return selected3, "trigram"
    return selected2, "bigram"


def blocks_for_per_group_mesh(
    blocks: list[Block],
    literal: bytes,
    k: int,
    *,
    target_ratio: float,
    max_edges: int,
) -> tuple[set[int], list[tuple[bytes, bytes]], set[int]]:
    edge_df, _ = edge_frequency(blocks, k)
    literal_edges = list(dict.fromkeys(edges(literal, k)))
    if not literal_edges:
        selected = {block.block_id for block in blocks if literal in block.data}
        groups = {block.group_id for block in blocks if block.block_id in selected}
        return selected, [], groups

    if any(edge_df.get(edge, 0) == 0 for edge in literal_edges):
        return set(), [edge for edge in literal_edges if edge_df.get(edge, 0) == 0][:1], set()

    sorted_edges = sorted(literal_edges, key=lambda edge: (edge_df.get(edge, 0), edge))
    chosen = sorted_edges[:max_edges]

    groups: set[int] = set()
    selected: set[int] = set()
    grouped_blocks: dict[int, list[Block]] = defaultdict(list)
    for block in blocks:
        grouped_blocks[block.group_id].append(block)

    for group_id, group_blocks in grouped_blocks.items():
        group_selected = {block.block_id for block in group_blocks}
        for edge in chosen:
            edge_blocks = {
                block.block_id
                for block in group_blocks
                if edge in block_edges(block, k)
            }
            group_selected &= edge_blocks
            if not group_selected:
                break
        if group_selected:
            groups.add(group_id)
            selected |= group_selected

    total = max(1, len(blocks))
    if len(selected) / total > target_ratio:
        # A planner would fall back to full scan when a local mesh is not selective.
        return {block.block_id for block in blocks}, chosen, set(grouped_blocks)
    return selected, chosen, groups


def summarize_selection(blocks: list[Block], selected: set[int]) -> tuple[int, int, float, float, int, int, int]:
    total_blocks = len(blocks)
    total_bytes = sum(block.byte_count for block in blocks)
    selected_blocks = len(selected)
    selected_bytes = sum(block.byte_count for block in blocks if block.block_id in selected)
    if selected:
        first = min(selected)
        last = max(selected)
        span = last - first + 1
    else:
        first = -1
        last = -1
        span = 0
    return (
        selected_blocks,
        selected_bytes,
        selected_blocks / total_blocks if total_blocks else 0.0,
        selected_bytes / total_bytes if total_bytes else 0.0,
        first,
        last,
        span,
    )


def feature_stats(blocks: list[Block], feature_edges: list[tuple[bytes, bytes]], k: int) -> tuple[int, int, int, int, int, float]:
    if not feature_edges:
        return -1, -1, 0, 0, 0, 0.0

    first = -1
    last = -1
    df = 0
    count = 0

    for block in blocks:
        edge_list = edges(block.data, k)
        edge_counts = Counter(edge_list)
        block_count = min(edge_counts.get(edge, 0) for edge in feature_edges)
        if block_count > 0:
            df += 1
            count += block_count
            if first < 0:
                first = block.block_id
            last = block.block_id

    span = 0 if first < 0 else last - first + 1
    density = count / df if df else 0.0
    return first, last, span, df, count, density


def storage_for_mesh(blocks: list[Block], k: int, layout: str, group_lines: int) -> EdgeStats:
    by_edge: dict[tuple[bytes, bytes], set[int]] = defaultdict(set)
    edge_occ = 0
    for block in blocks:
        edge_list = edges(block.data, k)
        edge_occ += len(edge_list)
        for edge in set(edge_list):
            if layout.startswith("per_group"):
                key_block = block.group_id * 1_000_000_000 + block.block_id
                by_edge[edge].add(key_block)
            else:
                by_edge[edge].add(block.block_id)

    edge_count = len(by_edge)
    postings_entries = sum(len(v) for v in by_edge.values())

    if k == 2:
        gram_bytes = 2
        edge_key_bytes = 4
    else:
        gram_bytes = 3
        edge_key_bytes = 6

    if layout.startswith("sorted"):
        row_bytes = 24
    elif layout.startswith("edge_postings"):
        row_bytes = 32
    elif layout.startswith("per_group"):
        row_bytes = 28
    else:
        row_bytes = 32

    raw_index = edge_count * (edge_key_bytes + row_bytes) + postings_entries * 4

    delta_bytes = edge_count * (edge_key_bytes + 12)
    for postings in by_edge.values():
        sorted_ids = sorted(postings)
        if not sorted_ids:
            continue
        prev = 0
        for idx, item in enumerate(sorted_ids):
            delta = item if idx == 0 else item - prev
            delta_bytes += varint_len(delta)
            prev = item

    if raw_index == 0:
        compressed = 0
    else:
        # Heuristic. Real compression must be measured in a serialized prototype.
        compressed = max(16, int(delta_bytes * 0.70))

    return EdgeStats(
        edge_count=edge_count,
        edge_occurrences=edge_occ,
        postings_entries=postings_entries,
        raw_index_bytes=raw_index,
        delta_varint_bytes=delta_bytes,
        compressed_estimate_bytes=compressed,
    )


def varint_len(value: int) -> int:
    if value < 0:
        return 10
    length = 1
    value >>= 7
    while value:
        length += 1
        value >>= 7
    return length


def info_bits(ratio: float) -> float:
    if ratio <= 0:
        return 64.0
    return -math.log2(ratio)


def query_patterns() -> list[tuple[str, str, str]]:
    return list(PATTERNS) + EXTRA_PATTERNS + [
        ("needle_exact_ip_regex_escaped", "regex", rf"src_ip={NEEDLE_IP.replace('.', r'\.')}"),
        ("needle_ip_fixed", "fixed", NEEDLE_IP),
        ("needle_src_ip_fixed", "fixed", f"src_ip={NEEDLE_IP}"),
        ("needle_request_id_prefix", "fixed", "NEEDLE-001000"),
    ]


def add_row(
    rows: list[dict[str, object]],
    *,
    blocks: list[Block],
    meta: dict[str, object],
    block_lines: int,
    group_lines: int,
    pattern_name: str,
    engine: str,
    pattern: str,
    selector_mode: str,
    selector_index: int,
    literal: bytes,
    variant: str,
    gram_k: int,
    selected: set[int],
    chosen_edges: list[tuple[bytes, bytes]],
    mesh_stats: EdgeStats,
    extra: str = "",
) -> None:
    selected_blocks, selected_bytes, selected_ratio, decoded_ratio, first, last, span = summarize_selection(blocks, selected)
    f_first, f_last, f_span, f_df, f_count, f_density = feature_stats(blocks, chosen_edges, gram_k) if gram_k else (-1, -1, 0, 0, 0, 0.0)
    needle_block = (int(meta["needle_line"]) - 1) // block_lines
    contains_needle = "yes" if needle_block in selected else "no"

    rows.append({
        "pattern_name": pattern_name,
        "engine": engine,
        "pattern": pattern,
        "selector_mode": selector_mode,
        "selector_index": selector_index,
        "literal": literal.decode("utf-8", "replace"),
        "literal_len": len(literal),
        "block_lines": block_lines,
        "group_lines": group_lines,
        "total_blocks": len(blocks),
        "variant": variant,
        "gram_k": gram_k,
        "selected_blocks": selected_blocks,
        "selected_bytes": selected_bytes,
        "selected_ratio": f"{selected_ratio:.6f}",
        "decoded_ratio": f"{decoded_ratio:.6f}",
        "first_selected_block": first,
        "last_selected_block": last,
        "selected_block_span": span,
        "chosen_edge_count": len(chosen_edges),
        "feature_first_seen_block": f_first,
        "feature_last_seen_block": f_last,
        "feature_block_span": f_span,
        "feature_block_df": f_df,
        "feature_occurrence_count": f_count,
        "feature_density": f"{f_density:.6f}",
        "feature_info_bits": f"{info_bits(selected_ratio):.6f}",
        "mesh_edge_count": mesh_stats.edge_count,
        "mesh_edge_occurrences": mesh_stats.edge_occurrences,
        "mesh_postings_entries": mesh_stats.postings_entries,
        "estimated_raw_index_bytes": mesh_stats.raw_index_bytes,
        "estimated_delta_varint_bytes": mesh_stats.delta_varint_bytes,
        "estimated_compressed_index_bytes": mesh_stats.compressed_estimate_bytes,
        "needle_block": needle_block,
        "contains_needle_block": contains_needle,
        "extra": extra,
    })


def run_probe(lines: int, needle_ratio: float, block_sizes: list[int], group_sizes: list[int]) -> tuple[list[dict[str, object]], dict[str, object]]:
    raw_lines, meta = make_corpus(lines, needle_ratio)
    rows: list[dict[str, object]] = []

    for block_lines in block_sizes:
        for group_lines in group_sizes:
            if group_lines < block_lines:
                continue
            blocks = make_blocks(raw_lines, block_lines, group_lines)

            stats = {
                ("edge_postings_bigram", 2): storage_for_mesh(blocks, 2, "edge_postings", group_lines),
                ("edge_postings_trigram", 3): storage_for_mesh(blocks, 3, "edge_postings", group_lines),
                ("sorted_edge_table_bigram", 2): storage_for_mesh(blocks, 2, "sorted", group_lines),
                ("sorted_edge_table_trigram", 3): storage_for_mesh(blocks, 3, "sorted", group_lines),
                ("per_group_mesh_bigram", 2): storage_for_mesh(blocks, 2, "per_group", group_lines),
                ("per_group_mesh_trigram", 3): storage_for_mesh(blocks, 3, "per_group", group_lines),
            }

            edge_df2, _ = edge_frequency(blocks, 2)
            edge_df3, _ = edge_frequency(blocks, 3)

            for pattern_name, engine, pattern in query_patterns():
                mode, literals = selector(pattern, engine)
                if mode == "none" or not literals:
                    add_row(
                        rows,
                        blocks=blocks,
                        meta=meta,
                        block_lines=block_lines,
                        group_lines=group_lines,
                        pattern_name=pattern_name,
                        engine=engine,
                        pattern=pattern,
                        selector_mode=mode,
                        selector_index=0,
                        literal=b"",
                        variant="full_scan_no_selector",
                        gram_k=0,
                        selected={block.block_id for block in blocks},
                        chosen_edges=[],
                        mesh_stats=EdgeStats(0, 0, 0, 0, 0, 0),
                    )
                    continue

                for selector_index, literal in enumerate(literals, start=1):
                    # Full path traversal baselines.
                    for variant, gram_k, store_key in [
                        ("edge_postings_bigram", 2, ("edge_postings_bigram", 2)),
                        ("edge_postings_trigram", 3, ("edge_postings_trigram", 3)),
                        ("sorted_edge_table_bigram", 2, ("sorted_edge_table_bigram", 2)),
                        ("sorted_edge_table_trigram", 3, ("sorted_edge_table_trigram", 3)),
                    ]:
                        selected = blocks_for_edge_all(blocks, literal, gram_k)
                        chosen = edges(literal, gram_k)
                        add_row(
                            rows,
                            blocks=blocks,
                            meta=meta,
                            block_lines=block_lines,
                            group_lines=group_lines,
                            pattern_name=pattern_name,
                            engine=engine,
                            pattern=pattern,
                            selector_mode=mode,
                            selector_index=selector_index,
                            literal=literal,
                            variant=variant,
                            gram_k=gram_k,
                            selected=selected,
                            chosen_edges=chosen,
                            mesh_stats=stats[store_key],
                        )

                    # Path-exact traversal variants.
                    for variant, gram_k in [
                        ("path_exact_bigram", 2),
                        ("path_exact_trigram", 3),
                    ]:
                        selected = blocks_for_path(blocks, literal, gram_k)
                        chosen = edges(literal, gram_k)
                        mesh_key = ("sorted_edge_table_bigram", 2) if gram_k == 2 else ("sorted_edge_table_trigram", 3)
                        add_row(
                            rows,
                            blocks=blocks,
                            meta=meta,
                            block_lines=block_lines,
                            group_lines=group_lines,
                            pattern_name=pattern_name,
                            engine=engine,
                            pattern=pattern,
                            selector_mode=mode,
                            selector_index=selector_index,
                            literal=literal,
                            variant=variant,
                            gram_k=gram_k,
                            selected=selected,
                            chosen_edges=chosen,
                            mesh_stats=stats[mesh_key],
                        )

                    # Rarest-edge guided traversal variants.
                    selected2, chosen2 = blocks_for_rarest_edges(
                        blocks, literal, 2, edge_df=edge_df2, target_ratio=0.10, max_edges=4
                    )
                    add_row(
                        rows,
                        blocks=blocks,
                        meta=meta,
                        block_lines=block_lines,
                        group_lines=group_lines,
                        pattern_name=pattern_name,
                        engine=engine,
                        pattern=pattern,
                        selector_mode=mode,
                        selector_index=selector_index,
                        literal=literal,
                        variant="rarest_edge_traversal_bigram",
                        gram_k=2,
                        selected=selected2,
                        chosen_edges=chosen2,
                        mesh_stats=stats[("sorted_edge_table_bigram", 2)],
                    )

                    selected3, chosen3 = blocks_for_rarest_edges(
                        blocks, literal, 3, edge_df=edge_df3, target_ratio=0.10, max_edges=4
                    )
                    add_row(
                        rows,
                        blocks=blocks,
                        meta=meta,
                        block_lines=block_lines,
                        group_lines=group_lines,
                        pattern_name=pattern_name,
                        engine=engine,
                        pattern=pattern,
                        selector_mode=mode,
                        selector_index=selector_index,
                        literal=literal,
                        variant="rarest_edge_traversal_trigram",
                        gram_k=3,
                        selected=selected3,
                        chosen_edges=chosen3,
                        mesh_stats=stats[("sorted_edge_table_trigram", 3)],
                    )

                    # Hybrid planner.
                    selected_h, picked = blocks_for_hybrid(blocks, literal, edge_df2, edge_df3)
                    gram_k = 3 if picked == "trigram" else 2
                    mesh_key = ("sorted_edge_table_trigram", 3) if gram_k == 3 else ("sorted_edge_table_bigram", 2)
                    chosen_h = chosen3 if picked == "trigram" else chosen2
                    add_row(
                        rows,
                        blocks=blocks,
                        meta=meta,
                        block_lines=block_lines,
                        group_lines=group_lines,
                        pattern_name=pattern_name,
                        engine=engine,
                        pattern=pattern,
                        selector_mode=mode,
                        selector_index=selector_index,
                        literal=literal,
                        variant="hybrid_bigram_trigram",
                        gram_k=gram_k,
                        selected=selected_h,
                        chosen_edges=chosen_h,
                        mesh_stats=stats[mesh_key],
                        extra=f"picked={picked}",
                    )

                    # Per-group meshes.
                    for variant, gram_k, edge_df, mesh_key in [
                        ("per_group_mesh_bigram", 2, edge_df2, ("per_group_mesh_bigram", 2)),
                        ("per_group_mesh_trigram", 3, edge_df3, ("per_group_mesh_trigram", 3)),
                    ]:
                        selected, chosen, groups = blocks_for_per_group_mesh(
                            blocks, literal, gram_k, target_ratio=0.10, max_edges=4
                        )
                        add_row(
                            rows,
                            blocks=blocks,
                            meta=meta,
                            block_lines=block_lines,
                            group_lines=group_lines,
                            pattern_name=pattern_name,
                            engine=engine,
                            pattern=pattern,
                            selector_mode=mode,
                            selector_index=selector_index,
                            literal=literal,
                            variant=variant,
                            gram_k=gram_k,
                            selected=selected,
                            chosen_edges=chosen,
                            mesh_stats=stats[mesh_key],
                            extra=f"groups={len(groups)}",
                        )

    return rows, meta


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
        "group_lines",
        "total_blocks",
        "variant",
        "gram_k",
        "selected_blocks",
        "selected_bytes",
        "selected_ratio",
        "decoded_ratio",
        "first_selected_block",
        "last_selected_block",
        "selected_block_span",
        "chosen_edge_count",
        "feature_first_seen_block",
        "feature_last_seen_block",
        "feature_block_span",
        "feature_block_df",
        "feature_occurrence_count",
        "feature_density",
        "feature_info_bits",
        "mesh_edge_count",
        "mesh_edge_occurrences",
        "mesh_postings_entries",
        "estimated_raw_index_bytes",
        "estimated_delta_varint_bytes",
        "estimated_compressed_index_bytes",
        "needle_block",
        "contains_needle_block",
        "extra",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, object]], meta: dict[str, object]) -> None:
    variant_values: defaultdict[str, list[float]] = defaultdict(list)
    variant_storage: defaultdict[str, list[int]] = defaultdict(list)
    for row in rows:
        variant_values[str(row["variant"])].append(float(row["decoded_ratio"]))
        variant_storage[str(row["variant"])].append(int(row["estimated_compressed_index_bytes"]))

    summary = []
    for variant in variant_values:
        values = variant_values[variant]
        sizes = variant_storage[variant]
        summary.append((
            variant,
            sum(values) / len(values),
            min(values),
            max(values),
            int(sum(sizes) / len(sizes)) if sizes else 0,
            len(values),
        ))
    summary.sort(key=lambda item: (item[1], item[4], item[0]))

    needle_rows = [
        row for row in rows
        if str(row["pattern_name"]).startswith("needle")
        and row["contains_needle_block"] == "yes"
    ]
    best_needle = sorted(
        needle_rows,
        key=lambda row: (
            float(row["decoded_ratio"]),
            int(row["estimated_compressed_index_bytes"]),
            row["variant"],
        ),
    )[:16]

    best_by_pattern: dict[str, dict[str, object]] = {}
    for row in rows:
        pattern = str(row["pattern_name"])
        score = (
            float(row["decoded_ratio"]),
            int(row["estimated_compressed_index_bytes"]),
            row["variant"],
        )
        prev = best_by_pattern.get(pattern)
        if prev is None or score < (
            float(prev["decoded_ratio"]),
            int(prev["estimated_compressed_index_bytes"]),
            prev["variant"],
        ):
            best_by_pattern[pattern] = row

    doc = [
        "# zlg Phase 0t k-gram mesh shootout",
        "",
        "This offline probe compares multiple k-gram mesh implementation variants",
        "before changing the .zlg format.",
        "",
        "## Corpus",
        "",
        f"- Lines: {meta['lines']}",
        f"- Input bytes: {meta['input_bytes']}",
        f"- Input sha256: {meta['sha256']}",
        f"- Needle IP: {meta['needle_ip']}",
        f"- Needle line: {meta['needle_line']}",
        f"- Needle ratio: {float(meta['needle_ratio']):.3f}",
        "",
        "## Variant aggregate summary",
        "",
        "| variant | mean_decoded_ratio | min | max | avg_compressed_index_est | rows |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for variant, mean_value, min_value, max_value, avg_size, count in summary:
        doc.append(
            f"| {variant} | {mean_value:.6f} | {min_value:.6f} | "
            f"{max_value:.6f} | {avg_size} | {count} |"
        )

    doc.extend([
        "",
        "## Best needle rows",
        "",
        "| pattern | block | group | variant | gram_k | selected_blocks | decoded_ratio | index_est | extra |",
        "|---|---:|---:|---|---:|---:|---:|---:|---|",
    ])
    for row in best_needle:
        doc.append(
            f"| {row['pattern_name']} | {row['block_lines']} | {row['group_lines']} | "
            f"{row['variant']} | {row['gram_k']} | {row['selected_blocks']} | "
            f"{float(row['decoded_ratio']):.6f} | {row['estimated_compressed_index_bytes']} | "
            f"{row['extra']} |"
        )

    doc.extend([
        "",
        "## Best variant by pattern",
        "",
        "| pattern | variant | block | group | selected_blocks | decoded_ratio | index_est | first_seen | count | span |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for pattern in sorted(best_by_pattern):
        row = best_by_pattern[pattern]
        doc.append(
            f"| {pattern} | {row['variant']} | {row['block_lines']} | {row['group_lines']} | "
            f"{row['selected_blocks']} | {float(row['decoded_ratio']):.6f} | "
            f"{row['estimated_compressed_index_bytes']} | {row['feature_first_seen_block']} | "
            f"{row['feature_occurrence_count']} | {row['feature_block_span']} |"
        )

    doc.extend([
        "",
        "## Interpretation guide",
        "",
        "- Edge postings variants store postings for graph transitions.",
        "- Sorted edge table variants model a compact footer-friendly layout.",
        "- Rarest-edge traversal starts at the most selective edge in the query path.",
        "- Per-group mesh variants model local mesh indexes under larger logical groups.",
        "- These are heuristic storage estimates, not final serialized file sizes.",
        "- A future runtime phase should serialize only the top one or two variants.",
    ])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")


def parse_csv_ints(value: str) -> list[int]:
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lines", type=int, default=125000)
    parser.add_argument("--needle-ratio", type=float, default=0.80)
    parser.add_argument("--block-lines", default="512,1024,2048,4096")
    parser.add_argument("--group-lines", default="16384,65536")
    parser.add_argument("--output", default="validation_results/phase0t_mesh_shootout.md")
    parser.add_argument("--csv", default="validation_results/phase0t_mesh_shootout.csv")
    args = parser.parse_args()

    rows, meta = run_probe(
        args.lines,
        args.needle_ratio,
        parse_csv_ints(args.block_lines),
        parse_csv_ints(args.group_lines),
    )
    write_csv(REPO / args.csv, rows)
    write_markdown(REPO / args.output, rows, meta)
    print(f"wrote {REPO / args.output}")
    print(f"wrote {REPO / args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
