"""
Text-to-embroidery engine: converts text into satin-stitched JEF files.

Uses Hershey vector fonts (public domain single-stroke fonts) as the
letterform source, then generates satin column stitches by buffering
each stroke into left/right rails and zigzagging between them.

Quality improvements over baseline:
- 3-pass underlay: center-walk + zigzag before top satin
- Denser default satin spacing (0.25mm vs 0.35mm)
- Auto satin width scaled to font height
- Wider normal smoothing window for rounder curves
- Adaptive stitch width reduction at tight curves
"""

import math
import numpy as np
from HersheyFonts import HersheyFonts
from shapely.geometry import LineString
import pyembroidery


# ── Font helpers ──────────────────────────────────────────────────────

FONT_ALIASES = {
    # Script / Cursive
    'script':       'scriptc',   # Script complex (connected cursive)
    'script2':      'scripts',   # Script simplex (lighter cursive)
    'cursive':      'timesib',   # Times Italic Bold (elegant, distinct from script)
    # Sans-Serif
    'sans':         'futural',   # Futura light (thin strokes)
    'sans-bold':    'futuram',   # Futura medium (thicker, better small size)
    # Serif
    'serif':        'rowmans',   # Roman simplex (single-stroke serif)
    'serif-medium': 'rowmant',   # Roman triplex (medium weight)
    'serif-bold':   'rowmand',   # Roman duplex (bold serif)
    # Times
    'italic':       'timesi',    # Times italic
    'times':        'timesr',    # Times Roman
    'times-bold':   'timesrb',   # Times Bold
    # Display / Gothic
    'gothic':         'gothgbt',    # Gothic German block
    'gothic-italic':  'gothitt',    # Gothic Italian triplex
    'gothic-eng':     'gothiceng',  # Gothic English (Old English blackletter)
    'gothic-ger':     'gothicger',  # Gothic German (angular blackletter)
    'gothic-ita':     'gothicita',  # Gothic Italian (rounded blackletter)
    'gothic-round':   'gothgrt',    # Gothic German Round (softer strokes)
}

def available_fonts():
    """Return dict of user-friendly name -> hershey internal name."""
    return dict(FONT_ALIASES)


def _make_hf(font_name, height_mm):
    """Create a normalized HersheyFonts instance (helper)."""
    internal = FONT_ALIASES.get(font_name, font_name)
    hf = HersheyFonts()
    hf.load_default_font(internal)
    hf.normalize_rendering(height_mm)
    return hf


def _char_strokes_and_advance(char, hf):
    """Return (strokes_mm, advance_mm) for a single character.

    strokes_mm: list of np.array shape (N,2), Y-flipped.
    advance_mm: the natural x-advance for the glyph.
    """
    raw = list(hf.strokes_for_text(char))
    strokes = []
    x_max = 0.0
    x_min = float('inf')
    for stroke in raw:
        pts = [(x, -y) for x, y in stroke]
        if len(pts) >= 2:
            arr = np.array(pts, dtype=float)
            strokes.append(arr)
            x_max = max(x_max, arr[:, 0].max())
            x_min = min(x_min, arr[:, 0].min())
    # Natural advance: width of whole-text render minus a space-like offset
    # Use the space character width as the advance for spaces
    advance = x_max if strokes else x_max
    # For strokes, measure from left edge of glyph box
    x_left = x_min if strokes else 0.0
    return strokes, x_left, x_max


def get_text_strokes(text, font_name='script', height_mm=15.0, spacing_factor=1.0):
    """Extract stroke polylines for a text string with optional letter spacing.

    Returns list of numpy arrays, each shape (N, 2) in mm coordinates,
    with Y flipped for embroidery (positive Y = down).

    spacing_factor=1.0 is natural spacing; <1 tighter, >1 wider.
    Spacing is applied by scaling x-coordinates relative to the left edge.
    """
    hf = _make_hf(font_name, height_mm)

    # Render naturally (always use the library's native layout)
    strokes = []
    for stroke in hf.strokes_for_text(text):
        pts = [(x, -y) for x, y in stroke]
        if len(pts) >= 2:
            strokes.append(np.array(pts, dtype=float))

    if not strokes or spacing_factor == 1.0:
        return strokes

    # Scale x-coordinates relative to the leftmost point so spacing widens/tightens
    x_min = min(float(arr[:, 0].min()) for arr in strokes)
    result = []
    for arr in strokes:
        scaled = arr.copy()
        scaled[:, 0] = x_min + (arr[:, 0] - x_min) * spacing_factor
        result.append(scaled)
    return result


