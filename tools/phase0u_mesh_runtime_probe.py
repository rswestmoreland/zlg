#!/usr/bin/env python3
"""Phase 0u sorted bigram mesh runtime/storage probe.

This probe validates the focused winning strategy: a compact sorted bigram-edge
summary over small search blocks. It compares mesh-bigram against bitmap,
none, gzip, and zgrep for a deterministic needle corpus.

Generated corpora and compressed files live in a temporary directory. Only
compact CSV/Markdown reports are preserved.
"""

from __future__ import annotations

import argparse
import csv
import json
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


POLICIES = ["fixed-lines1024", "fixed-lines2048", "fixed-lines64k"]
SUMMARY_MODES = ["mesh-bigram", "bitmap", "none"]


def run_capture(cmd: list[str], *, stdout_path: Path | None = None) -> tuple[int, str, str, float]:
    start = time.perf_counter()
    if stdout_path is None:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    else:
        with stdout_path.open("wb") as handle:
            proc = subprocess.run(cmd, stdout=handle, stderr=subprocess.PIPE)
        # stderr is bytes in this path.
        err = proc.stderr.decode("utf-8", "replace") if isinstance(proc.stderr, bytes) else str(proc.stderr)
        elapsed = time.perf_counter() - start
        return proc.returncode, "", err, elapsed
    elapsed = time.perf_counter() - start
    return proc.returncode, proc.stdout, proc.stderr, elapsed


def require_ok(cmd: list[str], *, stdout_path: Path | None = None) -> float:
    rc, out, err, elapsed = run_capture(cmd, stdout_path=stdout_path)
    if rc != 0:
        raise SystemExit(f"command failed {rc}: {' '.join(cmd)}\nSTDOUT:\n{out}\nSTDERR:\n{err}")
    return elapsed


def timed_median(cmd_factory, repeats: int) -> float:
    values = []
    for _ in range(repeats):
        cmd, stdout_path = cmd_factory()
        values.append(require_ok(cmd, stdout_path=stdout_path))
    return median(values)


