#!/usr/bin/env python3
import argparse
import csv
import statistics
from collections import defaultdict


def as_float(row, key):
    try:
        return float(row.get(key, "") or 0.0)
    except ValueError:
        return 0.0


def as_int(row, key):
    try:
        return int(float(row.get(key, "") or 0))
    except ValueError:
        return 0


def maybe_ratio(num, den):
    if den <= 0:
        return None
    return num / den


def fmt_secs(v):
    return f"{v:.4f}s"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    rows = []
    with open(args.csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    by_kind = defaultdict(list)
    for r in rows:
        by_kind[r.get("kind", "unknown")].append(r)

    md = []
    md.append("# Phase 0k Search Bottleneck Analysis")
    md.append("")

    compress_rows = by_kind.get("compress", [])
    if compress_rows:
        comp = compress_rows[-1]
        out_mb = as_float(comp, "output_bytes") / (1024 * 1024)
        in_mb = as_float(comp, "input_bytes") / (1024 * 1024)
        secs = as_float(comp, "wall_seconds")
        throughput = (in_mb / secs) if secs > 0 else 0.0
        ratio = maybe_ratio(as_float(comp, "output_bytes"), as_float(comp, "input_bytes"))
        md.append("## Compression highlights")
        md.append(f"- Input size: {in_mb:.2f} MiB")
        md.append(f"- Output size: {out_mb:.2f} MiB")
        if ratio is not None:
            md.append(f"- Compression ratio (output/input): {ratio:.3f}")
        md.append(f"- Compression time: {fmt_secs(secs)}")
        md.append(f"- Compression throughput: {throughput:.2f} MiB/s")
        md.append("")

    grep_rows = by_kind.get("grep", [])
    md.append("## Grep/search timing highlights")
    if not grep_rows:
        md.append("- No grep rows found in CSV.")
    else:
        times = [as_float(r, "wall_seconds") for r in grep_rows]
        first_out = [as_float(r, "first_output_seconds") for r in grep_rows if r.get("first_output_seconds") not in (None, "")]
        md.append(f"- Grep runs: {len(grep_rows)}")
        md.append(f"- Mean grep seconds: {statistics.mean(times):.4f}s")
        md.append(f"- Min grep seconds: {min(times):.4f}s")
        md.append(f"- Max grep seconds: {max(times):.4f}s")
        if first_out:
            md.append(f"- Mean first_output_seconds: {statistics.mean(first_out):.4f}s")
            md.append(f"- Min first_output_seconds: {min(first_out):.4f}s")
            md.append(f"- Max first_output_seconds: {max(first_out):.4f}s")
        md.append("")

        md.append("## Per-pattern chunk counters")
        headers = [
            "pattern", "policy", "wall_seconds", "first_output_seconds", "chunks_total", "chunks_skipped",
            "candidate_chunks", "chunks_decoded", "decoded_bytes", "matching_lines", "skip_ratio", "decode_ratio"
        ]
        md.append("| " + " | ".join(headers) + " |")
        md.append("|" + "|".join(["---"] * len(headers)) + "|")

        decode_all = []
        skip_effective = []
        for r in sorted(grep_rows, key=lambda x: as_float(x, "wall_seconds")):
            total = as_int(r, "chunks_total")
            skipped = as_int(r, "chunks_skipped")
            decoded = as_int(r, "chunks_decoded")
            cand = as_int(r, "candidate_chunks")
            sk = maybe_ratio(skipped, total)
            dr = maybe_ratio(decoded, total)
            if total > 0 and decoded == total:
                decode_all.append(f"{r.get('policy','')}:{r.get('pattern_name','')}")
            if sk is not None and sk >= 0.25:
                skip_effective.append(f"{r.get('policy','')}:{r.get('pattern_name','')}")
            md.append("| " + " | ".join([
                r.get("pattern_name", ""),
                r.get("policy", ""),
                f"{as_float(r, 'wall_seconds'):.4f}",
                (f"{as_float(r, 'first_output_seconds'):.4f}" if r.get("first_output_seconds", "") else "n/a"),
                str(total),
                str(skipped),
                str(cand),
                str(decoded),
                str(as_int(r, "decoded_bytes")),
                str(as_int(r, "matching_lines")),
                f"{sk:.3f}" if sk is not None else "n/a",
                f"{dr:.3f}" if dr is not None else "n/a",
            ]) + " |")

        md.append("")
        md.append("## Selector effectiveness summary")
        if decode_all:
            md.append("- Patterns decoding all chunks: " + ", ".join(sorted(set(decode_all))))
        else:
            md.append("- No patterns decoded all chunks.")
        if skip_effective:
            md.append("- Patterns with effective skipping (skip_ratio >= 0.25): " + ", ".join(sorted(set(skip_effective))))
        else:
            md.append("- No patterns reached skip_ratio >= 0.25.")

        md.append("")
        md.append("## Next likely optimization")
        if decode_all:
            md.append("- Most likely next step: summary refinement or selector extraction, because some patterns still force full decode.")
        elif skip_effective:
            md.append("- Most likely next step: chunk policy tuning, then parallel decode/search once selector gains plateau.")
        else:
            md.append("- Most likely next step: selector extraction first, then summary refinement.")

    with open(args.output, "w", encoding="ascii") as f:
        f.write("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