def get_text_width(text, font_name='script', height_mm=15.0, spacing_factor=1.0):
    """Get total width of rendered text in mm."""
    strokes = get_text_strokes(text, font_name, height_mm, spacing_factor)
    if not strokes:
        return 0.0
    all_pts = np.vstack(strokes)
    return float(all_pts[:, 0].max() - all_pts[:, 0].min())


# ── Geometry utilities ────────────────────────────────────────────────

def resample_line(points, spacing):
    """Resample a polyline to evenly spaced points."""
    line = LineString(points)
    if line.length < spacing * 0.5:
        return np.array(points[:2])
    num = max(3, round(line.length / spacing))
    result = []
    for i in range(num + 1):
        pt = line.interpolate(i / num, normalized=True)
        result.append([pt.x, pt.y])
    return np.array(result)


def compute_normals(pts):
    """Compute unit perpendicular normals at each point of a polyline.

    For closed strokes (end ≈ start, like the letter 'O') uses centroid-based
    outward normals which are perfectly smooth around circles and prevent the
    starburst artifacts caused by tangent-flip at the join point.
    For open strokes uses central-difference tangents as before.
    """
    n = len(pts)

    # Detect closed stroke: endpoints within 2 mm of each other
    closed = np.linalg.norm(pts[-1] - pts[0]) < 2.0

    if closed and n >= 6:
        centroid = pts.mean(axis=0)
        diff = pts - centroid
        lengths = np.linalg.norm(diff, axis=1, keepdims=True)
        lengths = np.maximum(lengths, 1e-8)
        return diff / lengths   # outward normals from centroid

    tangents = np.zeros_like(pts)
    tangents[0] = pts[min(1, n-1)] - pts[0]
    tangents[-1] = pts[-1] - pts[max(0, n-2)]
    for i in range(1, n - 1):
        tangents[i] = pts[i + 1] - pts[i - 1]

    lengths = np.linalg.norm(tangents, axis=1, keepdims=True)
    lengths = np.maximum(lengths, 1e-8)
    tangents = tangents / lengths

    # 90-degree rotation -> normals
    normals = np.column_stack([-tangents[:, 1], tangents[:, 0]])
    return normals


def smooth_array(arr, window=7):
    """Apply simple moving average smoothing with wider window for rounder curves."""
    if len(arr) <= window:
        return arr
    kernel = np.ones(window) / window
    smoothed = np.copy(arr)
    for col in range(arr.shape[1]):
        smoothed[:, col] = np.convolve(arr[:, col], kernel, mode='same')
    lengths = np.linalg.norm(smoothed, axis=1, keepdims=True)
    lengths = np.maximum(lengths, 1e-8)
    return smoothed / lengths


def clamp_normals(normals, max_angle_rad=0.18):
    """Clamp consecutive normal direction changes to prevent starburst artifacts.

    Uses a bidirectional pass (forward then backward) so that both endpoints
    and both sides of sharp corners are smoothed equally.  The tighter default
    angle (0.18 rad ≈ 10°, down from 0.25) gives crisper corners on T, L, F
    without introducing new artifacts on curves.
    """
    def _single_pass(arr, forward=True):
        result = arr.copy()
        indices = range(1, len(arr)) if forward else range(len(arr) - 2, -1, -1)
        prev_idx = lambda i: i - 1 if forward else i + 1
        for i in indices:
            p = prev_idx(i)
            dot = float(np.clip(np.dot(result[p], arr[i]), -1.0, 1.0))
            angle = np.arccos(dot)
            if angle > max_angle_rad:
                t = max_angle_rad / angle
                blended = result[p] * (1.0 - t) + arr[i] * t
                norm = np.linalg.norm(blended)
                result[i] = blended / max(norm, 1e-8)
            else:
                result[i] = arr[i]
        return result

    # Forward pass: propagates smoothness left→right
    clamped = _single_pass(normals, forward=True)
    # Backward pass: catches starburst at the end of each stroke (right→left)
    clamped = _single_pass(clamped, forward=False)
    return clamped


