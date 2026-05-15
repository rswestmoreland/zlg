#!/usr/bin/env python3
"""Phase 0p adaptive weighted k-gram planner probe.

This is an offline experiment. It does not change the .zlg format.

The probe treats gram and graph-edge metadata as a query-planning problem:
use DF/IDF, occurrence counts, estimated decoded bytes, and simple cost gates
to decide whether to use a candidate index strategy or fall back to full scan.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from phase0h_bench import PATTERNS, make_corpus, sha256  # noqa: E402
from phase0m_postings_probe import selector  # noqa: E402
from phase0o_creative_index_probe import EXTRA_PATTERNS  # noqa: E402


@dataclass(frozen=True)
class Feature:
    kind: str
    value: object
    df: int
    count: int
    idf: float
    info_bits: float


@dataclass(frozen=True)
class BlockStats:
    block_id: int
    first_line: int
    line_count: int
    byte_count: int
    bigrams: frozenset[int]
    trigrams: frozenset[int]
    edges: frozenset[tuple[int, int]]
    bigram_counts: Counter[int]
    trigram_counts: Counter[int]
    edge_counts: Counter[tuple[int, int]]


def grams2(value: bytes) -> list[int]:
    if len(value) < 2:
        return []
    return [value[idx] << 8 | value[idx + 1] for idx in range(len(value) - 1)]


def grams3(value: bytes) -> list[int]:
    if len(value) < 3:
        return []
    return [
        value[idx] << 16 | value[idx + 1] << 8 | value[idx + 2]
        for idx in range(len(value) - 2)
    ]


def edges(value: bytes) -> list[tuple[int, int]]:
    if len(value) < 3:
        return []
    out: list[tuple[int, int]] = []
    for idx in range(len(value) - 2):
        left = value[idx] << 8 | value[idx + 1]
        right = value[idx + 1] << 8 | value[idx + 2]
        out.append((left, right))
    return out


def build_blocks(lines: list[bytes], block_lines: int) -> list[BlockStats]:
    blocks: list[BlockStats] = []
    for block_id, offset in enumerate(range(0, len(lines), block_lines)):
        block_lines_data = lines[offset:offset + block_lines]
        data = b"".join(block_lines_data)
        bigram_counts: Counter[int] = Counter(grams2(data))
        trigram_counts: Counter[int] = Counter(grams3(data))
        edge_counts: Counter[tuple[int, int]] = Counter(edges(data))
        blocks.append(
            BlockStats(
                block_id=block_id,
                first_line=offset + 1,
                line_count=len(block_lines_data),
                byte_count=len(data),
                bigrams=frozenset(bigram_counts),
                trigrams=frozenset(trigram_counts),
                edges=frozenset(edge_counts),
                bigram_counts=bigram_counts,
                trigram_counts=trigram_counts,
                edge_counts=edge_counts,
            )
        )
    return blocks


def df_counter(blocks: list[BlockStats], attr: str) -> Counter:
    counter: Counter = Counter()
    for block in blocks:
        counter.update(getattr(block, attr))
    return counter


def occurrence_counter(blocks: list[BlockStats], attr: str) -> Counter:
    counter: Counter = Counter()
    for block in blocks:
        counter.update(getattr(block, attr))
    return counter


def all_block_ids(blocks: list[BlockStats]) -> set[int]:
    return {block.block_id for block in blocks}


def has_feature(block: BlockStats, feature: Feature) -> bool:
    if feature.kind == "bigram":
        return int(feature.value) in block.bigrams
    if feature.kind == "trigram":
        return int(feature.value) in block.trigrams
    if feature.kind == "edge":
        return feature.value in block.edges
    raise ValueError(f"unknown feature kind {feature.kind}")


def blocks_for_features(blocks: list[BlockStats], features: list[Feature]) -> set[int]:
    if not features:
        return all_block_ids(blocks)
    if any(feature.df == 0 for feature in features):
        return set()
    out: set[int] = set()
    for block in blocks:
        if all(has_feature(block, feature) for feature in features):
            out.add(block.block_id)
    return out


def combine(mode: str, sets: list[set[int]], blocks: list[BlockStats]) -> set[int]:
    if mode == "none" or not sets:
        return all_block_ids(blocks)
    if mode == "all":
        out = all_block_ids(blocks)
        for item in sets:
            out &= item
        return out
    if mode == "any":
        out: set[int] = set()
        for item in sets:
            out |= item
        return out
    return all_block_ids(blocks)


def feature_score(df: int, total_blocks: int, count: int) -> tuple[float, float]:
    if total_blocks <= 0:
        return 0.0, 0.0
    if df <= 0:
        return 64.0, 64.0
    p = df / total_blocks
    info_bits = -math.log2(p)
    idf = math.log((total_blocks + 1) / (df + 1)) + 1.0
    count_penalty = math.log2(count + 2)
    return idf / count_penalty, info_bits


def literal_features(
    literal: bytes,
    total_blocks: int,
    bigram_df: Counter[int],
    trigram_df: Counter[int],
    edge_df: Counter[tuple[int, int]],
    bigram_occ: Counter[int],
    trigram_occ: Counter[int],
    edge_occ: Counter[tuple[int, int]],
) -> list[Feature]:
    features: list[Feature] = []

    for value in set(grams2(literal)):
        df = bigram_df.get(value, 0)
        count = bigram_occ.get(value, 0)
        idf, info_bits = feature_score(df, total_blocks, count)
        features.append(Feature("bigram", value, df, count, idf, info_bits))

    for value in set(grams3(literal)):
        df = trigram_df.get(value, 0)
        count = trigram_occ.get(value, 0)
        idf, info_bits = feature_score(df, total_blocks, count)
        features.append(Feature("trigram", value, df, count, idf, info_bits))

    for value in set(edges(literal)):
        df = edge_df.get(value, 0)
        count = edge_occ.get(value, 0)
        idf, info_bits = feature_score(df, total_blocks, count)
        features.append(Feature("edge", value, df, count, idf, info_bits))

    return features


def sort_features(features: list[Feature]) -> list[Feature]:
    return sorted(
        features,
        key=lambda item: (
            item.df,
            -item.info_bits,
            -item.idf,
            item.kind,
            str(item.value),
        ),
    )


def pick_features(
    features: list[Feature],
    *,
    allowed_kinds: set[str],
    limit: int,
    min_info_bits: float = 0.0,
) -> list[Feature]:
    chosen = [
        feature for feature in sort_features(features)
        if feature.kind in allowed_kinds and feature.info_bits >= min_info_bits
    ]
    return chosen[:limit]


def choose_adaptive(
    blocks: list[BlockStats],
    features: list[Feature],
    *,
    allowed_kinds: set[str],
    target_ratio: float,
    max_features: int,
    min_info_bits: float,
) -> list[Feature]:
    candidates = [
        feature for feature in sort_features(features)
        if feature.kind in allowed_kinds and feature.info_bits >= min_info_bits
    ]

    if not candidates:
        return []

    selected = all_block_ids(blocks)
    chosen: list[Feature] = []
    total_blocks = max(1, len(blocks))

    for feature in candidates:
        proposal = chosen + [feature]
        proposal_blocks = blocks_for_features(blocks, proposal)
        if len(proposal_blocks) <= len(selected):
            chosen = proposal
            selected = proposal_blocks
        if len(selected) / total_blocks <= target_ratio:
            break
        if len(chosen) >= max_features:
            break

    return chosen


def choose_cost_gate(
    blocks: list[BlockStats],
    features: list[Feature],
    *,
    allowed_kinds: set[str],
    max_features: int,
    min_info_bits: float,
    use_threshold: float,
    postings_weight: float,
) -> tuple[str, list[Feature], set[int]]:
    total_bytes = sum(block.byte_count for block in blocks)
    total_blocks = max(1, len(blocks))

    candidates = [
        feature for feature in sort_features(features)
        if feature.kind in allowed_kinds and feature.info_bits >= min_info_bits
    ]

    if not candidates:
        return "full_scan_no_features", [], all_block_ids(blocks)

    chosen: list[Feature] = []
    best_selected = all_block_ids(blocks)
    best_score = float("inf")

    for feature in candidates[:max_features * 3]:
        proposal = chosen + [feature]
        selected = blocks_for_features(blocks, proposal)
        selected_bytes = sum(block.byte_count for block in blocks if block.block_id in selected)
        postings_ops = sum(max(feature.df, 0) for feature in proposal)
        decode_ratio = selected_bytes / total_bytes if total_bytes else 1.0
        index_ratio = postings_ops / total_blocks
        score = decode_ratio + postings_weight * index_ratio

        if score <= best_score:
            chosen = proposal
            best_selected = selected
            best_score = score

        if len(chosen) >= max_features:
            break

    selected_bytes = sum(block.byte_count for block in blocks if block.block_id in best_selected)
    decode_ratio = selected_bytes / total_bytes if total_bytes else 1.0
    if decode_ratio <= use_threshold:
        return "use_index", chosen, best_selected
    return "full_scan_cost_gate", [], all_block_ids(blocks)


def choose_for_literal(
    strategy: str,
    blocks: list[BlockStats],
    features: list[Feature],
) -> tuple[str, list[Feature], set[int]]:
    if strategy == "full_scan":
        return "full_scan_forced", [], all_block_ids(blocks)
    if strategy == "best_trigram_1":
        chosen = pick_features(features, allowed_kinds={"trigram"}, limit=1)
        return "use_index", chosen, blocks_for_features(blocks, chosen)
    if strategy == "best_trigram_2":
        chosen = pick_features(features, allowed_kinds={"trigram"}, limit=2)
        return "use_index", chosen, blocks_for_features(blocks, chosen)
    if strategy == "best_edge_1":
        chosen = pick_features(features, allowed_kinds={"edge"}, limit=1)
        return "use_index", chosen, blocks_for_features(blocks, chosen)
    if strategy == "best_edge_2":
        chosen = pick_features(features, allowed_kinds={"edge"}, limit=2)
        return "use_index", chosen, blocks_for_features(blocks, chosen)
    if strategy == "best_mixed_2":
        chosen = pick_features(features, allowed_kinds={"bigram", "trigram", "edge"}, limit=2)
        return "use_index", chosen, blocks_for_features(blocks, chosen)
    if strategy == "entropy_gate_2bits":
        chosen = pick_features(
            features,
            allowed_kinds={"bigram", "trigram", "edge"},
            limit=2,
            min_info_bits=2.0,
        )
        if not chosen:
            return "full_scan_low_entropy", [], all_block_ids(blocks)
        return "use_index", chosen, blocks_for_features(blocks, chosen)
    if strategy == "entropy_gate_4bits":
        chosen = pick_features(
            features,
            allowed_kinds={"bigram", "trigram", "edge"},
            limit=2,
            min_info_bits=4.0,
        )
        if not chosen:
            return "full_scan_low_entropy", [], all_block_ids(blocks)
        return "use_index", chosen, blocks_for_features(blocks, chosen)
    if strategy == "adaptive_25pct":
        chosen = choose_adaptive(
            blocks,
            features,
            allowed_kinds={"bigram", "trigram", "edge"},
            target_ratio=0.25,
            max_features=4,
            min_info_bits=0.0,
        )
        return "use_index" if chosen else "full_scan_no_features", chosen, blocks_for_features(blocks, chosen)
    if strategy == "adaptive_10pct":
        chosen = choose_adaptive(
            blocks,
            features,
            allowed_kinds={"bigram", "trigram", "edge"},
            target_ratio=0.10,
            max_features=4,
            min_info_bits=0.0,
        )
        return "use_index" if chosen else "full_scan_no_features", chosen, blocks_for_features(blocks, chosen)
    if strategy == "cost_gate_75pct":
        return choose_cost_gate(
            blocks,
            features,
            allowed_kinds={"bigram", "trigram", "edge"},
            max_features=4,
            min_info_bits=0.0,
            use_threshold=0.75,
            postings_weight=0.005,
        )
    if strategy == "cost_gate_35pct":
        return choose_cost_gate(
            blocks,
            features,
            allowed_kinds={"bigram", "trigram", "edge"},
            max_features=4,
            min_info_bits=0.0,
            use_threshold=0.35,
            postings_weight=0.005,
        )
    raise ValueError(f"unknown strategy {strategy}")


def select_for_pattern(
    strategy: str,
    blocks: list[BlockStats],
    mode: str,
    literal_feature_sets: list[list[Feature]],
) -> tuple[str, list[Feature], set[int]]:
    if mode == "none" or not literal_feature_sets:
        return "full_scan_no_selector", [], all_block_ids(blocks)

    decisions: list[str] = []
    chosen_sets: list[list[Feature]] = []
    block_sets: list[set[int]] = []

    for features in literal_feature_sets:
        decision, chosen, selected = choose_for_literal(strategy, blocks, features)
        decisions.append(decision)
        chosen_sets.append(chosen)
        block_sets.append(selected)

    selected = combine(mode, block_sets, blocks)
    chosen_flat = [feature for chosen in chosen_sets for feature in chosen]

    if not chosen_flat:
        return "full_scan_no_features", [], all_block_ids(blocks)

    if all(decision.startswith("full_scan") for decision in decisions):
        return "full_scan_planner", [], all_block_ids(blocks)

    if selected == all_block_ids(blocks) and strategy.startswith("cost_gate"):
        return "full_scan_cost_gate", [], all_block_ids(blocks)

    return "use_index", chosen_flat, selected


def estimate_index_bytes(blocks: list[BlockStats]) -> int:
    trigram_postings = sum(len(block.trigrams) for block in blocks)
    edge_postings = sum(len(block.edges) for block in blocks)
    return (trigram_postings * 7) + (edge_postings * 8)


def summarize_features(features: list[Feature]) -> tuple[int, int, int, float, float, str]:
    if not features:
        return 0, 0, 0, 0.0, 0.0, ""
    df_values = [feature.df for feature in features]
    info_values = [feature.info_bits for feature in features]
    label = ";".join(
        f"{feature.kind}:df={feature.df}:bits={feature.info_bits:.2f}"
        for feature in features[:4]
    )
    return (
        min(df_values),
        max(df_values),
        sum(feature.count for feature in features),
        max(info_values),
        sum(info_values),
        label,
    )


def summarize_selection(blocks: list[BlockStats], selected: set[int]) -> tuple[int, int, float, float]:
    total_blocks = len(blocks)
    total_bytes = sum(block.byte_count for block in blocks)
    selected_blocks = len(selected)
    selected_bytes = sum(block.byte_count for block in blocks if block.block_id in selected)
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
        "planner_decision",
        "block_lines",
        "total_blocks",
        "selected_blocks",
        "selected_ratio",
        "estimated_decoded_bytes",
        "estimated_decoded_ratio",
        "estimated_index_bytes",
        "chosen_feature_count",
        "chosen_df_min",
        "chosen_df_max",
        "chosen_occurrence_sum",
        "chosen_info_max",
        "chosen_info_sum",
        "chosen_feature_summary",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    path: Path,
    rows: list[dict[str, object]],
    *,
    lines: int,
    input_bytes: int,
    digest: str,
) -> None:
    best_by_pattern: dict[str, dict[str, object]] = {}
    best_by_pattern_block: dict[tuple[str, int], dict[str, object]] = {}

    for row in rows:
        pattern = str(row["pattern_name"])
        key = (pattern, int(row["block_lines"]))
        score = (
            float(row["estimated_decoded_ratio"]),
            0 if row["planner_decision"] == "use_index" else 1,
            int(row["estimated_index_bytes"]),
        )

        prev = best_by_pattern.get(pattern)
        if prev is None or score < (
            float(prev["estimated_decoded_ratio"]),
            0 if prev["planner_decision"] == "use_index" else 1,
            int(prev["estimated_index_bytes"]),
        ):
            best_by_pattern[pattern] = row

        prev_key = best_by_pattern_block.get(key)
        if prev_key is None or score < (
            float(prev_key["estimated_decoded_ratio"]),
            0 if prev_key["planner_decision"] == "use_index" else 1,
            int(prev_key["estimated_index_bytes"]),
        ):
            best_by_pattern_block[key] = row

    decision_counts: Counter[str] = Counter(str(row["planner_decision"]) for row in rows)
    strategy_wins: Counter[str] = Counter(str(row["strategy"]) for row in best_by_pattern.values())

    doc = [
        "# zlg Phase 0p adaptive weighted k-gram planner probe",
        "",
        "This offline probe treats k-gram metadata as a query-planning problem.",
        "It compares full scan, rarest-feature selection, entropy gates, cost gates,",
        "and adaptive IDF-style selectors. It does not change the .zlg file format.",
        "",
        "## Corpus",
        "",
        f"- Lines: {lines}",
        f"- Input bytes: {input_bytes}",
        f"- Input sha256: {digest}",
        "",
        "## Planner decision counts",
        "",
        "| planner_decision | rows |",
        "|---|---:|",
    ]
    for decision, count in sorted(decision_counts.items()):
        doc.append(f"| {decision} | {count} |")

    doc.extend([
        "",
        "## Strategy wins by pattern",
        "",
        "| strategy | pattern_wins |",
        "|---|---:|",
    ])
    for strategy, count in sorted(strategy_wins.items()):
        doc.append(f"| {strategy} | {count} |")

    doc.extend([
        "",
        "## Best strategy by pattern",
        "",
        "| pattern | block_lines | strategy | decision | selected_blocks | decoded_ratio | features | info_max | feature_summary |",
        "|---|---:|---|---|---:|---:|---:|---:|---|",
    ])
    for pattern in sorted(best_by_pattern):
        row = best_by_pattern[pattern]
        doc.append(
            f"| {pattern} | {row['block_lines']} | {row['strategy']} | {row['planner_decision']} | "
            f"{row['selected_blocks']} | {float(row['estimated_decoded_ratio']):.3f} | "
            f"{row['chosen_feature_count']} | {float(row['chosen_info_max']):.2f} | "
            f"{row['chosen_feature_summary']} |"
        )

    doc.extend([
        "",
        "## Best strategy by pattern and block size",
        "",
        "| pattern | block_lines | strategy | decision | selected_blocks | decoded_ratio | info_sum |",
        "|---|---:|---|---|---:|---:|---:|",
    ])
    for key in sorted(best_by_pattern_block):
        row = best_by_pattern_block[key]
        doc.append(
            f"| {row['pattern_name']} | {row['block_lines']} | {row['strategy']} | "
            f"{row['planner_decision']} | {row['selected_blocks']} | "
            f"{float(row['estimated_decoded_ratio']):.3f} | {float(row['chosen_info_sum']):.2f} |"
        )

    doc.extend([
        "",
        "## Interpretation guide",
        "",
        "- `use_index` means the planner found a useful selective feature set.",
        "- `full_scan_low_entropy` means selector features were too common to be worth index use.",
        "- `full_scan_cost_gate` means estimated decode ratio stayed too high.",
        "- High chosen_info_max means at least one selector feature is rare in the block population.",
        "- If common patterns remain full scan, that is acceptable; the planner is learning not to waste index work.",
        "- A useful future on-disk profile should store only the statistics and postings needed by winning planner variants.",
    ])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")


def parse_block_lines(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lines", type=int, default=125000)
    parser.add_argument("--block-lines", default="512,1024,2048,4096")
    parser.add_argument("--output", default="validation_results/phase0p_adaptive_planner_probe.md")
    parser.add_argument("--csv", default="validation_results/phase0p_adaptive_planner_probe.csv")
    args = parser.parse_args()

    tmp = REPO / "validation_results" / "phase0p_adaptive_planner_corpus.tmp"
    make_corpus(tmp, args.lines)
    raw = tmp.read_bytes()
    raw_lines = raw.splitlines(keepends=True)
    digest = sha256(tmp)
    input_bytes = tmp.stat().st_size
    tmp.unlink()

    patterns = list(PATTERNS) + EXTRA_PATTERNS
    strategies = [
        "full_scan",
        "best_trigram_1",
        "best_trigram_2",
        "best_edge_1",
        "best_edge_2",
        "best_mixed_2",
        "entropy_gate_2bits",
        "entropy_gate_4bits",
        "adaptive_25pct",
        "adaptive_10pct",
        "cost_gate_75pct",
        "cost_gate_35pct",
    ]

    rows: list[dict[str, object]] = []
    for block_lines in parse_block_lines(args.block_lines):
        blocks = build_blocks(raw_lines, block_lines)
        bigram_df = df_counter(blocks, "bigrams")
        trigram_df = df_counter(blocks, "trigrams")
        edge_df = df_counter(blocks, "edges")
        bigram_occ = occurrence_counter(blocks, "bigram_counts")
        trigram_occ = occurrence_counter(blocks, "trigram_counts")
        edge_occ = occurrence_counter(blocks, "edge_counts")
        index_bytes = estimate_index_bytes(blocks)
        total_blocks = len(blocks)

        for name, engine, pattern in patterns:
            mode, literals = selector(pattern, engine)
            literal_feature_sets = [
                literal_features(
                    literal,
                    total_blocks,
                    bigram_df,
                    trigram_df,
                    edge_df,
                    bigram_occ,
                    trigram_occ,
                    edge_occ,
                )
                for literal in literals
            ]

            for strategy in strategies:
                decision, chosen, selected = select_for_pattern(
                    strategy,
                    blocks,
                    mode,
                    literal_feature_sets,
                )
                selected_blocks, selected_bytes, selected_ratio, decoded_ratio = summarize_selection(
                    blocks,
                    selected,
                )
                (
                    chosen_df_min,
                    chosen_df_max,
                    chosen_occ_sum,
                    chosen_info_max,
                    chosen_info_sum,
                    chosen_feature_summary,
                ) = summarize_features(chosen)

                rows.append({
                    "pattern_name": name,
                    "engine": engine,
                    "pattern": pattern,
                    "selector_mode": mode,
                    "selector_count": len(literals),
                    "strategy": strategy,
                    "planner_decision": decision,
                    "block_lines": block_lines,
                    "total_blocks": total_blocks,
                    "selected_blocks": selected_blocks,
                    "selected_ratio": f"{selected_ratio:.6f}",
                    "estimated_decoded_bytes": selected_bytes,
                    "estimated_decoded_ratio": f"{decoded_ratio:.6f}",
                    "estimated_index_bytes": index_bytes,
                    "chosen_feature_count": len(chosen),
                    "chosen_df_min": chosen_df_min,
                    "chosen_df_max": chosen_df_max,
                    "chosen_occurrence_sum": chosen_occ_sum,
                    "chosen_info_max": f"{chosen_info_max:.6f}",
                    "chosen_info_sum": f"{chosen_info_sum:.6f}",
                    "chosen_feature_summary": chosen_feature_summary,
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
