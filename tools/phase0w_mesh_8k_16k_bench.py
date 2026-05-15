#!/usr/bin/env python3
"""Phase 0w focused mesh-bigram benchmark.

This benchmark drops non-mesh zlg candidates and compares only mesh-bigram
profiles against gzip/zgrep and original/plain grep baselines.

It tests fixed-lines4096, fixed-lines8192, fixed-lines16384, and fixed-lines64k
so we can see whether 8K or 16K improves storage while preserving the selective
search advantage observed at 4096.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import resource
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

POLICIES = ["fixed-lines4096", "fixed-lines8192", "fixed-lines16384", "fixed-lines64k"]
SUMMARY_MODE = "mesh-bigram"

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
        "query_name": "common_fixed_failed_password",
        "mode": "fixed",
        "pattern": "failed password",
        "zlg_args": ["-F", "failed password"],
        "grep_args": ["-F", "failed password"],
        "zgrep_args": ["-F", "failed password"],
    },
    {
        "query_name": "regex_key_value",
        "mode": "rust_regex",
        "pattern": r'key="[^"]+"',
        "zlg_args": [r'key="[^"]+"'],
        "grep_args": ["-E", r'key="[^"]+"'],
        "zgrep_args": ["-E", r'key="[^"]+"'],
    },
    {
        "query_name": "fancy_regex_key_value",
        "mode": "fancy_regex",
        "pattern": r'(?<=key=")[^"]+',
        "zlg_args": ["-P", r'(?<=key=")[^"]+'],
        "grep_args": ["-P", r'(?<=key=")[^"]+'],
        "zgrep_args": ["-P", r'(?<=key=")[^"]+'],
    },
]


def tool_exists(name: str) -> bool:
    return shutil.which(name) is not None


def time_tool() -> str | None:
    candidate = "/usr/bin/time"
    if Path(candidate).exists():
        return candidate
    found = shutil.which("time")
    return found


def parse_time_v(path: Path) -> dict[str, str]:
    out = {"user_seconds": "", "system_seconds": "", "max_rss_kb": ""}
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


def rusage_snapshot() -> resource.struct_rusage:
    return resource.getrusage(resource.RUSAGE_CHILDREN)


def rusage_delta(before: resource.struct_rusage, after: resource.struct_rusage) -> dict[str, str]:
    user = max(0.0, after.ru_utime - before.ru_utime)
    system = max(0.0, after.ru_stime - before.ru_stime)
    max_rss = max(0, after.ru_maxrss - before.ru_maxrss)
    return {
        "user_seconds": f"{user:.6f}",
        "system_seconds": f"{system:.6f}",
        "max_rss_kb": str(max_rss) if max_rss else "",
    }


def run_measured(cmd: list[str], *, stdout_path: Path | None, tmp: Path) -> dict[str, object]:
    stamp = str(time.perf_counter_ns())
    time_path = tmp / f"time-{stamp}.txt"
    time_bin = time_tool()
    actual_cmd = cmd
    uses_time = False
    if time_bin:
        actual_cmd = [time_bin, "-v", "-o", str(time_path)] + cmd
        uses_time = True

    before = rusage_snapshot()
    start = time.perf_counter()
    if stdout_path is None:
        proc = subprocess.run(actual_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        with stdout_path.open("wb") as handle:
            proc = subprocess.run(actual_cmd, stdout=handle, stderr=subprocess.PIPE)
    wall = time.perf_counter() - start
    after = rusage_snapshot()

    parsed = parse_time_v(time_path) if uses_time else {"user_seconds": "", "system_seconds": "", "max_rss_kb": ""}
    if time_path.exists():
        time_path.unlink()

    if parsed["user_seconds"] == "" and parsed["system_seconds"] == "":
        parsed = rusage_delta(before, after)

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
        "original_bytes": meta["input_bytes"],
        "gzip6_bytes": "",
        "size_vs_original_bytes": "",
        "size_vs_gzip6_bytes": "",
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
    with tempfile.TemporaryDirectory(prefix="zlg-phase0w-") as tmp_name:
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
            row.update({
                "tool": "gzip",
                "operation": "compress",
                "output_bytes": gzip6_bytes,
                "gzip6_bytes": gzip6_bytes,
                "size_vs_original_bytes": str(int(gzip6_bytes) - corpus_bytes),
                "size_vs_gzip6_bytes": "0",
            })
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

        zlg_paths: dict[str, Path] = {}
        for policy in POLICIES:
            out = tmp / f"{policy}-{SUMMARY_MODE}.zlg"
            def compress_cmd(policy=policy, out=out):
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
                    SUMMARY_MODE,
                ], None)
            timing = run_repeated(compress_cmd, args.repeats, tmp)
            out_bytes = out.stat().st_size
            zlg_paths[policy] = out
            row = base_row(meta)
            row.update({
                "tool": "zlg",
                "operation": "compress",
                "policy": policy,
                "summary_mode": SUMMARY_MODE,
                "output_bytes": out_bytes,
                "gzip6_bytes": gzip6_bytes,
                "size_vs_original_bytes": str(out_bytes - corpus_bytes),
            })
            if gzip6_bytes:
                row["size_vs_gzip6_bytes"] = str(out_bytes - int(gzip6_bytes))
            add_timing(row, timing)
            rows.append(row)

        for policy, path in zlg_paths.items():
            def cat_cmd(path=path):
                return ([str(binary), "cat", str(path)], devnull)
            timing = run_repeated(cat_cmd, args.repeats, tmp)
            row = base_row(meta)
            row.update({
                "tool": "zlg",
                "operation": "decompress",
                "policy": policy,
                "summary_mode": SUMMARY_MODE,
                "output_bytes": path.stat().st_size,
                "gzip6_bytes": gzip6_bytes,
            })
            add_timing(row, timing)
            rows.append(row)

            for query in QUERIES:
                stats_path = tmp / f"{policy}-{query['query_name']}.json"
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
                    "summary_mode": SUMMARY_MODE,
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


def by_operation(rows: list[dict[str, object]], operation: str) -> list[dict[str, object]]:
    return [row for row in rows if row["operation"] == operation]


def write_markdown(path: Path, rows: list[dict[str, object]], meta: dict[str, object]) -> None:
    doc = [
        "# zlg Phase 0w mesh-bigram 8K/16K benchmark",
        "",
        "This report compares mesh-bigram only at fixed-lines4096, fixed-lines8192,",
        "fixed-lines16384, and fixed-lines64k against gzip/zgrep and original grep.",
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
        f"- external time available: {meta['time_available']}",
        "",
        "## Compression and storage",
        "",
        "| tool | policy | summary | bytes | vs_original | vs_gzip6 | wall_s | cpu_s | max_rss_kb |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in by_operation(rows, "compress"):
        doc.append(
            f"| {row['tool']} | {row['policy']} | {row['summary_mode']} | "
            f"{row['output_bytes']} | {row['size_vs_original_bytes']} | {row['size_vs_gzip6_bytes']} | "
            f"{row['wall_seconds']} | {row['total_cpu_seconds']} | {row['max_rss_kb']} |"
        )

    doc.extend([
        "",
        "## Decompression",
        "",
        "| tool | policy | summary | wall_s | cpu_s | max_rss_kb |",
        "|---|---|---|---:|---:|---:|",
    ])
    for row in by_operation(rows, "decompress"):
        doc.append(
            f"| {row['tool']} | {row['policy']} | {row['summary_mode']} | "
            f"{row['wall_seconds']} | {row['total_cpu_seconds']} | {row['max_rss_kb']} |"
        )

    doc.extend([
        "",
        "## Search",
        "",
        "| tool | policy | query | mode | wall_s | cpu_s | max_rss_kb | decoded_ratio | chunks_decoded | chunks_total | matches | available |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in by_operation(rows, "search"):
        doc.append(
            f"| {row['tool']} | {row['policy']} | {row['query_name']} | {row['query_mode']} | "
            f"{row['wall_seconds']} | {row['total_cpu_seconds']} | {row['max_rss_kb']} | "
            f"{row['decoded_ratio']} | {row['chunks_decoded']} | {row['chunks_total']} | "
            f"{row['matching_lines']} | {row['available']} |"
        )

    doc.extend([
        "",
        "## Interpretation guide",
        "",
        "- `fixed-lines8192` and `fixed-lines16384` are the new candidates.",
        "- `fixed-lines4096` remains as the prior selective-search reference.",
        "- `fixed-lines64k` remains as the compression-first reference.",
        "- Non-mesh zlg candidates are intentionally omitted from this phase.",
        "- `regex_key_value` uses Rust's standard regex path.",
        "- `fancy_regex_key_value` uses fancy-regex with lookbehind.",
        "- CPU/RSS values use `/usr/bin/time -v` when available and Python `resource` fallback otherwise.",
    ])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", default="target/release/zlg")
    parser.add_argument("--lines", type=int, default=125000)
    parser.add_argument("--needle-ratio", type=float, default=0.80)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", default="validation_results/phase0w_mesh_8k_16k_bench.md")
    parser.add_argument("--csv", default="validation_results/phase0w_mesh_8k_16k_bench.csv")
    args = parser.parse_args()

    rows, meta = probe(args)
    write_csv(REPO / args.csv, rows)
    write_markdown(REPO / args.output, rows, meta)
    print(f"wrote {REPO / args.output}")
    print(f"wrote {REPO / args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
