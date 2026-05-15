#!/usr/bin/env python3
"""Phase 0x 8192 mesh-bigram PCRE2 and early-stop benchmark."""

from __future__ import annotations

import argparse
import csv
import json
import os
import resource
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from statistics import median

NEEDLE_IP = "198.18.99.123"
RANGE_PATTERN = r"src_ip=192\.168\.10[234]"
RANGE_PLAIN = "src_ip=192.168.102"


def sha256(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_corpus(path: Path, lines: int, needle_ratio: float) -> int:
    needle_index = max(0, min(lines - 1, int(lines * needle_ratio)))
    range_lines = min(lines - 1, 100_000)
    with path.open("w", encoding="utf-8") as handle:
        for i in range(lines):
            if i == needle_index:
                handle.write(
                    f"warn event_id={i} src_ip={NEEDLE_IP} request_id=NEEDLE-{i:08d} "
                    "user=needle_user key=\"needle-value\" msg=find-the-needle\n"
                )
            elif i < range_lines:
                ip = f"192.168.10{2 + (i % 3)}"
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
                    f"info event_id={i} src_ip=203.0.113.{i % 255} msg=normal component=app shard={i % 16}\n"
                )
    return needle_index + 1


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
    samples = []
    for _ in range(repeats):
        samples.append(factory())
    return {
        "returncode": samples[-1]["returncode"],
        "wall_seconds": median(float(item["wall_seconds"]) for item in samples),
        "user_seconds": median(float(item["user_seconds"]) for item in samples),
        "system_seconds": median(float(item["system_seconds"]) for item in samples),
        "max_rss_kb": int(median(int(item["max_rss_kb"]) for item in samples)),
    }


def add_timing(row: dict[str, object], result: dict[str, object]) -> None:
    row["wall_seconds"] = f"{float(result['wall_seconds']):.6f}"
    row["user_seconds"] = f"{float(result['user_seconds']):.6f}"
    row["system_seconds"] = f"{float(result['system_seconds']):.6f}"
    row["total_cpu_seconds"] = f"{float(result['user_seconds']) + float(result['system_seconds']):.6f}"
    row["max_rss_kb"] = str(result["max_rss_kb"])
    row["returncode"] = result["returncode"]


def read_stats(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def base(meta: dict[str, object]) -> dict[str, object]:
    return {
        "corpus_lines": meta["lines"],
        "corpus_bytes": meta["input_bytes"],
        "needle_ip": meta["needle_ip"],
        "needle_line": meta["needle_line"],
        "needle_ratio": f"{meta['needle_ratio']:.6f}",
        "range_hit_lines": meta["range_hit_lines"],
        "tool": "",
        "operation": "",
        "policy": "",
        "summary_mode": "",
        "query_name": "",
        "pattern": "",
        "head_limit": "",
        "decode_mode": "",
        "output_bytes": "",
        "gzip6_bytes": "",
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
        "matching_lines": "",
        "selector_kind": "",
        "selector_len": "",
        "selector_count": "",
        "stream_decode": "",
        "crc_checked_chunks": "",
        "stream_early_stopped_chunks": "",
        "returncode": "",
        "available": "yes",
        "notes": "",
    }


def add_stats(row: dict[str, object], stats: dict[str, object], corpus_bytes: int) -> None:
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
        "stream_decode",
        "crc_checked_chunks",
        "stream_early_stopped_chunks",
    ]:
        row[key] = stats.get(key, "")
    decoded = int(stats.get("decoded_bytes", 0))
    row["decoded_ratio"] = f"{decoded / corpus_bytes:.6f}" if corpus_bytes else ""


