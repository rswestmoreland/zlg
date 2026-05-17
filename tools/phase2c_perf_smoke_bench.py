#!/usr/bin/env python3
"""Phase 2c performance smoke bench for plain grep, zgrep, and zlg grep.

This is intentionally small and deterministic. It is not a replacement for the
larger Phase 0/1 benchmark matrix.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a compact zlg performance smoke bench")
    parser.add_argument("--zlg-bin", default=os.environ.get("ZLG_BIN", "target/release/zlg"))
    parser.add_argument("--out-csv", default="validation_results/phase2c_perf_smoke.csv")
    parser.add_argument("--out-md", default="validation_results/phase2c_perf_smoke.md")
    parser.add_argument("--lines", type=int, default=60_000)
    parser.add_argument("--keep-temp", action="store_true")
    return parser.parse_args()


def write_repeated_regex_log(path: Path, lines: int) -> None:
    with path.open("wb") as handle:
        for index in range(lines):
            if index % 3 == 0:
                status = b"failed"
            elif index % 3 == 1:
                status = b"denied"
            else:
                status = b"ok"
            handle.write(
                b"ts=2026-05-17T12:%02d:%02dZ host=auth%02d app=sshd "
                b"user=user%05d src=10.%d.%d.%d status="
                % (
                    (index // 60) % 60,
                    index % 60,
                    index % 17,
                    index,
                    index % 255,
                    (index // 255) % 255,
                    (index // (255 * 255)) % 255,
                )
            )
            handle.write(status)
            handle.write(b" msg=login-attempt\n")


def write_needle_log(path: Path, lines: int) -> str:
    needle = "ULTRA_NEEDLE_7f2a9d_once"
    needle_index = max(0, min(lines - 1, int(lines * 0.80)))
    with path.open("w", encoding="utf-8", newline="") as handle:
        for index in range(lines):
            if index == needle_index:
                handle.write(
                    f"ts=2026-05-17T13:00:00Z host=web01 level=warn marker={needle} msg=single deep hit\n"
                )
            else:
                handle.write(
                    f"ts=2026-05-17T13:{(index // 60) % 60:02d}:{index % 60:02d}Z "
                    f"host=web{index % 29:02d} level=info marker=common_{index % 997:03d} "
                    f"msg=ordinary background line {index}\n"
                )
    return needle


def parse_elapsed(value: str) -> float:
    parts = value.strip().split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        if len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        return float(parts[0])
    except (ValueError, IndexError):
        return 0.0


def parse_time_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_output_lines(path: Path) -> int:
    data = path.read_bytes()
    if not data:
        return 0
    return data.count(b"\n") + (0 if data.endswith(b"\n") else 1)


def run_timed(cmd: list[str], stdout_path: Path, cwd: Path | None = None) -> dict[str, object]:
    time_bin = shutil.which("time")
    if time_bin is None and Path("/usr/bin/time").exists():
        time_bin = "/usr/bin/time"

    time_path = stdout_path.with_suffix(stdout_path.suffix + ".time.txt")
    start = time.perf_counter()
    with stdout_path.open("wb") as stdout_handle:
        if time_bin:
            wrapped = [time_bin, "-v", "-o", str(time_path)] + cmd
            proc = subprocess.run(wrapped, stdout=stdout_handle, stderr=subprocess.PIPE, cwd=cwd)
        else:
            proc = subprocess.run(cmd, stdout=stdout_handle, stderr=subprocess.PIPE, cwd=cwd)
    wall = time.perf_counter() - start

    parsed = parse_time_file(time_path)
    if parsed:
        wall = parse_elapsed(parsed.get("Elapsed (wall clock) time (h:mm:ss or m:ss)", "0"))
        user = parsed.get("User time (seconds)", "")
        system = parsed.get("System time (seconds)", "")
        cpu = parsed.get("Percent of CPU this job got", "")
        rss = parsed.get("Maximum resident set size (kbytes)", "")
    else:
        user = ""
        system = ""
        cpu = ""
        rss = ""

    return {
        "wall_seconds": f"{wall:.6f}",
        "user_seconds": user,
        "system_seconds": system,
        "cpu_percent": cpu,
        "max_rss_kb": rss,
        "exit_code": proc.returncode,
        "stderr": proc.stderr.decode("utf-8", errors="replace"),
    }


def row_for(
    scenario: str,
    backend: str,
    operation: str,
    pattern_type: str,
    storage_bytes: int,
    metrics: dict[str, object],
    output_path: Path,
    command: list[str],
) -> dict[str, object]:
    output_bytes = output_path.stat().st_size if output_path.exists() else 0
    output_sha = sha256_file(output_path) if output_path.exists() else ""
    match_count = count_output_lines(output_path) if output_path.exists() else 0
    return {
        "scenario": scenario,
        "backend": backend,
        "operation": operation,
        "pattern_type": pattern_type,
        "storage_bytes": storage_bytes,
        "wall_seconds": metrics.get("wall_seconds", ""),
        "user_seconds": metrics.get("user_seconds", ""),
        "system_seconds": metrics.get("system_seconds", ""),
        "cpu_percent": metrics.get("cpu_percent", ""),
        "max_rss_kb": metrics.get("max_rss_kb", ""),
        "exit_code": metrics.get("exit_code", ""),
        "output_bytes": output_bytes,
        "output_sha256": output_sha,
        "match_count": match_count,
        "command": " ".join(command),
    }


def add_build_rows(rows: list[dict[str, object]], scenario: str, paths: dict[str, Path], work: Path, zlg_bin: str) -> None:
    plain = paths["plain"]
    gz = paths["gzip"]
    zlg = paths["zlg"]

    empty = work / f"{scenario}_plain_build.out"
    empty.write_bytes(b"")
    rows.append(row_for(scenario, "plain_grep", "build", "n/a", plain.stat().st_size, {
        "wall_seconds": "0.000000",
        "user_seconds": "0.000000",
        "system_seconds": "0.000000",
        "cpu_percent": "n/a",
        "max_rss_kb": "n/a",
        "exit_code": 0,
    }, empty, ["plain log already available"]))

    gz_out = work / f"{scenario}_gzip_build.out"
    gz_cmd = ["gzip", "-c", str(plain)]
    metrics = run_timed(gz_cmd, gz_out)
    if metrics["exit_code"] != 0:
        raise RuntimeError(f"gzip build failed: {metrics['stderr']}")
    gz.write_bytes(gz_out.read_bytes())
    rows.append(row_for(scenario, "gzip_zgrep", "build", "n/a", gz.stat().st_size, metrics, gz_out, gz_cmd))

    zlg_out = work / f"{scenario}_zlg_build.out"
    zlg_cmd = [zlg_bin, "compress", "--mode", "standard", "-o", str(zlg), str(plain)]
    metrics = run_timed(zlg_cmd, zlg_out)
    if metrics["exit_code"] != 0:
        raise RuntimeError(f"zlg build failed: {metrics['stderr']}")
    rows.append(row_for(scenario, "zlg", "build", "n/a", zlg.stat().st_size, metrics, zlg_out, zlg_cmd))


def add_search_rows(
    rows: list[dict[str, object]],
    scenario: str,
    pattern_type: str,
    pattern: str,
    paths: dict[str, Path],
    work: Path,
    zlg_bin: str,
) -> None:
    if pattern_type == "regex":
        commands = {
            "plain_grep": ["grep", "-E", pattern, str(paths["plain"])],
            "gzip_zgrep": ["zgrep", "-E", pattern, str(paths["gzip"])],
            "zlg": [zlg_bin, "grep", pattern, str(paths["zlg"])],
        }
    else:
        commands = {
            "plain_grep": ["grep", "-F", pattern, str(paths["plain"])],
            "gzip_zgrep": ["zgrep", "-F", pattern, str(paths["gzip"])],
            "zlg": [zlg_bin, "grep", "-f", pattern, str(paths["zlg"])],
        }

    storage = {
        "plain_grep": paths["plain"].stat().st_size,
        "gzip_zgrep": paths["gzip"].stat().st_size,
        "zlg": paths["zlg"].stat().st_size,
    }

    for backend, cmd in commands.items():
        out = work / f"{scenario}_{backend}_search.out"
        metrics = run_timed(cmd, out)
        rows.append(row_for(scenario, backend, "search", pattern_type, storage[backend], metrics, out, cmd))


def write_markdown(rows: list[dict[str, object]], path: Path) -> None:
    lines = [
        "# Phase 2c performance smoke bench",
        "",
        "This is a compact smoke comparison, not the full historical benchmark matrix.",
        "",
        "| scenario | backend | operation | storage bytes | wall seconds | user seconds | system seconds | max rss kb | match count | exit |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {scenario} | {backend} | {operation} | {storage_bytes} | {wall_seconds} | {user_seconds} | {system_seconds} | {max_rss_kb} | {match_count} | {exit_code} |".format(
                **row
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    zlg_bin = args.zlg_bin
    if not Path(zlg_bin).exists() and shutil.which(zlg_bin) is None:
        raise SystemExit(f"zlg binary not found: {zlg_bin}")
    for required in ("grep", "gzip", "zgrep"):
        if shutil.which(required) is None:
            raise SystemExit(f"required tool not found: {required}")

    out_csv = Path(args.out_csv)
    out_md = Path(args.out_md)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory(prefix="zlg-phase2c-perf-") as temp_name:
        work = Path(temp_name)
        repeated_plain = work / "repeated_regex.log"
        needle_plain = work / "needle_haystack.log"
        write_repeated_regex_log(repeated_plain, args.lines)
        needle = write_needle_log(needle_plain, args.lines)

        scenarios = {
            "repeated_regex": {
                "plain": repeated_plain,
                "gzip": work / "repeated_regex.log.gz",
                "zlg": work / "repeated_regex.zlg",
                "pattern_type": "regex",
                "pattern": "status=(failed|denied)",
            },
            "needle_haystack": {
                "plain": needle_plain,
                "gzip": work / "needle_haystack.log.gz",
                "zlg": work / "needle_haystack.zlg",
                "pattern_type": "fixed",
                "pattern": needle,
            },
        }

        for scenario, spec in scenarios.items():
            add_build_rows(rows, scenario, spec, work, zlg_bin)
            add_search_rows(
                rows,
                scenario,
                spec["pattern_type"],
                spec["pattern"],
                spec,
                work,
                zlg_bin,
            )

        if args.keep_temp:
            keep = Path("validation_results/phase2c_perf_smoke_temp_path.txt")
            keep.write_text(str(work) + "\n", encoding="utf-8")
            print(f"temp retained until process exit only: {work}")

    fieldnames = [
        "scenario",
        "backend",
        "operation",
        "pattern_type",
        "storage_bytes",
        "wall_seconds",
        "user_seconds",
        "system_seconds",
        "cpu_percent",
        "max_rss_kb",
        "exit_code",
        "output_bytes",
        "output_sha256",
        "match_count",
        "command",
    ]
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    write_markdown(rows, out_md)
    print(f"wrote {out_csv}")
    print(f"wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
