#!/usr/bin/env python3
"""Phase 1m production cleanup and same-run A/B benchmark.

This harness builds the cleaned final stack from the current checkout and a
Phase 1k source snapshot in a temporary directory, then compares them in the
same run. It alternates command order and attempts to reduce OS cache skew by
using drop_caches when available, otherwise by reading a cache-buster file
before each measured command.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from statistics import median

SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parents[0]
sys.path.insert(0, str(SCRIPT_DIR))
import phase1g_size_overhead_bench as base  # noqa: E402

CORPUS_DEFAULT = (
    "high_dup,high_cardinality,unicode,binaryish,"
    "realistic_mixed_log,long_line_log,short_line_log"
)

COMPRESSION_FIELDS = [
    "corpus",
    "seed",
    "corpus_bytes",
    "corpus_sha256",
    "operation",
    "variant",
    "repeat",
    "order_index",
    "cache_control",
    "wall_seconds",
    "user_seconds",
    "system_seconds",
    "total_cpu_seconds",
    "max_rss_kb",
    "returncode",
    "output_bytes",
    "roundtrip_ok",
    "build_profile",
    "build_chunks",
    "build_summary_ns",
    "build_zstd_ns",
    "build_write_ns",
    "build_total_ns",
    "build_summary_bytes",
    "build_compressed_bytes",
    "build_uncompressed_bytes",
    "build_scratch_bytes",
    "build_bitset_scratch_bytes",
    "build_edge_scratch_capacity_bytes",
    "build_max_chunk_uncompressed_bytes",
    "build_max_chunk_compressed_bytes",
    "build_max_chunk_summary_bytes",
]

SEARCH_FIELDS = [
    "corpus",
    "seed",
    "operation",
    "query_name",
    "variant",
    "repeat",
    "order_index",
    "cache_control",
    "wall_seconds",
    "user_seconds",
    "system_seconds",
    "total_cpu_seconds",
    "max_rss_kb",
    "returncode",
    "stdout_sha256",
    "stdout_bytes",
    "stats_chunks_total",
    "stats_chunks_skipped",
    "stats_candidate_chunks",
    "stats_chunks_decoded",
    "stats_decoded_bytes",
    "stats_matching_lines",
    "stats_stream_decode",
    "stats_crc_checked_chunks",
    "stats_stream_early_stopped_chunks",
]

SUMMARY_FIELDS = [
    "operation",
    "corpus",
    "query_name",
    "variant",
    "median_wall_seconds",
    "median_total_cpu_seconds",
    "median_max_rss_kb",
    "median_output_bytes",
    "runs",
]

SEARCH_QUERIES = [
    ("selective_fixed", ["--stream-decode", "-F", "src_ip=192.168.102.55"]),
    ("common_fixed", ["--stream-decode", "-F", "failed password"]),
    ("rust_regex_key", ["--stream-decode", r'key="[^"]+"']),
    ("pcre2_lookbehind_key", ["--stream-decode", "-P", r'(?<=key=")[^"]+']),
    ("head1_fixed", ["--stream-decode", "-F", "src_ip=192.168.102.55", "--head", "1"]),
]


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_baseline_binary(tmp: Path) -> Path:
    baseline_dir = tmp / "phase1k-baseline-src"
    ignore = shutil.ignore_patterns(
        "target",
        ".git",
        "validation_results/phase1m_*",
        "*.zlg",
        "*.gz",
        "*.zst",
    )
    shutil.copytree(REPO, baseline_dir, ignore=ignore)
    snapshot = REPO / "tools" / "phase1m_baseline_src" / "src"
    if not snapshot.exists():
        raise RuntimeError(f"missing baseline source snapshot: {snapshot}")
    for src_file in snapshot.glob("*.rs"):
        shutil.copy2(src_file, baseline_dir / "src" / src_file.name)

    target_dir = tmp / "phase1k-target"
    env = os.environ.copy()
    env["CARGO_TARGET_DIR"] = str(target_dir)
    subprocess.run(["cargo", "build", "--release"], cwd=baseline_dir, env=env, check=True)
    return target_dir / "release" / "zlg"


def build_final_binary(tmp: Path) -> Path:
    target_dir = tmp / "phase1m-target"
    env = os.environ.copy()
    env["CARGO_TARGET_DIR"] = str(target_dir)
    subprocess.run(["cargo", "build", "--release"], cwd=REPO, env=env, check=True)
    return target_dir / "release" / "zlg"


def make_cache_buster(path: Path, mib: int) -> None:
    if mib <= 0:
        return
    block = bytes((idx * 131 + 17) & 0xff for idx in range(1024 * 1024))
    with path.open("wb") as handle:
        for _ in range(mib):
            handle.write(block)


def control_cache(cache_buster: Path | None) -> str:
    drop = Path("/proc/sys/vm/drop_caches")
    if os.name == "posix" and hasattr(os, "geteuid") and os.geteuid() == 0 and drop.exists():
        try:
            subprocess.run(["sync"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            drop.write_text("3\n", encoding="ascii")
            return "drop_caches"
        except OSError:
            pass
    if cache_buster is not None and cache_buster.exists():
        with cache_buster.open("rb") as handle:
            while handle.read(8 * 1024 * 1024):
                pass
        return f"cache_buster_{cache_buster.stat().st_size // (1024 * 1024)}m"
    return "none"


def measured(cmd: list[str], tmp: Path, cache_buster: Path | None, *, stdout_path: Path | None = None, allow_nonzero: bool = False) -> tuple[dict[str, object], str]:
    cache_method = control_cache(cache_buster)
    timing = base.run_measured(cmd, stdout_path=stdout_path, tmp=tmp, allow_nonzero=allow_nonzero)
    return timing, cache_method


def add_build_stats(row: dict[str, object], stats_path: Path) -> None:
    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    mapping = {
        "build_profile": "build_profile",
        "chunks": "build_chunks",
        "summary_ns": "build_summary_ns",
        "zstd_ns": "build_zstd_ns",
        "write_ns": "build_write_ns",
        "total_ns": "build_total_ns",
        "summary_bytes": "build_summary_bytes",
        "compressed_bytes": "build_compressed_bytes",
        "uncompressed_bytes": "build_uncompressed_bytes",
        "scratch_bytes": "build_scratch_bytes",
        "bitset_scratch_bytes": "build_bitset_scratch_bytes",
        "edge_scratch_capacity_bytes": "build_edge_scratch_capacity_bytes",
        "max_chunk_uncompressed_bytes": "build_max_chunk_uncompressed_bytes",
        "max_chunk_compressed_bytes": "build_max_chunk_compressed_bytes",
        "max_chunk_summary_bytes": "build_max_chunk_summary_bytes",
    }
    for src, dst in mapping.items():
        row[dst] = stats.get(src, "")


def compress_cmd(variant: str, binary: Path, source: Path, archive: Path, stats: Path) -> list[str]:
    if variant == "baseline_phase1k":
        return [
            str(binary),
            "compress",
            "--chunk-policy",
            "fixed-lines8192-cap8m",
            "--summary-mode",
            "mesh-bigram",
            "--build-profile",
            "combined-bitset-seen",
            "--level",
            "6",
            "--build-stats-json",
            str(stats),
            "-o",
            str(archive),
            str(source),
        ]
    return [
        str(binary),
        "compress",
        "--preset",
        "standard",
        "--build-stats-json",
        str(stats),
        "-o",
        str(archive),
        str(source),
    ]


def check_roundtrip(binary: Path, archive: Path, source: Path, tmp: Path, cache_buster: Path | None) -> bool:
    decoded = tmp / f"decoded-{archive.stem}.bin"
    timing, _ = measured([str(binary), "cat", str(archive), "-o", str(decoded)], tmp, cache_buster)
    return timing["returncode"] == 0 and decoded.exists() and sha256_path(decoded) == sha256_path(source)


def compression_rows(corpus: str, seed: int, source: Path, final_bin: Path, baseline_bin: Path, repeats: int, tmp: Path, cache_buster: Path | None) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    meta = {
        "corpus": corpus,
        "seed": seed,
        "corpus_bytes": source.stat().st_size,
        "corpus_sha256": sha256_path(source),
        "operation": "compress",
    }
    binaries = {
        "baseline_phase1k": baseline_bin,
        "final_phase1m": final_bin,
    }
    for repeat in range(repeats):
        order = ["baseline_phase1k", "final_phase1m"] if repeat % 2 == 0 else ["final_phase1m", "baseline_phase1k"]
        for order_index, variant in enumerate(order):
            archive = tmp / f"{corpus}-{variant}-r{repeat}.zlg"
            stats_path = tmp / f"{corpus}-{variant}-r{repeat}.json"
            timing, cache_method = measured(
                compress_cmd(variant, binaries[variant], source, archive, stats_path),
                tmp,
                cache_buster,
            )
            row = {field: "" for field in COMPRESSION_FIELDS}
            row.update(meta)
            row.update({
                "variant": variant,
                "repeat": repeat,
                "order_index": order_index,
                "cache_control": cache_method,
                "wall_seconds": f"{float(timing['wall_seconds']):.6f}",
                "user_seconds": timing["user_seconds"],
                "system_seconds": timing["system_seconds"],
                "total_cpu_seconds": timing["total_cpu_seconds"],
                "max_rss_kb": timing["max_rss_kb"],
                "returncode": timing["returncode"],
                "output_bytes": archive.stat().st_size if archive.exists() else "",
                "roundtrip_ok": check_roundtrip(binaries[variant], archive, source, tmp, cache_buster),
            })
            if stats_path.exists():
                add_build_stats(row, stats_path)
            rows.append(row)
    return rows


def make_reference_archive(corpus: str, source: Path, final_bin: Path, tmp: Path, cache_buster: Path | None) -> Path:
    archive = tmp / f"{corpus}-search-reference.zlg"
    stats = tmp / f"{corpus}-search-reference.json"
    measured(compress_cmd("final_phase1m", final_bin, source, archive, stats), tmp, cache_buster)
    return archive


def load_stats(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def search_rows(corpus: str, seed: int, archive: Path, final_bin: Path, baseline_bin: Path, repeats: int, tmp: Path, cache_buster: Path | None) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    binaries = {
        "baseline_phase1k": baseline_bin,
        "final_phase1m": final_bin,
    }
    for query_name, query_args in SEARCH_QUERIES:
        stdout_by_variant: dict[str, str] = {}
        for repeat in range(repeats):
            order = ["baseline_phase1k", "final_phase1m"] if repeat % 2 == 0 else ["final_phase1m", "baseline_phase1k"]
            for order_index, variant in enumerate(order):
                stdout = tmp / f"search-{corpus}-{query_name}-{variant}-r{repeat}.out"
                stats_path = tmp / f"search-{corpus}-{query_name}-{variant}-r{repeat}.json"
                cmd = [str(binaries[variant]), "grep"] + query_args + ["--stats-json", str(stats_path), str(archive)]
                timing, cache_method = measured(cmd, tmp, cache_buster, stdout_path=stdout, allow_nonzero=True)
                if timing["returncode"] not in (0, 1):
                    raise RuntimeError(f"grep command failed unexpectedly: {cmd}")
                stdout_hash = sha256_path(stdout) if stdout.exists() else ""
                if variant in stdout_by_variant and stdout_by_variant[variant] != stdout_hash:
                    raise RuntimeError(f"unstable stdout for {corpus} {query_name} {variant}")
                stdout_by_variant[variant] = stdout_hash
                if len(stdout_by_variant) == 2 and len(set(stdout_by_variant.values())) != 1:
                    raise RuntimeError(f"search output mismatch for {corpus} {query_name}: {stdout_by_variant}")
                stats = load_stats(stats_path)
                row = {field: "" for field in SEARCH_FIELDS}
                row.update({
                    "corpus": corpus,
                    "seed": seed,
                    "operation": "search",
                    "query_name": query_name,
                    "variant": variant,
                    "repeat": repeat,
                    "order_index": order_index,
                    "cache_control": cache_method,
                    "wall_seconds": f"{float(timing['wall_seconds']):.6f}",
                    "user_seconds": timing["user_seconds"],
                    "system_seconds": timing["system_seconds"],
                    "total_cpu_seconds": timing["total_cpu_seconds"],
                    "max_rss_kb": timing["max_rss_kb"],
                    "returncode": timing["returncode"],
                    "stdout_sha256": stdout_hash,
                    "stdout_bytes": stdout.stat().st_size if stdout.exists() else 0,
                    "stats_chunks_total": stats.get("chunks_total", ""),
                    "stats_chunks_skipped": stats.get("chunks_skipped", ""),
                    "stats_candidate_chunks": stats.get("candidate_chunks", ""),
                    "stats_chunks_decoded": stats.get("chunks_decoded", ""),
                    "stats_decoded_bytes": stats.get("decoded_bytes", ""),
                    "stats_matching_lines": stats.get("matching_lines", ""),
                    "stats_stream_decode": stats.get("stream_decode", ""),
                    "stats_crc_checked_chunks": stats.get("crc_checked_chunks", ""),
                    "stats_stream_early_stopped_chunks": stats.get("stream_early_stopped_chunks", ""),
                })
                rows.append(row)
    return rows


def median_value(rows: list[dict[str, object]], key: str, cast=float) -> str:
    values = [cast(row[key]) for row in rows if row.get(key) not in ("", None)]
    if not values:
        return ""
    value = median(values)
    if cast is int:
        return str(int(value))
    return f"{float(value):.6f}"


def summarize(compression: list[dict[str, object]], search: list[dict[str, object]]) -> list[dict[str, object]]:
    summary: list[dict[str, object]] = []
    groups: dict[tuple[str, str, str, str], list[dict[str, object]]] = {}
    for row in compression:
        groups.setdefault(("compress", row["corpus"], "", row["variant"]), []).append(row)
    for row in search:
        groups.setdefault(("search", row["corpus"], row["query_name"], row["variant"]), []).append(row)
    for (operation, corpus, query_name, variant), rows in sorted(groups.items()):
        out = {field: "" for field in SUMMARY_FIELDS}
        out.update({
            "operation": operation,
            "corpus": corpus,
            "query_name": query_name,
            "variant": variant,
            "median_wall_seconds": median_value(rows, "wall_seconds", float),
            "median_total_cpu_seconds": median_value(rows, "total_cpu_seconds", float),
            "median_max_rss_kb": median_value(rows, "max_rss_kb", int),
            "median_output_bytes": median_value(rows, "output_bytes", int) if operation == "compress" else "",
            "runs": len(rows),
        })
        summary.append(out)
    return summary


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_report(path: Path, summary: list[dict[str, object]], cache_method_notes: str) -> None:
    lines = [
        "# Phase 1m production cleanup A/B benchmark",
        "",
        "This benchmark compares a Phase 1k baseline source snapshot against the cleaned Phase 1m final source in the same run.",
        "",
        f"Cache control: {cache_method_notes}",
        "",
        "## Median summary",
        "",
        "| operation | corpus | query | variant | wall_s | cpu_s | rss_kb | output_bytes | runs |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            f"| {row['operation']} | {row['corpus']} | {row['query_name']} | {row['variant']} | "
            f"{row['median_wall_seconds']} | {row['median_total_cpu_seconds']} | {row['median_max_rss_kb']} | "
            f"{row['median_output_bytes']} | {row['runs']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_rows(compression: list[dict[str, object]], search: list[dict[str, object]]) -> None:
    for row in compression + search:
        if row.get("max_rss_kb", "") == "" or row.get("total_cpu_seconds", "") == "":
            raise RuntimeError(f"missing RSS/CPU in row: {row}")
    if any(str(row.get("roundtrip_ok")) != "True" for row in compression):
        raise RuntimeError("roundtrip failed for at least one compression row")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="validation_results/phase1m_cleanup_ab_bench.csv")
    parser.add_argument("--search-output", default="validation_results/phase1m_cleanup_ab_search.csv")
    parser.add_argument("--summary-output", default="validation_results/phase1m_cleanup_ab_summary.csv")
    parser.add_argument("--report", default="validation_results/phase1m_cleanup_ab_report.md")
    parser.add_argument("--corpora", default=CORPUS_DEFAULT)
    parser.add_argument("--lines", type=int, default=75000)
    parser.add_argument("--seed", type=int, default=424242)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--cache-buster-mb", type=int, default=256)
    args = parser.parse_args()

    corpora = [item.strip() for item in args.corpora.split(",") if item.strip()]
    with tempfile.TemporaryDirectory(prefix="zlg-phase1m-") as tmp_name:
        tmp = Path(tmp_name)
        cache_buster = tmp / "cache-buster.bin"
        make_cache_buster(cache_buster, args.cache_buster_mb)
        final_bin = build_final_binary(tmp)
        baseline_bin = build_baseline_binary(tmp)

        compression: list[dict[str, object]] = []
        search: list[dict[str, object]] = []
        cache_methods: set[str] = set()
        for corpus in corpora:
            source = tmp / f"{corpus}.log"
            base.make_corpus(corpus, source, args.lines, args.seed)
            compression.extend(
                compression_rows(corpus, args.seed, source, final_bin, baseline_bin, args.repeats, tmp, cache_buster)
            )
            cache_methods.update(str(row["cache_control"]) for row in compression if row["corpus"] == corpus)
            archive = make_reference_archive(corpus, source, final_bin, tmp, cache_buster)
            search.extend(search_rows(corpus, args.seed, archive, final_bin, baseline_bin, args.repeats, tmp, cache_buster))
            cache_methods.update(str(row["cache_control"]) for row in search if row["corpus"] == corpus)

        validate_rows(compression, search)
        summary = summarize(compression, search)
        write_csv(REPO / args.output, COMPRESSION_FIELDS, compression)
        write_csv(REPO / args.search_output, SEARCH_FIELDS, search)
        write_csv(REPO / args.summary_output, SUMMARY_FIELDS, summary)
        write_report(REPO / args.report, summary, ", ".join(sorted(cache_methods)))


if __name__ == "__main__":
    main()
