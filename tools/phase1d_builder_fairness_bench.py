#!/usr/bin/env python3
"""Phase 1d builder fairness and robustness benchmark.

The on-disk format remains unchanged. This benchmark keeps fixed-lines8192 +
mesh-bigram and compares build profiles with explicit scratch/memory accounting.
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

BUILD_PROFILES = [
    "combined",
    "combined-inline-lower-delta",
    "combined-bitset-seen",
    "combined-lower-only-bitset-seen",
    "combined-sparse-first-bitset",
    "combined-grouped-buckets",
    "combined-bucket256",
    "combined-radix",
    "combined-case-raw",
    "combined-lower-only",
]

QUERIES = [
    ("needle_fixed_ip", "fixed", NEEDLE_IP, ["-F", NEEDLE_IP], ["-F", NEEDLE_IP]),
    ("common_fixed", "fixed", "failed password", ["-F", "failed password"], ["-F", "failed password"]),
    ("rust_regex_key", "rust_regex", r'key="[^"]+"', [r'key="[^"]+"'], ["-E", r'key="[^"]+"']),
    ("pcre2_lookbehind_key", "pcre2", r'(?<=key=")[^"]+', ["-P", r'(?<=key=")[^"]+'], ["-P", r'(?<=key=")[^"]+']),
    ("pcre2_ip_range_full", "pcre2", r'src_ip=192\.168\.10[234]', ["-P", r'src_ip=192\.168\.10[234]'], ["-P", r'src_ip=192\.168\.10[234]']),
    ("pcre2_ip_range_head1", "pcre2", r'src_ip=192\.168\.10[234]', ["--head", "1", "-P", r'src_ip=192\.168\.10[234]'], ["-P", r'src_ip=192\.168\.10[234]']),
]


def tool_exists(name: str) -> bool:
    return shutil.which(name) is not None


def time_tool() -> str | None:
    candidate = "/usr/bin/time"
    if Path(candidate).exists():
        return candidate
    return shutil.which("time")


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


def run_measured(cmd: list[str], *, stdout_path: Path | None, tmp: Path, allow_nonzero: bool = False) -> dict[str, object]:
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

    stdout = proc.stdout.decode("utf-8", "replace") if isinstance(proc.stdout, bytes) else str(proc.stdout)
    stderr = proc.stderr.decode("utf-8", "replace") if isinstance(proc.stderr, bytes) else str(proc.stderr)

    if proc.returncode != 0 and not allow_nonzero:
        raise SystemExit(
            "command failed {}: {}\nSTDOUT:\n{}\nSTDERR:\n{}".format(
                proc.returncode,
                " ".join(cmd),
                stdout,
                stderr,
            )
        )

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
    nums = [float(value) for value in values if value != "" and value is not None]
    if not nums:
        return ""
    return f"{median(nums):.6f}"


def median_int(values: list[object]) -> str:
    nums = [int(float(value)) for value in values if value != "" and value is not None]
    if not nums:
        return ""
    return str(int(median(nums)))


def run_repeated(factory, repeats: int, tmp: Path, *, allow_nonzero: bool = False) -> dict[str, object]:
    samples = []
    last = None
    for _ in range(repeats):
        cmd, stdout_path = factory()
        last = run_measured(cmd, stdout_path=stdout_path, tmp=tmp, allow_nonzero=allow_nonzero)
        samples.append(last)

    return {
        "returncode": last["returncode"] if last else 0,
        "wall_seconds": median_float([item["wall_seconds"] for item in samples]),
        "user_seconds": median_float([item["user_seconds"] for item in samples]),
        "system_seconds": median_float([item["system_seconds"] for item in samples]),
        "max_rss_kb": median_int([item["max_rss_kb"] for item in samples]),
        "last_stdout": last["stdout"] if last else "",
        "last_stderr": last["stderr"] if last else "",
    }


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_zlg_components(path: Path) -> dict[str, int]:
    # Reuse the known-correct Phase 0y-fix offsets.
    import struct

    data = path.read_bytes()
    offset = 32
    out = {
        "zlg_total_bytes": len(data),
        "zlg_chunk_count": 0,
        "zlg_chunk_header_bytes": 0,
        "zlg_summary_bytes": 0,
        "zlg_compressed_payload_bytes": 0,
        "zlg_directory_footer_bytes": 0,
    }

    while offset + 4 <= len(data):
        magic = data[offset:offset + 4]
        if magic == b"ZCH1":
            if offset + 64 > len(data):
                raise ValueError(f"truncated zlg chunk header at offset {offset}")
            header_len = struct.unpack_from("<H", data, offset + 4)[0]
            compressed_len = struct.unpack_from("<Q", data, offset + 40)[0]
            summary_len = struct.unpack_from("<I", data, offset + 48)[0]
            record_len = header_len + summary_len + compressed_len
            if offset + record_len > len(data):
                raise ValueError("zlg chunk record exceeds file size")
            out["zlg_chunk_count"] += 1
            out["zlg_chunk_header_bytes"] += header_len
            out["zlg_summary_bytes"] += summary_len
            out["zlg_compressed_payload_bytes"] += compressed_len
            offset += record_len
        elif magic == b"ZDR1":
            entry_len = struct.unpack_from("<I", data, offset + 4)[0]
            count = struct.unpack_from("<Q", data, offset + 8)[0]
            directory_len = 4 + 4 + 8 + entry_len * count
            footer_len = 48
            out["zlg_directory_footer_bytes"] = directory_len + footer_len
            offset += directory_len + footer_len
            break
        else:
            raise ValueError(f"unexpected zlg magic {magic!r} at offset {offset}")

    component_sum = (
        32
        + out["zlg_chunk_header_bytes"]
        + out["zlg_summary_bytes"]
        + out["zlg_compressed_payload_bytes"]
        + out["zlg_directory_footer_bytes"]
    )
    if component_sum != out["zlg_total_bytes"]:
        raise ValueError(f"component sum {component_sum} != total {out['zlg_total_bytes']}")

    return out


def base_row(meta: dict[str, object]) -> dict[str, object]:
    return {
        "corpus_lines": meta["lines"],
        "corpus_bytes": meta["input_bytes"],
        "needle_ip": meta["needle_ip"],
        "needle_line": meta["needle_line"],
        "needle_ratio": f"{float(meta['needle_ratio']):.6f}",
        "tool": "",
        "operation": "",
        "build_profile": "",
        "query_name": "",
        "query_mode": "",
        "pattern": "",
        "stream_decode": "",
        "output_bytes": "",
        "gzip6_bytes": "",
        "size_vs_gzip6_bytes": "",
        "wall_seconds": "",
        "user_seconds": "",
        "system_seconds": "",
        "total_cpu_seconds": "",
        "max_rss_kb": "",
        "zlg_total_bytes": "",
        "zlg_chunk_count": "",
        "zlg_chunk_header_bytes": "",
        "zlg_summary_bytes": "",
        "zlg_compressed_payload_bytes": "",
        "zlg_directory_footer_bytes": "",
        "build_chunks": "",
        "build_summary_ns": "",
        "build_zstd_ns": "",
        "build_write_ns": "",
        "build_total_ns": "",
        "build_summary_bytes": "",
        "build_compressed_bytes": "",
        "build_uncompressed_bytes": "",
        "build_raw_edge_windows": "",
        "build_pushed_edges": "",
        "build_unique_edges": "",
        "build_duplicate_ratio": "",
        "build_bitset_resizes": "",
        "build_bitset_cleared_edges": "",
        "build_touched_first_buckets": "",
        "build_scratch_bytes": "",
        "build_bitset_scratch_bytes": "",
        "build_first_bitset_scratch_bytes": "",
        "build_edge_scratch_capacity_bytes": "",
        "build_sort_scratch_capacity_bytes": "",
        "build_lower_scratch_capacity_bytes": "",
        "build_summary_scratch_capacity_bytes": "",
        "build_group_bucket_scratch_bytes": "",
        "chunks_total": "",
        "chunks_skipped": "",
        "candidate_chunks": "",
        "chunks_decoded": "",
        "decoded_bytes": "",
        "decoded_ratio": "",
        "matching_lines": "",
        "lines_scanned": "",
        "fixed_calls": "",
        "rust_regex_calls": "",
        "pcre2_calls": "",
        "fast_path_calls": "",
        "prefilter_rejects": "",
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


def add_components(row: dict[str, object], components: dict[str, int]) -> None:
    for key, value in components.items():
        row[key] = value


def add_build_stats(row: dict[str, object], stats: dict[str, object]) -> None:
    mapping = {
        "chunks": "build_chunks",
        "summary_ns": "build_summary_ns",
        "zstd_ns": "build_zstd_ns",
        "write_ns": "build_write_ns",
        "total_ns": "build_total_ns",
        "summary_bytes": "build_summary_bytes",
        "compressed_bytes": "build_compressed_bytes",
        "uncompressed_bytes": "build_uncompressed_bytes",
        "raw_edge_windows": "build_raw_edge_windows",
        "pushed_edges": "build_pushed_edges",
        "unique_edges": "build_unique_edges",
        "bitset_resizes": "build_bitset_resizes",
        "bitset_cleared_edges": "build_bitset_cleared_edges",
        "touched_first_buckets": "build_touched_first_buckets",
        "scratch_bytes": "build_scratch_bytes",
        "bitset_scratch_bytes": "build_bitset_scratch_bytes",
        "first_bitset_scratch_bytes": "build_first_bitset_scratch_bytes",
        "edge_scratch_capacity_bytes": "build_edge_scratch_capacity_bytes",
        "sort_scratch_capacity_bytes": "build_sort_scratch_capacity_bytes",
        "lower_scratch_capacity_bytes": "build_lower_scratch_capacity_bytes",
        "summary_scratch_capacity_bytes": "build_summary_scratch_capacity_bytes",
        "group_bucket_scratch_bytes": "build_group_bucket_scratch_bytes",
    }
    for source, target in mapping.items():
        row[target] = stats.get(source, "")
    pushed = int(stats.get("pushed_edges", 0) or 0)
    unique = int(stats.get("unique_edges", 0) or 0)
    if pushed:
        row["build_duplicate_ratio"] = f"{(pushed - unique) / pushed:.6f}"


def add_grep_stats(row: dict[str, object], stats: dict[str, object], corpus_bytes: int) -> None:
    for key in [
        "chunks_total",
        "chunks_skipped",
        "candidate_chunks",
        "chunks_decoded",
        "decoded_bytes",
        "matching_lines",
        "stream_decode",
        "lines_scanned",
        "fixed_calls",
        "rust_regex_calls",
        "pcre2_calls",
        "fast_path_calls",
        "prefilter_rejects",
    ]:
        row[key] = stats.get(key, "")
    decoded = int(stats.get("decoded_bytes", 0))
    row["decoded_ratio"] = f"{decoded / corpus_bytes:.6f}" if corpus_bytes else ""


def probe(args: argparse.Namespace) -> tuple[list[dict[str, object]], dict[str, object]]:
    binary = Path(args.binary)
    if not binary.exists():
        raise SystemExit(f"binary not found: {binary}")

    rows: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="zlg-phase1d-") as tmp_name:
        tmp = Path(tmp_name)
        devnull = Path(os.devnull)
        corpus = tmp / "bench.log"
        needle_line = make_needle_corpus(corpus, args.lines, args.needle_ratio)
        corpus_bytes = corpus.stat().st_size
        meta = {
            "lines": args.lines,
            "input_bytes": corpus_bytes,
            "sha256": sha256(corpus),
            "needle_ip": NEEDLE_IP,
            "needle_line": needle_line,
            "needle_ratio": needle_line / args.lines,
            "gzip_available": tool_exists("gzip"),
            "zgrep_available": tool_exists("zgrep"),
            "grep_available": tool_exists("grep"),
        }

        gzip_path = tmp / "bench.log.gz"
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
                "size_vs_gzip6_bytes": "0",
            })
            add_timing(row, timing)
            rows.append(row)

        zlg_paths: dict[str, Path] = {}
        for profile in BUILD_PROFILES:
            zlg_path = tmp / f"{profile}.zlg"
            stats_path = tmp / f"{profile}-build.json"

            def compress_cmd(profile=profile, zlg_path=zlg_path, stats_path=stats_path):
                if zlg_path.exists():
                    zlg_path.unlink()
                if stats_path.exists():
                    stats_path.unlink()
                return ([
                    str(binary),
                    "compress",
                    str(corpus),
                    "-o",
                    str(zlg_path),
                    "--chunk-policy",
                    "fixed-lines8192",
                    "--summary-mode",
                    "mesh-bigram",
                    "--build-profile",
                    profile,
                    "--build-stats-json",
                    str(stats_path),
                ], None)

            timing = run_repeated(compress_cmd, args.repeats, tmp)
            components = parse_zlg_components(zlg_path)
            build_stats = read_json(stats_path)
            zlg_paths[profile] = zlg_path

            row = base_row(meta)
            row.update({
                "tool": "zlg",
                "operation": "compress",
                "build_profile": profile,
                "output_bytes": zlg_path.stat().st_size,
                "gzip6_bytes": gzip6_bytes,
            })
            if gzip6_bytes:
                row["size_vs_gzip6_bytes"] = str(zlg_path.stat().st_size - int(gzip6_bytes))
            add_timing(row, timing)
            add_components(row, components)
            add_build_stats(row, build_stats)
            rows.append(row)

        if meta["grep_available"]:
            for query_name, query_mode, pattern, _zlg_args, grep_args in QUERIES:
                def grep_cmd(grep_args=grep_args):
                    return (["grep"] + grep_args + [str(corpus)], devnull)
                timing = run_repeated(grep_cmd, args.repeats, tmp, allow_nonzero=True)
                row = base_row(meta)
                row.update({
                    "tool": "grep_original",
                    "operation": "search",
                    "query_name": query_name,
                    "query_mode": query_mode,
                    "pattern": pattern,
                    "gzip6_bytes": gzip6_bytes,
                })
                add_timing(row, timing)
                rows.append(row)

        if meta["zgrep_available"] and gzip_path.exists():
            for query_name, query_mode, pattern, _zlg_args, grep_args in QUERIES:
                def zgrep_cmd(grep_args=grep_args):
                    return (["zgrep"] + grep_args + [str(gzip_path)], devnull)
                timing = run_repeated(zgrep_cmd, args.repeats, tmp, allow_nonzero=True)
                row = base_row(meta)
                row.update({
                    "tool": "zgrep",
                    "operation": "search",
                    "query_name": query_name,
                    "query_mode": query_mode,
                    "pattern": pattern,
                    "gzip6_bytes": gzip6_bytes,
                })
                add_timing(row, timing)
                rows.append(row)

        # Runtime checks only need one file because all build profiles produce
        # the same format. Use combined if available, otherwise current.
        runtime_profile = "combined" if "combined" in zlg_paths else "current"
        runtime_path = zlg_paths[runtime_profile]

        for query_name, query_mode, pattern, zlg_args, _grep_args in QUERIES:
            for stream in [False, True]:
                stats_path = tmp / f"{runtime_profile}-{query_name}-{stream}.json"

                def zlg_grep_cmd(zlg_args=zlg_args, stats_path=stats_path, stream=stream):
                    if stats_path.exists():
                        stats_path.unlink()
                    cmd = [
                        str(binary),
                        "grep",
                        "--stats-json",
                        str(stats_path),
                    ]
                    if stream:
                        cmd.append("--stream-decode")
                    cmd.extend(zlg_args)
                    cmd.append(str(runtime_path))
                    return (cmd, devnull)

                timing = run_repeated(zlg_grep_cmd, args.repeats, tmp, allow_nonzero=True)
                row = base_row(meta)
                row.update({
                    "tool": "zlg",
                    "operation": "search",
                    "build_profile": runtime_profile,
                    "query_name": query_name,
                    "query_mode": query_mode,
                    "pattern": pattern,
                    "stream_decode": "yes" if stream else "no",
                    "output_bytes": runtime_path.stat().st_size,
                    "gzip6_bytes": gzip6_bytes,
                })
                add_timing(row, timing)
                if stats_path.exists():
                    add_grep_stats(row, read_json(stats_path), corpus_bytes)
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


def rows_for(rows: list[dict[str, object]], operation: str) -> list[dict[str, object]]:
    return [row for row in rows if row["operation"] == operation]


def write_markdown(path: Path, rows: list[dict[str, object]], meta: dict[str, object]) -> None:
    doc = [
        "# zlg Phase 1d builder fairness and robustness shootout",
        "",
        "This report compares builder profiles and scratch-memory tradeoffs for the same format:",
        "fixed-lines8192 + mesh-bigram ZBM1 v2.",
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
        "## Compression and build profile",
        "",
        "| tool | profile | bytes | vs_gzip6 | wall_s | cpu_s | total_ns | summary_ns | scratch_bytes | bitset_bytes | first_bitset_bytes | grouped_bucket_bytes | pushed_edges | unique_edges | duplicate_ratio |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows_for(rows, "compress"):
        doc.append(
            f"| {row['tool']} | {row['build_profile']} | {row['output_bytes']} | "
            f"{row['size_vs_gzip6_bytes']} | {row['wall_seconds']} | {row['total_cpu_seconds']} | "
            f"{row['build_total_ns']} | {row['build_summary_ns']} | {row['build_scratch_bytes']} | "
            f"{row['build_bitset_scratch_bytes']} | {row['build_first_bitset_scratch_bytes']} | "
            f"{row['build_group_bucket_scratch_bytes']} | {row['build_pushed_edges']} | "
            f"{row['build_unique_edges']} | {row['build_duplicate_ratio']} |"
        )

    profile_rows = [row for row in rows_for(rows, "compress") if row["tool"] == "zlg"]
    ranked = sorted(
        profile_rows,
        key=lambda row: (
            float(row["wall_seconds"]) if row["wall_seconds"] else 999999.0,
            int(row["build_total_ns"]) if row["build_total_ns"] else 999999999999,
            str(row["build_profile"]),
        ),
    )
    non_bitset = [row for row in ranked if "bitset" not in str(row["build_profile"])]

    doc.extend([
        "",
        "## Build profile ranking",
        "",
        "| rank | profile | wall_s | total_ns | summary_ns | scratch_bytes | bitset_bytes | first_bitset_bytes | grouped_bucket_bytes | pushed_edges | unique_edges | duplicate_ratio | bytes |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for index, row in enumerate(ranked, start=1):
        doc.append(
            f"| {index} | {row['build_profile']} | {row['wall_seconds']} | "
            f"{row['build_total_ns']} | {row['build_summary_ns']} | "
            f"{row['build_scratch_bytes']} | {row['build_bitset_scratch_bytes']} | "
            f"{row['build_first_bitset_scratch_bytes']} | {row['build_group_bucket_scratch_bytes']} | "
            f"{row['build_pushed_edges']} | {row['build_unique_edges']} | "
            f"{row['build_duplicate_ratio']} | {row['output_bytes']} |"
        )

    if non_bitset:
        best_non_bitset = non_bitset[0]
        doc.extend([
            "",
            "## Best non-bitset profile",
            "",
            "| profile | wall_s | total_ns | summary_ns | scratch_bytes | grouped_bucket_bytes | pushed_edges | unique_edges | duplicate_ratio | bytes |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            (
                f"| {best_non_bitset['build_profile']} | {best_non_bitset['wall_seconds']} | "
                f"{best_non_bitset['build_total_ns']} | {best_non_bitset['build_summary_ns']} | "
                f"{best_non_bitset['build_scratch_bytes']} | "
                f"{best_non_bitset['build_group_bucket_scratch_bytes']} | "
                f"{best_non_bitset['build_pushed_edges']} | {best_non_bitset['build_unique_edges']} | "
                f"{best_non_bitset['build_duplicate_ratio']} | {best_non_bitset['output_bytes']} |"
            ),
        ])

    doc.extend([
        "",
        "## Search sanity using combined profile",
        "",
        "| tool | query | stream | wall_s | cpu_s | decoded_ratio | lines | fixed | rust_regex | pcre2 | fast_path | rejects |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in rows_for(rows, "search"):
        doc.append(
            f"| {row['tool']} | {row['query_name']} | {row['stream_decode']} | "
            f"{row['wall_seconds']} | {row['total_cpu_seconds']} | {row['decoded_ratio']} | "
            f"{row['lines_scanned']} | {row['fixed_calls']} | {row['rust_regex_calls']} | "
            f"{row['pcre2_calls']} | {row['fast_path_calls']} | {row['prefilter_rejects']} |"
        )

    doc.extend([
        "",
        "## Interpretation guide",
        "",
        "- `combined` is the Phase 1a/1b winner and remains the control.",
        "- `combined-case-raw` stores exact byte edges only and is a case-sensitive control.",
        "- `combined-lower-only` stores lowercase-normalized edges only and is an experimental permissive skip filter.",
        "- `combined-inline-lower-delta` stores original edges and only adds lowercase edges when they differ.",
        "- `combined-bitset-seen` deduplicates with a reusable 2 MiB u24 presence bitset before sorting.",
        "- `combined-lower-only-bitset-seen` is lower-only and experimental; it is not semantically equivalent for case-sensitive uppercase queries.",
        "- `combined-sparse-first-bitset` uses a sparse first-byte to two-byte-suffix bitset. It is baseline-equivalent and allocates 8 KiB only for first bytes touched during the run.",
        "- `combined-grouped-buckets` uses grouped first-byte arrays: digit, uppercase, lowercase a-z buckets, and ordered spill buckets. It is baseline-equivalent and avoids a full u24 bitset.",
        "- `combined-bucket256` buckets by high byte before sorting and deduping smaller ranges.",
        "- Only `combined`, `combined-inline-lower-delta`, `combined-bitset-seen`, `combined-sparse-first-bitset`, `combined-grouped-buckets`, `combined-bucket256`, and `combined-radix` are intended to preserve baseline search pruning semantics.",
        "- `combined-case-raw`, `combined-lower-only`, and `combined-lower-only-bitset-seen` are controls with narrower semantics.",
        "- This phase does not change the on-disk format.",
    ])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", default="target/release/zlg")
    parser.add_argument("--lines", type=int, default=125000)
    parser.add_argument("--needle-ratio", type=float, default=0.80)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", default="validation_results/phase1c_case_duplicate_bench.md")
    parser.add_argument("--csv", default="validation_results/phase1c_case_duplicate_bench.csv")
    args = parser.parse_args()

    rows, meta = probe(args)
    write_csv(REPO / args.csv, rows)
    write_markdown(REPO / args.output, rows, meta)
    print(f"wrote {REPO / args.output}")
    print(f"wrote {REPO / args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
