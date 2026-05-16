#!/usr/bin/env python3
"""Phase 1h locked-stack size diagnosis.

This is a diagnostic-only pass. It keeps the decided stack fixed and measures
where archive bytes go, especially when .zlg is larger than gzip. It does not
introduce new builder candidates or change the on-disk format.
"""

from __future__ import annotations

import argparse
import csv
import json
import struct
import sys
import tempfile
from pathlib import Path

# Reuse the Phase 1g corpus generation and fail-closed timing helpers so RSS
# and CPU behavior stay consistent with the validated benchmark harness.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import phase1g_size_overhead_bench as base  # noqa: E402

REPO = Path(__file__).resolve().parents[1]

# Diagnostic-only set. combined-bitset-seen is the locked production candidate.
# combined-sparse-first-bitset is carried as the memory reference. combined is
# kept as the reference baseline. This is not a builder bakeoff.
PROFILES = [
    "combined-bitset-seen",
    "combined-sparse-first-bitset",
    "combined",
]

CORPUS_DEFAULT = (
    "high_dup,high_cardinality,unicode,binaryish,"
    "realistic_mixed_log,long_line_log,short_line_log"
)

ARCHIVE_FIELDS = [
    "corpus",
    "seed",
    "corpus_bytes",
    "corpus_sha256",
    "tool",
    "build_profile",
    "wall_seconds",
    "user_seconds",
    "system_seconds",
    "total_cpu_seconds",
    "max_rss_kb",
    "returncode",
    "output_bytes",
    "gzip_output_bytes",
    "delta_vs_gzip_bytes",
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
    "zlg_payload_delta_vs_gzip_bytes",
    "build_chunks",
    "build_summary_ns",
    "build_zstd_ns",
    "build_write_ns",
    "build_total_ns",
    "build_summary_bytes",
    "build_compressed_bytes",
    "build_uncompressed_bytes",
    "build_raw_edge_windows",
    "build_pushed_edges",
    "build_unique_edges",
    "build_duplicate_ratio",
    "build_bitset_resizes",
    "build_bitset_cleared_edges",
    "build_touched_first_buckets",
    "build_scratch_bytes",
    "build_bitset_scratch_bytes",
    "build_first_bitset_scratch_bytes",
    "notes",
]