def taper_scale(i, n, taper_frac=0.18, min_scale=0.25,
                taper_start=True, taper_end=True):
    """Return a width scale factor (0.25–1.0) that tapers satin near stroke ends.

    Without tapering, each stroke endpoint produces a starburst because all the
    satin lines radiate from the same tip.  Tapering reduces satin width smoothly
    from *min_scale* at the very end to 1.0 in the body of the stroke.

    taper_start / taper_end: set False when this stroke end meets another stroke
    (a junction).  At junctions the satin should run full-width so the two
    strokes blend flush rather than leaving a gap.
    """
    taper_n = max(2, int(n * taper_frac))
    if taper_start and i < taper_n:
        return min_scale + (1.0 - min_scale) * (i / taper_n)
    if taper_end and i >= n - taper_n:
        return min_scale + (1.0 - min_scale) * ((n - 1 - i) / taper_n)
    return 1.0


# ── Quality constants ─────────────────────────────────────────────────

# Strokes shorter than this are skipped entirely — too short to stitch cleanly.
MIN_STROKE_MM = 0.4

# Strokes shorter than this are rendered as compact satin dots (no column underlay).
# Covers i-dots, j-dots, periods, colons, diacritics.
DOT_THRESHOLD_MM = 2.0

# Underlays add bulk and stiffness; they help large fills but hurt small text.
# Skip the 2-pass underlay for text below this height.
UNDERLAY_MIN_HEIGHT_MM = 10.0

# Connect strokes with a running stitch bridge instead of TRIM when they are
# this close together — reduces thread tails and sew time.
JUMP_THRESHOLD_MM = 3.0


def auto_density(height_mm):
    """Return appropriate satin density for a given font height (mm).

    Small text needs tighter stitching to retain detail; large text can use
    looser spacing.  Range is 0.18–0.38mm — outside that range thread quality
    degrades (too tight → puckers/breaks; too loose → gaps show).

    Examples:  8mm → 0.18mm   15mm → 0.25mm   25mm → 0.35mm
    """
    return round(max(0.18, min(0.38, 0.10 + height_mm * 0.010)), 3)


def auto_satin_width(height_mm):
    """Return appropriate satin column width for a given font height (mm).

    Uses a piecewise curve so that:
    - Small text (<= 10mm): wider relative to height for better stitch visibility
    - Mid range (10–22mm): smooth linear growth
    - Large text (> 22mm): plateau at 2.0mm — beyond this columns look baggy
      and the machine has trouble maintaining thread tension

    Examples:  6mm → 0.80mm   12mm → 1.05mm   18mm → 1.55mm   30mm → 2.00mm
    """
    if height_mm <= 10.0:
        # Slightly more generous coefficient for small text (visibility)
        return round(max(0.80, height_mm * 0.092), 2)
    elif height_mm <= 22.0:
        return round(max(0.80, height_mm * 0.086), 2)
    else:
        # Plateau — prevents overly thick columns on large display text
        return round(min(2.00, 0.80 + height_mm * 0.057), 2)


# ── Stitch generation ─────────────────────────────────────────────────

def generate_underlay(points, stitch_length_mm=2.5):
    """Center-walk underlay: walk the stroke centerline forward and back.
    Stabilizes fabric position before the satin stitches."""
    line = LineString(points)
    num = max(2, int(line.length / stitch_length_mm))

    forward = []
    for i in range(num + 1):
        pt = line.interpolate(i / num, normalized=True)
        forward.append((pt.x, pt.y))

    back = list(reversed(forward))
    return forward + back


def generate_zigzag_underlay(points, satin_width_mm=1.2, stitch_length_mm=1.5):
    """Zigzag edge-walk underlay: alternates left/right at 60% of satin width.

    Runs along the stroke path, building up fabric loft under the satin.
    This is the second underlay pass, placed between center-walk and top satin.
    60% width keeps it well inside the final satin column edges.
    """
    pts = resample_line(points, stitch_length_mm)
    if len(pts) < 2:
        return []

    half_w = satin_width_mm * 0.30   # 60% total / 2
    normals = compute_normals(pts)
    normals = smooth_array(normals, window=5)

    stitches = []
    for i in range(len(pts)):
        x, y = pts[i]
        nx, ny = normals[i]
        if i % 2 == 0:
            stitches.append((x + nx * half_w, y + ny * half_w))
        else:
            stitches.append((x - nx * half_w, y - ny * half_w))
    return stitches


