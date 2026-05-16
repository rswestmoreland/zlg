#!/usr/bin/env python3
"""Phase 1k final-stack memory and level diagnostic.

This pass keeps the selected production stack fixed: fixed-lines8192 with an
8 MiB byte cap, mesh-bigram ZBM1 v2, combined-bitset-seen, zstd::bulk, and
streaming grep. It compares gzip levels 6/8/9 against zlg levels 3/6/8/9,
checks the default CLI path, and keeps no-summary rows only as memory
diagnostics.
"""

from __future__ import annotations

import argparse
import csv
import filecmp
import json
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import phase1g_size_overhead_bench as base  # noqa: E402
import phase1i_level_memory_probe as diag  # noqa: E402

REPO = Path(__file__).resolve().parents[1]

CORPUS_DEFAULT = (
    "high_dup,high_cardinality,unicode,binaryish,"
    "realistic_mixed_log,long_line_log,short_line_log"
)

CSV_FIELDS = [
    "corpus",
    "seed",
    "corpus_bytes",
    "corpus_sha256",
    "tool",
    "mode",
    "chunk_policy",
    "zstd_level",
    "gzip_level",
    "build_profile",
    "summary_mode",
    "wall_seconds",
    "user_seconds",
    "system_seconds",
    "total_cpu_seconds",
    "max_rss_kb",
    "returncode",
    "output_bytes",
    "gzip_6_bytes",
    "gzip_8_bytes",
    "gzip_9_bytes",
    "delta_vs_gzip_6_bytes",
    "delta_vs_gzip_8_bytes",
    "delta_vs_gzip_9_bytes",
    "zlg_total_bytes",
    "zlg_chunk_count",
    "zlg_chunk_header_bytes",
    "zlg_summary_bytes",
    "zlg_compressed_payload_bytes",
    "zlg_directory_footer_bytes",
    "zlg_global_header_bytes",
    "zlg_component_sum_bytes",
    "summary_pct_of_zlg",
    "payload_pct_of_zlg",
    "max_chunk_uncompressed_bytes",
    "max_chunk_compressed_payload_bytes",
    "max_chunk_summary_bytes",
    "avg_chunk_uncompressed_bytes",
    "max_chunk_lines",
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
    "build_max_chunk_uncompressed_bytes",
    "build_max_chunk_compressed_bytes",
    "build_max_chunk_summary_bytes",
    "roundtrip_ok",
    "notes",
]

CHUNK_FIELDS = [
    "corpus",
    "seed",
    "mode",
    "chunk_policy",
    "zstd_level",
    "build_profile",
    "summary_mode",
    "chunk_index",
    "first_line_number",
    "line_count",
    "uncompressed_bytes",
    "compressed_payload_bytes",
    "summary_bytes",
    "chunk_header_bytes",
    "total_chunk_bytes",
    "payload_ratio",
    "summary_pct_of_chunk",
]


def f6(value: float) -> str:
    return f"{value:.6f}"


def pct(part: int, whole: int) -> str:
    if whole <= 0:
        return ""
    return f6((part / whole) * 100.0)


def ratio(part: int, whole: int) -> str:
    if whole <= 0:
        return ""
    return f6(part / whole)


def empty_row(meta: dict[str, object]) -> dict[str, object]:
    row = {field: "" for field in CSV_FIELDS}
    row.update({
        "corpus": meta["corpus"],
        "seed": meta["seed"],
        "corpus_bytes": meta["corpus_bytes"],
        "corpus_sha256": meta["corpus_sha256"],
    })
    return row


def add_timing(row: dict[str, object], timing: dict[str, object]) -> None:
    for key in [
        "wall_seconds",
        "user_seconds",
        "system_seconds",
        "total_cpu_seconds",
        "max_rss_kb",
        "returncode",
    ]:
        row[key] = timing[key]


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
        "scratch_bytes": "build_scratch_bytes",
        "bitset_scratch_bytes": "build_bitset_scratch_bytes",
        "max_chunk_uncompressed_bytes": "build_max_chunk_uncompressed_bytes",
        "max_chunk_compressed_bytes": "build_max_chunk_compressed_bytes",
        "max_chunk_summary_bytes": "build_max_chunk_summary_bytes",
    }
    for src, dst in mapping.items():
        row[dst] = stats.get(src, "")


