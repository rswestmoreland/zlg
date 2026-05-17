#!/usr/bin/env python3
"""Phase 2g archive hardening probe.

This tool creates a valid .zlg archive, mutates copies in targeted ways, and
checks that zlg commands reject the malformed archives. It intentionally writes
only compact CSV/Markdown summaries to validation_results; generated archives
stay in a temporary directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import shlex
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable, Iterable

FOOTER_LEN = 48
DIRECTORY_HEADER_LEN = 16
CHUNK_HEADER_LEN = 64


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 2g archive hardening checks")
    parser.add_argument("--zlg", required=True, help="zlg command, for example target/release/zlg")
    parser.add_argument("--out-dir", default="validation_results")
    return parser.parse_args()


def run(cmd: list[str], *, cwd: Path | None = None, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def le_u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def le_u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def le_u64(data: bytes, offset: int) -> int:
    return struct.unpack_from("<Q", data, offset)[0]


def put_u16(data: bytearray, offset: int, value: int) -> None:
    struct.pack_into("<H", data, offset, value)


def put_u64(data: bytearray, offset: int, value: int) -> None:
    struct.pack_into("<Q", data, offset, value)


def footer_offset(data: bytes) -> int:
    return len(data) - FOOTER_LEN


def directory_offset(data: bytes) -> int:
    return le_u64(data, footer_offset(data) + 32)


def first_entry_offset(data: bytes) -> int:
    return directory_offset(data) + DIRECTORY_HEADER_LEN


def first_chunk_offset(data: bytes) -> int:
    return le_u64(data, first_entry_offset(data))


def first_summary_offset(data: bytes) -> int:
    return le_u64(data, first_entry_offset(data) + 8)


def first_compressed_offset(data: bytes) -> int:
    return le_u64(data, first_entry_offset(data) + 24)


def mutate_bad_global_magic(data: bytes) -> bytes:
    out = bytearray(data)
    out[0:4] = b"BAD!"
    return bytes(out)


def mutate_unsupported_version(data: bytes) -> bytes:
    out = bytearray(data)
    put_u16(out, 8, 999)
    return bytes(out)


def mutate_bad_footer_magic(data: bytes) -> bytes:
    out = bytearray(data)
    out[footer_offset(out):footer_offset(out) + 4] = b"BAD!"
    return bytes(out)


def mutate_bad_directory_magic(data: bytes) -> bytes:
    out = bytearray(data)
    off = directory_offset(out)
    out[off:off + 4] = b"BAD!"
    return bytes(out)


def mutate_directory_count_mismatch(data: bytes) -> bytes:
    out = bytearray(data)
    put_u64(out, directory_offset(out) + 8, 999)
    return bytes(out)


def mutate_payload_out_of_bounds(data: bytes) -> bytes:
    out = bytearray(data)
    put_u64(out, first_entry_offset(out) + 32, (1 << 63))
    return bytes(out)


def mutate_chunk_header_mismatch(data: bytes) -> bytes:
    out = bytearray(data)
    chunk = first_chunk_offset(out)
    line_count_offset = chunk + 4 + 2 + 2 + 8 + 8
    put_u64(out, line_count_offset, 999)
    return bytes(out)


def mutate_crc_mismatch(data: bytes) -> bytes:
    out = bytearray(data)
    chunk = first_chunk_offset(out)
    crc_offset = chunk + 4 + 2 + 2 + 8 + 8 + 8 + 8 + 8 + 4
    out[crc_offset] ^= 0x55
    return bytes(out)


def mutate_summary_truncated(data: bytes) -> bytes:
    summary = first_summary_offset(data)
    compressed = first_compressed_offset(data)
    if compressed <= summary:
        return data[:-1]
    cut = summary + max(1, (compressed - summary) // 2)
    return data[:cut]


def mutate_payload_truncated(data: bytes) -> bytes:
    compressed = first_compressed_offset(data)
    footer = footer_offset(data)
    if footer <= compressed:
        return data[:-1]
    cut = compressed + max(1, (footer - compressed) // 2)
    return data[:cut]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def make_valid_archive(zlg: list[str], work: Path, mode: str) -> tuple[Path, Path]:
    raw = work / f"input_{mode}.log"
    archive = work / f"valid_{mode}.zlg"
    with raw.open("wb") as fh:
        for i in range(50_000):
            if i == 40_000:
                fh.write(b"ts=2026-05-17 level=error needle=phase2g_hardening status=failed\n")
            else:
                fh.write(f"ts=2026-05-17 level=info seq={i} status=ok user=user{i % 17}\n".encode())
    result = run(zlg + ["compress", str(raw), "-o", str(archive), "--mode", mode])
    if result.returncode != 0:
        sys.stderr.write(result.stderr.decode(errors="replace"))
        raise RuntimeError(f"failed to build valid archive for mode {mode}")
    return raw, archive


def command_name(cmd: list[str]) -> str:
    return " ".join(cmd)


def expect_ok(zlg: list[str], args: list[str], path: Path) -> tuple[bool, str]:
    result = run(zlg + args + [str(path)])
    return result.returncode == 0, (result.stderr + result.stdout).decode(errors="replace")[:240]


def expect_fail(zlg: list[str], args: list[str], path: Path) -> tuple[bool, str]:
    result = run(zlg + args + [str(path)])
    return result.returncode != 0, (result.stderr + result.stdout).decode(errors="replace")[:240]


def write_reports(rows: list[dict[str, str]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "phase2g_archive_hardening.csv"
    md_path = out_dir / "phase2g_archive_hardening.md"
    fields = ["mode", "case", "command", "expected", "ok", "note"]
    with csv_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with md_path.open("w") as fh:
        fh.write("# Phase 2g Archive Hardening Probe\n\n")
        fh.write("This report is generated from mutated temporary archives. Generated archives are not committed.\n\n")
        fh.write("| Mode | Case | Command | Expected | Result | Note |\n")
        fh.write("|---|---|---|---|---|---|\n")
        for row in rows:
            note = row["note"].replace("\n", " ").replace("|", "/")
            fh.write(
                f"| {row['mode']} | {row['case']} | `{row['command']}` | {row['expected']} | {row['ok']} | {note} |\n"
            )


def main() -> int:
    args = parse_args()
    zlg = shlex.split(args.zlg)
    out_dir = Path(args.out_dir)
    rows: list[dict[str, str]] = []
    failures = 0

    mutations: list[tuple[str, Callable[[bytes], bytes], list[list[str]]]] = [
        ("bad_global_magic", mutate_bad_global_magic, [["test"], ["info"], ["stats"]]),
        ("unsupported_version", mutate_unsupported_version, [["test"], ["info"], ["stats"]]),
        ("bad_footer_magic", mutate_bad_footer_magic, [["test"], ["info"], ["stats"], ["tail", "-n", "5"]]),
        ("bad_directory_magic", mutate_bad_directory_magic, [["test"], ["info"], ["stats"], ["tail", "-n", "5"]]),
        ("directory_count_mismatch", mutate_directory_count_mismatch, [["test"], ["info"], ["stats"], ["tail", "-n", "5"]]),
        ("payload_out_of_bounds", mutate_payload_out_of_bounds, [["test"], ["info"], ["stats"], ["tail", "-n", "5"]]),
        ("chunk_header_mismatch", mutate_chunk_header_mismatch, [["test"]]),
        ("crc_mismatch", mutate_crc_mismatch, [["test"], ["cat"], ["grep", "seq=1"]]),
        ("summary_truncated", mutate_summary_truncated, [["test"], ["cat"], ["grep", "needle"]]),
        ("payload_truncated", mutate_payload_truncated, [["test"], ["cat"], ["grep", "needle"]]),
    ]

    with tempfile.TemporaryDirectory(prefix="zlg_phase2g_") as tmp:
        work = Path(tmp)
        for mode in ["fast", "standard"]:
            raw, valid = make_valid_archive(zlg, work, mode)
            for check in [["test"], ["test", "--json"], ["test", "--quiet"], ["info"], ["stats"], ["head", "-n", "3"], ["tail", "-n", "3"]]:
                ok, note = expect_ok(zlg, check, valid)
                if not ok:
                    failures += 1
                rows.append({
                    "mode": mode,
                    "case": "valid_archive",
                    "command": command_name(check),
                    "expected": "pass",
                    "ok": "ok" if ok else "fail",
                    "note": note,
                })

            valid_bytes = valid.read_bytes()
            for name, mutate, commands in mutations:
                corrupt = work / f"{mode}_{name}.zlg"
                corrupt.write_bytes(mutate(valid_bytes))
                for command in commands:
                    ok, note = expect_fail(zlg, command, corrupt)
                    if not ok:
                        failures += 1
                    rows.append({
                        "mode": mode,
                        "case": name,
                        "command": command_name(command),
                        "expected": "fail",
                        "ok": "ok" if ok else "fail",
                        "note": note,
                    })

        non_zlg = work / "plain.txt"
        non_zlg.write_text("not a zlg file\n", encoding="utf-8")
        for command in [["test"], ["info"], ["stats"], ["cat"], ["grep", "zlg"]]:
            ok, note = expect_fail(zlg, command, non_zlg)
            if not ok:
                failures += 1
            rows.append({
                "mode": "n/a",
                "case": "non_zlg_input",
                "command": command_name(command),
                "expected": "fail",
                "ok": "ok" if ok else "fail",
                "note": note,
            })

    write_reports(rows, out_dir)
    print(f"phase2g archive hardening rows={len(rows)} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