def generate_satin(points, width_mm=1.2, spacing_mm=0.25, pull_comp_mm=0.1,
                   taper_start=True, taper_end=True):
    """Generate satin column stitches along a stroke path.

    Creates a zigzag pattern by alternating between left and right sides
    of the stroke, perpendicular to the path direction.

    Args:
        points:        Stroke centerline as (N, 2) array in mm
        width_mm:      Total satin column width
        spacing_mm:    Distance between stitch points along the path (0.25 = dense)
        pull_comp_mm:  Extra width to compensate for thread tension
        taper_start:   Whether to taper width at the stroke start
        taper_end:     Whether to taper width at the stroke end
    """
    pts = resample_line(points, spacing_mm)
    if len(pts) < 3:
        return []

    half_w = (width_mm / 2.0) + pull_comp_mm

    # Wider smoothing window (7) for rounder letterforms
    normals = compute_normals(pts)
    normals = smooth_array(normals, window=7)
    normals = clamp_normals(normals)   # prevent starburst at endpoints/curves

    n = len(pts)
    stitches = []
    for i in range(n):
        x, y = pts[i]
        nx, ny = normals[i]
        w = half_w * taper_scale(i, n, taper_start=taper_start, taper_end=taper_end)

        if i % 2 == 0:
            stitches.append((x + nx * w, y + ny * w))
        else:
            stitches.append((x - nx * w, y - ny * w))

    return stitches


# ── Pattern assembly ──────────────────────────────────────────────────

def _sort_strokes_nearest_neighbor(strokes):
    """Greedy nearest-neighbor sort to minimise travel distance between strokes.

    Starting from the first stroke, each subsequent stroke is chosen as the one
    whose start point is closest to the end point of the previous stroke.
    This reduces the number of long jumps and thread tails in the final file.
    """
    if len(strokes) <= 1:
        return strokes
    remaining = list(strokes)
    sorted_strokes = [remaining.pop(0)]
    while remaining:
        last_end = sorted_strokes[-1][-1]   # endpoint of last stroke
        dists = [np.linalg.norm(s[0] - last_end) for s in remaining]
        nearest = int(np.argmin(dists))
        sorted_strokes.append(remaining.pop(nearest))
    return sorted_strokes


def _lock_stitches(pt, direction_pt, n=2, dist_mm=0.4):
    """Return n tiny lock-stitch points stepping away from pt toward direction_pt.

    These micro-stitches (0.4mm) anchor the thread at the start or end of a
    satin pass so it cannot unravel when the machine trims.  Apply 2 stitches
    going *away* from the pass, then return to the original point.
    """
    dx = pt[0] - direction_pt[0]
    dy = pt[1] - direction_pt[1]
    length = max(math.sqrt(dx * dx + dy * dy), 1e-8)
    ux, uy = dx / length, dy / length
    lock_pts = [(pt[0] + ux * dist_mm * (i + 1),
                 pt[1] + uy * dist_mm * (i + 1)) for i in range(n)]
    return lock_pts + [pt]   # step away, then return to anchor point


def _emit_stitches(pattern, stitch_list, first_ref):
    """Write a list of (x, y) mm coords to the pattern with TRIM before first."""
    for j, (x, y) in enumerate(stitch_list):
        x10, y10 = round(x * 10), round(y * 10)
        if first_ref[0]:
            pattern.add_stitch_absolute(pyembroidery.STITCH, x10, y10)
            first_ref[0] = False
        elif j == 0:
            pattern.add_stitch_absolute(pyembroidery.TRIM, x10, y10)
        else:
            pattern.add_stitch_absolute(pyembroidery.STITCH, x10, y10)