CHUNK_FIELDS = [
    "corpus",
    "seed",
    "build_profile",
    "chunk_index",
    "first_line_number",
    "line_count",
    "uncompressed_bytes",
    "compressed_payload_bytes",
    "summary_bytes",
    "chunk_header_bytes",
    "total_chunk_bytes",
    "mesh_edge_count",
    "avg_line_bytes",
    "payload_ratio",
    "summary_pct_of_chunk",
    "payload_pct_of_chunk",
    "summary_bytes_per_line",
    "payload_bytes_per_line",
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


def parse_mesh_edge_count(summary: bytes) -> int:
    if len(summary) >= 12 and summary[:4] == b"ZBM1":
        return struct.unpack_from("<I", summary, 8)[0]
    return 0


def parse_zlg_chunks(path: Path) -> tuple[dict[str, int], list[dict[str, int]]]:
    data = path.read_bytes()
    offset = 32
    chunks: list[dict[str, int]] = []
    totals = {
        "zlg_total_bytes": len(data),
        "zlg_chunk_count": 0,
        "zlg_chunk_header_bytes": 0,
        "zlg_summary_bytes": 0,
        "zlg_compressed_payload_bytes": 0,
        "zlg_directory_footer_bytes": 0,
        "zlg_global_header_bytes": 32,
        "zlg_component_sum_bytes": 0,
    }

    while offset + 4 <= len(data):
        magic = data[offset:offset + 4]
        if magic == b"ZCH1":
            header_len = struct.unpack_from("<H", data, offset + 4)[0]
            chunk_index = struct.unpack_from("<Q", data, offset + 8)[0]
            first_line_number = struct.unpack_from("<Q", data, offset + 16)[0]
            line_count = struct.unpack_from("<Q", data, offset + 24)[0]
            uncompressed_len = struct.unpack_from("<Q", data, offset + 32)[0]
            compressed_len = struct.unpack_from("<Q", data, offset + 40)[0]
            summary_len = struct.unpack_from("<I", data, offset + 48)[0]
            summary_offset = offset + header_len
            compressed_offset = summary_offset + summary_len
            record_len = header_len + summary_len + compressed_len
            if compressed_offset + compressed_len > len(data):
                raise ValueError("zlg chunk record exceeds file size")
            summary = data[summary_offset:summary_offset + summary_len]
            total_chunk_bytes = header_len + summary_len + compressed_len
            chunks.append({
                "chunk_index": chunk_index,
                "first_line_number": first_line_number,
                "line_count": line_count,
                "uncompressed_bytes": uncompressed_len,
                "compressed_payload_bytes": compressed_len,
                "summary_bytes": summary_len,
                "chunk_header_bytes": header_len,
                "total_chunk_bytes": total_chunk_bytes,
                "mesh_edge_count": parse_mesh_edge_count(summary),
            })
            totals["zlg_chunk_count"] += 1
            totals["zlg_chunk_header_bytes"] += header_len
            totals["zlg_summary_bytes"] += summary_len
            totals["zlg_compressed_payload_bytes"] += compressed_len
            offset += record_len
        elif magic == b"ZDR1":
            entry_len = struct.unpack_from("<I", data, offset + 4)[0]
            count = struct.unpack_from("<Q", data, offset + 8)[0]
            directory_len = 4 + 4 + 8 + entry_len * count
            footer_len = 48
            totals["zlg_directory_footer_bytes"] = directory_len + footer_len
            offset += directory_len + footer_len
            break
        else:
            raise ValueError(f"unexpected zlg magic {magic!r} at offset {offset}")

    totals["zlg_component_sum_bytes"] = (
        totals["zlg_global_header_bytes"]
        + totals["zlg_chunk_header_bytes"]
        + totals["zlg_summary_bytes"]
        + totals["zlg_compressed_payload_bytes"]
        + totals["zlg_directory_footer_bytes"]
    )
    if totals["zlg_component_sum_bytes"] != totals["zlg_total_bytes"]:
        raise ValueError(
            f"component sum {totals['zlg_component_sum_bytes']} != total {totals['zlg_total_bytes']}"
        )
    return totals, chunks


def empty_archive_row(meta: dict[str, object]) -> dict[str, object]:
    row = {field: "" for field in ARCHIVE_FIELDS}
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
        "pushed_edges": "build_pushed_edges",
        "unique_edges": "build_unique_edges",
        "bitset_resizes": "build_bitset_resizes",
        "bitset_cleared_edges": "build_bitset_cleared_edges",
        "touched_first_buckets": "build_touched_first_buckets",
        "scratch_bytes": "build_scratch_bytes",
        "bitset_scratch_bytes": "build_bitset_scratch_bytes",
        "first_bitset_scratch_bytes": "build_first_bitset_scratch_bytes",
    }
    for source, target in mapping.items():
        row[target] = stats.get(source, "")
    raw = stats.get("raw_edge_windows", 0) or 0
    unique = stats.get("unique_edges", 0) or 0
    row["build_duplicate_ratio"] = f6(1.0 - (float(unique) / float(raw))) if raw else ""


