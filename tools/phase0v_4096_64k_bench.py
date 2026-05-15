#!/usr/bin/env python3
"""Phase 0v focused mesh-bigram benchmark.

This probe compares fixed-lines4096 and fixed-lines64k with mesh-bigram and
no-index summaries against gzip/zgrep and original/plain grep baselines.

It records wall time, user/system CPU, max RSS, output size, compression,
decompression, fixed-string search, and fancy-regex search. Generated corpora
and compressed files are temporary; only compact CSV/Markdown reports are saved.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from statistics import median
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from phase0q_needle_corpus_probe import NEEDLE_IP, make_needle_corpus, sha256  # noqa: E402

POLICIES = ["fixed-lines4096", "fixed-lines64k"]
SUMMARY_MODES = ["mesh-bigram", "none"]

QUERIES = [
    {
        "query_name": "needle_fixed_ip",
        "mode": "fixed",
        "pattern": NEEDLE_IP,
        "zlg_args": ["-F", NEEDLE_IP],
        "grep_args": ["-F", NEEDLE_IP],
        "zgrep_args": ["-F", NEEDLE_IP],
    },
    {
        "query_name": "general_fixed_failed_password",
        "mode": "fixed",
        "pattern": "failed password",
        "zlg_args": ["-F", "failed password"],
        "grep_args": ["-F", "failed password"],
        "zgrep_args": ["-F", "failed password"],
    },
    {
        "query_name": "fancy_regex_key_value",
        "mode": "fancy_regex",
        "pattern": r'(?<=key=")[^\"]+',
        "zlg_args": ["-P", r'(?<=key=")[^\"]+'],
        "grep_args": ["-P", r'(?<=key=")[^\"]+'],
        "zgrep_args": ["-P", r'(?<=key=")[^\"]+'],
    },
]


def tool_exists(name: str) -> bool:
    return shutil.which(name) is not None


def time_tool() -> str | None:
    for candidate in ("/usr/bin/time", "time"):
        found = shutil.which(candidate) if candidate != "/usr/bin/time" else candidate
        if found and Path(found).exists():
            return found
    return None


def parse_time_v(path: Path) -> dict[str, str]:
    out = {
        "user_seconds": "",
        "system_seconds": "",
        "max_rss_kb": "",
    }
    if not path.exists():
        return out
    text = path.read_text(encoding="utf-8", errors="replace")
    patterns = {
        "user_seconds": r"User time \(seconds\):\s*([0-9.]+)",
        "system_seconds": r"System time \(seconds\):\s*([0-9.]+)",
        "max_rss_kb": r"Maximum resident set size \(kbytes\):\s*([0-9]+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            out[key] = match.group(1)
    return out


def run_measured(cmd: list[str], *, stdout_path: Path | None, tmp: Path) -> dict[str, object]:
    stamp = str(time.perf_counter_ns())
    time_path = tmp / f"time-{stamp}.txt"
    time_bin = time_tool()
    actual_cmd = cmd
    if time_bin:
        actual_cmd = [time_bin, "-v", "-o", str(time_path)] + cmd

    start = time.perf_counter()
    if stdout_path is None:
        proc = subprocess.run(actual_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        with stdout_path.open("wb") as handle:
            proc = subprocess.run(actual_cmd, stdout=handle, stderr=subprocess.PIPE)
    wall = time.perf_counter() - start

    parsed = parse_time_v(time_path)
    if time_path.exists():
        time_path.unlink()

    stderr = proc.stderr.decode("utf-8", "replace") if isinstance(proc.stderr, bytes) else str(proc.stderr)
    stdout = proc.stdout.decode("utf-8", "replace") if isinstance(proc.stdout, bytes) else str(proc.stdout)
    return {
        "returncode": proc.returncode,
        "wall_seconds": wall,
        "user_seconds": parsed["user_seconds"],
        "system_seconds": parsed["system_seconds"],
        "max_rss_kb": parsed["max_rss_kb"],
        "stdout": stdout,
        "stderr": stderr,
    }


def median_float(values: list[object]) -> str:
    nums = []
    for value in values:
        if value == "" or value is None:
            continue
        nums.append(float(value))
    if not nums:
        return ""
    return f"{median(nums):.6f}"


def median_int(values: list[object]) -> str:
    nums = []
    for value in values:
        if value == "" or value is None:
            continue
        nums.append(int(float(value)))
    if not nums:
        return ""
    return str(int(median(nums)))


def run_repeated(cmd_factory, repeats: int, tmp: Path, *, allow_nonzero: bool = False) -> dict[str, object]:
    samples = []
    last = None
    for _ in range(repeats):
        cmd, stdout_path = cmd_factory()
        result = run_measured(cmd, stdout_path=stdout_path, tmp=tmp)
        last = result
        if result["returncode"] != 0 and not allow_nonzero:
            raise SystemExit(
                "command failed {}: {}\nSTDOUT:\n{}\nSTDERR:\n{}".format(
                    result["returncode"], " ".join(cmd), result["stdout"], result["stderr"]
                )
            )
        samples.append(result)
    return {
        "returncode": last["returncode"] if last else 0,
        "wall_seconds": median_float([item["wall_seconds"] for item in samples]),
        "user_seconds": median_float([item["user_seconds"] for item in samples]),
        "system_seconds": median_float([item["system_seconds"] for item in samples]),
        "max_rss_kb": median_int([item["max_rss_kb"] for item in samples]),
        "last_stdout": last["stdout"] if last else "",
        "last_stderr": last["stderr"] if last else "",
    }


def read_stats(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def base_row(meta: dict[str, object]) -> dict[str, object]:
    return {
        "corpus_lines": meta["lines"],
        "corpus_bytes": meta["input_bytes"],
        "needle_ip": meta["needle_ip"],
        "needle_line": meta["needle_line"],
        "needle_ratio": f"{float(meta['needle_ratio']):.6f}",
        "tool": "",
        "operation": "",
        "policy": "",
        "summary_mode": "",
        "query_name": "",
        "query_mode": "",
        "pattern": "",
        "output_bytes": "",
        "gzip6_bytes": "",
        "size_vs_gzip6_bytes": "",
        "overhead_vs_none_bytes": "",
        "wall_seconds": "",
        "user_seconds": "",
        "system_seconds": "",
        "total_cpu_seconds": "",
        "max_rss_kb": "",
        "chunks_total": "",
        "chunks_skipped": "",
        "candidate_chunks": "",
        "chunks_decoded": "",
        "decoded_bytes": "",
        "decoded_ratio": "",
        "selected_chunk_ratio": "",
        "matching_lines": "",
        "selector_kind": "",
        "selector_len": "",
        "selector_count": "",
        "returncode": "",
        "available": "yes",
        "notes": "",
    }


def add_timing(row: dict[str, object], timing: dict[str, object]) -> None:
    row["wall_seconds"] = timing["wall_seconds"]
    row["user_seconds"] = timing["user_seconds"]
    row["system_seconds"] = timing["system_seconds"]
    if timing["user_seconds"] != "" and timing["system_seconds"] != "":
        row["total_cpu_seconds"] = f"{float(timing['user_seconds']) + float(timing['system_seconds']):.6f}"
    row["max_rss_kb"] = timing["max_rss_kb"]
    row["returncode"] = timing["returncode"]


def add_grep_stats(row: dict[str, object], stats: dict[str, object], corpus_bytes: int) -> None:
    for key in [
        "chunks_total",
        "chunks_skipped",
        "candidate_chunks",
        "chunks_decoded",
        "decoded_bytes",
        "matching_lines",
        "selector_kind",
        "selector_len",
        "selector_count",
    ]:
        row[key] = stats.get(key, "")
    decoded = int(stats.get("decoded_bytes", 0))
    total = int(stats.get("chunks_total", 0))
    decoded_chunks = int(stats.get("chunks_decoded", 0))
    row["decoded_ratio"] = f"{decoded / corpus_bytes:.6f}" if corpus_bytes else ""
    row["selected_chunk_ratio"] = f"{decoded_chunks / total:.6f}" if total else ""


def probe(args: argparse.Namespace) -> tuple[list[dict[str, object]], dict[str, object]]:
    binary = Path(args.binary)
    if not binary.exists():
        raise SystemExit(f"binary not found: {binary}")

    rows: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="zlg-phase0v-") as tmp_name:
        tmp = Path(tmp_name)
        devnull = Path(os.devnull)
        corpus = tmp / "needle.log"
        needle_line = make_needle_corpus(corpus, args.lines, args.needle_ratio)
        corpus_bytes = corpus.stat().st_size
        digest = sha256(corpus)
        meta = {
            "lines": args.lines,
            "input_bytes": corpus_bytes,
            "sha256": digest,
            "needle_ip": NEEDLE_IP,
            "needle_line": needle_line,
            "needle_ratio": needle_line / args.lines,
            "gzip_available": tool_exists("gzip"),
            "zgrep_available": tool_exists("zgrep"),
            "grep_available": tool_exists("grep"),
            "time_available": time_tool() is not None,
        }

        gzip_path = tmp / "needle.log.gz"
        gzip6_bytes = ""
        if meta["gzip_available"]:
            def gzip_cmd():
                if gzip_path.exists():
                    gzip_path.unlink()
                return (["gzip", "-6", "-c", str(corpus)], gzip_path)
            timing = run_repeated(gzip_cmd, args.repeats, tmp)
            gzip6_bytes = str(gzip_path.stat().st_size)
            row = base_row(meta)
            row.update({"tool": "gzip", "operation": "compress", "output_bytes": gzip6_bytes, "gzip6_bytes": gzip6_bytes})
            add_timing(row, timing)
            rows.append(row)

            def gunzip_cmd():
                return (["gzip", "-dc", str(gzip_path)], devnull)
            timing = run_repeated(gunzip_cmd, args.repeats, tmp)
            row = base_row(meta)
            row.update({"tool": "gzip", "operation": "decompress", "gzip6_bytes": gzip6_bytes})
            add_timing(row, timing)
            rows.append(row)

        if meta["grep_available"]:
            for query in QUERIES:
                def grep_cmd(query=query):
                    return (["grep"] + query["grep_args"] + [str(corpus)], devnull)
                timing = run_repeated(grep_cmd, args.repeats, tmp, allow_nonzero=True)
                row = base_row(meta)
                row.update({
                    "tool": "grep_original",
                    "operation": "search",
                    "query_name": query["query_name"],
                    "query_mode": query["mode"],
                    "pattern": query["pattern"],
                    "gzip6_bytes": gzip6_bytes,
                })
                add_timing(row, timing)
                if timing["returncode"] not in (0, 1):
                    row["available"] = "no"
                    row["notes"] = "grep command failed, likely unsupported option"
                rows.append(row)

        if meta["zgrep_available"] and gzip_path.exists():
            for query in QUERIES:
                def zgrep_cmd(query=query):
                    return (["zgrep"] + query["zgrep_args"] + [str(gzip_path)], devnull)
                timing = run_repeated(zgrep_cmd, args.repeats, tmp, allow_nonzero=True)
                row = base_row(meta)
                row.update({
                    "tool": "zgrep",
                    "operation": "search",
                    "query_name": query["query_name"],
                    "query_mode": query["mode"],
                    "pattern": query["pattern"],
                    "gzip6_bytes": gzip6_bytes,
                })
                add_timing(row, timing)
                if timing["returncode"] not in (0, 1):
                    row["available"] = "no"
                    row["notes"] = "zgrep command failed, likely unsupported option"
                rows.append(row)

        zlg_paths: dict[tuple[str, str], Path] = {}
        none_sizes: dict[str, int] = {}
        for policy in POLICIES:
            for mode in SUMMARY_MODES:
                out = tmp / f"{policy}-{mode}.zlg"
                def compress_cmd(policy=policy, mode=mode, out=out):
                    if out.exists():
                        out.unlink()
                    return ([
                        str(binary),
                        "compress",
                        str(corpus),
                        "-o",
                        str(out),
                        "--chunk-policy",
                        policy,
                        "--summary-mode",
                        mode,
                    ], None)
                timing = run_repeated(compress_cmd, args.repeats, tmp)
                out_bytes = out.stat().st_size
                zlg_paths[(policy, mode)] = out
                if mode == "none":
                    none_sizes[policy] = out_bytes
                row = base_row(meta)
                row.update({
                    "tool": "zlg",
                    "operation": "compress",
                    "policy": policy,
                    "summary_mode": mode,
                    "output_bytes": out_bytes,
                    "gzip6_bytes": gzip6_bytes,
                })
                if gzip6_bytes:
                    row["size_vs_gzip6_bytes"] = str(out_bytes - int(gzip6_bytes))
                add_timing(row, timing)
                rows.append(row)

        # Fill overhead now that none sizes are known.
        for row in rows:
            if row["tool"] == "zlg" and row["operation"] == "compress":
                policy = str(row["policy"])
                if policy in none_sizes:
                    row["overhead_vs_none_bytes"] = str(int(row["output_bytes"]) - none_sizes[policy])

        for (policy, mode), path in zlg_paths.items():
            def cat_cmd(path=path):
                return ([str(binary), "cat", str(path)], devnull)
            timing = run_repeated(cat_cmd, args.repeats, tmp)
            row = base_row(meta)
            row.update({
                "tool": "zlg",
                "operation": "decompress",
                "policy": policy,
                "summary_mode": mode,
                "output_bytes": path.stat().st_size,
                "gzip6_bytes": gzip6_bytes,
            })
            add_timing(row, timing)
            rows.append(row)

            for query in QUERIES:
                stats_path = tmp / f"{policy}-{mode}-{query['query_name']}.json"
                def grep_cmd(path=path, query=query, stats_path=stats_path):
                    if stats_path.exists():
                        stats_path.unlink()
                    return ([
                        str(binary),
                        "grep",
                        "--stats-json",
                        str(stats_path),
                    ] + query["zlg_args"] + [str(path)], devnull)
                timing = run_repeated(grep_cmd, args.repeats, tmp, allow_nonzero=True)
                row = base_row(meta)
                row.update({
                    "tool": "zlg",
                    "operation": "search",
                    "policy": policy,
                    "summary_mode": mode,
                    "query_name": query["query_name"],
                    "query_mode": query["mode"],
                    "pattern": query["pattern"],
                    "output_bytes": path.stat().st_size,
                    "gzip6_bytes": gzip6_bytes,
                })
                add_timing(row, timing)
                if stats_path.exists():
                    add_grep_stats(row, read_stats(stats_path), corpus_bytes)
                if timing["returncode"] not in (0, 1):
                    row["available"] = "no"
                    row["notes"] = "zlg grep returned unexpected status"
                rows.append(row)

        return rows, meta


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = list(base_row({
        "lines": "",
        "input_bytes": "",
        "needle_ip": "",
        "needle_line": "",
        "needle_ratio": 0.0,
    }).keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def table_rows(rows: list[dict[str, object]], *, operation: str, tool: str | None = None) -> list[dict[str, object]]:
    out = [row for row in rows if row["operation"] == operation]
    if tool:
        out = [row for row in out if row["tool"] == tool]
    return out


def write_markdown(path: Path, rows: list[dict[str, object]], meta: dict[str, object]) -> None:
    doc = [
        "# zlg Phase 0v 4096 vs 64K benchmark",
        "",
        "This report compares the focused mesh-bigram candidate at fixed-lines4096",
        "and fixed-lines64k against no-index zlg, gzip/zgrep, and original grep.",
        "",
        "## Corpus",
        "",
        f"- Lines: {meta['lines']}",
        f"- Input bytes: {meta['input_bytes']}",
        f"- Input sha256: {meta['sha256']}",
        f"- Needle IP: {meta['needle_ip']}",
        f"- Needle line: {meta['needle_line']}",
        f"- Needle ratio: {float(meta['needle_ratio']):.3f}",
        f"- gzip available: {meta['gzip_available']}",
        f"- zgrep available: {meta['zgrep_available']}",
        f"- grep available: {meta['grep_available']}",
        f"- /usr/bin/time available: {meta['time_available']}",
        "",
        "## Compression and storage",
        "",
        "| tool | policy | summary | bytes | vs_gzip6 | overhead_vs_none | wall_s | cpu_s | max_rss_kb |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in table_rows(rows, operation="compress"):
        doc.append(
            f"| {row['tool']} | {row['policy']} | {row['summary_mode']} | "
            f"{row['output_bytes']} | {row['size_vs_gzip6_bytes']} | "
            f"{row['overhead_vs_none_bytes']} | {row['wall_seconds']} | "
            f"{row['total_cpu_seconds']} | {row['max_rss_kb']} |"
        )

    doc.extend([
        "",
        "## Decompression",
        "",
        "| tool | policy | summary | wall_s | cpu_s | max_rss_kb |",
        "|---|---|---|---:|---:|---:|",
    ])
    for row in table_rows(rows, operation="decompress"):
        doc.append(
            f"| {row['tool']} | {row['policy']} | {row['summary_mode']} | "
            f"{row['wall_seconds']} | {row['total_cpu_seconds']} | {row['max_rss_kb']} |"
        )

    doc.extend([
        "",
        "## Search",
        "",
        "| tool | policy | summary | query | mode | wall_s | cpu_s | max_rss_kb | decoded_ratio | chunks_decoded | chunks_total | matches | available |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in table_rows(rows, operation="search"):
        doc.append(
            f"| {row['tool']} | {row['policy']} | {row['summary_mode']} | "
            f"{row['query_name']} | {row['query_mode']} | {row['wall_seconds']} | "
            f"{row['total_cpu_seconds']} | {row['max_rss_kb']} | {row['decoded_ratio']} | "
            f"{row['chunks_decoded']} | {row['chunks_total']} | {row['matching_lines']} | {row['available']} |"
        )

    doc.extend([
        "",
        "## Interpretation guide",
        "",
        "- `fixed-lines4096` is the new storage/search compromise candidate.",
        "- `fixed-lines64k` is the compression-friendly baseline candidate.",
        "- `mesh-bigram` is the only indexed candidate in this phase.",
        "- `none` shows the cost of zlg chunking without search summaries.",
        "- `grep_original` measures plain grep over the uncompressed corpus.",
        "- `zgrep` measures gzip-compressed search when available.",
        "- CPU fields come from `/usr/bin/time -v` when available.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", default="target/release/zlg")
    parser.add_argument("--lines", type=int, default=125000)
    parser.add_argument("--needle-ratio", type=float, default=0.80)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", default="validation_results/phase0v_4096_64k_bench.md")
    parser.add_argument("--csv", default="validation_results/phase0v_4096_64k_bench.csv")
    args = parser.parse_args()

    rows, meta = probe(args)
    write_csv(REPO / args.csv, rows)
    write_markdown(REPO / args.output, rows, meta)
    print(f"wrote {REPO / args.output}")
    print(f"wrote {REPO / args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