def _add_stroke_to_pattern(pattern, stroke_pts, satin_width_mm, density_mm,
                            first_ref, height_mm=15.0,
                            taper_start=True, taper_end=True):
    """Add a single stroke to the pattern with quality-adaptive passes.

    Quality improvements:
    - Minimum stroke filter: skip strokes too short to stitch cleanly
    - Dot handling: short strokes (i-dots, periods) → compact satin, no underlay
    - Small text (<10mm): skip 2-pass underlay to reduce bulk/puckering
    - Large text (≥10mm): full 3-pass: center-walk + zigzag + top satin
    - Lock stitches: tie-in + tie-off on the top satin pass to prevent unraveling
    - Junction-aware taper: suppress taper at ends that connect to adjacent strokes
    """
    if len(stroke_pts) < 2:
        return

    stroke_len = LineString(stroke_pts).length

    # ── #2 Minimum stroke filter ──────────────────────────────────────
    if stroke_len < MIN_STROKE_MM:
        return   # too short to stitch; would cause needle tangles

    # ── #1 Short-stroke / dot handling ───────────────────────────────
    # i-dots, j-dots, periods, colons — skip underlay, widen satin.
    if stroke_len < DOT_THRESHOLD_MM:
        dot_width = max(satin_width_mm * 1.3, stroke_len * 1.2)
        satin = generate_satin(stroke_pts, dot_width, density_mm)
        if satin:
            tie_in  = _lock_stitches(satin[0],  satin[min(1, len(satin)-1)])
            tie_off = _lock_stitches(satin[-1], satin[max(0, len(satin)-2)])
            _emit_stitches(pattern, tie_in + satin + tie_off, first_ref)
        pattern.add_command(pyembroidery.TRIM)
        return

    # ── Normal stroke handling ────────────────────────────────────────
    use_underlay = height_mm >= UNDERLAY_MIN_HEIGHT_MM

    if use_underlay:
        # Pass 1: center-walk underlay — stabilises fabric along the stroke axis
        underlay = generate_underlay(stroke_pts, stitch_length_mm=2.5)
        _emit_stitches(pattern, underlay, first_ref)

        # Pass 2: zigzag underlay — builds loft under the satin column
        zigzag = generate_zigzag_underlay(stroke_pts, satin_width_mm, stitch_length_mm=1.5)
        _emit_stitches(pattern, zigzag, first_ref)

    # ── #6 Top satin with tie-in / tie-off lock stitches ─────────────
    satin = generate_satin(stroke_pts, satin_width_mm, density_mm,
                           taper_start=taper_start, taper_end=taper_end)
    if satin:
        tie_in  = _lock_stitches(satin[0],  satin[min(1, len(satin)-1)])
        tie_off = _lock_stitches(satin[-1], satin[max(0, len(satin)-2)])
        _emit_stitches(pattern, tie_in + satin + tie_off, first_ref)
    pattern.add_command(pyembroidery.TRIM)


JUNCTION_THRESHOLD_MM = 1.5   # endpoints closer than this are treated as connected

def _run_strokes(pattern, strokes, satin_width_mm, density_mm, first_ref, height_mm):
    """Emit a list of strokes with #7 jump-stitch routing and #10 junction taper.

    Jump routing: short gaps (≤ JUMP_THRESHOLD_MM) get a running-stitch bridge
    instead of TRIM — fewer thread tails, faster sew time.

    Junction taper (#10): when a stroke end is within JUNCTION_THRESHOLD_MM of
    the next stroke start, taper is suppressed at that end so both strokes meet
    flush (full-width) rather than leaving a thin gap.
    """
    # Pre-compute which ends are "connected" to the next stroke
    n = len(strokes)
    start_tapers = [True] * n    # suppress start taper when connected to prev
    end_tapers   = [True] * n    # suppress end taper when connected to next

    for i in range(n - 1):
        if len(strokes[i]) < 2 or len(strokes[i + 1]) < 2:
            continue
        gap = float(np.linalg.norm(strokes[i][-1] - strokes[i + 1][0]))
        if gap <= JUNCTION_THRESHOLD_MM:
            end_tapers[i]      = False   # this stroke ends at a junction
            start_tapers[i + 1] = False  # next stroke starts at that junction

    last_end = None
    for idx, stroke_pts in enumerate(strokes):
        if len(stroke_pts) < 2:
            continue
        stroke_start = stroke_pts[0]

        if last_end is not None and not first_ref[0]:
            gap = float(np.linalg.norm(stroke_start - last_end))
            if gap <= JUMP_THRESHOLD_MM:
                # Bridge with one running stitch at the midpoint
                mid = (last_end + stroke_start) / 2.0
                pattern.add_stitch_absolute(
                    pyembroidery.STITCH,
                    round(float(mid[0]) * 10), round(float(mid[1]) * 10)
                )
            else:
                pattern.add_command(pyembroidery.TRIM)

        _add_stroke_to_pattern(pattern, stroke_pts, satin_width_mm, density_mm,
                               first_ref, height_mm=height_mm,
                               taper_start=start_tapers[idx],
                               taper_end=end_tapers[idx])
        last_end = stroke_pts[-1]


