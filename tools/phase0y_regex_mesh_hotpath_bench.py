#!/usr/bin/env python3
"""Phase 0y regex hot-path and mesh-overhead benchmark.

This benchmark keeps the current primary candidate fixed: fixed-lines8192 with
mesh-bigram. It compares zlg to gzip/zgrep/original grep and records the new
regex hot-path counters plus coarse zlg storage component accounting.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import resource
import shutil
import struct
import subprocess
import tempfile
import time
from pathlib import Path
from statistics import median

NEEDLE_IP = "198.18.99.123"
RANGE_PATTERN = r"src_ip=192\.168\.10[234]"

QUERIES = [
    ("needle_fixed_ip", "fixed", NEEDLE_IP, ["-F", NEEDLE_IP], ["-F", NEEDLE_IP]),
    ("common_fixed", "fixed", "failed password", ["-F", "failed password"], ["-F", "failed password"]),
    ("rust_regex_key", "rust_regex", r'key="[^"]+"', [r'key="[^"]+"'], ["-E", r'key="[^"]+"']),
    ("pcre2_lookbehind_key", "pcre2", r'(?<=key=")[^"]+', ["-P", r'(?<=key=")[^"]+'], ["-P", r'(?<=key=")[^"]+']),
    ("pcre2_ip_range_full", "pcre2", RANGE_PATTERN, ["-P", RANGE_PATTERN], ["-P", RANGE_PATTERN]),
    ("pcre2_ip_range_head1", "pcre2", RANGE_PATTERN, ["--head", "1", "-P", RANGE_PATTERN], ["-P", RANGE_PATTERN]),
]


def sha256(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_corpus(path: Path, lines: int, needle_ratio: float) -> tuple[int, int]:
    needle_index = max(0, min(lines - 1, int(lines * needle_ratio)))
    range_lines = min(lines - 1, 100_000)
    range_hits = 0
    with path.open("w", encoding="utf-8") as handle:
        for i in range(lines):
            if i == needle_index:
                handle.write(
                    f"warn event_id={i} src_ip={NEEDLE_IP} request_id=NEEDLE-{i:08d} "
                    "user=needle_user key=\"needle-value\" msg=find-the-needle\n"
                )
            elif i < range_lines:
                ip = f"192.168.10{2 + (i % 3)}"
                range_hits += 1
                handle.write(
                    f"info event_id={i} src_ip={ip} user=user{i % 97} "
                    f"key=\"range{i % 1000}\" msg=ip-range-hit component=app\n"
                )
            elif i % 97 == 0:
                handle.write(
                    f"error key=\"abc{i}\" src_ip=192.0.2.{i % 255} "
                    f"foo{i % 10} component=auth\n"
                )
            elif i % 131 == 0:
                handle.write(
                    f"failed password user=test{i} src_ip=198.51.100.{i % 255} component=sshd\n"
                )
            else:
                handle.write(
                    f"info event_id={i} src_ip=203.0.113.{i % 255} msg=normal "
                    f"component=app shard={i % 16}\n"
                )
    return needle_index + 1, range_hits


def tool_exists(name: str) -> bool:
    return shutil.which(name) is not None


def rusage_snapshot() -> resource.struct_rusage:
    return resource.getrusage(resource.RUSAGE_CHILDREN)


def measure(cmd: list[str], stdout_path: Path | None = None, allow_nonzero: bool = False) -> dict[str, object]:
    before = rusage_snapshot()
    start = time.perf_counter()
    if stdout_path is None:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        with stdout_path.open("wb") as out:
            proc = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE)
    elapsed = time.perf_counter() - start
    after = rusage_snapshot()
    if proc.returncode not in (0, 1) and not allow_nonzero:
        raise SystemExit(
            "command failed {}: {}\nSTDOUT:\n{}\nSTDERR:\n{}".format(
                proc.returncode,
                " ".join(cmd),
                proc.stdout.decode("utf-8", "replace") if proc.stdout else "",
                proc.stderr.decode("utf-8", "replace") if proc.stderr else "",
            )
        )
    return {
        "returncode": proc.returncode,
        "wall_seconds": elapsed,
        "user_seconds": max(0.0, after.ru_utime - before.ru_utime),
        "system_seconds": max(0.0, after.ru_stime - before.ru_stime),
        "max_rss_kb": max(0, after.ru_maxrss - before.ru_maxrss),
    }


def measure_shell(command: str, allow_nonzero: bool = True) -> dict[str, object]:
    before = rusage_snapshot()
    start = time.perf_counter()
    proc = subprocess.run(["sh", "-c", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elapsed = time.perf_counter() - start
    after = rusage_snapshot()
    if proc.returncode not in (0, 1, 141) and not allow_nonzero:
        raise SystemExit(f"command failed {proc.returncode}: {command}")
    return {
        "returncode": proc.returncode,
        "wall_seconds": elapsed,
        "user_seconds": max(0.0, after.ru_utime - before.ru_utime),
        "system_seconds": max(0.0, after.ru_stime - before.ru_stime),
        "max_rss_kb": max(0, after.ru_maxrss - before.ru_maxrss),
    }


def repeated(factory, repeats: int, allow_nonzero: bool = False) -> dict[str, object]:
    samples = [factory() for _ in range(repeats)]
    return {
        "returncode": samples[-1]["returncode"],
        "wall_seconds": median([float(s["wall_seconds"]) for s in samples]),
        "user_seconds": median([float(s["user_seconds"]) for s in samples]),
        "system_seconds": median([float(s["system_seconds"]) for s in samples]),
        "max_rss_kb": int(median([int(s["max_rss_kb"]) for s in samples])),
    }


def parse_zlg_components(path: Path) -> dict[str, int]:
    """Parse top-level zlg component sizes for benchmark accounting.

    Layout offsets are relative to the start of each ZCH1 record:
      0  magic [4]
      4  header_len u16
      6  flags u16
      8  chunk_index u64
      16 first_line_number u64
      24 line_count u64
      32 uncompressed_len u64
      40 compressed_len u64
      48 summary_len u32
      52 crc32 u32
      56 reserved u64
    """
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
            if header_len != 64:
                raise ValueError(f"unexpected zlg chunk header length {header_len} at offset {offset}")

            compressed_len = struct.unpack_from("<Q", data, offset + 40)[0]
            summary_len = struct.unpack_from("<I", data, offset + 48)[0]
            record_len = header_len + summary_len + compressed_len
            if record_len <= header_len:
                raise ValueError(f"invalid zlg chunk record length {record_len} at offset {offset}")
            if offset + record_len > len(data):
                raise ValueError(
                    f"zlg chunk record exceeds file size at offset {offset}: "
                    f"record_len={record_len}, total={len(data)}"
                )

            out["zlg_chunk_count"] += 1
            out["zlg_chunk_header_bytes"] += header_len
            out["zlg_summary_bytes"] += summary_len
            out["zlg_compressed_payload_bytes"] += compressed_len
            offset += record_len
        elif magic == b"ZDR1":
            if offset + 16 > len(data):
                raise ValueError(f"truncated zlg directory at offset {offset}")
            entry_len = struct.unpack_from("<I", data, offset + 4)[0]
            count = struct.unpack_from("<Q", data, offset + 8)[0]
            directory_len = 4 + 4 + 8 + entry_len * count
            footer_len = 48
            component_len = directory_len + footer_len
            if offset + component_len > len(data):
                raise ValueError(
                    f"zlg directory/footer exceeds file size at offset {offset}: "
                    f"component_len={component_len}, total={len(data)}"
                )
            out["zlg_directory_footer_bytes"] = component_len
            offset += component_len
            break
        else:
            raise ValueError(f"unexpected zlg record magic {magic!r} at offset {offset}")

    component_sum = (
        out["zlg_chunk_header_bytes"]
        + out["zlg_summary_bytes"]
        + out["zlg_compressed_payload_bytes"]
        + out["zlg_directory_footer_bytes"]
        + 32
    )
    if component_sum != out["zlg_total_bytes"]:
        raise ValueError(
            f"zlg component accounting mismatch: components={component_sum}, "
            f"total={out['zlg_total_bytes']}"
        )
    for key in [
        "zlg_chunk_header_bytes",
        "zlg_summary_bytes",
        "zlg_compressed_payload_bytes",
        "zlg_directory_footer_bytes",
    ]:
        if out[key] > out["zlg_total_bytes"]:
            raise ValueError(f"zlg component {key} exceeds total file size")

    return out


def fmt_float(value: object) -> str:
    return f"{float(value):.6f}"


def add_timing(row: dict[str, object], timing: dict[str, object]) -> None:
    row["returncode"] = timing["returncode"]
    row["wall_seconds"] = fmt_float(timing["wall_seconds"])
    row["user_seconds"] = fmt_float(timing["user_seconds"])
    row["system_seconds"] = fmt_float(timing["system_seconds"])
    row["total_cpu_seconds"] = fmt_float(float(timing["user_seconds"]) + float(timing["system_seconds"]))
    row["max_rss_kb"] = timing["max_rss_kb"]


def base_row(meta: dict[str, object]) -> dict[str, object]:
    return {
        "corpus_lines": meta["lines"],
        "corpus_bytes": meta["input_bytes"],
        "needle_ip": meta["needle_ip"],
        "needle_line": meta["needle_line"],
        "needle_ratio": f"{float(meta['needle_ratio']):.6f}",
        "range_hit_lines": meta["range_hit_lines"],
        "tool": "",
        "operation": "",
        "decode_mode": "",
        "query_name": "",
        "query_mode": "",
        "pattern": "",
        "output_bytes": "",
        "gzip6_bytes": "",
        "size_vs_gzip6_bytes": "",
        "zlg_total_bytes": "",
        "zlg_chunk_count": "",
        "zlg_chunk_header_bytes": "",
        "zlg_summary_bytes": "",
        "zlg_compressed_payload_bytes": "",
        "zlg_directory_footer_bytes": "",
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
        "matching_lines": "",
        "selector_kind": "",
        "selector_len": "",
        "selector_count": "",
        "stream_decode": "",
        "crc_checked_chunks": "",
        "stream_early_stopped_chunks": "",
        "lines_scanned": "",
        "fixed_calls": "",
        "rust_regex_calls": "",
        "pcre2_calls": "",
        "fast_path_calls": "",
        "prefilter_rejects": "",
        "returncode": "",
    }


def add_stats(row: dict[str, object], stats_path: Path, corpus_bytes: int) -> None:
    if not stats_path.exists():
        return
    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    for key in [
        "chunks_total", "chunks_skipped", "candidate_chunks", "chunks_decoded",
        "decoded_bytes", "matching_lines", "selector_kind", "selector_len",
        "selector_count", "stream_decode", "crc_checked_chunks",
        "stream_early_stopped_chunks", "lines_scanned", "fixed_calls",
        "rust_regex_calls", "pcre2_calls", "fast_path_calls", "prefilter_rejects",
    ]:
        row[key] = stats.get(key, "")
    decoded = int(stats.get("decoded_bytes", 0))
    row["decoded_ratio"] = f"{decoded / corpus_bytes:.6f}" if corpus_bytes else ""


def probe(args: argparse.Namespace) -> tuple[list[dict[str, object]], dict[str, object]]:
    binary = Path(args.binary)
    if not binary.exists():
        raise SystemExit(f"binary not found: {binary}")

    rows: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="zlg-phase0y-") as tmp_name:
        tmp = Path(tmp_name)
        corpus = tmp / "bench.log"
        needle_line, range_hits = make_corpus(corpus, args.lines, args.needle_ratio)
        corpus_bytes = corpus.stat().st_size
        meta = {
            "lines": args.lines,
            "input_bytes": corpus_bytes,
            "sha256": sha256(corpus),
            "needle_ip": NEEDLE_IP,
            "needle_line": needle_line,
            "needle_ratio": needle_line / args.lines,
            "range_hit_lines": range_hits,
        }
        devnull = Path(os.devnull)

        gzip_path = tmp / "bench.log.gz"
        gzip6_bytes = ""
        if tool_exists("gzip"):
            def gzip_cmd():
                return measure(["gzip", "-6", "-c", str(corpus)], gzip_path)
            timing = repeated(gzip_cmd, args.repeats)
            gzip6_bytes = str(gzip_path.stat().st_size)
            row = base_row(meta)
            row.update({"tool": "gzip", "operation": "compress", "output_bytes": gzip6_bytes, "gzip6_bytes": gzip6_bytes, "size_vs_gzip6_bytes": "0"})
            add_timing(row, timing)
            rows.append(row)

            timing = repeated(lambda: measure(["gzip", "-dc", str(gzip_path)], devnull), args.repeats)
            row = base_row(meta)
            row.update({"tool": "gzip", "operation": "decompress", "gzip6_bytes": gzip6_bytes})
            add_timing(row, timing)
            rows.append(row)

        zlg_path = tmp / "bench.zlg"
        timing = repeated(lambda: measure([
            str(binary), "compress", str(corpus), "-o", str(zlg_path),
            "--chunk-policy", "fixed-lines8192", "--summary-mode", "mesh-bigram",
        ], None), args.repeats)
        components = parse_zlg_components(zlg_path)
        row = base_row(meta)
        row.update({"tool": "zlg", "operation": "compress", "output_bytes": zlg_path.stat().st_size, "gzip6_bytes": gzip6_bytes})
        if gzip6_bytes:
            row["size_vs_gzip6_bytes"] = str(zlg_path.stat().st_size - int(gzip6_bytes))
        row.update(components)
        add_timing(row, timing)
        rows.append(row)

        timing = repeated(lambda: measure([str(binary), "cat", str(zlg_path)], devnull), args.repeats)
        row = base_row(meta)
        row.update({"tool": "zlg", "operation": "decompress", "output_bytes": zlg_path.stat().st_size, "gzip6_bytes": gzip6_bytes})
        row.update(components)
        add_timing(row, timing)
        rows.append(row)

        for query_name, query_mode, pattern, zlg_args, grep_args in QUERIES:
            if tool_exists("grep"):
                if query_name.endswith("head1"):
                    command = "grep {} {} | head -n1 > /dev/null".format(" ".join(grep_args), corpus)
                    timing = repeated(lambda command=command: measure_shell(command), args.repeats, allow_nonzero=True)
                else:
                    timing = repeated(lambda grep_args=grep_args: measure(["grep"] + grep_args + [str(corpus)], devnull, allow_nonzero=True), args.repeats, allow_nonzero=True)
                row = base_row(meta)
                row.update({"tool": "grep_original", "operation": "search", "query_name": query_name, "query_mode": query_mode, "pattern": pattern})
                add_timing(row, timing)
                rows.append(row)

            if gzip_path.exists() and tool_exists("zgrep"):
                if query_name.endswith("head1"):
                    command = "zgrep {} {} | head -n1 > /dev/null".format(" ".join(grep_args), gzip_path)
                    timing = repeated(lambda command=command: measure_shell(command), args.repeats, allow_nonzero=True)
                else:
                    timing = repeated(lambda grep_args=grep_args: measure(["zgrep"] + grep_args + [str(gzip_path)], devnull, allow_nonzero=True), args.repeats, allow_nonzero=True)
                row = base_row(meta)
                row.update({"tool": "zgrep", "operation": "search", "query_name": query_name, "query_mode": query_mode, "pattern": pattern, "gzip6_bytes": gzip6_bytes})
                add_timing(row, timing)
                rows.append(row)

            for decode_mode, extra_args in [("full", []), ("stream", ["--stream-decode"] )]:
                stats_path = tmp / f"{query_name}-{decode_mode}.json"
                cmd = [str(binary), "grep", "--stats-json", str(stats_path)] + extra_args + zlg_args + [str(zlg_path)]
                timing = repeated(lambda cmd=cmd: measure(cmd, devnull, allow_nonzero=True), args.repeats, allow_nonzero=True)
                row = base_row(meta)
                row.update({
                    "tool": "zlg", "operation": "search", "decode_mode": decode_mode,
                    "query_name": query_name, "query_mode": query_mode, "pattern": pattern,
                    "output_bytes": zlg_path.stat().st_size, "gzip6_bytes": gzip6_bytes,
                })
                row.update(components)
                add_timing(row, timing)
                add_stats(row, stats_path, corpus_bytes)
                rows.append(row)

    return rows, meta


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = list(base_row({"lines": "", "input_bytes": "", "needle_ip": "", "needle_line": "", "needle_ratio": 0.0, "range_hit_lines": ""}).keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, object]], meta: dict[str, object]) -> None:
    doc = [
        "# zlg Phase 0y regex hot-path and mesh-overhead benchmark",
        "",
        "## Corpus",
        "",
        f"- Lines: {meta['lines']}",
        f"- Input bytes: {meta['input_bytes']}",
        f"- Input sha256: {meta['sha256']}",
        f"- Needle IP: {meta['needle_ip']}",
        f"- Needle line: {meta['needle_line']}",
        f"- Range-hit lines: {meta['range_hit_lines']}",
        "",
        "## Storage components",
        "",
        "| tool | operation | bytes | payload | summary | chunk_headers | directory_footer | wall_s | cpu_s |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        if row["operation"] in ("compress", "decompress"):
            doc.append(
                f"| {row['tool']} | {row['operation']} | {row['output_bytes']} | "
                f"{row['zlg_compressed_payload_bytes']} | {row['zlg_summary_bytes']} | "
                f"{row['zlg_chunk_header_bytes']} | {row['zlg_directory_footer_bytes']} | "
                f"{row['wall_seconds']} | {row['total_cpu_seconds']} |"
            )
    doc.extend([
        "",
        "## Search hot-path counters",
        "",
        "| tool | mode | query | wall_s | cpu_s | decoded_ratio | matches | lines | fixed | rust_regex | pcre2 | fast_path | prefilter_rejects |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in rows:
        if row["operation"] == "search":
            mode = row["decode_mode"] or row["tool"]
            doc.append(
                f"| {row['tool']} | {mode} | {row['query_name']} | {row['wall_seconds']} | "
                f"{row['total_cpu_seconds']} | {row['decoded_ratio']} | {row['matching_lines']} | "
                f"{row['lines_scanned']} | {row['fixed_calls']} | {row['rust_regex_calls']} | "
                f"{row['pcre2_calls']} | {row['fast_path_calls']} | {row['prefilter_rejects']} |"
            )
    doc.extend([
        "",
        "## Interpretation guide",
        "",
        "- `pcre2_calls` should drop when the literal prefilter or lookbehind fast path is effective.",
        "- `fast_path_calls` is used for simple positive-lookbehind extraction such as `(?<=key=\")[^\"]+`.",
        "- `prefilter_rejects` shows how many lines were rejected before invoking Rust regex or PCRE2.",
        "- Storage components split the zlg total into compressed payload, mesh summary, chunk headers, and directory/footer bytes.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", default="target/release/zlg")
    parser.add_argument("--lines", type=int, default=125000)
    parser.add_argument("--needle-ratio", type=float, default=0.80)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", default="validation_results/phase0y_regex_mesh_hotpath_bench.md")
    parser.add_argument("--csv", default="validation_results/phase0y_regex_mesh_hotpath_bench.csv")
    args = parser.parse_args()
    rows, meta = probe(args)
    write_csv(Path(args.csv), rows)
    write_markdown(Path(args.output), rows, meta)
    print(f"wrote {args.output}")
    print(f"wrote {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
