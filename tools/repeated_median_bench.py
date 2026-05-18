#!/usr/bin/env python3
"""Repeated-median wrapper for the performance smoke bench.

This wrapper intentionally reuses the performance benchmark so the command
matrix stays consistent while adding repeated runs and median rows for trend
comparisons.
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import tempfile
from pathlib import Path
from statistics import median
from typing import Iterable

METRIC_FIELDS = ("wall_seconds", "user_seconds", "system_seconds", "cpu_percent", "max_rss_kb")
GROUP_FIELDS = ("scenario", "backend", "mode", "operation", "pattern_type")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run repeated median zlg bench")
    parser.add_argument("--zlg-bin", default=os.environ.get("ZLG_BIN", "target/release/zlg"))
    parser.add_argument("--out-csv", default="validation_results/repeated_median_smoke.csv")
    parser.add_argument("--out-md", default="validation_results/repeated_median_smoke.md")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--repeated-lines", type=int, default=120_000)
    parser.add_argument("--needle-lines", type=int, default=1_000_000)
    parser.add_argument("--needle-position-ratio", type=float, default=0.80)
    parser.add_argument("--head-lines", type=int, default=10)
    parser.add_argument("--tail-lines", type=int, default=10)
    parser.add_argument("--tail-large-lines", type=int, default=5_000)
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_float(value: str) -> float:
    if value == "" or value.lower() == "n/a":
        raise ValueError(f"missing numeric metric: {value!r}")
    return float(value)


def group_key(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row[field] for field in GROUP_FIELDS)


def median_row(rows: list[dict[str, str]]) -> dict[str, str]:
    first = rows[0]
    out = dict(first)
    out["run"] = "median"
    out["aggregate"] = "median"
    for field in METRIC_FIELDS:
        out[field] = f"{median(parse_float(row[field]) for row in rows):.6f}"
    for field in ("storage_bytes", "output_bytes", "match_count"):
        values = [row[field] for row in rows]
        out[field] = values[0] if all(value == values[0] for value in values) else "varies"
    parities = {row.get("parity", "") for row in rows}
    out["parity"] = "ok" if parities == {"ok"} else ",".join(sorted(parities))
    exits = {row.get("exit_code", "") for row in rows}
    out["exit_code"] = "0" if exits == {"0"} else ",".join(sorted(exits))
    out["output_sha256"] = rows[0].get("output_sha256", "")
    out["measurement_source"] = "median(os.wait4)"
    out["command"] = f"median of {len(rows)} runs"
    return out


def validate_rows(rows: Iterable[dict[str, str]]) -> None:
    errors: list[str] = []
    for index, row in enumerate(rows, start=2):
        for field in METRIC_FIELDS:
            try:
                parse_float(row[field])
            except ValueError:
                errors.append(f"row {index}: missing {field}")
        if row.get("parity") not in ("ok", "n/a"):
            errors.append(f"row {index}: bad parity {row.get('parity')}")
        if row.get("exit_code") not in ("0", 0):
            errors.append(f"row {index}: bad exit {row.get('exit_code')}")
    if errors:
        raise RuntimeError("invalid repeated-median rows:\n" + "\n".join(errors))


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "run",
        "aggregate",
        "scenario",
        "backend",
        "mode",
        "operation",
        "pattern_type",
        "storage_bytes",
        "wall_seconds",
        "user_seconds",
        "system_seconds",
        "cpu_percent",
        "max_rss_kb",
        "exit_code",
        "output_bytes",
        "output_sha256",
        "match_count",
        "parity",
        "measurement_source",
        "command",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def wall_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], float]:
    out: dict[tuple[str, str, str], float] = {}
    for row in rows:
        if row.get("aggregate") == "median":
            out[(row["scenario"], row["operation"], row["backend"])] = parse_float(row["wall_seconds"])
    return out


def write_markdown(rows: list[dict[str, str]], path: Path) -> None:
    medians = [row for row in rows if row.get("aggregate") == "median"]
    lines = [
        "# Repeated median bench",
        "",
        "This report repeats the fast/standard benchmark and summarizes median resource metrics.",
        "",
        "| scenario | backend | mode | operation | storage bytes | median wall | median user | median system | median cpu percent | median rss kb | matches | parity |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in medians:
        lines.append(
            "| {scenario} | {backend} | {mode} | {operation} | {storage_bytes} | {wall_seconds} | {user_seconds} | {system_seconds} | {cpu_percent} | {max_rss_kb} | {match_count} | {parity} |".format(**row)
        )
    ratios = wall_lookup(rows)
    lines.extend(["", "## Median wall-time ratios", ""])
    for scenario in sorted({row["scenario"] for row in medians}):
        for operation in ("build", "search", "head", "tail", "tail_large"):
            gzip = ratios.get((scenario, operation, "gzip"))
            plain = ratios.get((scenario, operation, "plain"))
            standard = ratios.get((scenario, operation, "zlg_standard"))
            fast = ratios.get((scenario, operation, "zlg_fast"))
            if fast and gzip:
                lines.append(f"- {scenario} {operation}: zlg_fast vs gzip median wall ratio {fast / gzip:.3f}")
            if standard and gzip:
                lines.append(f"- {scenario} {operation}: zlg_standard vs gzip median wall ratio {standard / gzip:.3f}")
            if fast and plain and operation != "build":
                lines.append(f"- {scenario} {operation}: zlg_fast vs plain median wall ratio {fast / plain:.3f}")
            if fast and standard:
                lines.append(f"- {scenario} {operation}: zlg_fast vs zlg_standard median wall ratio {fast / standard:.3f}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.repeats < 1:
        raise SystemExit("--repeats must be at least 1")
    script = Path("tools/perf_modes_head_tail_bench.py")
    if not script.exists():
        raise SystemExit(f"missing benchmark script: {script}")

    all_rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="zlg-median-") as temp_dir:
        temp = Path(temp_dir)
        for run in range(1, args.repeats + 1):
            run_csv = temp / f"run_{run}.csv"
            run_md = temp / f"run_{run}.md"
            cmd = [
                "python3",
                str(script),
                "--zlg-bin",
                args.zlg_bin,
                "--out-csv",
                str(run_csv),
                "--out-md",
                str(run_md),
                "--repeated-lines",
                str(args.repeated_lines),
                "--needle-lines",
                str(args.needle_lines),
                "--needle-position-ratio",
                str(args.needle_position_ratio),
                "--head-lines",
                str(args.head_lines),
                "--tail-lines",
                str(args.tail_lines),
                "--tail-large-lines",
                str(args.tail_large_lines),
            ]
            subprocess.run(cmd, check=True)
            for row in read_csv(run_csv):
                row["run"] = str(run)
                row["aggregate"] = "run"
                all_rows.append(row)

    validate_rows(all_rows)
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = {}
    for row in all_rows:
        grouped.setdefault(group_key(row), []).append(row)
    median_rows = [median_row(group) for group in grouped.values()]
    median_rows.sort(key=lambda row: (row["scenario"], row["operation"], row["backend"], row["mode"]))
    output_rows = all_rows + median_rows
    write_csv(output_rows, Path(args.out_csv))
    write_markdown(output_rows, Path(args.out_md))
    print(f"wrote {args.out_csv}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
