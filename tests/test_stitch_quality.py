"""
Regression test: stitch quality should not slip below Tier 1 thresholds.

Run from repo root with:
    source files/.venv/bin/activate
    python tests/test_stitch_quality.py

Returns non-zero exit on any failure. Each fixture runs the full pipeline
(image -> raster_to_stitch_groups -> _build_pattern -> JEF round-trip)
then checks the measured metrics against the Tier 1 targets from
STITCH_IMPROVEMENTS.md.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))

from benchmark_stitch import run_pipeline, measure  # noqa: E402

# (label, image_path, target_overrides) — overrides relax specific thresholds
# for fixtures that legitimately can't hit Tier 1 (e.g. sunflower has many
# disconnected yellow petals that produce unavoidable cross-component jumps).
FIXTURES = [
    {
        "label":   "sunflower",
        "image":   ROOT / "public" / "library" / "sunflower" / "image.png",
        "targets": {
            "mean_mm":         (1.5, 2.5),
            "p99_mm":          (None, 5.0),
            # Tier 4.1 satin allows bars up to MAX_SATIN_BAR_MM = 8 mm; some
            # naturally fall in the 7–8 mm range and count as "long".
            "long_pct":        (None, 0.5),
            # Sunflower has many disconnected yellow petals separated by
            # > 8mm gaps. Pro hand-routing can hit 1%; auto-conversion sits
            # ~3%, with branch walking on each petal adding a small extra.
            "jump_pct":        (None, 3.5),
            "short_jumps":     (None, 200),
            "density_per_cm2": (None, 250),
            # Selective outlines now avoid outlining every posterized colour;
            # pro files range from single-use colours to repeated detail stops.
            "multipass_ratio": (1.0, 3.0),
        },
        "pipeline_args": {},
    },
    {
        "label":   "test_shapes",
        "image":   Path("/tmp/test_shapes.png"),
        "targets": {
            # Test shapes are large simple polygons; means run higher because
            # the fills are dominated by edge-walk runs at full 4 mm step.
            "mean_mm":         (None, 4.0),
            "p99_mm":          (None, 5.0),
            "long_pct":        (None, 0.20),
            "jump_pct":        (None, 2.0),
            "short_jumps":     (None, 200),
            "density_per_cm2": (None, 250),
            "multipass_ratio": (1.0, 3.0),
        },
        "pipeline_args": {},
    },
    {
        "label":   "layered_accents",
        "image":   Path("/tmp/layered_test.png"),
        "targets": {
            "mean_mm":         (None, 4.0),
            "p99_mm":          (None, 5.0),
            "long_pct":        (None, 0.20),
            # Black accents trigger long-distance jumps between tiny features.
            "jump_pct":        (None, 3.0),
            "short_jumps":     (None, 200),
            "density_per_cm2": (None, 250),
            # Should still reintroduce detail/accent colours without outlining
            # every fill colour.
            "multipass_ratio": (1.5, 3.0),
        },
        "pipeline_args": {"num_colors": 5},
    },
    {
        "label":   "narrow_satin",
        "image":   Path("/tmp/narrow_test.png"),
        "targets": {
            # Satin columns produce longer individual stitches (each bar IS
            # one stitch). Mean and p99 run higher than tatami fills.
            "mean_mm":         (None, 4.0),
            "p99_mm":          (None, 6.0),       # satin allows up to 8mm bars
            "long_pct":        (None, 0.50),      # some bars slightly > 7mm OK
            "jump_pct":        (None, 3.0),
            "short_jumps":     (None, 200),
            "density_per_cm2": (None, 250),
            "multipass_ratio": (1.0, 3.0),
        },
        "pipeline_args": {"num_colors": 4},
    },
    {
        "label":   "letterforms",
        "image":   Path("/tmp/letterform_test.png"),
        "targets": {
            # Each letterform has a Y-junction or T-junction in its medial
            # axis; trail decomposition must walk every branch (not just
            # the longest one). Failure mode: missing satin bars on side
            # strokes leaves visible empty patches → density drops far
            # below the floor (the letters are spread across the canvas
            # so bbox-based density is naturally low; absent branch
            # walking it would crash to ~10/cm²).
            "mean_mm":         (None, 4.0),
            "p99_mm":          (None, 6.0),
            "long_pct":        (None, 0.50),
            "jump_pct":        (None, 4.0),
            "short_jumps":     (None, 200),
            "density_per_cm2": (30, 250),
            "multipass_ratio": (1.0, 3.0),
        },
        "pipeline_args": {"num_colors": 4},
    },
]


def _make_test_shapes_if_missing():
    """Generate /tmp/test_shapes.png if it doesn't exist."""
    from PIL import Image, ImageDraw

    p = Path("/tmp/test_shapes.png")
    if not p.exists():
        img = Image.new('RGB', (400, 400), '#f5f0eb')
        d = ImageDraw.Draw(img)
        d.ellipse([60, 60, 180, 180], fill='#d0413f')
        d.polygon([(220, 80), (320, 100), (340, 200), (260, 220), (210, 160)], fill='#3a7a4a')
        d.rectangle([60, 220, 200, 320], fill='#2a508c')
        d.polygon([(240, 240), (340, 320), (240, 320)], fill='#e8c020')
        d.line([(60, 350), (340, 350)], fill='#1a1a1a', width=4)
        img.save(p)

    # Layered accent fixture (tests Tier 2 detail + accent passes)
    p = Path("/tmp/layered_test.png")
    if not p.exists():
        img = Image.new('RGB', (400, 400), '#f5f0eb')
        d = ImageDraw.Draw(img)
        # Big gold body + tiny gold corner dots (detail accents same colour)
        d.ellipse([100, 80, 280, 220], fill='#e8c020')
        d.ellipse([60, 60, 75, 75], fill='#e8c020')
        d.ellipse([320, 60, 335, 75], fill='#e8c020')
        d.ellipse([60, 320, 75, 335], fill='#e8c020')
        # Big green leaf
        d.polygon([(90, 240), (200, 260), (220, 360), (140, 380)], fill='#3a7a4a')
        # Big blue rectangle
        d.rectangle([260, 250, 360, 350], fill='#2a508c')
        # Tiny black accents — under 8% of pixels
        d.ellipse([170, 130, 185, 145], fill='#0c0c0c')
        d.ellipse([200, 130, 215, 145], fill='#0c0c0c')
        d.line([(165, 175), (215, 175)], fill='#0c0c0c', width=3)
        img.save(p)

    # Narrow shape fixture (tests Tier 4.1 satin columns)
    p = Path("/tmp/narrow_test.png")
    if not p.exists():
        import math
        img = Image.new('RGB', (400, 400), '#f5f0eb')
        d = ImageDraw.Draw(img)
        # Vertical narrow stem
        d.rectangle([195, 100, 213, 320], fill='#3a7a4a')
        # Diagonal narrow stripe
        d.polygon([(60, 80), (75, 80), (180, 280), (165, 280)], fill='#2a508c')
        # Curved narrow C-shape
        cx, cy = 320, 200
        pts = []
        for theta_deg in range(-90, 91, 3):
            theta = math.radians(theta_deg)
            pts.append((cx + 80 * math.cos(theta), cy + 80 * math.sin(theta)))
        for theta_deg in range(90, -91, -3):
            theta = math.radians(theta_deg)
            pts.append((cx + 60 * math.cos(theta), cy + 60 * math.sin(theta)))
        d.polygon(pts, fill='#d0413f')
        img.save(p)

    # Letterform fixture (tests Tier 4.1 trail decomposition / branch walking)
    p = Path("/tmp/letterform_test.png")
    if not p.exists():
        img = Image.new('RGB', (400, 400), '#f5f0eb')
        d = ImageDraw.Draw(img)
        # T-shape (medial axis has a 3-way junction)
        d.rectangle([60, 60, 180, 78], fill='#3a7a4a')
        d.rectangle([110, 60, 130, 200], fill='#3a7a4a')
        # Y-shape approximation (one junction, three branches)
        d.polygon([(220, 60), (260, 60), (290, 130), (300, 130), (260, 60), (300, 60),
                   (300, 60), (260, 130), (260, 200), (240, 200), (240, 130), (220, 60)],
                  fill='#2a508c')
        # Plus / cross (two perpendicular bars meeting at centre)
        d.rectangle([280, 240, 360, 258], fill='#d0413f')
        d.rectangle([311, 220, 329, 290], fill='#d0413f')
        img.save(p)


