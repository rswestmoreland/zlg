#!/usr/bin/env python3
"""Phase 1l final-stack streamlining and reserve-strategy benchmark.

This pass keeps the selected stack fixed and tests only safe micro-optimization
paths plus the four mesh edge reserve options for combined-bitset-seen:
current, none, capped, and previous-unique.
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
    "delta_vs_gzip_6_bytes",
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
    "build_raw_edge_windows",
    "build_candidate_edge_events",
    "build_pushed_edges",
    "build_unique_edges",
    "build_scratch_bytes",
    "build_bitset_scratch_bytes",
    "build_edge_scratch_capacity_bytes",
    "build_edge_capacity_before",
    "build_edge_capacity_after",
    "build_max_chunk_uncompressed_bytes",
    "build_max_chunk_compressed_bytes",
    "build_max_chunk_summary_bytes",
    "roundtrip_ok",
    "matches_current_output",
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
        "raw_edge_windows": "build_raw_edge_windows",
        "candidate_edge_events": "build_candidate_edge_events",
        "pushed_edges": "build_pushed_edges",
        "unique_edges": "build_unique_edges",
        "scratch_bytes": "build_scratch_bytes",
        "bitset_scratch_bytes": "build_bitset_scratch_bytes",
        "edge_scratch_capacity_bytes": "build_edge_scratch_capacity_bytes",
        "edge_capacity_before": "build_edge_capacity_before",
        "edge_capacity_after": "build_edge_capacity_after",
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


def run_gzip(binary: str, source: Path, out: Path, tmp: Path) -> dict[str, object]:
    return base.run_measured([binary, "-6", "-c", str(source)], stdout_path=out, tmp=tmp)


def run_zlg_compress(
    zlg: Path,
    source: Path,
    out: Path,
    stats: Path,
    tmp: Path,
    *,
    profile: str,
) -> dict[str, object]:
    cmd = [
        str(zlg),
        "compress",
        "--chunk-policy",
        "fixed-lines8192-cap8m",
        "--summary-mode",
        "mesh-bigram",
        "--build-profile",
        profile,
        "--level",
        "6",
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
    profile: str,
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
            "chunk_policy": "fixed-lines8192-cap8m",
            "zstd_level": 6,
            "build_profile": profile,
            "summary_mode": "mesh-bigram",
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


def write_report(path: Path, rows: list[dict[str, object]]) -> None:
    zlg_rows = [r for r in rows if r["tool"] == "zlg"]
    lines = []
    lines.append("# Phase 1l final-stack streamlining benchmark")
    lines.append("")
    lines.append("This pass keeps the final stack fixed and compares the four edge reserve options.")
    lines.append("")
    lines.append("## Reserve strategy rows")
    lines.append("")
    lines.append("| corpus | mode | profile | wall_s | cpu_s | rss_kb | output_bytes | edge_capacity_after | unique_edges | candidate_edges | roundtrip | matches_current |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|")
    for r in zlg_rows:
        lines.append(
            f"| {r['corpus']} | {r['mode']} | {r['build_profile']} | {r['wall_seconds']} | "
            f"{r['total_cpu_seconds']} | {r['max_rss_kb']} | {r['output_bytes']} | "
            f"{r['build_edge_capacity_after']} | {r['build_unique_edges']} | "
            f"{r['build_candidate_edge_events']} | {r['roundtrip_ok']} | {r['matches_current_output']} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Production default remains combined-bitset-seen unless a reserve option is promoted after validation.")
    lines.append("- All reserve variants must produce byte-identical zlg output to the current reserve path.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    zlg = (REPO / args.binary).resolve()
    corpora = [part.strip() for part in args.corpora.split(",") if part.strip()]
    rows: list[dict[str, object]] = []
    chunk_rows: list[dict[str, object]] = []

    profiles = [
        ("reserve-current", "combined-bitset-seen"),
        ("reserve-none", "combined-bitset-seen-reserve-none"),
        ("reserve-capped", "combined-bitset-seen-reserve-capped"),
        ("reserve-prev-unique", "combined-bitset-seen-reserve-prev-unique"),
    ]

    with tempfile.TemporaryDirectory(prefix="zlg-phase1l-") as tmp_name:
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

            gzip_out = tmp / f"{corpus}.gz6"
            gzip_timing = run_gzip(args.gzip_binary, source, gzip_out, tmp)
            gzip_size = gzip_out.stat().st_size
            gzip_row = empty_row(meta)
            gzip_row.update({
                "tool": "gzip",
                "mode": "gzip-6",
                "gzip_level": 6,
                "output_bytes": gzip_size,
                "gzip_6_bytes": gzip_size,
            })
            add_timing(gzip_row, gzip_timing)
            rows.append(gzip_row)

            current_bytes = None
            for mode, profile in profiles:
                out = tmp / f"{corpus}-{mode}.zlg"
                stats_path = tmp / f"{corpus}-{mode}.json"
                timing = run_zlg_compress(zlg, source, out, stats_path, tmp, profile=profile)
                row = empty_row(meta)
                row.update({
                    "tool": "zlg",
                    "mode": mode,
                    "chunk_policy": "fixed-lines8192-cap8m",
                    "zstd_level": 6,
                    "build_profile": profile,
                    "summary_mode": "mesh-bigram",
                    "gzip_6_bytes": gzip_size,
                })
                add_timing(row, timing)
                if timing["returncode"] == 0:
                    stats = json.loads(stats_path.read_text(encoding="utf-8"))
                    add_build_stats(row, stats)
                    add_zlg_components(row, out, meta, chunk_rows, mode=mode, profile=profile)
                    row["delta_vs_gzip_6_bytes"] = int(row["output_bytes"]) - gzip_size
                    row["roundtrip_ok"] = "true" if check_roundtrip(zlg, out, source, tmp) else "false"
                    data = out.read_bytes()
                    if mode == "reserve-current":
                        current_bytes = data
                        row["matches_current_output"] = "true"
                    else:
                        row["matches_current_output"] = "true" if data == current_bytes else "false"
                rows.append(row)

    assert_metric_capture(rows)
    bad_roundtrip = [r for r in rows if r.get("tool") == "zlg" and r.get("roundtrip_ok") != "true"]
    if bad_roundtrip:
        raise RuntimeError(f"roundtrip failed for {len(bad_roundtrip)} zlg rows")
    bad_equiv = [r for r in rows if r.get("tool") == "zlg" and r.get("matches_current_output") != "true"]
    if bad_equiv:
        raise RuntimeError(f"reserve output mismatch for {len(bad_equiv)} zlg rows")

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
    parser.add_argument("--output", type=Path, default=REPO / "validation_results/phase1l_final_stack_streamline.md")
    parser.add_argument("--csv", type=Path, default=REPO / "validation_results/phase1l_final_stack_streamline.csv")
    parser.add_argument("--chunks-csv", type=Path, default=REPO / "validation_results/phase1l_final_stack_streamline_chunks.csv")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