def run_probe(args: argparse.Namespace) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    archive_rows: list[dict[str, object]] = []
    chunk_rows: list[dict[str, object]] = []
    binary = (REPO / args.binary).resolve()
    corpora = [name.strip() for name in args.corpora.split(",") if name.strip()]

    with tempfile.TemporaryDirectory(prefix="zlg-phase1h-") as tmp_name:
        tmp = Path(tmp_name)
        for corpus_name in corpora:
            corpus = tmp / f"{corpus_name}.log"
            base.make_corpus(corpus_name, corpus, args.lines, args.seed)
            meta = {
                "corpus": corpus_name,
                "seed": args.seed,
                "corpus_bytes": corpus.stat().st_size,
                "corpus_sha256": base.sha256(corpus),
            }

            gzip_path = tmp / f"{corpus_name}.gz"

            def gzip_cmd(gzip_path=gzip_path, corpus=corpus):
                gzip_path.unlink(missing_ok=True)
                return (["gzip", "-6", "-c", str(corpus)], gzip_path)

            gzip_timing = base.run_repeated(gzip_cmd, args.repeats, tmp)
            gzip_size = gzip_path.stat().st_size
            gzip_row = empty_archive_row(meta)
            gzip_row.update({
                "tool": "gzip",
                "build_profile": "gzip-6",
                "output_bytes": gzip_size,
                "gzip_output_bytes": gzip_size,
                "delta_vs_gzip_bytes": 0,
                "notes": "external baseline",
            })
            add_timing(gzip_row, gzip_timing)
            archive_rows.append(gzip_row)

            for profile in PROFILES:
                zlg_path = tmp / f"{corpus_name}-{profile}.zlg"
                stats_path = tmp / f"{corpus_name}-{profile}.stats.json"

                def zlg_cmd(profile=profile, zlg_path=zlg_path, stats_path=stats_path, corpus=corpus):
                    zlg_path.unlink(missing_ok=True)
                    stats_path.unlink(missing_ok=True)
                    cmd = [
                        str(binary),
                        "compress",
                        "--chunk-policy",
                        "fixed-lines8192",
                        "--summary-mode",
                        "mesh-bigram",
                        "--build-profile",
                        profile,
                        "--build-stats-json",
                        str(stats_path),
                        "-o",
                        str(zlg_path),
                        str(corpus),
                    ]
                    return (cmd, None)

                timing = base.run_repeated(zlg_cmd, args.repeats, tmp)
                stats = json.loads(stats_path.read_text(encoding="utf-8"))
                totals, chunks = parse_zlg_chunks(zlg_path)
                zlg_size = zlg_path.stat().st_size

                row = empty_archive_row(meta)
                row.update({
                    "tool": "zlg",
                    "build_profile": profile,
                    "output_bytes": zlg_size,
                    "gzip_output_bytes": gzip_size,
                    "delta_vs_gzip_bytes": zlg_size - gzip_size,
                    "summary_pct_of_zlg": pct(totals["zlg_summary_bytes"], zlg_size),
                    "payload_pct_of_zlg": pct(totals["zlg_compressed_payload_bytes"], zlg_size),
                    "zlg_payload_delta_vs_gzip_bytes": totals["zlg_compressed_payload_bytes"] - gzip_size,
                    "notes": "locked" if profile == "combined-bitset-seen" else "reference",
                })
                row.update(totals)
                add_timing(row, timing)
                add_build_stats(row, stats)
                archive_rows.append(row)

                for chunk in chunks:
                    chunk_row = {field: "" for field in CHUNK_FIELDS}
                    chunk_row.update({
                        "corpus": corpus_name,
                        "seed": args.seed,
                        "build_profile": profile,
                    })
                    chunk_row.update(chunk)
                    lines = int(chunk["line_count"])
                    uncomp = int(chunk["uncompressed_bytes"])
                    payload = int(chunk["compressed_payload_bytes"])
                    summary = int(chunk["summary_bytes"])
                    total = int(chunk["total_chunk_bytes"])
                    chunk_row["avg_line_bytes"] = ratio(uncomp, lines)
                    chunk_row["payload_ratio"] = ratio(payload, uncomp)
                    chunk_row["summary_pct_of_chunk"] = pct(summary, total)
                    chunk_row["payload_pct_of_chunk"] = pct(payload, total)
                    chunk_row["summary_bytes_per_line"] = ratio(summary, lines)
                    chunk_row["payload_bytes_per_line"] = ratio(payload, lines)
                    chunk_rows.append(chunk_row)
    return archive_rows, chunk_rows


