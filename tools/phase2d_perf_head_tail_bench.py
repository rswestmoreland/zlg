#!/usr/bin/env python3
"""Phase 2d performance smoke bench for search, head, and tail.

The measurement path intentionally uses Linux os.wait4() so wall time,
user CPU, system CPU, CPU percent, and max RSS are populated reliably.
GNU /usr/bin/time -v is optional and only used as a cross-check artifact.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Iterable

REQUIRED_METRIC_FIELDS = ("wall_seconds", "user_seconds", "system_seconds", "cpu_percent", "max_rss_kb")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 2d zlg performance smoke bench")
    parser.add_argument("--zlg-bin", default=os.environ.get("ZLG_BIN", "target/release/zlg"))
    parser.add_argument("--out-csv", default="validation_results/phase2d_perf_head_tail_smoke.csv")
    parser.add_argument("--out-md", default="validation_results/phase2d_perf_head_tail_smoke.md")
    parser.add_argument("--repeated-lines", type=int, default=120_000)
    parser.add_argument("--needle-lines", type=int, default=1_000_000)
    parser.add_argument("--needle-position-ratio", type=float, default=0.80)
    parser.add_argument("--head-lines", type=int, default=10)
    parser.add_argument("--tail-lines", type=int, default=10)
    parser.add_argument("--tail-large-lines", type=int, default=5_000)
    parser.add_argument("--allow-missing-resource-metrics", action="store_true")
    parser.add_argument("--keep-temp", action="store_true")
    parser.add_argument("--time-verbose-cross-check", action="store_true")
    return parser.parse_args()


def ensure_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"required tool not found: {name}")


def ensure_zlg(zlg_bin: str) -> str:
    path = Path(zlg_bin)
    if path.exists():
        return str(path)
    resolved = shutil.which(zlg_bin)
    if resolved:
        return resolved
    raise SystemExit(f"zlg binary not found: {zlg_bin}")


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
                b"user=user%07d src=10.%d.%d.%d status="
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
            handle.write(b" msg=login-attempt repeated-regex-corpus\n")


def write_needle_log(path: Path, lines: int, ratio: float) -> str:
    needle = "ULTRA_NEEDLE_7f2a9d_once"
    needle_index = max(0, min(lines - 1, int(lines * ratio)))
    with path.open("w", encoding="utf-8", newline="") as handle:
        for index in range(lines):
            if index == needle_index:
                handle.write(
                    f"ts=2026-05-17T13:00:00Z host=web01 level=warn marker={needle} "
                    f"msg=single deep hit line={index}\n"
                )
            else:
                handle.write(
                    f"ts=2026-05-17T13:{(index // 60) % 60:02d}:{index % 60:02d}Z "
                    f"host=web{index % 29:02d} level=info marker=common_{index % 997:03d} "
                    f"tenant=t{index % 41:02d} src=192.0.2.{index % 251} "
                    f"msg=ordinary background line {index}\n"
                )
    return needle


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


def format_float(value: float) -> str:
    return f"{value:.6f}"


def command_to_text(cmd: list[str]) -> str:
    return " ".join(cmd)


def status_from_wait(status: int) -> int:
    if os.WIFEXITED(status):
        return os.WEXITSTATUS(status)
    if os.WIFSIGNALED(status):
        return 128 + os.WTERMSIG(status)
    return status


def run_wait4(cmd: list[str], stdout_path: Path, stderr_path: Path | None = None, cwd: Path | None = None) -> dict[str, object]:
    if stderr_path is None:
        stderr_path = stdout_path.with_suffix(stdout_path.suffix + ".stderr.txt")
    start = time.perf_counter()
    with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
        proc = subprocess.Popen(cmd, stdout=stdout_handle, stderr=stderr_handle, cwd=cwd)
        waited_pid, status, usage = os.wait4(proc.pid, 0)
    wall = time.perf_counter() - start
    if waited_pid != proc.pid:
        raise RuntimeError(f"wait4 returned unexpected pid {waited_pid}, expected {proc.pid}")
    exit_code = status_from_wait(status)
    user = float(usage.ru_utime)
    system = float(usage.ru_stime)
    cpu_percent = ((user + system) / wall * 100.0) if wall > 0 else 0.0
    return {
        "wall_seconds": format_float(wall),
        "user_seconds": format_float(user),
        "system_seconds": format_float(system),
        "cpu_percent": format_float(cpu_percent),
        "max_rss_kb": str(int(usage.ru_maxrss)),
        "exit_code": exit_code,
        "stderr_path": str(stderr_path),
        "measurement_source": "os.wait4",
    }


def run_time_verbose_cross_check(cmd: list[str], output_path: Path) -> None:
    time_bin = Path("/usr/bin/time")
    if not time_bin.exists():
        return
    time_path = output_path.with_suffix(output_path.suffix + ".time-v.txt")
    discard_path = output_path.with_suffix(output_path.suffix + ".time-v.out")
    with discard_path.open("wb") as stdout_handle:
        subprocess.run([str(time_bin), "-v", "-o", str(time_path)] + cmd, stdout=stdout_handle, stderr=subprocess.DEVNULL)


def run_measured(cmd: list[str], stdout_path: Path, cross_check: bool = False) -> dict[str, object]:
    metrics = run_wait4(cmd, stdout_path)
    if cross_check:
        run_time_verbose_cross_check(cmd, stdout_path)
    return metrics


def bash_pipe(script: str) -> list[str]:
    return ["bash", "-lc", script]


def row_for(
    scenario: str,
    backend: str,
    operation: str,
    pattern_type: str,
    storage_bytes: int | str,
    metrics: dict[str, object],
    output_path: Path,
    command: list[str],
    expected_sha: str | None = None,
    match_count_override: str | None = None,
) -> dict[str, object]:
    output_bytes = output_path.stat().st_size if output_path.exists() else 0
    output_sha = sha256_file(output_path) if output_path.exists() else ""
    match_count = match_count_override if match_count_override is not None else str(count_output_lines(output_path) if output_path.exists() else 0)
    parity = "n/a" if expected_sha is None else ("ok" if output_sha == expected_sha else "mismatch")
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
        "parity": parity,
        "measurement_source": metrics.get("measurement_source", ""),
        "command": command_to_text(command),
    }


def add_build_rows(rows: list[dict[str, object]], scenario: str, paths: dict[str, Path], work: Path, zlg_bin: str, cross_check: bool) -> None:
    plain = paths["plain"]
    gz = paths["gzip"]
    zlg = paths["zlg"]
    zero_metrics = {
        "wall_seconds": "0.000000",
        "user_seconds": "0.000000",
        "system_seconds": "0.000000",
        "cpu_percent": "0.000000",
        "max_rss_kb": "0",
        "exit_code": 0,
        "measurement_source": "n/a",
    }
    empty = work / f"{scenario}_plain_build.out"
    empty.write_bytes(b"")
    rows.append(row_for(scenario, "plain_grep", "build", "n/a", plain.stat().st_size, zero_metrics, empty, ["plain log already available"], match_count_override="n/a"))

    gz_out = work / f"{scenario}_gzip_build.out"
    gz_cmd = ["gzip", "-c", str(plain)]
    metrics = run_measured(gz_cmd, gz_out, cross_check=cross_check)
    if metrics["exit_code"] != 0:
        raise RuntimeError(f"gzip build failed for {scenario}; see {metrics['stderr_path']}")
    gz.write_bytes(gz_out.read_bytes())
    rows.append(row_for(scenario, "gzip_zgrep", "build", "n/a", gz.stat().st_size, metrics, gz_out, gz_cmd, match_count_override="n/a"))

    zlg_out = work / f"{scenario}_zlg_build.out"
    zlg_cmd = [zlg_bin, "compress", "--mode", "standard", "-o", str(zlg), str(plain)]
    metrics = run_measured(zlg_cmd, zlg_out, cross_check=cross_check)
    if metrics["exit_code"] != 0:
        raise RuntimeError(f"zlg build failed for {scenario}; see {metrics['stderr_path']}")
    rows.append(row_for(scenario, "zlg", "build", "n/a", zlg.stat().st_size, metrics, zlg_out, zlg_cmd, match_count_override="n/a"))


def add_search_rows(rows: list[dict[str, object]], scenario: str, pattern_type: str, pattern: str, paths: dict[str, Path], work: Path, zlg_bin: str, cross_check: bool) -> None:
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
    add_equivalence_rows(rows, scenario, "search", pattern_type, paths, work, commands, cross_check)


def add_head_tail_rows(rows: list[dict[str, object]], scenario: str, paths: dict[str, Path], work: Path, zlg_bin: str, cross_check: bool, head_lines: int, tail_lines: int, tail_large_lines: int) -> None:
    head_n = str(head_lines)
    tail_n = str(tail_lines)
    tail_large_n = str(tail_large_lines)
    add_equivalence_rows(
        rows,
        scenario,
        "head",
        "n/a",
        paths,
        work,
        {
            "plain_grep": ["head", "-n", head_n, str(paths["plain"])],
            "gzip_zgrep": bash_pipe(f"gzip -dc {str(paths['gzip'])!r} | head -n {head_n}"),
            "zlg": [zlg_bin, "head", "-n", head_n, str(paths["zlg"])],
        },
        cross_check,
    )
    add_equivalence_rows(
        rows,
        scenario,
        "tail",
        "n/a",
        paths,
        work,
        {
            "plain_grep": ["tail", "-n", tail_n, str(paths["plain"])],
            "gzip_zgrep": bash_pipe(f"gzip -dc {str(paths['gzip'])!r} | tail -n {tail_n}"),
            "zlg": [zlg_bin, "tail", "-n", tail_n, str(paths["zlg"])],
        },
        cross_check,
    )
    add_equivalence_rows(
        rows,
        scenario,
        "tail_large",
        "n/a",
        paths,
        work,
        {
            "plain_grep": ["tail", "-n", tail_large_n, str(paths["plain"])],
            "gzip_zgrep": bash_pipe(f"gzip -dc {str(paths['gzip'])!r} | tail -n {tail_large_n}"),
            "zlg": [zlg_bin, "tail", "-n", tail_large_n, str(paths["zlg"])],
        },
        cross_check,
    )


def add_equivalence_rows(rows: list[dict[str, object]], scenario: str, operation: str, pattern_type: str, paths: dict[str, Path], work: Path, commands: dict[str, list[str]], cross_check: bool) -> None:
    storage = {
        "plain_grep": paths["plain"].stat().st_size,
        "gzip_zgrep": paths["gzip"].stat().st_size,
        "zlg": paths["zlg"].stat().st_size,
    }
    expected_sha: str | None = None
    for backend, cmd in commands.items():
        out = work / f"{scenario}_{backend}_{operation}.out"
        metrics = run_measured(cmd, out, cross_check=cross_check)
        if metrics["exit_code"] != 0:
            raise RuntimeError(f"{operation} failed for {scenario}/{backend}; see {metrics['stderr_path']}")
        if expected_sha is None:
            expected_sha = sha256_file(out)
        rows.append(row_for(scenario, backend, operation, pattern_type, storage[backend], metrics, out, cmd, expected_sha=expected_sha))


def validate_rows(rows: Iterable[dict[str, object]], allow_missing: bool) -> None:
    errors: list[str] = []
    for index, row in enumerate(rows, start=2):
        if row.get("parity") == "mismatch":
            errors.append(f"row {index}: output hash mismatch for {row.get('scenario')}/{row.get('operation')}/{row.get('backend')}")
        if row.get("exit_code") not in (0, "0"):
            errors.append(f"row {index}: non-zero exit for {row.get('scenario')}/{row.get('operation')}/{row.get('backend')}")
        for field in REQUIRED_METRIC_FIELDS:
            value = str(row.get(field, ""))
            if value == "" or value.lower() == "n/a":
                errors.append(f"row {index}: missing {field} for {row.get('scenario')}/{row.get('operation')}/{row.get('backend')}")
    if errors and not allow_missing:
        raise RuntimeError("invalid bench metrics:\n" + "\n".join(errors))


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
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
        "parity",
        "measurement_source",
        "command",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_speed(rows: list[dict[str, object]], scenario: str, operation: str) -> list[str]:
    subset = [row for row in rows if row["scenario"] == scenario and row["operation"] == operation]
    by_backend = {str(row["backend"]): float(str(row["wall_seconds"])) for row in subset}
    lines: list[str] = []
    if "zlg" in by_backend and "gzip_zgrep" in by_backend and by_backend["zlg"] > 0:
        lines.append(f"- {scenario} {operation}: zlg vs gzip/zgrep wall ratio {by_backend['zlg'] / by_backend['gzip_zgrep']:.3f}")
    if "zlg" in by_backend and "plain_grep" in by_backend and by_backend["plain_grep"] > 0:
        lines.append(f"- {scenario} {operation}: zlg vs plain wall ratio {by_backend['zlg'] / by_backend['plain_grep']:.3f}")
    return lines


def write_markdown(rows: list[dict[str, object]], path: Path) -> None:
    lines = [
        "# Phase 2d performance smoke bench",
        "",
        "This bench compares plain logs, gzip streams, and zlg archives for search, head, and tail.",
        "Resource metrics are captured with Linux os.wait4().",
        "",
        "| scenario | backend | operation | storage bytes | wall seconds | user seconds | system seconds | cpu percent | max rss kb | matches | parity | exit |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {scenario} | {backend} | {operation} | {storage_bytes} | {wall_seconds} | {user_seconds} | {system_seconds} | {cpu_percent} | {max_rss_kb} | {match_count} | {parity} | {exit_code} |".format(
                **row
            )
        )
    lines.extend(["", "## Wall-time ratios", ""])
    for scenario in sorted({str(row["scenario"]) for row in rows}):
        for operation in ("search", "head", "tail", "tail_large"):
            lines.extend(summarize_speed(rows, scenario, operation))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    zlg_bin = ensure_zlg(args.zlg_bin)
    for required in ("grep", "gzip", "zgrep", "head", "tail", "bash"):
        ensure_tool(required)

    out_csv = Path(args.out_csv)
    out_md = Path(args.out_md)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []

    temp_obj = tempfile.TemporaryDirectory(prefix="zlg-phase2d-perf-")
    try:
        work = Path(temp_obj.name)
        repeated_plain = work / "repeated_regex.log"
        needle_plain = work / "needle_haystack_large.log"
        write_repeated_regex_log(repeated_plain, args.repeated_lines)
        needle = write_needle_log(needle_plain, args.needle_lines, args.needle_position_ratio)

        scenarios = {
            "repeated_regex": {
                "plain": repeated_plain,
                "gzip": work / "repeated_regex.log.gz",
                "zlg": work / "repeated_regex.zlg",
                "pattern_type": "regex",
                "pattern": "status=(failed|denied)",
            },
            "needle_haystack_large": {
                "plain": needle_plain,
                "gzip": work / "needle_haystack_large.log.gz",
                "zlg": work / "needle_haystack_large.zlg",
                "pattern_type": "fixed",
                "pattern": needle,
            },
        }

        for scenario, spec in scenarios.items():
            add_build_rows(rows, scenario, spec, work, zlg_bin, args.time_verbose_cross_check)
            add_search_rows(rows, scenario, spec["pattern_type"], spec["pattern"], spec, work, zlg_bin, args.time_verbose_cross_check)
            add_head_tail_rows(rows, scenario, spec, work, zlg_bin, args.time_verbose_cross_check, args.head_lines, args.tail_lines, args.tail_large_lines)

        validate_rows(rows, args.allow_missing_resource_metrics)
        write_csv(rows, out_csv)
        write_markdown(rows, out_md)
        print(f"wrote {out_csv}")
        print(f"wrote {out_md}")
        if args.keep_temp:
            keep = Path("validation_results/phase2d_perf_temp_path.txt")
            keep.write_text(str(work) + "\n", encoding="utf-8")
            print(f"temp retained until process exit only: {work}")
        return 0
    finally:
        if not args.keep_temp:
            temp_obj.cleanup()


if __name__ == "__main__":
    if os.name != "posix" or not hasattr(os, "wait4"):
        raise SystemExit("phase2d bench requires POSIX os.wait4 resource accounting")
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        raise SystemExit(130)
