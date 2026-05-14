#!/usr/bin/env python3
"""Phase 0h/0i benchmark-prep harness.

This is still not the final zlg performance proof. It is intended to produce
repeatable pre-bench evidence before a larger corpus and final matrix are run.

Outputs:
  validation_results/*.csv
  validation_results/*_summary.md
  validation_results/*_env.txt

The harness keeps generated corpora and compressed outputs in a temporary
directory by default. Use --keep-temp only for debugging.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import statistics
import struct
import subprocess
import sys
import tempfile
import time
from typing import Iterable


POLICIES_QUICK = [
    "fixed-lines64k",
    "progressive-lines",
    "hybrid-progressive-cap8m",
    "hybrid-progressive-cap16m",
]

POLICIES_PREBENCH = [
    "fixed-lines64k",
    "progressive-lines",
    "hybrid-progressive-cap8m",
    "hybrid-progressive-cap16m",
    "hybrid-fixed64k-cap8m",
    "hybrid-fixed64k-cap16m",
]

POLICIES_FULL = [
    "fixed-lines64k",
    "progressive-lines",
    "byte1m",
    "byte4m",
    "byte8m",
    "hybrid-progressive-cap4m",
    "hybrid-progressive-cap8m",
    "hybrid-progressive-cap16m",
    "hybrid-progressive-cap32m",
    "hybrid-fixed64k-cap8m",
    "hybrid-fixed64k-cap16m",
    "hybrid-fixed64k-cap32m",
]

PATTERNS = [
    ("literal_failed_password", "regex", "failed password"),
    ("alternation_error_failed_denied", "regex", "error|failed|denied"),
    ("quoted_key", "regex", r"key=\"[^\"]+\""),
    ("branch_suffix", "regex", r"(?:foo|bar)[0-9]"),
    ("src_ip", "regex", r"src_ip=[0-9.]+"),
    ("lookbehind_key", "fancy", r"(?<=key=\")[^\"]+"),
    ("no_match_literal", "fixed", "no_such_token_zzzz"),
]

FIELDNAMES = [
    "mode",
    "repeat",
    "kind",
    "name",
    "policy",
    "pattern_name",
    "engine",
    "command",
    "wall_seconds",
    "first_output_seconds",
    "exit_code",
    "input_bytes",
    "output_bytes",
    "chunk_count",
    "zlg_compressed_payload_bytes",
    "zlg_summary_bytes",
    "zlg_overhead_bytes",
    "chunks_total",
    "chunks_skipped",
    "candidate_chunks",
    "chunks_decoded",
    "decoded_bytes",
    "matching_lines",
    "notes",
]


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
    if result.returncode not in (0, 1):
        sys.stderr.write(f"command failed: {' '.join(cmd)}\n")
        sys.stderr.write(stderr)
        raise SystemExit(result.returncode)
    return elapsed, result.returncode, out_len, stderr



def run_with_first_output(cmd: list[str], cwd: Path) -> tuple[float, int, int, str, str]:
    """Run a command and measure time to first stdout byte.

    The first-output value is empty when the command writes no stdout. This is
    useful for grep no-match cases where exit 1 is still a valid result.
    """
    start = time.perf_counter()
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdout is not None
    assert proc.stderr is not None

    first_output = ""
    first = proc.stdout.read(1)
    if first:
        first_output = f"{time.perf_counter() - start:.6f}"
        rest = proc.stdout.read()
        out_len = 1 + len(rest)
    else:
        out_len = 0

    stderr_bytes = proc.stderr.read()
    code = proc.wait()
    elapsed = time.perf_counter() - start
    stderr = stderr_bytes.decode("utf-8", errors="replace")

    if code not in (0, 1):
        sys.stderr.write(f"command failed: {' '.join(cmd)}\n")
        sys.stderr.write(stderr)
        raise SystemExit(code)

    return elapsed, code, out_len, stderr, first_output


def read_json_file(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def inspect_zlg(path: Path) -> dict[str, int]:
    """Read provisional ZLG1P0 chunk metadata without decoding payloads."""
    size = path.stat().st_size
    chunk_count = 0
    compressed_payload = 0
    summary_bytes = 0
    uncompressed_bytes = 0
    line_count = 0

    with path.open("rb") as handle:
        magic = handle.read(8)
        if magic != b"ZLG1P0\0\0":
            return {}
        handle.seek(32)

        while True:
            record_magic = handle.read(4)
            if not record_magic:
                break
            if record_magic == b"ZDR1":
                break
            if record_magic != b"ZCH1":
                raise SystemExit(f"unexpected zlg record magic in {path}: {record_magic!r}")

            header = handle.read(60)
            if len(header) != 60:
                raise SystemExit(f"short zlg chunk header in {path}")
            header_len, _flags = struct.unpack_from("<HH", header, 0)
            if header_len != 64:
                raise SystemExit(f"unexpected zlg chunk header length {header_len} in {path}")
            this_line_count = struct.unpack_from("<Q", header, 20)[0]
            this_uncompressed = struct.unpack_from("<Q", header, 28)[0]
            this_compressed = struct.unpack_from("<Q", header, 36)[0]
            this_summary = struct.unpack_from("<I", header, 44)[0]

            chunk_count += 1
            compressed_payload += this_compressed
            summary_bytes += this_summary
            uncompressed_bytes += this_uncompressed
            line_count += this_line_count
            handle.seek(this_summary + this_compressed, os.SEEK_CUR)

    return {
        "chunk_count": chunk_count,
        "zlg_compressed_payload_bytes": compressed_payload,
        "zlg_summary_bytes": summary_bytes,
        "zlg_overhead_bytes": size - compressed_payload,
        "zlg_uncompressed_bytes": uncompressed_bytes,
        "zlg_line_count": line_count,
    }


def tool_version(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        return "not_found"
    attempts = [
        [path, "--version"],
        [path, "-V"],
        [path, "-v"],
    ]
    for cmd in attempts:
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=5)
        except Exception:
            continue
        output = result.stdout.strip().splitlines()
        if output:
            return f"{path} :: {output[0]}"
    return f"{path} :: version_unknown"


def make_corpus(path: Path, lines: int) -> None:
    """Create deterministic mixed log-like data.

    The corpus intentionally includes:
      - rare literals
      - common literals
      - structured key/value fields
      - branch regex candidates
      - IP-like fields
      - mostly repetitive normal lines for compression testing
    """
    with path.open("w", encoding="utf-8") as handle:
        for i in range(lines):
            if i % 97 == 0:
                handle.write(f"error key=\"abc{i}\" src_ip=192.0.2.{i % 255} foo{i % 10} component=auth\n")
            elif i % 131 == 0:
                handle.write(f"failed password user=test{i} src_ip=198.51.100.{i % 255} component=sshd\n")
            elif i % 211 == 0:
                handle.write(f"denied action=drop bar{i % 10} key=\"deny{i}\" src_ip=10.0.{i % 255}.{(i * 7) % 255}\n")
            elif i % 503 == 0:
                handle.write(f"warning retry key=\"retry{i}\" src_ip=172.16.{i % 255}.{(i * 3) % 255}\n")
            else:
                handle.write(f"info event_id={i} src_ip=203.0.113.{i % 255} msg=normal component=app shard={i % 16}\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_row(writer: csv.DictWriter[str], **kwargs: object) -> None:
    row = {name: "" for name in FIELDNAMES}
    row.update({key: str(value) for key, value in kwargs.items()})
    writer.writerow(row)


def summarize(csv_path: Path, summary_path: Path, mode: str, corpus: Path, input_bytes: int, lines: int) -> None:
    rows = list(csv.DictReader(csv_path.open("r", encoding="utf-8")))
    grouped: dict[tuple[str, str, str, str], list[float]] = {}
    sizes: dict[tuple[str, str, str, str], str] = {}

    for row in rows:
        key = (
            row["kind"],
            row["name"],
            row["policy"],
            row["pattern_name"],
        )
        try:
            grouped.setdefault(key, []).append(float(row["wall_seconds"]))
        except ValueError:
            continue
        sizes[key] = row.get("output_bytes", "")

    lines_out = [
        f"# zlg Phase 0h/0i {mode} benchmark summary",
        "",
        "This is pre-bench evidence only, not the final performance proof.",
        "",
        "## Corpus",
        "",
        f"- Lines: {lines}",
        f"- Input bytes: {input_bytes}",
        f"- Input sha256: {sha256(corpus)}",
        "",
        "## Median timings",
        "",
        "| kind | name | policy | pattern | repeats | median_s | min_s | max_s | first_output_s | output_bytes |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]

    for key in sorted(grouped):
        values = grouped[key]
        kind, name, policy, pattern_name = key
        first_values = [
            float(row["first_output_seconds"])
            for row in rows
            if (row["kind"], row["name"], row["policy"], row["pattern_name"]) == key
            and row.get("first_output_seconds")
        ]
        first_output = f"{statistics.median(first_values):.6f}" if first_values else ""
        lines_out.append(
            f"| {kind} | {name} | {policy} | {pattern_name} | {len(values)} | "
            f"{statistics.median(values):.6f} | {min(values):.6f} | {max(values):.6f} | "
            f"{first_output} | {sizes.get(key, '')} |"
        )

    zlg_grep_rows = [row for row in rows if row["kind"] == "grep" and row["name"] == "zlg_grep"]
    if zlg_grep_rows:
        lines_out.extend([
            "",
            "## zlg grep counter medians",
            "",
            "| policy | pattern | repeats | chunks_total | chunks_skipped | chunks_decoded | decoded_bytes | matching_lines |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ])
        counter_groups: dict[tuple[str, str], list[dict[str, str]]] = {}
        for row in zlg_grep_rows:
            counter_groups.setdefault((row["policy"], row["pattern_name"]), []).append(row)
        for key in sorted(counter_groups):
            group = counter_groups[key]
            def med(field: str) -> str:
                values = [float(row[field]) for row in group if row.get(field)]
                return f"{statistics.median(values):.0f}" if values else ""
            policy, pattern_name = key
            lines_out.append(
                f"| {policy} | {pattern_name} | {len(group)} | {med('chunks_total')} | "
                f"{med('chunks_skipped')} | {med('chunks_decoded')} | {med('decoded_bytes')} | {med('matching_lines')} |"
            )

    summary_path.write_text("\n".join(lines_out) + "\n", encoding="utf-8")


def write_env_report(path: Path, mode: str, lines: int, repeats: int) -> None:
    repo = Path(__file__).resolve().parents[1]
    commands = [
        ("rustc", ["rustc", "--version"]),
        ("cargo", ["cargo", "--version"]),
    ]

    out = [
        "# zlg Phase 0h/0i environment report",
        "",
        f"Mode: {mode}",
        f"Lines: {lines}",
        f"Repeats: {repeats}",
        f"Platform: {platform.platform()}",
        f"Python: {sys.version.split()[0]}",
        f"Machine: {platform.machine()}",
        f"Processor: {platform.processor()}",
        f"Repo: {repo}",
        "",
        "## Rust",
        "",
    ]

    for name, cmd in commands:
        try:
            result = subprocess.run(cmd, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10)
            out.append(f"{name}: {result.stdout.strip()}")
        except Exception as exc:
            out.append(f"{name}: unavailable ({exc})")

    out.extend([
        "",
        "## External tools",
        "",
    ])

    for tool in ["gzip", "zgrep", "grep", "rg", "zstd", "zstdcat", "time"]:
        out.append(f"{tool}: {tool_version(tool)}")

    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def select_policies(mode: str) -> list[str]:
    if mode == "quick":
        return POLICIES_QUICK
    if mode == "prebench":
        return POLICIES_PREBENCH
    return POLICIES_FULL


def default_lines(mode: str) -> int:
    if mode == "quick":
        return 20_000
    if mode == "prebench":
        return 125_000
    return 1_000_000


def default_repeats(mode: str) -> int:
    if mode == "quick":
        return 1
    if mode == "prebench":
        return 3
    return 5


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["quick", "prebench", "full"], default="quick")
    parser.add_argument("--quick", action="store_true", help="compatibility alias for --mode quick")
    parser.add_argument("--lines", type=int, default=None)
    parser.add_argument("--repeats", type=int, default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--summary", default=None)
    parser.add_argument("--env-report", default=None)
    parser.add_argument("--keep-temp", action="store_true")
    args = parser.parse_args()

    mode = "quick" if args.quick else args.mode
    repo = Path(__file__).resolve().parents[1]
    lines = args.lines if args.lines is not None else default_lines(mode)
    repeats = args.repeats if args.repeats is not None else default_repeats(mode)

    output = repo / (args.output or f"validation_results/phase0h_{mode}_bench.csv")
    summary = repo / (args.summary or f"validation_results/phase0h_{mode}_bench_summary.md")
    env_report = repo / (args.env_report or f"validation_results/phase0h_{mode}_env.txt")

    output.parent.mkdir(parents=True, exist_ok=True)
    summary.parent.mkdir(parents=True, exist_ok=True)
    env_report.parent.mkdir(parents=True, exist_ok=True)

    policies = select_policies(mode)
    gzip = shutil.which("gzip")
    zgrep = shutil.which("zgrep")
    grep = shutil.which("grep")
    rg = shutil.which("rg")
    zstd = shutil.which("zstd")
    zstdcat = shutil.which("zstdcat")

    write_env_report(env_report, mode, lines, repeats)

    subprocess.run(["cargo", "build", "--release"], cwd=repo, check=True)
    zlg = repo / "target" / "release" / "zlg"

    temp_manager = tempfile.TemporaryDirectory(prefix=f"zlg-phase0h-{mode}-")
    tmp_path = Path(temp_manager.name)

    try:
        corpus = tmp_path / "corpus.txt"
        make_corpus(corpus, lines)
        input_bytes = corpus.stat().st_size

        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
            writer.writeheader()

            gz6 = tmp_path / "corpus.txt.gz"
            gz9 = tmp_path / "corpus.txt.gzip9.gz"
            zst = tmp_path / "corpus.txt.zst"

            for repeat in range(1, repeats + 1):
                if gzip:
                    elapsed, code, _, _ = run([gzip, "-c", "-6", str(corpus)], repo, gz6)
                    write_row(
                        writer,
                        mode=mode,
                        repeat=repeat,
                        kind="compress",
                        name="gzip_6",
                        command="gzip -c -6",
                        wall_seconds=f"{elapsed:.6f}",
                        exit_code=code,
                        input_bytes=input_bytes,
                        output_bytes=gz6.stat().st_size,
                    )

                    elapsed, code, _, _ = run([gzip, "-c", "-9", str(corpus)], repo, gz9)
                    write_row(
                        writer,
                        mode=mode,
                        repeat=repeat,
                        kind="compress",
                        name="gzip_9",
                        command="gzip -c -9",
                        wall_seconds=f"{elapsed:.6f}",
                        exit_code=code,
                        input_bytes=input_bytes,
                        output_bytes=gz9.stat().st_size,
                    )

                if zstd:
                    elapsed, code, _, _ = run([zstd, "-q", "-c", "-3", str(corpus)], repo, zst)
                    write_row(
                        writer,
                        mode=mode,
                        repeat=repeat,
                        kind="compress",
                        name="zstd_3",
                        command="zstd -q -c -3",
                        wall_seconds=f"{elapsed:.6f}",
                        exit_code=code,
                        input_bytes=input_bytes,
                        output_bytes=zst.stat().st_size,
                    )

                zlg_outputs: list[tuple[str, Path]] = []
                for policy in policies:
                    out = tmp_path / f"corpus.{policy}.zlg"
                    elapsed, code, _, _ = run(
                        [str(zlg), "compress", str(corpus), "--chunk-policy", policy, "-o", str(out)],
                        repo,
                    )
                    zlg_outputs.append((policy, out))
                    zlg_meta = inspect_zlg(out)
                    write_row(
                        writer,
                        mode=mode,
                        repeat=repeat,
                        kind="compress",
                        name="zlg",
                        policy=policy,
                        command=f"zlg compress --chunk-policy {policy}",
                        wall_seconds=f"{elapsed:.6f}",
                        exit_code=code,
                        input_bytes=input_bytes,
                        output_bytes=out.stat().st_size,
                        chunk_count=zlg_meta.get("chunk_count", ""),
                        zlg_compressed_payload_bytes=zlg_meta.get("zlg_compressed_payload_bytes", ""),
                        zlg_summary_bytes=zlg_meta.get("zlg_summary_bytes", ""),
                        zlg_overhead_bytes=zlg_meta.get("zlg_overhead_bytes", ""),
                    )

                for policy, zlg_file in zlg_outputs:
                    cat_out = tmp_path / f"cat.{policy}.{repeat}.txt"
                    elapsed, code, out_len, _ = run([str(zlg), "cat", str(zlg_file)], repo, cat_out)
                    if sha256(cat_out) != sha256(corpus):
                        raise SystemExit(f"cat output mismatch for policy {policy}")
                    write_row(
                        writer,
                        mode=mode,
                        repeat=repeat,
                        kind="cat",
                        name="zlg_cat",
                        policy=policy,
                        command="zlg cat",
                        wall_seconds=f"{elapsed:.6f}",
                        exit_code=code,
                        input_bytes=zlg_file.stat().st_size,
                        output_bytes=out_len,
                    )

                    for pattern_name, engine, pattern in PATTERNS:
                        stats_path = tmp_path / f"grep.{policy}.{repeat}.{pattern_name}.json"
                        cmd = [str(zlg), "grep", "--stats-json", str(stats_path)]
                        if engine == "fixed":
                            cmd.append("-F")
                        elif engine == "fancy":
                            cmd.append("-P")
                        cmd.extend([pattern, str(zlg_file)])
                        elapsed, code, out_len, _, first_output = run_with_first_output(cmd, repo)
                        stats = read_json_file(stats_path)
                        write_row(
                            writer,
                            mode=mode,
                            repeat=repeat,
                            kind="grep",
                            name="zlg_grep",
                            policy=policy,
                            pattern_name=pattern_name,
                            engine=engine,
                            command="zlg grep <opts> <pattern> <zlg>",
                            wall_seconds=f"{elapsed:.6f}",
                            first_output_seconds=first_output,
                            exit_code=code,
                            input_bytes=zlg_file.stat().st_size,
                            output_bytes=out_len,
                            chunks_total=stats.get("chunks_total", ""),
                            chunks_skipped=stats.get("chunks_skipped", ""),
                            candidate_chunks=stats.get("candidate_chunks", ""),
                            chunks_decoded=stats.get("chunks_decoded", ""),
                            decoded_bytes=stats.get("decoded_bytes", ""),
                            matching_lines=stats.get("matching_lines", ""),
                        )

                if grep:
                    for pattern_name, engine, pattern in PATTERNS:
                        if engine == "fancy":
                            continue
                        cmd = [grep]
                        if engine == "fixed":
                            cmd.append("-F")
                        else:
                            cmd.append("-E")
                        cmd.extend([pattern, str(corpus)])
                        elapsed, code, out_len, _, first_output = run_with_first_output(cmd, repo)
                        write_row(
                            writer,
                            mode=mode,
                            repeat=repeat,
                            kind="grep_baseline",
                            name="grep_plain",
                            pattern_name=pattern_name,
                            engine=engine,
                            command=" ".join(cmd[:-1]) + " <plain>",
                            wall_seconds=f"{elapsed:.6f}",
                            first_output_seconds=first_output,
                            exit_code=code,
                            input_bytes=input_bytes,
                            output_bytes=out_len,
                        )

                if rg:
                    for pattern_name, engine, pattern in PATTERNS:
                        if engine == "fancy":
                            continue
                        cmd = [rg]
                        if engine == "fixed":
                            cmd.append("-F")
                        cmd.extend([pattern, str(corpus)])
                        elapsed, code, out_len, _, first_output = run_with_first_output(cmd, repo)
                        write_row(
                            writer,
                            mode=mode,
                            repeat=repeat,
                            kind="grep_baseline",
                            name="rg_plain",
                            pattern_name=pattern_name,
                            engine=engine,
                            command=" ".join(cmd[:-1]) + " <plain>",
                            wall_seconds=f"{elapsed:.6f}",
                            first_output_seconds=first_output,
                            exit_code=code,
                            input_bytes=input_bytes,
                            output_bytes=out_len,
                        )

                if zgrep and gzip:
                    if not gz6.exists():
                        run([gzip, "-c", "-6", str(corpus)], repo, gz6)
                    for pattern_name, engine, pattern in PATTERNS:
                        if engine == "fancy":
                            continue
                        cmd = [zgrep]
                        if engine == "fixed":
                            cmd.append("-F")
                        else:
                            cmd.append("-E")
                        cmd.extend([pattern, str(gz6)])
                        elapsed, code, out_len, _, first_output = run_with_first_output(cmd, repo)
                        write_row(
                            writer,
                            mode=mode,
                            repeat=repeat,
                            kind="grep_baseline",
                            name="zgrep_gzip6",
                            pattern_name=pattern_name,
                            engine=engine,
                            command=" ".join(cmd[:-1]) + " <gz>",
                            wall_seconds=f"{elapsed:.6f}",
                            first_output_seconds=first_output,
                            exit_code=code,
                            input_bytes=gz6.stat().st_size,
                            output_bytes=out_len,
                        )

                if zstdcat and zstd and grep:
                    if not zst.exists():
                        run([zstd, "-q", "-c", "-3", str(corpus)], repo, zst)
                    for pattern_name, engine, pattern in PATTERNS:
                        if engine == "fancy":
                            continue
                        # Shell pipeline is acceptable here because this is a benchmark harness.
                        if engine == "fixed":
                            pipeline = f"{zstdcat} {zst} | {grep} -F {shell_quote(pattern)}"
                        else:
                            pipeline = f"{zstdcat} {zst} | {grep} -E {shell_quote(pattern)}"
                        elapsed, code, out_len, _, first_output = run_with_first_output(["bash", "-lc", pipeline], repo)
                        write_row(
                            writer,
                            mode=mode,
                            repeat=repeat,
                            kind="grep_baseline",
                            name="zstdcat_grep",
                            pattern_name=pattern_name,
                            engine=engine,
                            command="zstdcat <zst> | grep",
                            wall_seconds=f"{elapsed:.6f}",
                            first_output_seconds=first_output,
                            exit_code=code,
                            input_bytes=zst.stat().st_size,
                            output_bytes=out_len,
                        )

        summarize(output, summary, mode, corpus, input_bytes, lines)

        print(f"wrote {output}")
        print(f"wrote {summary}")
        print(f"wrote {env_report}")
        if args.keep_temp:
            print(f"kept temp directory: {tmp_path}")
            temp_manager = None
    finally:
        if temp_manager is not None:
            temp_manager.cleanup()

    return 0


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


if __name__ == "__main__":
    raise SystemExit(main())