def validate_rows(archive_rows: list[dict[str, object]], chunk_rows: list[dict[str, object]]) -> None:
    for row in archive_rows:
        if row.get("max_rss_kb") in ("", None):
            raise SystemExit(f"missing RSS for archive row {row}")
        if row.get("total_cpu_seconds") in ("", None):
            raise SystemExit(f"missing CPU for archive row {row}")
        if row["tool"] == "zlg":
            for key in [
                "zlg_total_bytes",
                "zlg_summary_bytes",
                "zlg_compressed_payload_bytes",
                "zlg_chunk_header_bytes",
                "zlg_directory_footer_bytes",
                "zlg_component_sum_bytes",
            ]:
                if row.get(key) in ("", None):
                    raise SystemExit(f"missing {key} for archive row {row}")
    if not chunk_rows:
        raise SystemExit("no chunk rows generated")
    for row in chunk_rows:
        for key in ["summary_bytes", "compressed_payload_bytes", "mesh_edge_count", "payload_ratio"]:
            if row.get(key) in ("", None):
                raise SystemExit(f"missing {key} for chunk row {row}")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_markdown(path: Path, archive_rows: list[dict[str, object]], chunk_rows: list[dict[str, object]]) -> None:
    locked_rows = [
        row for row in archive_rows
        if row["tool"] == "zlg" and row["build_profile"] == "combined-bitset-seen"
    ]
    doc = [
        "# Phase 1h Locked-Stack Size Diagnosis",
        "",
        "This is a diagnostic-only pass for the locked stack. It does not add new production candidates, change fixed-lines8192, change mesh-bigram ZBM1 v2, change the combined-bitset-seen builder, or change search behavior.",
        "",
        "## Locked stack under diagnosis",
        "",
        "```text",
        "fixed-lines8192",
        "+ mesh-bigram ZBM1 v2",
        "+ zstd::bulk::Compressor",
        "+ combined-bitset-seen",
        "+ streaming grep",
        "+ Rust regex default",
        "+ PCRE2 for -P",
        "+ literal prefiltering",
        "+ positive-lookbehind fast path",
        "+ --head / --max-count early stop",
        "```",
        "",
        "## Locked profile versus gzip",
        "",
        "| corpus | zlg_bytes | gzip_bytes | delta | payload_delta | summary_pct | payload_pct | wall_s | cpu_s | rss_kb | chunks |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(locked_rows, key=lambda item: item["corpus"]):
        doc.append(
            f"| {row['corpus']} | {row['output_bytes']} | {row['gzip_output_bytes']} | "
            f"{row['delta_vs_gzip_bytes']} | {row['zlg_payload_delta_vs_gzip_bytes']} | "
            f"{row['summary_pct_of_zlg']} | {row['payload_pct_of_zlg']} | "
            f"{row['wall_seconds']} | {row['total_cpu_seconds']} | {row['max_rss_kb']} | "
            f"{row['zlg_chunk_count']} |"
        )
    doc.extend([
        "",
        "## Component breakdown for locked profile",
        "",
        "| corpus | total | payload | summary | chunk_headers | directory_footer | global_header |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in sorted(locked_rows, key=lambda item: item["corpus"]):
        doc.append(
            f"| {row['corpus']} | {row['zlg_total_bytes']} | "
            f"{row['zlg_compressed_payload_bytes']} | {row['zlg_summary_bytes']} | "
            f"{row['zlg_chunk_header_bytes']} | {row['zlg_directory_footer_bytes']} | "
            f"{row['zlg_global_header_bytes']} |"
        )

    locked_chunk_rows = [
        row for row in chunk_rows if row["build_profile"] == "combined-bitset-seen"
    ]
    worst_summary = sorted(
        locked_chunk_rows,
        key=lambda row: float(row["summary_pct_of_chunk"] or 0.0),
        reverse=True,
    )[:10]
    worst_payload = sorted(
        locked_chunk_rows,
        key=lambda row: float(row["payload_ratio"] or 0.0),
        reverse=True,
    )[:10]
    doc.extend([
        "",
        "## Worst locked-profile chunks by summary percent",
        "",
        "| corpus | chunk | lines | uncomp | payload | summary | summary_pct | mesh_edges |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in worst_summary:
        doc.append(
            f"| {row['corpus']} | {row['chunk_index']} | {row['line_count']} | "
            f"{row['uncompressed_bytes']} | {row['compressed_payload_bytes']} | "
            f"{row['summary_bytes']} | {row['summary_pct_of_chunk']} | {row['mesh_edge_count']} |"
        )
    doc.extend([
        "",
        "## Worst locked-profile chunks by payload ratio",
        "",
        "| corpus | chunk | lines | uncomp | payload | summary | payload_ratio | avg_line_bytes |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in worst_payload:
        doc.append(
            f"| {row['corpus']} | {row['chunk_index']} | {row['line_count']} | "
            f"{row['uncompressed_bytes']} | {row['compressed_payload_bytes']} | "
            f"{row['summary_bytes']} | {row['payload_ratio']} | {row['avg_line_bytes']} |"
        )

    doc.extend([
        "",
        "## Reference rows",
        "",
        "The CSV also includes combined-sparse-first-bitset as the memory reference and combined as the historical reference baseline. These are not new production candidates in this phase.",
        "",
        "## Success criteria",
        "",
        "- RSS and CPU are captured for every archive row.",
        "- gzip -6 is present for every corpus.",
        "- Per-archive zlg component accounting is captured.",
        "- Per-chunk payload and summary accounting is captured.",
        "- The run does not change the active stack or on-disk format.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", default="target/release/zlg")
    parser.add_argument("--lines", type=int, default=80000)
    parser.add_argument("--seed", type=int, default=4242)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--corpora", default=CORPUS_DEFAULT)
    parser.add_argument("--archive-csv", default="validation_results/phase1h_size_diagnosis_archive.csv")
    parser.add_argument("--chunk-csv", default="validation_results/phase1h_size_diagnosis_chunks.csv")
    parser.add_argument("--output", default="validation_results/phase1h_size_diagnosis.md")
    args = parser.parse_args()

    archive_rows, chunk_rows = run_probe(args)
    validate_rows(archive_rows, chunk_rows)
    write_csv(REPO / args.archive_csv, ARCHIVE_FIELDS, archive_rows)
    write_csv(REPO / args.chunk_csv, CHUNK_FIELDS, chunk_rows)
    write_markdown(REPO / args.output, archive_rows, chunk_rows)
    print(f"wrote {REPO / args.output}")
    print(f"wrote {REPO / args.archive_csv}")
    print(f"wrote {REPO / args.chunk_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
