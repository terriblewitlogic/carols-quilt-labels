"""
Benchmark harness for the image→stitch pipeline.

Runs the full conversion on a fixed test image, writes a JEF, and reports the
metrics defined in STITCH_IMPROVEMENTS.md against the targets table:

    Mean / median / p95 / p99 stitch length
    Stitches > 7 mm (%)
    Jumps as % of total
    Short jumps (< 2 mm)
    Density per cm²
    Color blocks per design

Usage:
    source files/.venv/bin/activate
    python tests/benchmark_stitch.py             # default test image
    python tests/benchmark_stitch.py path.png    # custom test image
"""
import os
import sys
import math
import base64
import time
import tempfile
from pathlib import Path

# Make the function modules importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "functions" / "image_to_jef"))

import pyembroidery
from pyembroidery import EmbPattern, STITCH, JUMP, TRIM, STOP, END, COLOR_CHANGE

DEFAULT_TEST_IMAGE = ROOT / "public" / "library" / "sunflower" / "image.png"


# ── Targets from STITCH_IMPROVEMENTS.md ──────────────────────────────────────
TARGETS = {
    "tier1": {
        "mean_mm": (1.5, 2.5),       # acceptable range
        "p99_mm":  (None, 5.0),      # ≤ 5 mm
        "long_pct": (None, 0.20),    # ≤ 0.20%
        "jump_pct": (None, 2.0),     # ≤ 2.0%
        "short_jumps": (None, 200),  # < 200
        "density_per_cm2": (None, 250),  # ≤ 250
    },
    "tier2": {
        "mean_mm": (1.5, 2.5),
        "p99_mm":  (None, 5.0),
        "long_pct": (None, 0.20),
        "jump_pct": (None, 1.0),
        "short_jumps": (None, 50),
        "density_per_cm2": (None, 200),
    },
    "pro": {
        "mean_mm": (1.6, 2.5),
        "p99_mm":  (None, 4.5),
        "long_pct": (None, 0.10),
        "jump_pct": (None, 1.0),
        "short_jumps": (None, 100),
        "density_per_cm2": (60, 150),
    },
}


def run_pipeline(image_path: Path, **opts) -> dict:
    """Call raster_to_stitch_groups + write JEF, return all the metrics."""
    from raster_to_stitches import raster_to_stitch_groups

    img_b64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")

    t0 = time.time()
    groups, _svg, palette = raster_to_stitch_groups(
        img_b64,
        hoop_w_mm=opts.get("hoop_w_mm", 100),
        hoop_h_mm=opts.get("hoop_h_mm", 100),
        num_colors=opts.get("num_colors", 4),
        density_mm=opts.get("density_mm", 0.4),
        fill_angle_deg=opts.get("fill_angle_deg"),
        min_feature_mm=opts.get("min_feature_mm", 1.5),
        outline=opts.get("outline", "running"),
        outline_width_mm=opts.get("outline_width_mm", 1.0),
    )
    t_gen = time.time() - t0

    # Build the pyembroidery pattern using the same encoder as production
    from image_to_jef import _build_pattern
    t0 = time.time()
    pattern, stitch_count = _build_pattern(groups)
    pattern.add_command(pyembroidery.END)
    t_build = time.time() - t0

    # Write to temp JEF and reload to get final command stream
    tmp_path = "/tmp/_benchmark_output.jef"
    pyembroidery.write(pattern, tmp_path)
    final_pattern = EmbPattern(tmp_path)

    return {
        "generation_time_s": t_gen,
        "build_time_s": t_build,
        "groups": groups,
        "palette": palette,
        "stitch_count_logical": stitch_count,
        "pattern": final_pattern,
        "tmp_path": tmp_path,
    }


