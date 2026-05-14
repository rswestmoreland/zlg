#!/usr/bin/env python3
"""Summarize Phase 0l index strategy comparisons.

This reads the compact benchmark CSV and compares:
  - .zlg with bitmap summaries
  - .zlg with no search summaries
  - gzip/zgrep and plain grep/rg baselines when present
  - zstd/zstdcat baselines when present

The report is intentionally compact and ASCII-only.
"""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path


def f(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, "") or 0.0)
    except ValueError:
        return 0.0


def ratio(num: float, den: float) -> str:
    if den <= 0:
        return "n/a"
    return f"{num / den:.3f}"


def med(values: list[float]) -> float:
    return statistics.median(values) if values else 0.0


def group_medians(rows: list[dict[str, str]], keys: tuple[str, ...], value: str) -> dict[tuple[str, ...], float]:
    grouped: dict[tuple[str, ...], list[float]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row.get(key, "") for key in keys)].append(f(row, value))
    return {key: med(vals) for key, vals in grouped.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    csv_path = Path(args.csv)
    rows = list(csv.DictReader(csv_path.open("r", encoding="utf-8")))

    compress_rows = [row for row in rows if row.get("kind") == "compress"]
    grep_rows = [row for row in rows if row.get("kind") in ("grep", "grep_baseline")]
    zlg_grep = [row for row in grep_rows if row.get("name") == "zlg_grep"]
    no_index_grep = [row for row in grep_rows if row.get("name") == "zlg_grep_no_index"]

    out: list[str] = []
    out.append("# Phase 0l Index Strategy Analysis")
    out.append("")
    out.append("This is pre-bench evidence only, not the final performance proof.")
    out.append("")

    out.append("## Compression and metadata comparison")
    out.append("")
    out.append("| name | policy | summary_mode | median_s | median_output_bytes | median_payload_bytes | median_summary_bytes | median_overhead_bytes |")
    out.append("|---|---|---|---:|---:|---:|---:|---:|")
    comp_groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in compress_rows:
        comp_groups[(row.get("name", ""), row.get("policy", ""), row.get("summary_mode", ""))].append(row)
    for key in sorted(comp_groups):
        group = comp_groups[key]
        name, policy, summary_mode = key
        out.append(
            "| "
            + " | ".join(
                [
                    name,
                    policy,
                    summary_mode,
                    f"{med([f(r, 'wall_seconds') for r in group]):.6f}",
                    f"{med([f(r, 'output_bytes') for r in group]):.0f}",
                    f"{med([f(r, 'zlg_compressed_payload_bytes') for r in group]):.0f}" if name.startswith("zlg") else "",
                    f"{med([f(r, 'zlg_summary_bytes') for r in group]):.0f}" if name.startswith("zlg") else "",
                    f"{med([f(r, 'zlg_overhead_bytes') for r in group]):.0f}" if name.startswith("zlg") else "",
                ]
            )
            + " |"
        )

    out.append("")
    out.append("## Search timing comparison")
    out.append("")
    out.append("| name | policy | summary_mode | pattern | median_s | first_output_s | chunks_skipped | chunks_decoded | decoded_bytes | matching_lines |")
    out.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|")
    grep_groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in grep_rows:
        grep_groups[(row.get("name", ""), row.get("policy", ""), row.get("summary_mode", ""), row.get("pattern_name", ""))].append(row)
    for key in sorted(grep_groups):
        group = grep_groups[key]
        name, policy, summary_mode, pattern = key
        first_values = [f(r, "first_output_seconds") for r in group if r.get("first_output_seconds")]
        out.append(
            "| "
            + " | ".join(
                [
                    name,
                    policy,
                    summary_mode,
                    pattern,
                    f"{med([f(r, 'wall_seconds') for r in group]):.6f}",
                    f"{med(first_values):.6f}" if first_values else "",
                    f"{med([f(r, 'chunks_skipped') for r in group]):.0f}" if name.startswith("zlg") else "",
                    f"{med([f(r, 'chunks_decoded') for r in group]):.0f}" if name.startswith("zlg") else "",
                    f"{med([f(r, 'decoded_bytes') for r in group]):.0f}" if name.startswith("zlg") else "",
                    f"{med([f(r, 'matching_lines') for r in group]):.0f}" if name.startswith("zlg") else "",
                ]
            )
            + " |"
        )

    out.append("")
    out.append("## Bitmap versus no-index delta")
    out.append("")
    out.append("| policy | pattern | bitmap_s | no_index_s | bitmap/no_index | bitmap_decoded_bytes | no_index_decoded_bytes |")
    out.append("|---|---|---:|---:|---:|---:|---:|")
    bitmap_times = group_medians(zlg_grep, ("policy", "pattern_name"), "wall_seconds")
    no_index_times = group_medians(no_index_grep, ("policy", "pattern_name"), "wall_seconds")
    bitmap_decoded = group_medians(zlg_grep, ("policy", "pattern_name"), "decoded_bytes")
    no_index_decoded = group_medians(no_index_grep, ("policy", "pattern_name"), "decoded_bytes")
    for key in sorted(set(bitmap_times) | set(no_index_times)):
        b = bitmap_times.get(key, 0.0)
        n = no_index_times.get(key, 0.0)
        out.append(
            f"| {key[0]} | {key[1]} | {b:.6f} | {n:.6f} | {ratio(b, n)} | "
            f"{bitmap_decoded.get(key, 0.0):.0f} | {no_index_decoded.get(key, 0.0):.0f} |"
        )

    out.append("")
    out.append("## Preliminary decision notes")
    out.append("")
    if not no_index_grep:
        out.append("- No no-index rows were found. Run the harness with --include-no-index.")
    else:
        wins = 0
        losses = 0
        for key, bitmap in bitmap_times.items():
            no_index = no_index_times.get(key)
            if no_index is None or no_index <= 0:
                continue
            if bitmap < no_index:
                wins += 1
            elif bitmap > no_index:
                losses += 1
        out.append(f"- Bitmap summaries faster than no-index in {wins} grouped comparisons.")
        out.append(f"- Bitmap summaries slower than no-index in {losses} grouped comparisons.")
        out.append("- Keep or remove bitmap summaries should be decided by decoded-byte reduction, first-output latency, and metadata overhead, not by one timing alone.")
    out.append("- If common matching patterns still decode all chunks, next work should prioritize selector extraction and/or smaller independently compressed search blocks before async.")
    out.append("- zstd/zstdcat baselines should be reviewed when those tools are available in the environment.")

    Path(args.output).write_text("\n".join(out) + "\n", encoding="ascii")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