def text_to_pattern(text, font_name='script', height_mm=15.0,
                    satin_width_mm=None, density_mm=None,
                    thread_color=0xFF0000, spacing_factor=1.0):
    """Convert a single line of text to an EmbPattern.

    Returns (pattern, width_mm, height_mm).
    satin_width_mm and density_mm both default to auto (scaled to height).
    """
    if satin_width_mm is None:
        satin_width_mm = auto_satin_width(height_mm)
    if density_mm is None:
        density_mm = auto_density(height_mm)

    strokes = get_text_strokes(text, font_name, height_mm, spacing_factor)
    if not strokes:
        return None, 0, 0

    pattern = pyembroidery.EmbPattern()
    pattern.add_thread(pyembroidery.EmbThread(thread_color))

    first_ref = [True]
    strokes = _sort_strokes_nearest_neighbor(strokes)   # #8 sequencing
    _run_strokes(pattern, strokes, satin_width_mm, density_mm, first_ref, height_mm)

    pattern.add_command(pyembroidery.END)

    bounds = pattern.bounds()
    w = (bounds[2] - bounds[0]) / 10.0
    h = (bounds[3] - bounds[1]) / 10.0
    return pattern, w, h


def multiline_to_pattern(lines, font_name='script', height_mm=15.0,
                         line_spacing_factor=1.6, align='center',
                         satin_width_mm=None, density_mm=None,
                         thread_color=0xFF0000, spacing_factor=1.0):
    """Convert multiple lines of text to a single centered EmbPattern."""
    if satin_width_mm is None:
        satin_width_mm = auto_satin_width(height_mm)
    if density_mm is None:
        density_mm = auto_density(height_mm)

    line_spacing = height_mm * line_spacing_factor

    widths = [get_text_width(line, font_name, height_mm, spacing_factor) for line in lines]
    max_width = max(widths) if widths else 0

    combined = pyembroidery.EmbPattern()
    combined.add_thread(pyembroidery.EmbThread(thread_color))

    first_ref = [True]

    for line_idx, text in enumerate(lines):
        if not text.strip():
            continue

        strokes = get_text_strokes(text, font_name, height_mm, spacing_factor)
        if not strokes:
            continue

        y_offset = line_idx * line_spacing

        if align == 'center':
            x_offset = (max_width - widths[line_idx]) / 2.0
        elif align == 'right':
            x_offset = max_width - widths[line_idx]
        else:
            x_offset = 0.0

        shifted_strokes = []
        for stroke_pts in strokes:
            if len(stroke_pts) < 2:
                continue
            s = stroke_pts.copy()
            s[:, 0] += x_offset
            s[:, 1] += y_offset
            shifted_strokes.append(s)

        shifted_strokes = _sort_strokes_nearest_neighbor(shifted_strokes)  # #8
        _run_strokes(combined, shifted_strokes, satin_width_mm, density_mm,
                     first_ref, height_mm)

    combined.add_command(pyembroidery.END)
    return combined