def measure(pattern: EmbPattern) -> dict:
    """Compute all comparison metrics from a pyembroidery pattern."""
    stitches = pattern.stitches
    n = len(stitches)
    if n == 0:
        return {"empty": True}

    cmd_counts = {}
    for _, _, cmd in stitches:
        c = cmd & 0xFF
        cmd_counts[c] = cmd_counts.get(c, 0) + 1

    # Stitch lengths
    # Measure STITCH-to-STITCH distance, ignoring STITCHes that immediately
    # follow a JUMP (those are needle-down at the JUMP destination — by
    # construction zero length, not a real stitch on fabric).
    lengths = []
    n_zero = 0
    prev_stitch = None
    just_jumped = False
    for x, y, cmd in stitches:
        c = cmd & 0xFF
        if c == STITCH:
            if prev_stitch is not None and not just_jumped:
                d = math.hypot(x - prev_stitch[0], y - prev_stitch[1]) / 10.0
                lengths.append(d)
                if d < 0.01:
                    n_zero += 1
            prev_stitch = (x, y)
            just_jumped = False
        elif c == JUMP:
            just_jumped = True
            prev_stitch = (x, y)
        elif c in (TRIM, STOP, COLOR_CHANGE, END):
            # Any of these break the stitch run; the next STITCH should not
            # count its distance from the previous block's tail.
            prev_stitch = None
            just_jumped = False

    lengths.sort()
    L = len(lengths)

    def pct(p):
        return lengths[int(L * p)] if L else 0

    # Jumps
    jump_lens = []
    jump_total_mm = 0.0
    prev = None
    for x, y, cmd in stitches:
        c = cmd & 0xFF
        if c == JUMP and prev is not None:
            jump_len = math.hypot(x - prev[0], y - prev[1]) / 10.0
            jump_lens.append(jump_len)
            jump_total_mm += jump_len
        prev = (x, y)

    n_jumps = cmd_counts.get(JUMP, 0)
    jump_lens.sort()
    J = len(jump_lens)
    def jpct(p):
        return jump_lens[min(J - 1, int(J * p))] if J else 0

    short_jumps = sum(1 for j in jump_lens if j < 2.0)
    jumps_ge_15 = sum(j >= 15 for j in jump_lens)
    jumps_ge_30 = sum(j >= 30 for j in jump_lens)
    jumps_ge_50 = sum(j >= 50 for j in jump_lens)

    # Bounding box and density (only over actual stitches)
    xs = [s[0] for s in stitches if (s[2] & 0xFF) == STITCH]
    ys = [s[1] for s in stitches if (s[2] & 0xFF) == STITCH]
    bw_mm = (max(xs) - min(xs)) / 10.0 if xs else 0
    bh_mm = (max(ys) - min(ys)) / 10.0 if ys else 0
    area_cm2 = (bw_mm * bh_mm) / 100.0
    n_stitch = cmd_counts.get(STITCH, 0)
    density = (n_stitch / area_cm2) if area_cm2 > 0 else 0

    # Color blocks (color change OR stop counts as a block boundary)
    blocks = 0
    for _, _, cmd in stitches:
        c = cmd & 0xFF
        if c in (COLOR_CHANGE, STOP):
            blocks += 1
    blocks += 1  # final block ends with END

    # Distinct thread colours from threadlist (deduped by hex)
    seen_hex = set()
    for t in pattern.threadlist:
        rgb = (t.get_red(), t.get_green(), t.get_blue())
        seen_hex.add('#%02x%02x%02x' % rgb)
    unique_colors = len(seen_hex) or 1
    multipass_ratio = blocks / unique_colors

    return {
        "total_commands": n,
        "stitch_count": n_stitch,
        "jump_count": n_jumps,
        "trim_count": cmd_counts.get(TRIM, 0),
        "color_change_count": cmd_counts.get(COLOR_CHANGE, 0),
        "stop_count": cmd_counts.get(STOP, 0),

        "mean_mm":   sum(lengths) / L if L else 0,
        "median_mm": lengths[L // 2] if L else 0,
        "p90_mm":    pct(0.90),
        "p95_mm":    pct(0.95),
        "p99_mm":    pct(0.99),
        "max_mm":    lengths[-1] if L else 0,
        "min_mm":    lengths[0] if L else 0,

        "long_count":    sum(1 for d in lengths if d > 7.0),
        "long_pct":      100 * sum(1 for d in lengths if d > 7.0) / L if L else 0,
        "zero_count":    n_zero,
        "zero_pct":      100 * n_zero / L if L else 0,

        "jump_pct":      100 * n_jumps / n if n else 0,
        "short_jumps":   short_jumps,
        "long_jumps":    jumps_ge_15,
        "jump_total_mm": jump_total_mm,
        "jump_mean_mm":  jump_total_mm / J if J else 0,
        "jump_p95_mm":   jpct(0.95),
        "jump_max_mm":   jump_lens[-1] if J else 0,
        "jumps_ge_15mm": jumps_ge_15,
        "jumps_ge_30mm": jumps_ge_30,
        "jumps_ge_50mm": jumps_ge_50,

        "bbox_w_mm":     bw_mm,
        "bbox_h_mm":     bh_mm,
        "area_cm2":      area_cm2,
        "density_per_cm2": density,

        "color_blocks":  blocks,
        "unique_colors": unique_colors,
        "multipass_ratio": multipass_ratio,
    }


def summarize_groups(groups: list) -> list:
    """Return per-stage stitch source counts before pyembroidery encoding."""
    summary = {}
    for group in groups:
        key = (group.get("pass", "?"), group.get("role", "?"), group.get("type", "?"))
        item = summary.setdefault(key, {
            "pass": key[0],
            "role": key[1],
            "type": key[2],
            "groups": 0,
            "segments": 0,
            "points": 0,
            "components": set(),
            "gaps_gt_8mm": 0,
            "gaps_gt_12mm": 0,
        })
        segments = group.get("segments", [])
        component_ids = group.get("componentIds") or [0] * len(segments)
        item["groups"] += 1
        item["segments"] += len(segments)
        item["points"] += sum(len(seg) for seg in segments)
        item["components"].update(component_ids)

        prev = None
        for seg in segments:
            if prev is not None and seg:
                gap = math.hypot(seg[0]["x"] - prev[0], seg[0]["y"] - prev[1]) / 10.0
                if gap > 8:
                    item["gaps_gt_8mm"] += 1
                if gap > 12:
                    item["gaps_gt_12mm"] += 1
            if seg:
                prev = (seg[-1]["x"], seg[-1]["y"])

    rows = []
    for item in summary.values():
        row = dict(item)
        row["components"] = len(item["components"])
        rows.append(row)
    rows.sort(key=lambda r: (r["pass"], r["role"], r["type"]))
    return rows


def export_roundtrip_metrics(pattern: EmbPattern, fmt: str) -> dict:
    """Write a pattern to a format, reload it, and return format-neutral metrics."""
    with tempfile.NamedTemporaryFile(suffix=f".{fmt}", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        pyembroidery.write(pattern, tmp_path)
        return measure(EmbPattern(tmp_path))
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def format_targets_row(metric_name, value, targets):
    """Pretty-print a metric vs each target band."""
    parts = []
    for tname, t in targets.items():
        lo, hi = t.get(metric_name, (None, None))
        if lo is None and hi is None:
            parts.append(f"{tname}: -")
            continue
        ok = True
        if lo is not None and value < lo:
            ok = False
        if hi is not None and value > hi:
            ok = False
        flag = "✓" if ok else "✗"
        if lo is not None and hi is not None:
            target_str = f"{lo}-{hi}"
        elif hi is not None:
            target_str = f"≤{hi}"
        else:
            target_str = f"≥{lo}"
        parts.append(f"{tname}:{target_str}{flag}")
    return "  ".join(parts)


def report(metrics: dict, label: str = "") -> None:
    print(f"\n{'='*72}")
    if label:
        print(f"  {label}")
    print(f"{'='*72}")
    print(f"  total commands:      {metrics['total_commands']:>8,}")
    print(f"  STITCHes:            {metrics['stitch_count']:>8,}")
    print(f"  JUMPs:               {metrics['jump_count']:>8,}  ({metrics['jump_pct']:.2f}%)   "
          f"{format_targets_row('jump_pct', metrics['jump_pct'], TARGETS)}")
    print(f"  TRIMs:               {metrics['trim_count']:>8,}")
    print(f"  COLOR CHANGEs:       {metrics['color_change_count']:>8,}")
    print(f"  STOPs:               {metrics['stop_count']:>8,}")
    print(f"  color blocks:        {metrics['color_blocks']:>8,}   "
          f"({metrics['unique_colors']} unique threads, "
          f"multi-pass ratio {metrics['multipass_ratio']:.2f}× — "
          f"pro 1.5–2.0×)")
    print()
    print(f"  stitch lengths (mm):")
    print(f"    mean    {metrics['mean_mm']:.2f}    "
          f"{format_targets_row('mean_mm', metrics['mean_mm'], TARGETS)}")
    print(f"    median  {metrics['median_mm']:.2f}")
    print(f"    p90     {metrics['p90_mm']:.2f}")
    print(f"    p95     {metrics['p95_mm']:.2f}")
    print(f"    p99     {metrics['p99_mm']:.2f}    "
          f"{format_targets_row('p99_mm', metrics['p99_mm'], TARGETS)}")
    print(f"    max     {metrics['max_mm']:.2f}")
    print(f"    >7mm    {metrics['long_count']} ({metrics['long_pct']:.2f}%)   "
          f"{format_targets_row('long_pct', metrics['long_pct'], TARGETS)}")
    print(f"    ~0mm    {metrics['zero_count']} ({metrics['zero_pct']:.2f}%)")
    print()
    print(f"  short jumps (<2mm):  {metrics['short_jumps']:>8,}   "
          f"{format_targets_row('short_jumps', metrics['short_jumps'], TARGETS)}")
    print(f"  long jumps (>=15mm): {metrics['long_jumps']:>8,}")
    print(f"  jump travel:         total {metrics['jump_total_mm']:.1f} mm   "
          f"mean {metrics['jump_mean_mm']:.1f} mm   p95 {metrics['jump_p95_mm']:.1f} mm   "
          f"max {metrics['jump_max_mm']:.1f} mm")
    print(f"  jumps by length:     >=15mm {metrics['jumps_ge_15mm']:>5}   "
          f">=30mm {metrics['jumps_ge_30mm']:>5}   >=50mm {metrics['jumps_ge_50mm']:>5}")
    print()
    print(f"  bbox:                {metrics['bbox_w_mm']:.1f} × {metrics['bbox_h_mm']:.1f} mm   "
          f"area: {metrics['area_cm2']:.1f} cm²")
    print(f"  density:             {metrics['density_per_cm2']:.0f} stitches/cm²   "
          f"{format_targets_row('density_per_cm2', metrics['density_per_cm2'], TARGETS)}")


def report_group_summary(groups: list) -> None:
    rows = summarize_groups(groups)
    if not rows:
        return
    print()
    print("  source stages:")
    print("    pass  role          type      groups  segments    points  comps  gap>8  gap>12")
    for row in rows:
        print(
            f"    {str(row['pass']):>4}  {row['role']:<12}  {row['type']:<8}"
            f"  {row['groups']:>6}  {row['segments']:>8,}  {row['points']:>8,}"
            f"  {row['components']:>5}  {row['gaps_gt_8mm']:>5}  {row['gaps_gt_12mm']:>6}"
        )


def main():
    image_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TEST_IMAGE
    if not image_path.exists():
        print(f"NOT FOUND: {image_path}", file=sys.stderr)
        sys.exit(2)

    print(f"Test image: {image_path}")
    print(f"Size: {image_path.stat().st_size:,} bytes")

    result = run_pipeline(image_path)
    print(f"\nGenerated {result['stitch_count_logical']:,} logical stitches in "
          f"{result['generation_time_s']:.2f}s + {result['build_time_s']:.2f}s build")

    metrics = measure(result["pattern"])
    report(metrics, label=str(image_path.name))
    report_group_summary(result["groups"])


if __name__ == "__main__":
    main()