def assert_metric_capture(rows: list[dict[str, object]]) -> None:
    missing = [
        row for row in rows
        if str(row.get("max_rss_kb", "")) == ""
        or str(row.get("total_cpu_seconds", "")) == ""
    ]
    if missing:
        raise RuntimeError(f"missing RSS/CPU fields in {len(missing)} rows")


def run_gzip(binary: str, level: int, source: Path, out: Path, tmp: Path) -> dict[str, object]:
    return base.run_measured([binary, f"-{level}", "-c", str(source)], stdout_path=out, tmp=tmp)


def run_zlg_compress(
    zlg: Path,
    source: Path,
    out: Path,
    stats: Path,
    tmp: Path,
    *,
    level: int,
    profile: str,
    summary_mode: str,
    chunk_policy: str,
) -> dict[str, object]:
    cmd = [
        str(zlg),
        "compress",
        "--chunk-policy",
        chunk_policy,
        "--summary-mode",
        summary_mode,
        "--build-profile",
        profile,
        "--level",
        str(level),
        "--build-stats-json",
        str(stats),
        "-o",
        str(out),
        str(source),
    ]
    return base.run_measured(cmd, stdout_path=None, tmp=tmp)


def check_roundtrip(zlg: Path, archive: Path, source: Path, tmp: Path) -> bool:
    decoded = tmp / f"decoded-{archive.stem}.bin"
    result = base.run_measured([str(zlg), "cat", str(archive), "-o", str(decoded)], stdout_path=None, tmp=tmp)
    if result["returncode"] != 0:
        return False
    return filecmp.cmp(source, decoded, shallow=False)


def add_zlg_components(
    row: dict[str, object],
    archive: Path,
    meta: dict[str, object],
    chunks_out: list[dict[str, object]],
    *,
    mode: str,
    chunk_policy: str,
    level: int,
    profile: str,
    summary_mode: str,
) -> None:
    totals, chunks = diag.parse_zlg_chunks(archive)
    for key, value in totals.items():
        row[key] = value
    row["output_bytes"] = totals["zlg_total_bytes"]
    row["summary_pct_of_zlg"] = pct(totals["zlg_summary_bytes"], totals["zlg_total_bytes"])
    row["payload_pct_of_zlg"] = pct(totals["zlg_compressed_payload_bytes"], totals["zlg_total_bytes"])
    if chunks:
        max_uncompressed = max(int(c["uncompressed_bytes"]) for c in chunks)
        max_payload = max(int(c["compressed_payload_bytes"]) for c in chunks)
        max_summary = max(int(c["summary_bytes"]) for c in chunks)
        max_lines = max(int(c["line_count"]) for c in chunks)
        avg_uncompressed = sum(int(c["uncompressed_bytes"]) for c in chunks) / len(chunks)
    else:
        max_uncompressed = max_payload = max_summary = max_lines = 0
        avg_uncompressed = 0.0
    row["max_chunk_uncompressed_bytes"] = max_uncompressed
    row["max_chunk_compressed_payload_bytes"] = max_payload
    row["max_chunk_summary_bytes"] = max_summary
    row["max_chunk_lines"] = max_lines
    row["avg_chunk_uncompressed_bytes"] = f6(avg_uncompressed)

    for chunk in chunks:
        c_row = {field: "" for field in CHUNK_FIELDS}
        c_row.update({
            "corpus": meta["corpus"],
            "seed": meta["seed"],
            "mode": mode,
            "chunk_policy": chunk_policy,
            "zstd_level": level,
            "build_profile": profile,
            "summary_mode": summary_mode,
            "chunk_index": chunk["chunk_index"],
            "first_line_number": chunk["first_line_number"],
            "line_count": chunk["line_count"],
            "uncompressed_bytes": chunk["uncompressed_bytes"],
            "compressed_payload_bytes": chunk["compressed_payload_bytes"],
            "summary_bytes": chunk["summary_bytes"],
            "chunk_header_bytes": chunk["chunk_header_bytes"],
            "total_chunk_bytes": chunk["total_chunk_bytes"],
            "payload_ratio": ratio(int(chunk["compressed_payload_bytes"]), int(chunk["uncompressed_bytes"])),
            "summary_pct_of_chunk": pct(int(chunk["summary_bytes"]), int(chunk["total_chunk_bytes"])),
        })
        chunks_out.append(c_row)