def check_metric(value, lo, hi):
    if lo is not None and value < lo:
        return False, f"below floor {lo}"
    if hi is not None and value > hi:
        return False, f"over ceiling {hi}"
    return True, "ok"


def run():
    _make_test_shapes_if_missing()

    failures = []
    for fixture in FIXTURES:
        label = fixture["label"]
        image = fixture["image"]
        targets = fixture["targets"]
        pipeline_args = fixture.get("pipeline_args", {})

        print(f"\n[{label}]  {image.name}")
        if not image.exists():
            print(f"  SKIP (image not found)")
            continue

        result = run_pipeline(image, **pipeline_args)
        m = measure(result["pattern"])

        all_ok = True
        for metric, (lo, hi) in targets.items():
            v = m[metric]
            ok, reason = check_metric(v, lo, hi)
            target = (
                f"{lo}-{hi}" if lo is not None and hi is not None
                else f"≤{hi}" if hi is not None
                else f"≥{lo}"
            )
            mark = "✓" if ok else "✗"
            print(f"  {mark} {metric:18s} = {v:8.2f}   target {target}")
            if not ok:
                failures.append((label, metric, v, target, reason))
                all_ok = False
        if all_ok:
            print(f"  → PASS  ({m['stitch_count']} stitches, {m['jump_count']} jumps)")

    if failures:
        print(f"\n{'='*60}\nFAILED ({len(failures)} metric violations):")
        for label, metric, v, target, reason in failures:
            print(f"  {label}.{metric} = {v} ({reason}, target {target})")
        sys.exit(1)
    print(f"\n{'='*60}\nALL FIXTURES PASS")


if __name__ == "__main__":
    run()
