#!/usr/bin/env python3
"""Phase 1i locked-stack zstd level and memory probe.

This is a diagnostic confirmation pass. It keeps the decided zlg stack fixed
and varies only zstd level for the locked builder. It also runs a no-summary
zlg diagnostic mode to separate zstd/chunk writer memory from mesh-summary
memory. The no-summary rows are not production candidates.
"""

from __future__ import annotations

import argparse
import csv
import json
import struct
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import phase1g_size_overhead_bench as base  # noqa: E402

REPO = Path(__file__).resolve().parents[1]

CORPUS_DEFAULT = (
    "high_dup,high_cardinality,unicode,binaryish,"
    "realistic_mixed_log,long_line_log,short_line_log"
)
LEVELS_DEFAULT = "3,4,5,6"

ARCHIVE_FIELDS = [
    "corpus",
    "seed",
    "corpus_bytes",
    "corpus_sha256",
    "tool",
    "mode",
    "zstd_level",
    "build_profile",
    "summary_mode",
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
    "payload_bytes_per_input_byte",
    "output_bytes_per_input_byte",
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
    "build_candidate_edge_events",
    "build_dedupe_ratio_vs_candidates",
    "build_expansion_ratio_vs_raw_windows",
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
    "mode",
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
    "mesh_edge_count",
    "avg_line_bytes",
    "payload_ratio",
    "summary_pct_of_chunk",
    "payload_pct_of_chunk",
    "summary_bytes_per_line",
    "payload_bytes_per_line",
]