def generate_preview_svg(lines_text, font_name='script', height_mm=15.0,
                         line_spacing_factor=1.6, align='center',
                         satin_width_mm=None, density_mm=None,
                         thread_color='#cc0000', width_px=700):
    """Generate an SVG preview that simulates the stitched appearance."""
    if satin_width_mm is None:
        satin_width_mm = auto_satin_width(height_mm)
    if density_mm is None:
        density_mm = auto_density(height_mm)

    line_spacing = height_mm * line_spacing_factor

    all_strokes = []
    widths = [get_text_width(t, font_name, height_mm) for t in lines_text]
    max_width = max(widths) if widths else 0

    for line_idx, text in enumerate(lines_text):
        if not text.strip():
            continue
        strokes = get_text_strokes(text, font_name, height_mm)
        y_off = line_idx * line_spacing
        if align == 'center':
            x_off = (max_width - widths[line_idx]) / 2.0
        elif align == 'right':
            x_off = max_width - widths[line_idx]
        else:
            x_off = 0.0
        for s in strokes:
            shifted = s.copy()
            shifted[:, 0] += x_off
            shifted[:, 1] += y_off
            all_strokes.append(shifted)

    if not all_strokes:
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50"><text x="10" y="30" fill="#999">No text</text></svg>'

    all_pts = np.vstack(all_strokes)
    margin = satin_width_mm * 1.5
    x_min = all_pts[:, 0].min() - margin
    y_min = all_pts[:, 1].min() - margin
    x_max = all_pts[:, 0].max() + margin
    y_max = all_pts[:, 1].max() + margin
    w = x_max - x_min
    h = y_max - y_min

    scale = width_px / w if w > 0 else 1
    height_px = h * scale

    svg_lines = []
    for stroke_pts in all_strokes:
        if len(stroke_pts) < 2:
            continue
        pts = resample_line(stroke_pts, density_mm)
        if len(pts) < 3:
            continue
        half_w = (satin_width_mm / 2.0) + 0.1
        normals = compute_normals(pts)
        normals = smooth_array(normals, window=7)
        normals = clamp_normals(normals)   # prevent starburst

        # Build the zigzag thread path: left[0]→right[1]→left[2]→right[3]→...
        # This matches what embroidery viewers (StitchBuddy, etc.) render.
        n = len(pts)
        zigzag_pts = []
        for i in range(n):
            x, y = pts[i]
            nx, ny = normals[i]
            w = half_w * taper_scale(i, n)
            if i % 2 == 0:
                px = (x + nx * w - x_min) * scale
                py = (y + ny * w - y_min) * scale
            else:
                px = (x - nx * w - x_min) * scale
                py = (y - ny * w - y_min) * scale
            zigzag_pts.append(f'{px:.1f},{py:.1f}')

        if len(zigzag_pts) >= 2:
            pts_str = ' '.join(zigzag_pts)
            svg_lines.append(
                f'<polyline points="{pts_str}" '
                f'fill="none" stroke="{thread_color}" stroke-width="0.7" '
                f'stroke-linecap="round" stroke-linejoin="round"/>'
            )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width_px:.0f} {height_px:.0f}" '
        f'width="100%" preserveAspectRatio="xMidYMid meet">\n'
        f'  <rect width="100%" height="100%" fill="#f5f0e8" rx="6"/>\n'
        f'  {"".join(svg_lines)}\n'
        f'</svg>'
    )
    return svg


