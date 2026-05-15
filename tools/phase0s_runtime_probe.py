#!/usr/bin/env python3
"""Phase 0s path-window runtime probe.

This probe exercises the experimental runtime path-window summary mode against a
needle-in-haystack corpus. It measures whether grep can skip most independently
compressed search blocks before decompression.

Generated corpora and .zlg files stay in a temporary directory.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from phase0q_needle_corpus_probe import NEEDLE_IP, make_needle_corpus, sha256  # noqa: E402


def run(cmd: list[str], cwd: Path, stdout_path: Path | None = None) -> tuple[float, int, int, str]:
    start = time.perf_counter()
    if stdout_path is None:
        result = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out_len = len(result.stdout)
    else:
        with stdout_path.open("wb") as handle:
            result = subprocess.run(cmd, cwd=cwd, stdout=handle, stderr=subprocess.PIPE)
        out_len = stdout_path.stat().st_size
    elapsed = time.perf_counter() - start
    stderr = result.stderr.decode("utf-8", errors="replace")
    return elapsed, result.returncode, out_len, stderr


def run_checked(cmd: list[str], cwd: Path, stdout_path: Path | None = None) -> tuple[float, int, int, str]:
    elapsed, code, out_len, stderr = run(cmd, cwd, stdout_path)
    if code not in (0, 1):
        raise SystemExit(f"command failed {code}: {' '.join(cmd)}\n{stderr}")
    return elapsed, code, out_len, stderr


def gzip_baseline(corpus: Path, tmp: Path) -> tuple[str, str]:
    if shutil.which("gzip") is None:
        return "", ""
    gzip_path = tmp / "needle.log.gz"
    elapsed, _code, _out, _stderr = run_checked(
        ["gzip", "-6", "-c", str(corpus)],
        REPO,
        stdout_path=gzip_path,
    )
    return f"{elapsed:.6f}", str(gzip_path.stat().st_size)


def run_one(binary: Path, corpus: Path, tmp: Path, policy: str, summary_mode: str) -> dict[str, object]:
    zlg_path = tmp / f"needle-{policy}-{summary_mode}.zlg"
    stats_path = tmp / f"needle-{policy}-{summary_mode}.json"
    match_path = tmp / f"needle-{policy}-{summary_mode}.matches"

    compress_elapsed, code, _out, stderr = run_checked(
        [
            str(binary),
            "compress",
            "--chunk-policy",
            policy,
            "--summary-mode",
            summary_mode,
            str(corpus),
            "-o",
            str(zlg_path),
        ],
        REPO,
    )
    if code != 0:
        raise SystemExit(stderr)

    grep_elapsed, grep_code, match_bytes, grep_stderr = run_checked(
        [
            str(binary),
            "grep",
            "--stats-json",
            str(stats_path),
            "-F",
            NEEDLE_IP,
            str(zlg_path),
        ],
        REPO,
        stdout_path=match_path,
    )
    if grep_code != 0:
        raise SystemExit(f"expected needle match for {policy}/{summary_mode}: {grep_stderr}")

    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    if stats.get("matching_lines") != 1:
        raise SystemExit(f"expected one matching line for {policy}/{summary_mode}, got {stats}")

    chunks_total = int(stats.get("chunks_total", 0))
    chunks_decoded = int(stats.get("chunks_decoded", 0))
    decoded_bytes = int(stats.get("decoded_bytes", 0))
    input_bytes = corpus.stat().st_size

    return {
        "policy": policy,
        "summary_mode": summary_mode,
        "zlg_bytes": zlg_path.stat().st_size,
        "compress_seconds": f"{compress_elapsed:.6f}",
        "grep_seconds": f"{grep_elapsed:.6f}",
        "match_output_bytes": match_bytes,
        "chunks_total": chunks_total,
        "chunks_skipped": int(stats.get("chunks_skipped", 0)),
        "candidate_chunks": int(stats.get("candidate_chunks", 0)),
        "chunks_decoded": chunks_decoded,
        "decoded_bytes": decoded_bytes,
        "decoded_ratio": f"{decoded_bytes / input_bytes:.6f}",
        "selected_chunk_ratio": f"{chunks_decoded / chunks_total if chunks_total else 0.0:.6f}",
        "matching_lines": int(stats.get("matching_lines", 0)),
        "selector_kind": stats.get("selector_kind", ""),
        "selector_len": int(stats.get("selector_len", 0)),
        "selector_count": int(stats.get("selector_count", 0)),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "policy",
        "summary_mode",
        "zlg_bytes",
        "compress_seconds",
        "grep_seconds",
        "match_output_bytes",
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
        "gzip6_seconds",
        "gzip6_bytes",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, object]], meta: dict[str, object]) -> None:
    ordered = sorted(rows, key=lambda row: (float(row["decoded_ratio"]), float(row["grep_seconds"])))
    doc = [
        "# zlg Phase 0s path-window runtime probe",
        "",
        "This probe exercises an experimental runtime summary mode:",
        "",
        "```text",
        "zlg compress --summary-mode path-window --chunk-policy fixed-lines512",
        "```",
        "",
        "The generated corpus and .zlg files are temporary. Only this compact report",
        "and CSV should be committed.",
        "",
        "## Corpus",
        "",
        f"- Lines: {meta['lines']}",
        f"- Input bytes: {meta['input_bytes']}",
        f"- Input sha256: {meta['sha256']}",
        f"- Needle IP: {meta['needle_ip']}",
        f"- Needle line: {meta['needle_line']}",
        f"- Needle line ratio: {float(meta['needle_line_ratio']):.3f}",
        "",
        "## Results",
        "",
        "| policy | summary_mode | zlg_bytes | compress_s | grep_s | chunks_total | chunks_decoded | decoded_ratio | gzip6_bytes |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in ordered:
        doc.append(
            f"| {row['policy']} | {row['summary_mode']} | {row['zlg_bytes']} | "
            f"{row['compress_seconds']} | {row['grep_seconds']} | {row['chunks_total']} | "
            f"{row['chunks_decoded']} | {row['decoded_ratio']} | {row.get('gzip6_bytes', '')} |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", default="target/release/zlg")
    parser.add_argument("--lines", type=int, default=125000)
    parser.add_argument("--needle-ratio", type=float, default=0.80)
    parser.add_argument("--output", default="validation_results/phase0s_path_window_runtime.md")
    parser.add_argument("--csv", default="validation_results/phase0s_path_window_runtime.csv")
    args = parser.parse_args()

    binary = (REPO / args.binary).resolve()
    if not binary.exists():
        raise SystemExit(f"binary not found: {binary}")

    rows: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="zlg-phase0s-") as tmp_name:
        tmp = Path(tmp_name)
        corpus = tmp / "needle.log"
        needle_line = make_needle_corpus(corpus, args.lines, args.needle_ratio)
        digest = sha256(corpus)
        gzip_seconds, gzip_bytes = gzip_baseline(corpus, tmp)

        meta = {
            "lines": args.lines,
            "input_bytes": corpus.stat().st_size,
            "sha256": digest,
            "needle_ip": NEEDLE_IP,
            "needle_line": needle_line,
            "needle_line_ratio": needle_line / args.lines,
        }

        for policy in ["fixed-lines512", "fixed-lines1024"]:
            for summary_mode in ["path-window", "bitmap", "none"]:
                row = run_one(binary, corpus, tmp, policy, summary_mode)
                row["gzip6_seconds"] = gzip_seconds
                row["gzip6_bytes"] = gzip_bytes
                rows.append(row)

    write_csv(REPO / args.csv, rows)
    write_markdown(REPO / args.output, rows, meta)
    print(f"wrote {REPO / args.output}")
    print(f"wrote {REPO / args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
