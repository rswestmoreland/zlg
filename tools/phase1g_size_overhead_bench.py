#!/usr/bin/env python3
"""Phase 1g size-overhead benchmark.

This benchmark carries forward the production-facing builders and compares zlg
against gzip build speed, CPU, RSS, output size, and zlg component overhead
across several corpus shapes. RSS and CPU capture are fail-closed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import re
import resource
import shutil
import struct
import subprocess
import tempfile
import time
from pathlib import Path
from statistics import median

REPO = Path(__file__).resolve().parents[1]

CANDIDATE_PROFILES = [
    "combined",
    "combined-bitset-seen",
    "combined-bitset-paged-seen",
    "combined-sparse-first-bitset",
]

SEARCH_QUERIES = [
    ("needle_fixed_ip", ["-F", "src_ip=192.168.102.55"]),
    ("common_fixed", ["-F", "failed password"]),
    ("rust_regex_key", [r'key="[^"]+"']),
    ("pcre2_lookbehind_key", ["-P", r'(?<=key=")[^"]+']),
]

CSV_FIELDS = [
    "corpus",
    "seed",
    "corpus_bytes",
    "corpus_sha256",
    "tool",
    "operation",
    "build_profile",
    "query_name",
    "stream_decode",
    "wall_seconds",
    "user_seconds",
    "system_seconds",
    "total_cpu_seconds",
    "max_rss_kb",
    "returncode",
    "output_bytes",
    "zlg_total_bytes",
    "zlg_chunk_count",
    "zlg_chunk_header_bytes",
    "zlg_summary_bytes",
    "zlg_compressed_payload_bytes",
    "zlg_directory_footer_bytes",
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
    "build_edge_scratch_capacity_bytes",
    "build_sort_scratch_capacity_bytes",
    "build_lower_scratch_capacity_bytes",
    "build_summary_scratch_capacity_bytes",
    "build_group_bucket_scratch_bytes",
    "notes",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def make_high_dup_log(path: Path, lines: int, seed: int) -> None:
    rng = random.Random(seed)
    with path.open("wb") as handle:
        for index in range(lines):
            src = "192.168.102.55" if index % 5 == 0 else f"10.0.{index % 64}.{index % 251}"
            user = f"user{index % 128}"
            host = f"host{index % 256}"
            key = f"K{index % 4096:04x}"
            status = "failed password" if index % 3 else "accepted password"
            jitter = rng.randint(0, 9999)
            line = (
                f"ts=2026-05-16T12:{index % 60:02d}:00Z host={host} "
                f"src_ip={src} username={user} action=login status=\"{status}\" "
                f"key=\"{key}\" msg=\"ssh auth event {jitter}\"\n"
            )
            handle.write(line.encode("utf-8"))


def make_high_cardinality_log(path: Path, lines: int, seed: int) -> None:
    rng = random.Random(seed)
    with path.open("wb") as handle:
        for index in range(lines):
            token = rng.getrandbits(96).to_bytes(12, "big").hex()
            src = f"172.16.{rng.randrange(256)}.{rng.randrange(256)}"
            user = f"u{rng.randrange(1_000_000):06d}"
            line = (
                f"ts=2026-05-16T13:{index % 60:02d}:00Z src_ip={src} "
                f"username={user} action=download key=\"{token}\" "
                f"msg=\"high cardinality event {token}\"\n"
            )
            handle.write(line.encode("utf-8"))


def make_unicode_log(path: Path, lines: int, seed: int) -> None:
    names = ["\u305f\u308d\u3046", "\u30ab\u30ca", "\u30e6\u30fc\u30b6\u30fc", "\u307f\u3069\u308a", "\u30ed\u30b0"]
    messages = ["\u30ed\u30b0\u30a4\u30f3\u6210\u529f", "\u30ed\u30b0\u30a4\u30f3\u5931\u6557", "\u6a29\u9650\u78ba\u8a8d", "\u63a5\u7d9a\u958b\u59cb"]
    with path.open("wb") as handle:
        for index in range(lines):
            name = names[(index + seed) % len(names)]
            msg = messages[index % len(messages)]
            line = (
                f"ts=2026-05-16T14:{index % 60:02d}:00Z "
                f"username={name} user=\u30ab\u30ca src_ip=192.168.102.55 "
                f"key=\"unicode-{index % 1024}\" msg=\"{msg}\"\n"
            )
            handle.write(line.encode("utf-8"))


def make_binaryish(path: Path, lines: int, seed: int) -> None:
    rng = random.Random(seed)
    with path.open("wb") as handle:
        handle.write(b"\x89PNG\r\n\x1a\n")
        for index in range(max(1, lines // 16)):
            chunk = bytes(rng.randrange(256) for _ in range(96))
            handle.write(struct.pack(">I", len(chunk)))
            handle.write(b"zLGx")
            handle.write(chunk)
            handle.write(struct.pack(">I", index & 0xffff_ffff))
            if index % 7 == 0:
                handle.write(b"src_ip=192.168.102.55\n")


def make_realistic_mixed_log(path: Path, lines: int, seed: int) -> None:
    rng = random.Random(seed)
    vendors = ["sshd", "nginx", "firewall", "edr", "app", "dns", "proxy"]
    actions = ["allow", "deny", "login", "logout", "query", "connect", "download", "alert"]
    statuses = ["ok", "failed password", "blocked", "allowed", "timeout", "quarantined"]
    with path.open("wb") as handle:
        for index in range(lines):
            vendor = vendors[index % len(vendors)]
            action = actions[(index + rng.randrange(len(actions))) % len(actions)]
            status = statuses[(index + rng.randrange(len(statuses))) % len(statuses)]
            src = "192.168.102.55" if index % 11 == 0 else f"10.{index % 10}.{rng.randrange(256)}.{rng.randrange(256)}"
            dst = f"172.20.{rng.randrange(32)}.{rng.randrange(256)}"
            user = f"user{rng.randrange(5000):04d}"
            key = f"mix-{vendor}-{rng.getrandbits(32):08x}"
            if vendor == "nginx":
                line = (
                    f"10.{index % 64}.{rng.randrange(256)}.{rng.randrange(256)} - {user} "
                    f"[16/May/2026:15:{index % 60:02d}:00 +0000] \"GET /api/{key} HTTP/1.1\" "
                    f"{200 if status == 'ok' else 403} {rng.randrange(200, 5000)} src_ip={src} key=\"{key}\"\n"
                )
            elif vendor == "firewall":
                line = (
                    f"ts=2026-05-16T15:{index % 60:02d}:00Z vendor=firewall action={action} "
                    f"src_ip={src} dst_ip={dst} dst_port={22 + index % 2000} proto=tcp status=\"{status}\" key=\"{key}\"\n"
                )
            else:
                line = (
                    f"ts=2026-05-16T15:{index % 60:02d}:00Z vendor={vendor} host=host{index % 300} "
                    f"src_ip={src} username={user} action={action} status=\"{status}\" key=\"{key}\" "
                    f"msg=\"mixed log event from {vendor}\"\n"
                )
            handle.write(line.encode("utf-8"))


def make_long_line_log(path: Path, lines: int, seed: int) -> None:
    rng = random.Random(seed)
    with path.open("wb") as handle:
        for index in range(max(1000, lines // 8)):
            src = "192.168.102.55" if index % 7 == 0 else f"10.9.{index % 128}.{index % 251}"
            repeated = " ".join(f"field{i}=value{(index + i) % 1024}" for i in range(80))
            token = rng.getrandbits(128).to_bytes(16, "big").hex()
            line = (
                f"ts=2026-05-16T16:{index % 60:02d}:00Z src_ip={src} username=user{index % 2048} "
                f"action=bulk_update status=\"failed password\" key=\"long-{token}\" {repeated} "
                f"msg=\"long line payload {token} {repeated}\"\n"
            )
            handle.write(line.encode("utf-8"))


def make_short_line_log(path: Path, lines: int, seed: int) -> None:
    rng = random.Random(seed)
    with path.open("wb") as handle:
        for index in range(lines * 2):
            src = "192.168.102.55" if index % 13 == 0 else f"10.1.{index % 64}.{index % 251}"
            key = rng.randrange(2048)
            status = "failed password" if index % 4 == 0 else "ok"
            line = f"src_ip={src} u=u{index % 500} s=\"{status}\" key=\"s{key}\"\n"
            handle.write(line.encode("utf-8"))


def make_corpus(name: str, path: Path, lines: int, seed: int) -> None:
    if name == "high_dup":
        make_high_dup_log(path, lines, seed)
    elif name == "high_cardinality":
        make_high_cardinality_log(path, lines, seed)
    elif name == "unicode":
        make_unicode_log(path, max(1000, lines // 4), seed)
    elif name == "binaryish":
        make_binaryish(path, max(1000, lines // 4), seed)
    elif name == "realistic_mixed_log":
        make_realistic_mixed_log(path, lines, seed)
    elif name == "long_line_log":
        make_long_line_log(path, lines, seed)
    elif name == "short_line_log":
        make_short_line_log(path, lines, seed)
    else:
        raise ValueError(f"unknown corpus {name}")


def parse_time_output(path: Path) -> dict[str, str]:
    out = {"user_seconds": "", "system_seconds": "", "max_rss_kb": ""}
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key in out:
            out[key] = value.strip()
    return out


def run_measured(cmd: list[str], *, stdout_path: Path | None, tmp: Path, allow_nonzero: bool = False) -> dict[str, object]:
    time_candidate = shutil.which("time")
    if time_candidate is None:
        for fallback in ("/usr/bin/time", "/bin/time"):
            if Path(fallback).exists():
                time_candidate = fallback
                break
    parsed = {"user_seconds": "", "system_seconds": "", "max_rss_kb": ""}
    proc = None
    stdout = ""
    stderr = ""
    start = time.perf_counter()
    if time_candidate is not None:
        time_bin = Path(time_candidate)
        time_path = tmp / f"time-{time.perf_counter_ns()}.txt"
        actual_cmd = [str(time_bin), "-f", "user_seconds=%U\nsystem_seconds=%S\nmax_rss_kb=%M", "-o", str(time_path)] + cmd
        if stdout_path is None:
            proc = subprocess.run(actual_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            with stdout_path.open("wb") as handle:
                proc = subprocess.run(actual_cmd, stdout=handle, stderr=subprocess.PIPE)
        parsed = parse_time_output(time_path)
        time_path.unlink(missing_ok=True)
        stdout = proc.stdout.decode("utf-8", "replace") if isinstance(proc.stdout, bytes) else str(proc.stdout)
        stderr = proc.stderr.decode("utf-8", "replace") if isinstance(proc.stderr, bytes) else str(proc.stderr)
    else:
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        out_handle = stdout_path.open("wb") if stdout_path is not None else subprocess.PIPE
        run_proc = subprocess.Popen(cmd, stdout=out_handle, stderr=subprocess.PIPE)
        max_rss_kb = 0
        status_re = re.compile(r"^VmRSS:\s+(\d+)\s+kB$")
        while run_proc.poll() is None:
            try:
                status = Path(f"/proc/{run_proc.pid}/status").read_text(encoding="utf-8", errors="replace")
                for line in status.splitlines():
                    m = status_re.match(line)
                    if m:
                        max_rss_kb = max(max_rss_kb, int(m.group(1)))
                        break
            except FileNotFoundError:
                pass
            time.sleep(0.005)
        out_bytes, err_bytes = run_proc.communicate()
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        if stdout_path is not None:
            out_handle.close()
        proc = run_proc
        parsed["max_rss_kb"] = str(max_rss_kb) if max_rss_kb else ""
        parsed["user_seconds"] = f"{after.ru_utime - before.ru_utime:.6f}"
        parsed["system_seconds"] = f"{after.ru_stime - before.ru_stime:.6f}"
        stdout = out_bytes.decode("utf-8", "replace") if isinstance(out_bytes, bytes) else str(out_bytes)
        stderr = err_bytes.decode("utf-8", "replace") if isinstance(err_bytes, bytes) else str(err_bytes)
    wall = time.perf_counter() - start
    if not parsed["max_rss_kb"]:
        raise SystemExit(f"RSS capture failed for command: {' '.join(cmd)}")
    if not parsed["user_seconds"] or not parsed["system_seconds"]:
        raise SystemExit(f"CPU capture failed for command: {' '.join(cmd)}")

    if proc.returncode != 0 and not allow_nonzero:
        raise SystemExit(
            f"command failed {proc.returncode}: {' '.join(cmd)}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
        )

    total_cpu = f"{float(parsed['user_seconds']) + float(parsed['system_seconds']):.6f}"
    return {
        "returncode": proc.returncode,
        "wall_seconds": wall,
        "user_seconds": parsed["user_seconds"],
        "system_seconds": parsed["system_seconds"],
        "total_cpu_seconds": total_cpu,
        "max_rss_kb": parsed["max_rss_kb"],
        "stdout": stdout,
        "stderr": stderr,
    }


def median_float(values: list[object]) -> str:
    nums = [float(value) for value in values if value != "" and value is not None]
    return f"{median(nums):.6f}" if nums else ""


def median_int(values: list[object]) -> str:
    nums = [int(float(value)) for value in values if value != "" and value is not None]
    return str(int(median(nums))) if nums else ""


def run_repeated(factory, repeats: int, tmp: Path, *, allow_nonzero: bool = False) -> dict[str, object]:
    samples = []
    last = None
    for _ in range(repeats):
        cmd, stdout_path = factory()
        last = run_measured(cmd, stdout_path=stdout_path, tmp=tmp, allow_nonzero=allow_nonzero)
        samples.append(last)
    return {
        "returncode": last["returncode"] if last else 0,
        "wall_seconds": median_float([item["wall_seconds"] for item in samples]),
        "user_seconds": median_float([item["user_seconds"] for item in samples]),
        "system_seconds": median_float([item["system_seconds"] for item in samples]),
        "total_cpu_seconds": median_float([item["total_cpu_seconds"] for item in samples]),
        "max_rss_kb": median_int([item["max_rss_kb"] for item in samples]),
        "last_stdout": last["stdout"] if last else "",
        "last_stderr": last["stderr"] if last else "",
    }


def parse_zlg_components(path: Path) -> dict[str, int]:
    data = path.read_bytes()
    offset = 32
    out = {
        "zlg_total_bytes": len(data),
        "zlg_chunk_count": 0,
        "zlg_chunk_header_bytes": 0,
        "zlg_summary_bytes": 0,
        "zlg_compressed_payload_bytes": 0,
        "zlg_directory_footer_bytes": 0,
    }
    while offset + 4 <= len(data):
        magic = data[offset:offset + 4]
        if magic == b"ZCH1":
            header_len = struct.unpack_from("<H", data, offset + 4)[0]
            compressed_len = struct.unpack_from("<Q", data, offset + 40)[0]
            summary_len = struct.unpack_from("<I", data, offset + 48)[0]
            record_len = header_len + summary_len + compressed_len
            if offset + record_len > len(data):
                raise ValueError("zlg chunk record exceeds file size")
            out["zlg_chunk_count"] += 1
            out["zlg_chunk_header_bytes"] += header_len
            out["zlg_summary_bytes"] += summary_len
            out["zlg_compressed_payload_bytes"] += compressed_len
            offset += record_len
        elif magic == b"ZDR1":
            entry_len = struct.unpack_from("<I", data, offset + 4)[0]
            count = struct.unpack_from("<Q", data, offset + 8)[0]
            directory_len = 4 + 4 + 8 + entry_len * count
            footer_len = 48
            out["zlg_directory_footer_bytes"] = directory_len + footer_len
            offset += directory_len + footer_len
            break
        else:
            raise ValueError(f"unexpected zlg magic {magic!r} at offset {offset}")
    component_sum = 32 + out["zlg_chunk_header_bytes"] + out["zlg_summary_bytes"] + out["zlg_compressed_payload_bytes"] + out["zlg_directory_footer_bytes"]
    if component_sum != out["zlg_total_bytes"]:
        raise ValueError(f"component sum {component_sum} != total {out['zlg_total_bytes']}")
    return out


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
    for key in ["wall_seconds", "user_seconds", "system_seconds", "total_cpu_seconds", "max_rss_kb", "returncode"]:
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
        "edge_scratch_capacity_bytes": "build_edge_scratch_capacity_bytes",
        "sort_scratch_capacity_bytes": "build_sort_scratch_capacity_bytes",
        "lower_scratch_capacity_bytes": "build_lower_scratch_capacity_bytes",
        "summary_scratch_capacity_bytes": "build_summary_scratch_capacity_bytes",
        "group_bucket_scratch_bytes": "build_group_bucket_scratch_bytes",
    }
    for source, target in mapping.items():
        row[target] = stats.get(source, "")
    pushed = int(stats.get("pushed_edges", 0) or 0)
    unique = int(stats.get("unique_edges", 0) or 0)
    if pushed:
        row["build_duplicate_ratio"] = f"{(pushed - unique) / pushed:.6f}"


def run_probe(args: argparse.Namespace) -> list[dict[str, object]]:
    binary = Path(args.binary)
    if not binary.exists():
        raise SystemExit(f"binary not found: {binary}")
    gzip_bin = shutil.which("gzip")
    if gzip_bin is None:
        raise SystemExit("gzip not found; gzip build speed/memory is required")

    rows: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="zlg-phase1g-") as tmp_name:
        tmp = Path(tmp_name)
        for corpus_name in args.corpora.split(","):
            corpus_name = corpus_name.strip()
            corpus = tmp / f"{corpus_name}.dat"
            make_corpus(corpus_name, corpus, args.lines, args.seed)
            meta = {
                "corpus": corpus_name,
                "seed": args.seed,
                "corpus_bytes": corpus.stat().st_size,
                "corpus_sha256": sha256(corpus),
            }
            zlg_paths: dict[str, Path] = {}

            gzip_path = tmp / f"{corpus_name}.gz"

            def gzip_cmd():
                gzip_path.unlink(missing_ok=True)
                return ([gzip_bin, "-c", "-6", str(corpus)], gzip_path)

            timing = run_repeated(gzip_cmd, args.repeats, tmp)
            row = empty_row(meta)
            row.update({
                "tool": "gzip",
                "operation": "compress",
                "build_profile": "gzip-6",
                "output_bytes": gzip_path.stat().st_size,
                "notes": "gzip -6 external baseline",
            })
            add_timing(row, timing)
            rows.append(row)

            for profile in CANDIDATE_PROFILES:
                zlg_path = tmp / f"{corpus_name}-{profile}.zlg"
                stats_path = tmp / f"{corpus_name}-{profile}-build.json"

                def compress_cmd(profile=profile, zlg_path=zlg_path, stats_path=stats_path):
                    zlg_path.unlink(missing_ok=True)
                    stats_path.unlink(missing_ok=True)
                    return ([
                        str(binary),
                        "compress",
                        str(corpus),
                        "-o",
                        str(zlg_path),
                        "--chunk-policy",
                        "fixed-lines8192",
                        "--summary-mode",
                        "mesh-bigram",
                        "--build-profile",
                        profile,
                        "--build-stats-json",
                        str(stats_path),
                    ], None)

                timing = run_repeated(compress_cmd, args.repeats, tmp)
                if not zlg_path.exists():
                    raise SystemExit(f"missing zlg output for {profile}")
                zlg_paths[profile] = zlg_path
                stats = json.loads(stats_path.read_text(encoding="utf-8"))
                row = empty_row(meta)
                row.update({
                    "tool": "zlg",
                    "operation": "compress",
                    "build_profile": profile,
                    "output_bytes": zlg_path.stat().st_size,
                })
                add_timing(row, timing)
                row.update(parse_zlg_components(zlg_path))
                add_build_stats(row, stats)
                rows.append(row)

            # Byte-exact round trip check for combined on every corpus.
            roundtrip = tmp / f"{corpus_name}-roundtrip.out"

            def cat_cmd():
                roundtrip.unlink(missing_ok=True)
                return ([str(binary), "cat", str(zlg_paths["combined"])], roundtrip)

            timing = run_repeated(cat_cmd, args.repeats, tmp)
            if sha256(roundtrip) != meta["corpus_sha256"]:
                raise SystemExit(f"round trip mismatch for corpus {corpus_name}")
            row = empty_row(meta)
            row.update({"tool": "zlg", "operation": "roundtrip", "build_profile": "combined", "notes": "sha256_ok"})
            add_timing(row, timing)
            rows.append(row)

            # Search sanity is meaningful for line-oriented corpora.
            if corpus_name != "binaryish":
                baseline_profile = "combined"
                for query_name, query_args in SEARCH_QUERIES:
                    baseline_outputs: dict[str, bytes] = {}
                    for stream_decode in [False, True]:
                        out_path = tmp / f"{corpus_name}-{baseline_profile}-{query_name}-{stream_decode}.out"

                        def baseline_cmd(stream_decode=stream_decode, out_path=out_path):
                            out_path.unlink(missing_ok=True)
                            cmd = [str(binary), "grep"]
                            if stream_decode:
                                cmd.append("--stream-decode")
                            cmd += query_args + [str(zlg_paths[baseline_profile])]
                            return (cmd, out_path)

                        timing = run_repeated(baseline_cmd, args.repeats, tmp, allow_nonzero=True)
                        baseline_outputs[str(stream_decode)] = out_path.read_bytes()
                        row = empty_row(meta)
                        row.update({
                            "tool": "zlg",
                            "operation": "search",
                            "build_profile": baseline_profile,
                            "query_name": query_name,
                            "stream_decode": str(stream_decode).lower(),
                            "notes": "baseline",
                        })
                        add_timing(row, timing)
                        rows.append(row)

                    for profile in [p for p in CANDIDATE_PROFILES if p != baseline_profile]:
                        for stream_decode in [False, True]:
                            out_path = tmp / f"{corpus_name}-{profile}-{query_name}-{stream_decode}.out"

                            def profile_cmd(profile=profile, stream_decode=stream_decode, out_path=out_path):
                                out_path.unlink(missing_ok=True)
                                cmd = [str(binary), "grep"]
                                if stream_decode:
                                    cmd.append("--stream-decode")
                                cmd += query_args + [str(zlg_paths[profile])]
                                return (cmd, out_path)

                            timing = run_repeated(profile_cmd, args.repeats, tmp, allow_nonzero=True)
                            expected = baseline_outputs[str(stream_decode)]
                            if out_path.read_bytes() != expected:
                                raise SystemExit(
                                    f"search output mismatch corpus={corpus_name} profile={profile} query={query_name} stream={stream_decode}"
                                )
                            row = empty_row(meta)
                            row.update({
                                "tool": "zlg",
                                "operation": "search",
                                "build_profile": profile,
                                "query_name": query_name,
                                "stream_decode": str(stream_decode).lower(),
                                "notes": "matches_combined",
                            })
                            add_timing(row, timing)
                            rows.append(row)
    return rows


def validate_no_blank_metrics(rows: list[dict[str, object]]) -> None:
    missing_rss = [row for row in rows if row.get("max_rss_kb") in ("", None)]
    missing_cpu = [row for row in rows if row.get("total_cpu_seconds") in ("", None)]
    if missing_rss:
        raise SystemExit(f"RSS capture failed for {len(missing_rss)} rows")
    if missing_cpu:
        raise SystemExit(f"CPU capture failed for {len(missing_cpu)} rows")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def write_markdown(path: Path, rows: list[dict[str, object]]) -> None:
    compress_rows = [row for row in rows if row["operation"] == "compress"]
    doc = [
        "# Phase 1g Size Overhead Pass",
        "",
        "This benchmark compares the carried-forward builders against gzip build speed, CPU, RSS, output size, and zlg component overhead.",
        "",
        "RSS and CPU capture are fail-closed. Blank max_rss_kb or total_cpu_seconds fails the run.",
        "",
        "## Compression ranking by corpus",
        "",
    ]
    for corpus in sorted({row["corpus"] for row in compress_rows}):
        ranked = sorted(
            [row for row in compress_rows if row["corpus"] == corpus],
            key=lambda row: float(row["wall_seconds"]),
        )
        doc.extend([
            f"### {corpus}",
            "",
            "| rank | tool | profile | wall_s | cpu_s | rss_kb | output_bytes | scratch | bitset | first/trie bitset | pushed | unique | dup_ratio |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for index, row in enumerate(ranked, 1):
            doc.append(
                f"| {index} | {row['tool']} | {row['build_profile']} | {row['wall_seconds']} | "
                f"{row['total_cpu_seconds']} | {row['max_rss_kb']} | {row['output_bytes']} | "
                f"{row['build_scratch_bytes']} | {row['build_bitset_scratch_bytes']} | "
                f"{row['build_first_bitset_scratch_bytes']} | {row['build_pushed_edges']} | "
                f"{row['build_unique_edges']} | {row['build_duplicate_ratio']} |"
            )
        doc.append("")

    doc.extend([
        "## Size component comparison",
        "",
        "This section compares zlg component sizes against gzip output size. The zlg component fields are parsed from the .zlg archive and help identify whether size losses come from compressed payload, mesh summary, chunk headers, or directory/footer overhead.",
        "",
    ])
    for corpus in sorted({row["corpus"] for row in compress_rows}):
        gzip_rows = [
            row for row in compress_rows
            if row["corpus"] == corpus and row["tool"] == "gzip"
        ]
        if not gzip_rows:
            continue
        gzip_size = int(gzip_rows[0]["output_bytes"])
        zlg_rows = sorted(
            [row for row in compress_rows if row["corpus"] == corpus and row["tool"] == "zlg"],
            key=lambda row: row["build_profile"],
        )
        doc.extend([
            f"### {corpus}",
            "",
            "| profile | zlg_bytes | gzip_bytes | delta_vs_gzip | summary | payload | headers | dir_footer |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in zlg_rows:
            zlg_size = int(row["output_bytes"])
            delta = zlg_size - gzip_size
            doc.append(
                f"| {row['build_profile']} | {zlg_size} | {gzip_size} | {delta} | "
                f"{row['zlg_summary_bytes']} | {row['zlg_compressed_payload_bytes']} | "
                f"{row['zlg_chunk_header_bytes']} | {row['zlg_directory_footer_bytes']} |"
            )
        doc.append("")

    doc.extend([
        "## Candidates",
        "",
        "- combined: current safe baseline and reference builder.",
        "- combined-bitset-seen: full contiguous u24 bitset production candidate.",
        "- combined-bitset-paged-seen: full u24 bitset stored as 256 first-byte pages.",
        "- combined-sparse-first-bitset: sparse first-byte bitset second candidate.",
        "- gzip -6: external build speed, CPU, RSS, and size baseline.",
        "",
        "## Success criteria",
        "",
        "- Full validation script completes.",
        "- No CSV row has blank max_rss_kb.",
        "- No CSV row has blank total_cpu_seconds.",
        "- Search output for candidate profiles matches combined on line-oriented corpora.",
        "- Combined round trip is byte-exact for every corpus, including unicode and binaryish.",
        "- gzip compression speed, CPU, RSS, and output size are recorded for every corpus.",
        "- zlg summary, compressed payload, chunk header, and directory/footer bytes are recorded.",
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
    parser.add_argument(
        "--corpora",
        default="high_dup,high_cardinality,unicode,binaryish,realistic_mixed_log,long_line_log,short_line_log",
    )
    parser.add_argument("--output", default="validation_results/phase1g_size_overhead.md")
    parser.add_argument("--csv", default="validation_results/phase1g_size_overhead.csv")
    args = parser.parse_args()

    rows = run_probe(args)
    validate_no_blank_metrics(rows)
    write_csv(REPO / args.csv, rows)
    write_markdown(REPO / args.output, rows)
    print(f"wrote {REPO / args.output}")
    print(f"wrote {REPO / args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