MEMORY_FIELDS = [
    "corpus",
    "seed",
    "zstd_level",
    "gzip_rss_kb",
    "zlg_mesh_rss_kb",
    "zlg_no_summary_rss_kb",
    "mesh_minus_no_summary_rss_kb",
    "mesh_minus_gzip_rss_kb",
    "no_summary_minus_gzip_rss_kb",
    "mesh_scratch_bytes",
    "mesh_bitset_scratch_bytes",
    "mesh_summary_bytes",
    "mesh_payload_bytes",
    "no_summary_payload_bytes",
    "payload_delta_mesh_vs_no_summary_bytes",
    "notes",
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

    raw = int(stats.get("raw_edge_windows", 0) or 0)
    pushed = int(stats.get("pushed_edges", 0) or 0)
    unique = int(stats.get("unique_edges", 0) or 0)
    row["build_candidate_edge_events"] = pushed
    row["build_dedupe_ratio_vs_candidates"] = f6(1.0 - (float(unique) / float(pushed))) if pushed else ""
    row["build_expansion_ratio_vs_raw_windows"] = f6(float(pushed) / float(raw)) if raw else ""


def add_zlg_fields(row: dict[str, object], totals: dict[str, int], corpus_bytes: int, gzip_size: int) -> None:
    zlg_size = totals["zlg_total_bytes"]
    row.update(totals)
    row.update({
        "output_bytes": zlg_size,
        "gzip_output_bytes": gzip_size,
        "delta_vs_gzip_bytes": zlg_size - gzip_size,
        "summary_pct_of_zlg": pct(totals["zlg_summary_bytes"], zlg_size),
        "payload_pct_of_zlg": pct(totals["zlg_compressed_payload_bytes"], zlg_size),
        "zlg_payload_delta_vs_gzip_bytes": totals["zlg_compressed_payload_bytes"] - gzip_size,
        "payload_bytes_per_input_byte": ratio(totals["zlg_compressed_payload_bytes"], corpus_bytes),
        "output_bytes_per_input_byte": ratio(zlg_size, corpus_bytes),
    })


def run_probe(args: argparse.Namespace) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    archive_rows: list[dict[str, object]] = []
    chunk_rows: list[dict[str, object]] = []
    memory_rows: list[dict[str, object]] = []
    binary = (REPO / args.binary).resolve()
    corpora = [name.strip() for name in args.corpora.split(",") if name.strip()]
    levels = [int(value.strip()) for value in args.levels.split(",") if value.strip()]

    with tempfile.TemporaryDirectory(prefix="zlg-phase1i-") as tmp_name:
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
                "mode": "gzip-6",
                "zstd_level": "",
                "build_profile": "gzip-6",
                "summary_mode": "n/a",
                "output_bytes": gzip_size,
                "gzip_output_bytes": gzip_size,
                "delta_vs_gzip_bytes": 0,
                "output_bytes_per_input_byte": ratio(gzip_size, int(meta["corpus_bytes"])),
                "notes": "external baseline",
            })
            add_timing(gzip_row, gzip_timing)
            archive_rows.append(gzip_row)

            level_memory: dict[int, dict[str, object]] = {}

            for level in levels:
                level_memory[level] = {
                    "corpus": corpus_name,
                    "seed": args.seed,
                    "zstd_level": level,
                    "gzip_rss_kb": gzip_row["max_rss_kb"],
                    "notes": "mesh minus no-summary estimates summary-builder RSS delta",
                }
                for summary_mode, mode in [("mesh-bigram", "zlg-mesh"), ("none", "zlg-no-summary")]:
                    zlg_path = tmp / f"{corpus_name}-{mode}-l{level}.zlg"
                    stats_path = tmp / f"{corpus_name}-{mode}-l{level}.stats.json"

                    def zlg_cmd(
                        level=level,
                        summary_mode=summary_mode,
                        zlg_path=zlg_path,
                        stats_path=stats_path,
                        corpus=corpus,
                    ):
                        zlg_path.unlink(missing_ok=True)
                        stats_path.unlink(missing_ok=True)
                        cmd = [
                            str(binary),
                            "compress",
                            "--chunk-policy",
                            "fixed-lines8192",
                            "--summary-mode",
                            summary_mode,
                            "--build-profile",
                            "combined-bitset-seen",
                            "--build-stats-json",
                            str(stats_path),
                            "--level",
                            str(level),
                            "--output",
                            str(zlg_path),
                            str(corpus),
                        ]
                        return (cmd, None)

                    timing = base.run_repeated(zlg_cmd, args.repeats, tmp)
                    stats = json.loads(stats_path.read_text(encoding="utf-8"))
                    totals, chunks = parse_zlg_chunks(zlg_path)

                    row = empty_archive_row(meta)
                    row.update({
                        "tool": "zlg",
                        "mode": mode,
                        "zstd_level": level,
                        "build_profile": "combined-bitset-seen",
                        "summary_mode": summary_mode,
                        "notes": "locked" if mode == "zlg-mesh" else "diagnostic-no-summary",
                    })
                    add_zlg_fields(row, totals, int(meta["corpus_bytes"]), gzip_size)
                    add_timing(row, timing)
                    add_build_stats(row, stats)
                    archive_rows.append(row)

                    if mode == "zlg-mesh":
                        level_memory[level].update({
                            "zlg_mesh_rss_kb": row["max_rss_kb"],
                            "mesh_scratch_bytes": row["build_scratch_bytes"],
                            "mesh_bitset_scratch_bytes": row["build_bitset_scratch_bytes"],
                            "mesh_summary_bytes": totals["zlg_summary_bytes"],
                            "mesh_payload_bytes": totals["zlg_compressed_payload_bytes"],
                        })
                    else:
                        level_memory[level].update({
                            "zlg_no_summary_rss_kb": row["max_rss_kb"],
                            "no_summary_payload_bytes": totals["zlg_compressed_payload_bytes"],
                        })

                    for chunk in chunks:
                        chunk_row = {field: "" for field in CHUNK_FIELDS}
                        chunk_row.update({
                            "corpus": corpus_name,
                            "seed": args.seed,
                            "mode": mode,
                            "zstd_level": level,
                            "build_profile": "combined-bitset-seen",
                            "summary_mode": summary_mode,
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

                mem = level_memory[level]
                mesh_rss = int(mem.get("zlg_mesh_rss_kb", 0) or 0)
                no_sum_rss = int(mem.get("zlg_no_summary_rss_kb", 0) or 0)
                gzip_rss = int(mem.get("gzip_rss_kb", 0) or 0)
                mesh_payload = int(mem.get("mesh_payload_bytes", 0) or 0)
                no_summary_payload = int(mem.get("no_summary_payload_bytes", 0) or 0)
                mem["mesh_minus_no_summary_rss_kb"] = mesh_rss - no_sum_rss
                mem["mesh_minus_gzip_rss_kb"] = mesh_rss - gzip_rss
                mem["no_summary_minus_gzip_rss_kb"] = no_sum_rss - gzip_rss
                mem["payload_delta_mesh_vs_no_summary_bytes"] = mesh_payload - no_summary_payload
                memory_rows.append({field: mem.get(field, "") for field in MEMORY_FIELDS})

    return archive_rows, chunk_rows, memory_rows


def validate_rows(
    archive_rows: list[dict[str, object]],
    chunk_rows: list[dict[str, object]],
    memory_rows: list[dict[str, object]],
) -> None:
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
        for key in ["summary_bytes", "compressed_payload_bytes", "payload_ratio"]:
            if row.get(key) in ("", None):
                raise SystemExit(f"missing {key} for chunk row {row}")
    if not memory_rows:
        raise SystemExit("no memory rows generated")
    for row in memory_rows:
        for key in ["zlg_mesh_rss_kb", "zlg_no_summary_rss_kb", "mesh_minus_no_summary_rss_kb"]:
            if row.get(key) in ("", None):
                raise SystemExit(f"missing {key} for memory row {row}")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def by_corpus_level(rows: list[dict[str, object]], mode: str) -> dict[tuple[str, int], dict[str, object]]:
    out: dict[tuple[str, int], dict[str, object]] = {}
    for row in rows:
        if row.get("mode") == mode:
            out[(str(row["corpus"]), int(row["zstd_level"]))] = row
    return out


def write_markdown(
    path: Path,
    archive_rows: list[dict[str, object]],
    memory_rows: list[dict[str, object]],
) -> None:
    mesh_rows = [row for row in archive_rows if row.get("mode") == "zlg-mesh"]
    gzip_rows = {str(row["corpus"]): row for row in archive_rows if row.get("mode") == "gzip-6"}
    mesh_by = by_corpus_level(archive_rows, "zlg-mesh")
    no_summary_by = by_corpus_level(archive_rows, "zlg-no-summary")
    corpora = sorted(gzip_rows)
    levels = sorted({int(row["zstd_level"]) for row in mesh_rows})

    doc = [
        "# Phase 1i Zstd Level and Memory Diagnosis",
        "",
        "This is a diagnostic confirmation pass. It keeps the locked zlg stack fixed and varies only zstd level for the locked builder. It also runs a no-summary diagnostic path to estimate how much RSS belongs to chunking/zstd/writer behavior versus mesh-summary construction.",
        "",
        "## Locked stack",
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
        "## Zstd level comparison for locked mesh profile",
        "",
        "| corpus | gzip_bytes | level | zlg_bytes | delta_vs_gzip | payload_bytes | summary_bytes | wall_s | cpu_s | rss_kb |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for corpus in corpora:
        gzip_size = gzip_rows[corpus]["output_bytes"]
        for level in levels:
            row = mesh_by[(corpus, level)]
            doc.append(
                f"| {corpus} | {gzip_size} | {level} | {row['output_bytes']} | "
                f"{row['delta_vs_gzip_bytes']} | {row['zlg_compressed_payload_bytes']} | "
                f"{row['zlg_summary_bytes']} | {row['wall_seconds']} | "
                f"{row['total_cpu_seconds']} | {row['max_rss_kb']} |"
            )

    doc.extend([
        "",
        "## Payload-only diagnostic versus gzip",
        "",
        "| corpus | level | payload_delta_vs_gzip | total_delta_vs_gzip | summary_pct | payload_pct |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for corpus in corpora:
        for level in levels:
            row = mesh_by[(corpus, level)]
            doc.append(
                f"| {corpus} | {level} | {row['zlg_payload_delta_vs_gzip_bytes']} | "
                f"{row['delta_vs_gzip_bytes']} | {row['summary_pct_of_zlg']} | {row['payload_pct_of_zlg']} |"
            )

    doc.extend([
        "",
        "## Memory isolation: mesh profile versus no-summary diagnostic",
        "",
        "| corpus | level | gzip_rss | mesh_rss | no_summary_rss | mesh_minus_no_summary | mesh_minus_gzip | no_summary_minus_gzip | mesh_scratch | bitset_scratch |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in memory_rows:
        doc.append(
            f"| {row['corpus']} | {row['zstd_level']} | {row['gzip_rss_kb']} | "
            f"{row['zlg_mesh_rss_kb']} | {row['zlg_no_summary_rss_kb']} | "
            f"{row['mesh_minus_no_summary_rss_kb']} | {row['mesh_minus_gzip_rss_kb']} | "
            f"{row['no_summary_minus_gzip_rss_kb']} | {row['mesh_scratch_bytes']} | "
            f"{row['mesh_bitset_scratch_bytes']} |"
        )

    doc.extend([
        "",
        "## No-summary diagnostic size check",
        "",
        "These rows are diagnostic only. They show the size and RSS of zlg chunking plus zstd payloads without mesh summaries. They are not production candidates.",
        "",
        "| corpus | level | no_summary_bytes | no_summary_payload | mesh_payload | payload_delta_mesh_vs_no_summary | no_summary_rss | mesh_rss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for corpus in corpora:
        for level in levels:
            no_sum = no_summary_by[(corpus, level)]
            mesh = mesh_by[(corpus, level)]
            delta = int(mesh["zlg_compressed_payload_bytes"]) - int(no_sum["zlg_compressed_payload_bytes"])
            doc.append(
                f"| {corpus} | {level} | {no_sum['output_bytes']} | "
                f"{no_sum['zlg_compressed_payload_bytes']} | {mesh['zlg_compressed_payload_bytes']} | "
                f"{delta} | {no_sum['max_rss_kb']} | {mesh['max_rss_kb']} |"
            )

    doc.extend([
        "",
        "## Diagnostic questions this run is intended to answer",
        "",
        "1. Do zstd levels 4, 5, or 6 close the payload-size gap against gzip -6 for realistic_mixed_log and short_line_log?",
        "2. Does the locked mesh profile remain faster than gzip -6 as zstd level increases?",
        "3. How much RSS appears to come from zlg chunking/zstd/writer behavior before mesh-summary overhead is added?",
        "4. How much RSS does mesh-summary construction add over the no-summary diagnostic path?",
        "",
        "## Constraints",
        "",
        "- This run must not change the locked stack or promote new candidates.",
        "- No-summary rows are diagnostic only.",
        "- No on-disk format change is introduced.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", default="target/release/zlg")
    parser.add_argument("--lines", type=int, default=80000)
    parser.add_argument("--seed", type=int, default=4242)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--levels", default=LEVELS_DEFAULT)
    parser.add_argument("--corpora", default=CORPUS_DEFAULT)
    parser.add_argument("--archive-csv", default="validation_results/phase1i_level_memory_archive.csv")
    parser.add_argument("--chunk-csv", default="validation_results/phase1i_level_memory_chunks.csv")
    parser.add_argument("--memory-csv", default="validation_results/phase1i_level_memory_memory.csv")
    parser.add_argument("--output", default="validation_results/phase1i_level_memory.md")
    args = parser.parse_args()

    archive_rows, chunk_rows, memory_rows = run_probe(args)
    validate_rows(archive_rows, chunk_rows, memory_rows)
    write_csv(Path(args.archive_csv), ARCHIVE_FIELDS, archive_rows)
    write_csv(Path(args.chunk_csv), CHUNK_FIELDS, chunk_rows)
    write_csv(Path(args.memory_csv), MEMORY_FIELDS, memory_rows)
    write_markdown(Path(args.output), archive_rows, memory_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