def read_stats(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def gzip_available() -> bool:
    return shutil.which("gzip") is not None


def zgrep_available() -> bool:
    return shutil.which("zgrep") is not None


def probe(args: argparse.Namespace) -> tuple[list[dict[str, object]], dict[str, object]]:
    binary = Path(args.binary)
    if not binary.exists():
        raise SystemExit(f"binary not found: {binary}")

    rows: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="zlg-phase0u-") as tmp_name:
        tmp = Path(tmp_name)
        corpus = tmp / "needle.log"
        needle_line = make_needle_corpus(corpus, args.lines, args.needle_ratio)
        corpus_bytes = corpus.stat().st_size
        digest = sha256(corpus)

        gzip6_seconds = ""
        gzip6_bytes = ""
        zgrep_seconds = ""
        gzip_path = tmp / "needle.log.gz"
        if gzip_available():
            def gzip_cmd():
                if gzip_path.exists():
                    gzip_path.unlink()
                return (["gzip", "-6", "-c", str(corpus)], gzip_path)
            gzip6_seconds = f"{timed_median(gzip_cmd, args.repeats):.6f}"
            gzip6_bytes = str(gzip_path.stat().st_size)

            if zgrep_available():
                def zgrep_cmd():
                    return (["zgrep", "-F", NEEDLE_IP, str(gzip_path)], None)
                zgrep_seconds = f"{timed_median(zgrep_cmd, args.repeats):.6f}"

        for policy in POLICIES:
            none_size = None
            for mode in SUMMARY_MODES:
                out = tmp / f"{policy}-{mode}.zlg"

                def compress_cmd():
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

                compress_seconds = timed_median(compress_cmd, args.repeats)
                out_bytes = out.stat().st_size
                if mode == "none":
                    none_size = out_bytes

                stats_path = tmp / f"{policy}-{mode}.stats.json"

                def grep_cmd():
                    if stats_path.exists():
                        stats_path.unlink()
                    return ([
                        str(binary),
                        "grep",
                        "--stats-json",
                        str(stats_path),
                        "-F",
                        NEEDLE_IP,
                        str(out),
                    ], None)

                grep_seconds = timed_median(grep_cmd, args.repeats)
                stats = read_stats(stats_path)

                chunks_total = int(stats.get("chunks_total", 0))
                chunks_decoded = int(stats.get("chunks_decoded", 0))
                decoded_bytes = int(stats.get("decoded_bytes", 0))
                decoded_ratio = decoded_bytes / corpus_bytes if corpus_bytes else 0.0
                selected_chunk_ratio = chunks_decoded / chunks_total if chunks_total else 0.0
                overhead_vs_none = ""
                if none_size is not None:
                    overhead_vs_none = str(out_bytes - none_size)

                rows.append({
                    "kind": "zlg",
                    "policy": policy,
                    "summary_mode": mode,
                    "corpus_bytes": corpus_bytes,
                    "output_bytes": out_bytes,
                    "overhead_vs_none_bytes": overhead_vs_none,
                    "compress_seconds": f"{compress_seconds:.6f}",
                    "grep_seconds": f"{grep_seconds:.6f}",
                    "chunks_total": chunks_total,
                    "chunks_skipped": int(stats.get("chunks_skipped", 0)),
                    "candidate_chunks": int(stats.get("candidate_chunks", 0)),
                    "chunks_decoded": chunks_decoded,
                    "decoded_bytes": decoded_bytes,
                    "decoded_ratio": f"{decoded_ratio:.6f}",
                    "selected_chunk_ratio": f"{selected_chunk_ratio:.6f}",
                    "matching_lines": int(stats.get("matching_lines", 0)),
                    "selector_kind": stats.get("selector_kind", ""),
                    "selector_len": stats.get("selector_len", ""),
                    "selector_count": stats.get("selector_count", ""),
                    "gzip6_bytes": gzip6_bytes,
                    "gzip6_seconds": gzip6_seconds,
                    "zgrep_seconds": zgrep_seconds,
                })

        meta = {
            "lines": args.lines,
            "input_bytes": corpus_bytes,
            "sha256": digest,
            "needle_ip": NEEDLE_IP,
            "needle_line": needle_line,
            "needle_ratio": needle_line / args.lines,
            "gzip_available": gzip_available(),
            "zgrep_available": zgrep_available(),
        }
        return rows, meta


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "kind",
        "policy",
        "summary_mode",
        "corpus_bytes",
        "output_bytes",
        "overhead_vs_none_bytes",
        "compress_seconds",
        "grep_seconds",
        "chunks_total",
        "chunks_skipped",
        "candidate_chunks",
        "chunks_decoded",
        "decoded_bytes",
        "decoded_ratio",
        "selected_chunk_ratio",
        "matching_lines",
        "selector_kind",
        "selector_len",
        "selector_count",
        "gzip6_bytes",
        "gzip6_seconds",
        "zgrep_seconds",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, object]], meta: dict[str, object]) -> None:
    sorted_rows = sorted(rows, key=lambda r: (r["policy"], r["summary_mode"]))
    gzip_size = next((row["gzip6_bytes"] for row in rows if row["gzip6_bytes"]), "not_available")
    zgrep_time = next((row["zgrep_seconds"] for row in rows if row["zgrep_seconds"]), "not_available")

    doc = [
        "# zlg Phase 0u sorted bigram mesh runtime probe",
        "",
        "This runtime probe focuses on the current winning strategy only:",
        "compact sorted bigram-edge summaries over small search blocks.",
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
        f"- gzip -6 bytes: {gzip_size}",
        f"- zgrep seconds: {zgrep_time}",
        "",
        "## Runtime/storage table",
        "",
        "| policy | summary | bytes | overhead_vs_none | compress_s | grep_s | chunks | decoded | decoded_ratio | gzip6_bytes | zgrep_s |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted_rows:
        doc.append(
            f"| {row['policy']} | {row['summary_mode']} | {row['output_bytes']} | "
            f"{row['overhead_vs_none_bytes']} | {row['compress_seconds']} | "
            f"{row['grep_seconds']} | {row['chunks_total']} | {row['chunks_decoded']} | "
            f"{row['decoded_ratio']} | {row['gzip6_bytes'] or 'n/a'} | {row['zgrep_seconds'] or 'n/a'} |"
        )

    doc.extend([
        "",
        "## Interpretation guide",
        "",
        "- `mesh-bigram` is the focused experimental winner from Phase 0t-fix.",
        "- `bitmap` is the previous fixed-size per-block summary baseline.",
        "- `none` is compressed zstd chunks with no search summary.",
        "- `overhead_vs_none` is a direct storage-efficiency estimate for the summary mode.",
        "- A successful mesh candidate should stay below gzip -6 size while decoding fewer chunks than none and preferably beating zgrep on the needle query.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", default="target/release/zlg")
    parser.add_argument("--lines", type=int, default=125000)
    parser.add_argument("--needle-ratio", type=float, default=0.80)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", default="validation_results/phase0u_mesh_runtime.md")
    parser.add_argument("--csv", default="validation_results/phase0u_mesh_runtime.csv")
    args = parser.parse_args()

    rows, meta = probe(args)
    write_csv(REPO / args.csv, rows)
    write_markdown(REPO / args.output, rows, meta)
    print(f"wrote {REPO / args.output}")
    print(f"wrote {REPO / args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
