#!/usr/bin/env python3
"""Phase 0o creative k-gram index probe.

This is an offline design probe. It does not change the .zlg format. It fixes
and extends the Phase 0n rarest-kgram experiment by comparing multiple block
sizes, rare/selective patterns, and adaptive rarest-kgram strategies.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from phase0h_bench import PATTERNS, make_corpus, sha256  # noqa: E402
from phase0m_postings_probe import selector  # noqa: E402


EXTRA_PATTERNS = [
    ("exact_event_id", "regex", "event_id=42424"),
    ("exact_sshd_user", "regex", "user=test65500"),
    ("exact_error_key", "regex", r"key=\"abc9700\""),
    ("exact_retry_key", "regex", r"key=\"retry10060\""),
    ("exact_deny_key", "regex", r"key=\"deny21100\""),
    ("rare_failed_src", "regex", "src_ip=198.51.100.55"),
    ("component_auth", "regex", "component=auth"),
    ("normal_shard_7", "regex", "shard=7"),
    ("absent_traceid", "fixed", "TRACEID-deadbeef-cafebabe"),
]


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
        counter.update(getattr(block, attr))
    return counter


def edge_frequency_counter(blocks: list[BlockStats]) -> Counter[tuple[int, int]]:
    counter: Counter[tuple[int, int]] = Counter()
    for block in blocks:
        counter.update(block.edges)
    return counter


def block_ids(blocks: list[BlockStats]) -> set[int]:
    return {block.block_id for block in blocks}


def combine_literal_sets(mode: str, literal_sets: list[set[int]], all_blocks: set[int]) -> set[int]:
    if mode == "none" or not literal_sets:
        return set(all_blocks)
    if mode == "all":
        out = set(all_blocks)
        for item in literal_sets:
            out &= item
        return out
    if mode == "any":
        out: set[int] = set()
        for item in literal_sets:
            out |= item
        return out
    return set(all_blocks)


def blocks_with_all_bigrams(blocks: list[BlockStats], literal: bytes) -> set[int]:
    grams = grams2(literal)
    if not grams:
        return block_ids(blocks)
    return {block.block_id for block in blocks if grams.issubset(block.bigrams)}


def blocks_with_all_trigrams(blocks: list[BlockStats], literal: bytes) -> set[int]:
    grams = grams3(literal)
    if not grams:
        return blocks_with_all_bigrams(blocks, literal)
    return {block.block_id for block in blocks if grams.issubset(block.trigrams)}


def blocks_with_all_edges(blocks: list[BlockStats], literal: bytes) -> set[int]:
    edges = bigram_edges(literal)
    if not edges:
        return blocks_with_all_bigrams(blocks, literal)
    return {block.block_id for block in blocks if edges.issubset(block.edges)}


def gram_candidates(
    literal: bytes,
    bigram_freq: Counter[int],
    trigram_freq: Counter[int],
) -> list[tuple[int, str, int]]:
    candidates: list[tuple[int, str, int]] = []
    for gram in grams2(literal):
        candidates.append((bigram_freq.get(gram, 0), "bigram", gram))
    for gram in grams3(literal):
        candidates.append((trigram_freq.get(gram, 0), "trigram", gram))
    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    return candidates


def blocks_with_chosen_grams(
    blocks: list[BlockStats],
    chosen: list[tuple[int, str, int]],
) -> set[int]:
    if not chosen:
        return block_ids(blocks)
    out: set[int] = set()
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
            out.add(block.block_id)
    return out


def select_rarest_k(
    blocks: list[BlockStats],
    mode: str,
    literals: list[bytes],
    bigram_freq: Counter[int],
    trigram_freq: Counter[int],
    count: int,
) -> set[int]:
    if mode == "none" or not literals:
        return block_ids(blocks)
    per_literal = []
    for literal in literals:
        candidates = gram_candidates(literal, bigram_freq, trigram_freq)
        chosen = candidates[:max(1, count)]
        per_literal.append(blocks_with_chosen_grams(blocks, chosen))
    return combine_literal_sets(mode, per_literal, block_ids(blocks))


def select_adaptive_rarest(
    blocks: list[BlockStats],
    mode: str,
    literals: list[bytes],
    bigram_freq: Counter[int],
    trigram_freq: Counter[int],
    target_ratio: float,
) -> set[int]:
    if mode == "none" or not literals:
        return block_ids(blocks)
    all_blocks = block_ids(blocks)
    target_count = max(1, int(len(blocks) * target_ratio))
    per_literal = []
    for literal in literals:
        candidates = gram_candidates(literal, bigram_freq, trigram_freq)
        if not candidates:
            per_literal.append(set(all_blocks))
            continue
        chosen: list[tuple[int, str, int]] = []
        selected = set(all_blocks)
        for candidate in candidates:
            chosen.append(candidate)
            selected = blocks_with_chosen_grams(blocks, chosen)
            if len(selected) <= target_count:
                break
        per_literal.append(selected)
    return combine_literal_sets(mode, per_literal, all_blocks)


def select_strategy(
    strategy: str,
    blocks: list[BlockStats],
    mode: str,
    literals: list[bytes],
    bigram_freq: Counter[int],
    trigram_freq: Counter[int],
) -> set[int]:
    all_blocks = block_ids(blocks)
    if mode == "none" or not literals:
        return set(all_blocks)
    if strategy == "bigram_block":
        return combine_literal_sets(mode, [blocks_with_all_bigrams(blocks, lit) for lit in literals], all_blocks)
    if strategy == "trigram_sparse":
        return combine_literal_sets(mode, [blocks_with_all_trigrams(blocks, lit) for lit in literals], all_blocks)
    if strategy == "bigram_graph_edges":
        return combine_literal_sets(mode, [blocks_with_all_edges(blocks, lit) for lit in literals], all_blocks)
    if strategy == "rarest_kgram_2_fixed":
        return select_rarest_k(blocks, mode, literals, bigram_freq, trigram_freq, 2)
    if strategy == "rarest_kgram_4_fixed":
        return select_rarest_k(blocks, mode, literals, bigram_freq, trigram_freq, 4)
    if strategy == "adaptive_rarest_25pct":
        return select_adaptive_rarest(blocks, mode, literals, bigram_freq, trigram_freq, 0.25)
    if strategy == "adaptive_rarest_10pct":
        return select_adaptive_rarest(blocks, mode, literals, bigram_freq, trigram_freq, 0.10)
    raise ValueError(f"unknown strategy {strategy}")


def estimated_index_bytes(blocks: list[BlockStats]) -> dict[str, int]:
    bigram_postings = sum(len(block.bigrams) for block in blocks)
    trigram_postings = sum(len(block.trigrams) for block in blocks)
    edge_postings = sum(len(block.edges) for block in blocks)
    return {
        "bigram_block": bigram_postings * 6,
        "trigram_sparse": trigram_postings * 7,
        "bigram_graph_edges": edge_postings * 8,
        "rarest_kgram_2_fixed": (bigram_postings * 6) + (trigram_postings * 7),
        "rarest_kgram_4_fixed": (bigram_postings * 6) + (trigram_postings * 7),
        "adaptive_rarest_25pct": (bigram_postings * 6) + (trigram_postings * 7),
        "adaptive_rarest_10pct": (bigram_postings * 6) + (trigram_postings * 7),
    }


def literal_df_summary(
    literals: list[bytes],
    blocks: list[BlockStats],
    bigram_freq: Counter[int],
    trigram_freq: Counter[int],
) -> tuple[int, int, float]:
    dfs: list[int] = []
    for literal in literals:
        for freq, _kind, _gram in gram_candidates(literal, bigram_freq, trigram_freq):
            dfs.append(freq)
    if not dfs:
        return 0, 0, 0.0
    return min(dfs), max(dfs), statistics.mean(dfs)


def summarize_selection(blocks: list[BlockStats], selected: set[int]) -> tuple[int, int, float, float]:
    total_blocks = len(blocks)
    selected_blocks = len(selected)
    selected_bytes = sum(block.byte_count for block in blocks if block.block_id in selected)
    total_bytes = sum(block.byte_count for block in blocks)
    selected_ratio = selected_blocks / total_blocks if total_blocks else 0.0
    decoded_ratio = selected_bytes / total_bytes if total_bytes else 0.0
    return selected_blocks, selected_bytes, selected_ratio, decoded_ratio


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
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
        "estimated_index_bytes",
        "selector_df_min",
        "selector_df_max",
        "selector_df_mean",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, object]], *, lines: int, input_bytes: int, digest: str) -> None:
    best: dict[tuple[str, int], dict[str, object]] = {}
    for row in rows:
        key = (str(row["pattern_name"]), int(row["block_lines"]))
        ratio = float(row["estimated_decoded_ratio"])
        idx_bytes = int(row["estimated_index_bytes"])
        if key not in best:
            best[key] = row
            continue
        prev = best[key]
        prev_ratio = float(prev["estimated_decoded_ratio"])
        prev_idx = int(prev["estimated_index_bytes"])
        if (ratio, idx_bytes) < (prev_ratio, prev_idx):
            best[key] = row

    global_best: dict[str, dict[str, object]] = {}
    for row in rows:
        name = str(row["pattern_name"])
        score = (float(row["estimated_decoded_ratio"]), int(row["estimated_index_bytes"]))
        if name not in global_best:
            global_best[name] = row
            continue
        prev = global_best[name]
        prev_score = (float(prev["estimated_decoded_ratio"]), int(prev["estimated_index_bytes"]))
        if score < prev_score:
            global_best[name] = row

    doc = [
        "# zlg Phase 0o creative index probe",
        "",
        "This offline probe fixes the Phase 0n rarest-kgram absent-gram flaw and compares",
        "smaller block sizes, rare selectors, sparse trigrams, bigram graph edges, and adaptive",
        "rarest-kgram strategies. It does not change the .zlg file format.",
        "",
        "## Corpus",
        "",
        f"- Lines: {lines}",
        f"- Input bytes: {input_bytes}",
        f"- Input sha256: {digest}",
        "",
        "## Best strategy by pattern",
        "",
        "| pattern | block_lines | strategy | selected_blocks | decoded_ratio | index_bytes | df_min | df_mean |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for name in sorted(global_best):
        row = global_best[name]
        doc.append(
            f"| {name} | {row['block_lines']} | {row['strategy']} | {row['selected_blocks']} | "
            f"{float(row['estimated_decoded_ratio']):.3f} | {row['estimated_index_bytes']} | "
            f"{row['selector_df_min']} | {float(row['selector_df_mean']):.2f} |"
        )

    doc.extend([
        "",
        "## Best strategy per pattern and block size",
        "",
        "| pattern | block_lines | strategy | selected_blocks | decoded_ratio | index_bytes |",
        "|---|---:|---|---:|---:|---:|",
    ])
    for key in sorted(best):
        row = best[key]
        doc.append(
            f"| {row['pattern_name']} | {row['block_lines']} | {row['strategy']} | "
            f"{row['selected_blocks']} | {float(row['estimated_decoded_ratio']):.3f} | "
            f"{row['estimated_index_bytes']} |"
        )

    doc.extend([
        "",
        "## Interpretation guide",
        "",
        "- If decoded_ratio stays 1.000, that selector is too common for gram indexing at that block size.",
        "- If decoded_ratio falls only at smaller block sizes, the future format needs smaller independently decodable search blocks.",
        "- If trigram/graph does not beat bigram, the corpus likely has common literals in every block.",
        "- If rarest-kgram beats all-grams, frequency-guided query planning is worth carrying forward.",
        "- Index overhead is acceptable only while total .zlg size remains below comparable gzip outputs.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")


def parse_block_lines(value: str) -> list[int]:
    out = []
    for item in value.split(","):
        item = item.strip()
        if item:
            out.append(int(item))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lines", type=int, default=125000)
    parser.add_argument("--block-lines", default="512,1024,2048,4096")
    parser.add_argument("--output", default="validation_results/phase0o_creative_index_probe.md")
    parser.add_argument("--csv", default="validation_results/phase0o_creative_index_probe.csv")
    args = parser.parse_args()

    tmp = REPO / "validation_results" / "phase0o_creative_index_probe_corpus.tmp"
    make_corpus(tmp, args.lines)
    raw = tmp.read_bytes()
    raw_lines = raw.splitlines(keepends=True)
    digest = sha256(tmp)
    input_bytes = tmp.stat().st_size
    tmp.unlink()

    patterns = list(PATTERNS) + EXTRA_PATTERNS
    strategies = [
        "bigram_block",
        "trigram_sparse",
        "bigram_graph_edges",
        "rarest_kgram_2_fixed",
        "rarest_kgram_4_fixed",
        "adaptive_rarest_25pct",
        "adaptive_rarest_10pct",
    ]

    rows: list[dict[str, object]] = []
    for block_lines in parse_block_lines(args.block_lines):
        blocks = build_blocks(raw_lines, block_lines)
        bigram_freq = frequency_counter(blocks, "bigrams")
        trigram_freq = frequency_counter(blocks, "trigrams")
        index_bytes = estimated_index_bytes(blocks)
        for name, engine, pattern in patterns:
            mode, literals = selector(pattern, engine)
            df_min, df_max, df_mean = literal_df_summary(literals, blocks, bigram_freq, trigram_freq)
            for strategy in strategies:
                selected = select_strategy(strategy, blocks, mode, literals, bigram_freq, trigram_freq)
                selected_blocks, selected_bytes, selected_ratio, decoded_ratio = summarize_selection(blocks, selected)
                rows.append({
                    "pattern_name": name,
                    "engine": engine,
                    "pattern": pattern,
                    "selector_mode": mode,
                    "selector_count": len(literals),
                    "strategy": strategy,
                    "block_lines": block_lines,
                    "total_blocks": len(blocks),
                    "selected_blocks": selected_blocks,
                    "selected_ratio": f"{selected_ratio:.6f}",
                    "estimated_decoded_bytes": selected_bytes,
                    "estimated_decoded_ratio": f"{decoded_ratio:.6f}",
                    "estimated_index_bytes": index_bytes[strategy],
                    "selector_df_min": df_min,
                    "selector_df_max": df_max,
                    "selector_df_mean": f"{df_mean:.6f}",
                })

    csv_path = REPO / args.csv
    md_path = REPO / args.output
    write_csv(csv_path, rows)
    write_markdown(md_path, rows, lines=args.lines, input_bytes=input_bytes, digest=digest)
    print(f"wrote {md_path}")
    print(f"wrote {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