def run(args: argparse.Namespace) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    binary = Path(args.binary)
    with tempfile.TemporaryDirectory(prefix="zlg-phase0x-") as tmp_name:
        tmp = Path(tmp_name)
        devnull = Path(os.devnull)
        corpus = tmp / "corpus.log"
        needle_line = make_corpus(corpus, args.lines, args.needle_ratio)
        corpus_bytes = corpus.stat().st_size
        meta = {
            "lines": args.lines,
            "input_bytes": corpus_bytes,
            "sha256": sha256(corpus),
            "needle_ip": NEEDLE_IP,
            "needle_line": needle_line,
            "needle_ratio": needle_line / args.lines,
            "range_hit_lines": min(args.lines - 1, 100_000),
        }

        gzip_path = tmp / "corpus.log.gz"
        gzip_bytes = ""
        if tool_exists("gzip"):
            def gzip_compress():
                if gzip_path.exists():
                    gzip_path.unlink()
                return measure(["gzip", "-6", "-c", str(corpus)], stdout_path=gzip_path)
            timing = repeated(gzip_compress, args.repeats)
            gzip_bytes = str(gzip_path.stat().st_size)
            row = base(meta)
            row.update({"tool": "gzip", "operation": "compress", "output_bytes": gzip_bytes, "gzip6_bytes": gzip_bytes, "size_vs_gzip6_bytes": "0"})
            add_timing(row, timing)
            rows.append(row)

            timing = repeated(lambda: measure(["gzip", "-dc", str(gzip_path)], stdout_path=devnull), args.repeats)
            row = base(meta)
            row.update({"tool": "gzip", "operation": "decompress", "gzip6_bytes": gzip_bytes})
            add_timing(row, timing)
            rows.append(row)

        zlg_path = tmp / "corpus.8192.mesh.zlg"
        def zlg_compress():
            if zlg_path.exists():
                zlg_path.unlink()
            return measure([
                str(binary), "compress", str(corpus), "-o", str(zlg_path),
                "--chunk-policy", "fixed-lines8192", "--summary-mode", "mesh-bigram",
            ])
        timing = repeated(zlg_compress, args.repeats)
        zlg_bytes = zlg_path.stat().st_size
        row = base(meta)
        row.update({
            "tool": "zlg",
            "operation": "compress",
            "policy": "fixed-lines8192",
            "summary_mode": "mesh-bigram",
            "output_bytes": zlg_bytes,
            "gzip6_bytes": gzip_bytes,
            "size_vs_gzip6_bytes": str(zlg_bytes - int(gzip_bytes)) if gzip_bytes else "",
        })
        add_timing(row, timing)
        rows.append(row)

        timing = repeated(lambda: measure([str(binary), "cat", str(zlg_path)], stdout_path=devnull), args.repeats)
        row = base(meta)
        row.update({"tool": "zlg", "operation": "decompress", "policy": "fixed-lines8192", "summary_mode": "mesh-bigram", "output_bytes": zlg_bytes, "gzip6_bytes": gzip_bytes})
        add_timing(row, timing)
        rows.append(row)

        search_cases = [
            ("needle_fixed_ip", NEEDLE_IP, ["-F", NEEDLE_IP], ["-F", NEEDLE_IP], None),
            ("common_fixed_failed_password", "failed password", ["-F", "failed password"], ["-F", "failed password"], None),
            ("rust_regex_key_value", r'key="[^"]+"', [r'key="[^"]+"'], ["-E", r'key="[^"]+"'], None),
            ("pcre2_lookbehind_key", r'(?<=key=")[^"]+', ["-P", r'(?<=key=")[^"]+'], ["-P", r'(?<=key=")[^"]+'], None),
            ("pcre2_ip_range_full", RANGE_PATTERN, ["-P", RANGE_PATTERN], ["-P", RANGE_PATTERN], None),
            ("pcre2_ip_range_head1", RANGE_PATTERN, ["--head", "1", "-P", RANGE_PATTERN], ["-P", RANGE_PATTERN], 1),
        ]

        for name, pattern, zlg_args, grep_args, head_limit in search_cases:
            if tool_exists("grep"):
                if head_limit:
                    cmd = "grep {} {} | head -n {} >/dev/null".format(" ".join(shell_quote(x) for x in grep_args), shell_quote(str(corpus)), head_limit)
                    timing = repeated(lambda cmd=cmd: measure_shell(cmd), args.repeats, allow_nonzero=True)
                else:
                    timing = repeated(lambda grep_args=grep_args: measure(["grep"] + grep_args + [str(corpus)], stdout_path=devnull, allow_nonzero=True), args.repeats, allow_nonzero=True)
                row = base(meta)
                row.update({"tool": "grep_original", "operation": "search", "query_name": name, "pattern": pattern, "head_limit": head_limit or "", "gzip6_bytes": gzip_bytes})
                add_timing(row, timing)
                rows.append(row)

            if gzip_path.exists() and tool_exists("zgrep"):
                if head_limit:
                    cmd = "zgrep {} {} | head -n {} >/dev/null".format(" ".join(shell_quote(x) for x in grep_args), shell_quote(str(gzip_path)), head_limit)
                    timing = repeated(lambda cmd=cmd: measure_shell(cmd), args.repeats, allow_nonzero=True)
                else:
                    timing = repeated(lambda grep_args=grep_args: measure(["zgrep"] + grep_args + [str(gzip_path)], stdout_path=devnull, allow_nonzero=True), args.repeats, allow_nonzero=True)
                row = base(meta)
                row.update({"tool": "zgrep", "operation": "search", "query_name": name, "pattern": pattern, "head_limit": head_limit or "", "gzip6_bytes": gzip_bytes})
                add_timing(row, timing)
                rows.append(row)

            for decode_mode, extra_args in [("full", []), ("stream", ["--stream-decode"])]:
                stats = tmp / f"{name}-{decode_mode}.json"
                def zlg_search(zlg_args=zlg_args, stats=stats, extra_args=extra_args):
                    if stats.exists():
                        stats.unlink()
                    return measure(
                        [str(binary), "grep", "--stats-json", str(stats)]
                        + extra_args
                        + zlg_args
                        + [str(zlg_path)],
                        stdout_path=devnull,
                        allow_nonzero=True,
                    )
                timing = repeated(zlg_search, args.repeats, allow_nonzero=True)
                row = base(meta)
                row.update({
                    "tool": "zlg",
                    "operation": "search",
                    "policy": "fixed-lines8192",
                    "summary_mode": "mesh-bigram",
                    "query_name": name,
                    "pattern": pattern,
                    "head_limit": head_limit or "",
                    "decode_mode": decode_mode,
                    "output_bytes": zlg_bytes,
                    "gzip6_bytes": gzip_bytes,
                })
                add_timing(row, timing)
                if stats.exists():
                    add_stats(row, read_stats(stats), corpus_bytes)
                rows.append(row)

    return rows, meta


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = list(base({"lines": "", "input_bytes": "", "needle_ip": "", "needle_line": "", "needle_ratio": 0.0, "range_hit_lines": ""}).keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, rows: list[dict[str, object]], meta: dict[str, object]) -> None:
    doc = [
        "# zlg Phase 0x 8192 PCRE2 and early-stop benchmark",
        "",
        f"- Lines: {meta['lines']}",
        f"- Input bytes: {meta['input_bytes']}",
        f"- Input sha256: {meta['sha256']}",
        f"- Needle IP: {meta['needle_ip']}",
        f"- Needle line: {meta['needle_line']}",
        f"- Range hit lines: {meta['range_hit_lines']}",
        "",
        "## Compression and decompression",
        "",
        "| tool | operation | policy | bytes | vs_gzip6 | wall_s | cpu_s | max_rss_kb |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        if row["operation"] in ("compress", "decompress"):
            doc.append(f"| {row['tool']} | {row['operation']} | {row['policy']} | {row['output_bytes']} | {row['size_vs_gzip6_bytes']} | {row['wall_seconds']} | {row['total_cpu_seconds']} | {row['max_rss_kb']} |")
    doc.extend([
        "",
        "## Search",
        "",
        "| tool | query | head | wall_s | cpu_s | max_rss_kb | decoded_ratio | decoded_chunks | total_chunks | matches | rc |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in rows:
        if row["operation"] == "search":
            doc.append(f"| {row['tool']} | {row['query_name']} | {row['head_limit']} | {row['decode_mode']} | {row['wall_seconds']} | {row['total_cpu_seconds']} | {row['max_rss_kb']} | {row['decoded_ratio']} | {row['chunks_decoded']} | {row['chunks_total']} | {row['crc_checked_chunks']} | {row['stream_early_stopped_chunks']} | {row['matching_lines']} | {row['returncode']} |")
    doc.extend([
        "",
        "## Notes",
        "",
        "- `-P` uses the pcre2 crate in this phase.",
        "- `--head 1` is a synchronous early-stop path that stops scanning after the first emitted match.",
        "- Full mode decodes a selected chunk into memory before line scanning.",
        "- Stream mode uses zstd streaming decode and scans lines without materializing the whole uncompressed chunk.",
        "- In stream mode, early stop may leave CRC unchecked for the partially decoded chunk; stats expose this.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", default="target/release/zlg")
    parser.add_argument("--lines", type=int, default=125000)
    parser.add_argument("--needle-ratio", type=float, default=0.80)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", default="validation_results/phase0x_8192_pcre2_early_bench.md")
    parser.add_argument("--csv", default="validation_results/phase0x_8192_pcre2_early_bench.csv")
    args = parser.parse_args()
    rows, meta = run(args)
    write_csv(Path(args.csv), rows)
    write_md(Path(args.output), rows, meta)
    print(f"wrote {args.output}")
    print(f"wrote {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