def generate_layout_svg(text_elements, hoop_w_mm, hoop_h_mm,
                        border_type='none', border_color='#111111',
                        border_points=None,
                        canvas_w_px=700):
    """Generate a full-layout stitch preview SVG.

    Positions each text element at its real canvas coordinates, draws the
    hoop background, and renders actual border stitch points as polylines.

    text_elements: list of dicts with keys:
        text, font, size_mm, x_px, y_px, color, density_mm
        x_px/y_px are canvas-pixel centres (4 px/mm).
    border_points: list of [x_mm, y_mm] pairs (pre-computed by JS engine).
    """
    PX_PER_MM = 4.0
    scale = canvas_w_px / hoop_w_mm
    canvas_h_px = hoop_h_mm * scale

    svg_parts = []

    # Background
    svg_parts.append(
        f'<rect width="{canvas_w_px}" height="{canvas_h_px:.0f}" '
        f'fill="#f5f0e8" rx="6"/>'
    )

    # Border — render real stitch points sent from the JS engine
    if border_points and border_type and border_type != 'none':
        is_satin = border_type == 'satin-outline'
        if is_satin:
            # Alternating zigzag pairs → render as polyline (already interleaved)
            svg_pts = ' '.join(
                f'{x_mm * scale:.1f},{y_mm * scale:.1f}'
                for x_mm, y_mm in border_points
            )
            svg_parts.append(
                f'<polyline points="{svg_pts}" fill="none" '
                f'stroke="{border_color}" stroke-width="1.2" '
                f'stroke-linecap="round" stroke-linejoin="round"/>'
            )
        else:
            # Running stitch / double-line / motif: draw as connected dot path
            svg_pts = ' '.join(
                f'{x_mm * scale:.1f},{y_mm * scale:.1f}'
                for x_mm, y_mm in border_points
            )
            sw   = 1.0
            dash = 'stroke-dasharray="3,3"' if border_type == 'running' else ''
            svg_parts.append(
                f'<polyline points="{svg_pts}" fill="none" '
                f'stroke="{border_color}" stroke-width="{sw}" '
                f'stroke-linecap="round" stroke-linejoin="round" {dash}/>'
            )

    # Text elements at actual positions
    for el in text_elements:
        lines = [l for l in el.get('text', '').split('\n') if l.strip()]
        if not lines:
            continue
        font_name      = el.get('font', 'script')
        height_mm      = float(el.get('size_mm', 12.0))
        color_hex      = el.get('color', '#4A3820')
        _d             = el.get('density_mm')
        density_mm     = float(_d) if _d is not None else None
        _sf            = el.get('spacing_factor')
        spacing_factor = float(_sf) if _sf is not None else 1.0
        x_mm = float(el.get('x_px', hoop_w_mm * PX_PER_MM / 2)) / PX_PER_MM
        y_mm = float(el.get('y_px', hoop_h_mm * PX_PER_MM / 2)) / PX_PER_MM

        satin_w  = auto_satin_width(height_mm)
        density  = density_mm if density_mm else auto_density(height_mm)
        spacing  = height_mm * 1.6

        for line_idx, text in enumerate(lines):
            strokes = get_text_strokes(text, font_name, height_mm, spacing_factor)
            if not strokes:
                continue
            tw = get_text_width(text, font_name, height_mm, spacing_factor)
            # Centre horizontally on x_mm, baseline at y_mm for each line
            x_off = x_mm - tw / 2.0
            y_off = y_mm + line_idx * spacing - (len(lines) - 1) * spacing / 2.0

            for stroke_pts in strokes:
                shifted = stroke_pts.copy()
                shifted[:, 0] += x_off
                shifted[:, 1] += y_off
                pts = resample_line(shifted, density)
                if len(pts) < 3:
                    continue
                half_w = (satin_w / 2.0) + 0.1
                normals = compute_normals(pts)
                normals = smooth_array(normals, window=7)
                normals = clamp_normals(normals)
                n = len(pts)
                zigzag = []
                for i in range(n):
                    x, y = pts[i]
                    nx, ny = normals[i]
                    w = half_w * taper_scale(i, n)
                    side = 1 if i % 2 == 0 else -1
                    px = (x + side * nx * w) * scale
                    py = (y + side * ny * w) * scale
                    zigzag.append(f'{px:.1f},{py:.1f}')
                if len(zigzag) >= 2:
                    svg_parts.append(
                        f'<polyline points="{" ".join(zigzag)}" '
                        f'fill="none" stroke="{color_hex}" stroke-width="0.8" '
                        f'stroke-linecap="round" stroke-linejoin="round"/>'
                    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {canvas_w_px} {canvas_h_px:.0f}" '
        f'width="100%" preserveAspectRatio="xMidYMid meet">'
        + ''.join(svg_parts) +
        '</svg>'
    )


def save_pattern(pattern, output_path):
    """Save pattern as JEF (and PNG preview)."""
    pattern = pyembroidery.EmbPattern.get_normalized_pattern(pattern)
    pyembroidery.write_jef(pattern, output_path)

    png_path = output_path.rsplit('.', 1)[0] + '.png'
    pyembroidery.write_png(pattern, png_path)

    bounds = pattern.bounds()
    w_mm = (bounds[2] - bounds[0]) / 10.0
    h_mm = (bounds[3] - bounds[1]) / 10.0
    stitch_count = len([s for s in pattern.stitches
                        if s[2] == pyembroidery.STITCH])

    return {
        'jef_path': output_path,
        'png_path': png_path,
        'width_mm': w_mm,
        'height_mm': h_mm,
        'width_in': w_mm / 25.4,
        'height_in': h_mm / 25.4,
        'stitch_count': stitch_count,
    }