def fill_gzip_deltas(row: dict[str, object], gzip_sizes: dict[int, int]) -> None:
    row["gzip_6_bytes"] = gzip_sizes[6]
    row["gzip_8_bytes"] = gzip_sizes[8]
    row["gzip_9_bytes"] = gzip_sizes[9]
    if row.get("output_bytes", "") != "":
        out = int(row["output_bytes"])
        row["delta_vs_gzip_6_bytes"] = out - gzip_sizes[6]
        row["delta_vs_gzip_8_bytes"] = out - gzip_sizes[8]
        row["delta_vs_gzip_9_bytes"] = out - gzip_sizes[9]


def write_report(path: Path, rows: list[dict[str, object]]) -> None:
    zlg_rows = [r for r in rows if r["tool"] == "zlg"]
    gzip_rows = [r for r in rows if r["tool"] == "gzip"]
    by_corpus = sorted({str(r["corpus"]) for r in rows})
    lines = []
    lines.append("# Phase 1k final-stack memory and level diagnostic")
    lines.append("")
    lines.append("Diagnostic-only pass for the final stack defaults, zstd level 8, gzip level 8, and memory accounting.")
    lines.append("")
    lines.append("## Gzip rows")
    lines.append("")
    lines.append("| corpus | gzip level | wall_s | cpu_s | rss_kb | output_bytes |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for r in gzip_rows:
        lines.append(
            f"| {r['corpus']} | {r['gzip_level']} | {r['wall_seconds']} | "
            f"{r['total_cpu_seconds']} | {r['max_rss_kb']} | {r['output_bytes']} |"
        )
    lines.append("")
    lines.append("## ZLG mode summary")
    lines.append("")
    lines.append("| corpus | mode | policy | level | profile | summary | wall_s | cpu_s | rss_kb | output_bytes | max_chunk_bytes | delta_gzip6 | delta_gzip8 | delta_gzip9 | roundtrip |")
    lines.append("|---|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for r in zlg_rows:
        lines.append(
            f"| {r['corpus']} | {r['mode']} | {r['chunk_policy']} | {r['zstd_level']} | "
            f"{r['build_profile']} | {r['summary_mode']} | {r['wall_seconds']} | "
            f"{r['total_cpu_seconds']} | {r['max_rss_kb']} | {r['output_bytes']} | "
            f"{r['max_chunk_uncompressed_bytes']} | {r['delta_vs_gzip_6_bytes']} | "
            f"{r['delta_vs_gzip_8_bytes']} | {r['delta_vs_gzip_9_bytes']} | {r['roundtrip_ok']} |"
        )
    lines.append("")
    lines.append("## Best size per corpus among locked/capped zlg rows")
    lines.append("")
    lines.append("| corpus | best_mode | level | policy | output_bytes | gzip6 | gzip8 | gzip9 |")
    lines.append("|---|---|---:|---|---:|---:|---:|---:|")
    for corpus in by_corpus:
        candidates = [
            r for r in zlg_rows
            if r["corpus"] == corpus and str(r["mode"]).startswith("final-cap8m-l")
        ]
        best = min(candidates, key=lambda r: int(r["output_bytes"]))
        lines.append(
            f"| {corpus} | {best['mode']} | {best['zstd_level']} | {best['chunk_policy']} | "
            f"{best['output_bytes']} | {best['gzip_6_bytes']} | {best['gzip_8_bytes']} | {best['gzip_9_bytes']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    zlg = (REPO / args.binary).resolve()
    corpora = [part.strip() for part in args.corpora.split(",") if part.strip()]
    rows: list[dict[str, object]] = []
    chunk_rows: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory(prefix="zlg-phase1k-") as tmp_name:
        tmp = Path(tmp_name)
        for corpus in corpora:
            source = tmp / f"{corpus}.log"
            base.make_corpus(corpus, source, args.lines, args.seed)
            meta = {
                "corpus": corpus,
                "seed": args.seed,
                "corpus_bytes": source.stat().st_size,
                "corpus_sha256": base.sha256(source),
            }

            gzip_sizes: dict[int, int] = {}
            for gz_level in (6, 8, 9):
                out = tmp / f"{corpus}.gz{gz_level}"
                timing = run_gzip(args.gzip_binary, gz_level, source, out, tmp)
                row = empty_row(meta)
                row.update({
                    "tool": "gzip",
                    "mode": f"gzip-{gz_level}",
                    "gzip_level": gz_level,
                    "output_bytes": out.stat().st_size,
                })
                add_timing(row, timing)
                gzip_sizes[gz_level] = out.stat().st_size
                rows.append(row)

            zlg_configs = []
            for level in (3, 6, 8, 9):
                zlg_configs.append((f"final-cap8m-l{level}", "fixed-lines8192-cap8m", level, "combined-bitset-seen", "mesh-bigram"))
            for level in (6, 8, 9):
                zlg_configs.append((f"no-summary-cap8m-l{level}", "fixed-lines8192-cap8m", level, "combined-bitset-seen", "none"))
            zlg_configs.append(("default-cli", "default", 0, "default", "default"))
            if corpus == "long_line_log":
                for level in (6, 8, 9):
                    zlg_configs.append((f"uncapped-reference-l{level}", "fixed-lines8192", level, "combined-bitset-seen", "mesh-bigram"))

            for mode, policy, level, profile, summary_mode in zlg_configs:
                out = tmp / f"{corpus}-{mode}.zlg"
                stats_path = tmp / f"{corpus}-{mode}.json"
                if mode == "default-cli":
                    cmd = [str(zlg), "compress", "--build-stats-json", str(stats_path), "-o", str(out), str(source)]
                    timing = base.run_measured(cmd, stdout_path=None, tmp=tmp)
                    policy = "default"
                    level = 0
                    profile = "default"
                    summary_mode = "default"
                else:
                    timing = run_zlg_compress(
                        zlg,
                        source,
                        out,
                        stats_path,
                        tmp,
                        level=level,
                        profile=profile,
                        summary_mode=summary_mode,
                        chunk_policy=policy,
                    )
                row = empty_row(meta)
                row.update({
                    "tool": "zlg",
                    "mode": mode,
                    "chunk_policy": policy,
                    "zstd_level": level,
                    "build_profile": profile,
                    "summary_mode": summary_mode,
                })
                add_timing(row, timing)
                if timing["returncode"] == 0:
                    stats = json.loads(stats_path.read_text(encoding="utf-8"))
                    add_build_stats(row, stats)
                    add_zlg_components(
                        row,
                        out,
                        meta,
                        chunk_rows,
                        mode=mode,
                        chunk_policy=policy,
                        level=level,
                        profile=profile,
                        summary_mode=summary_mode,
                    )
                    row["roundtrip_ok"] = "true" if check_roundtrip(zlg, out, source, tmp) else "false"
                fill_gzip_deltas(row, gzip_sizes)
                rows.append(row)

    assert_metric_capture(rows)
    failed_roundtrip = [r for r in rows if r.get("tool") == "zlg" and r.get("roundtrip_ok") != "true"]
    if failed_roundtrip:
        raise RuntimeError(f"roundtrip failed for {len(failed_roundtrip)} zlg rows")

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    with args.chunks_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CHUNK_FIELDS)
        writer.writeheader()
        writer.writerows(chunk_rows)

    write_report(args.output, rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", default="target/release/zlg")
    parser.add_argument("--gzip-binary", default="gzip")
    parser.add_argument("--corpora", default=CORPUS_DEFAULT)
    parser.add_argument("--lines", type=int, default=125_000)
    parser.add_argument("--seed", type=int, default=20260516)
    parser.add_argument("--output", type=Path, default=REPO / "validation_results/phase1k_final_stack_memory.md")
    parser.add_argument("--csv", type=Path, default=REPO / "validation_results/phase1k_final_stack_memory.csv")
    parser.add_argument("--chunks-csv", type=Path, default=REPO / "validation_results/phase1k_final_stack_memory_chunks.csv")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
