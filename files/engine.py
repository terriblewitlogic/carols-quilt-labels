"""
Text-to-embroidery engine: converts text into satin-stitched JEF files.

Uses Hershey vector fonts (public domain single-stroke fonts) as the
letterform source, then generates satin column stitches by buffering
each stroke into left/right rails and zigzagging between them.
"""

import numpy as np
from HersheyFonts import HersheyFonts
from shapely.geometry import LineString, Point
from shapely.ops import substring
import pyembroidery


# ── Font helpers ──────────────────────────────────────────────────────

FONT_ALIASES = {
    'script':     'scriptc',
    'script2':    'scripts',
    'sans':       'futural',
    'serif':      'rowmans',
    'serif-bold': 'rowmand',
    'gothic':     'gothgbt',
    'italic':     'timesi',
    'times':      'timesr',
    'times-bold': 'timesrb',
}

def available_fonts():
    """Return dict of user-friendly name -> hershey internal name."""
    return dict(FONT_ALIASES)


def get_text_strokes(text, font_name='script', height_mm=15.0):
    """Extract stroke polylines for a text string.
    
    Returns list of numpy arrays, each shape (N, 2) in mm coordinates,
    with Y flipped for embroidery (positive Y = down).
    """
    internal = FONT_ALIASES.get(font_name, font_name)
    hf = HersheyFonts()
    hf.load_default_font(internal)
    hf.normalize_rendering(height_mm)
    
    strokes = []
    for stroke in hf.strokes_for_text(text):
        pts = [(x, -y) for x, y in stroke]
        if len(pts) >= 2:
            strokes.append(np.array(pts, dtype=float))
    return strokes


def get_text_width(text, font_name='script', height_mm=15.0):
    """Get total width of rendered text in mm."""
    strokes = get_text_strokes(text, font_name, height_mm)
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
    Uses central differences for interior points."""
    n = len(pts)
    tangents = np.zeros_like(pts)
    
    # Forward/backward/central differences
    tangents[0] = pts[min(1, n-1)] - pts[0]
    tangents[-1] = pts[-1] - pts[max(0, n-2)]
    for i in range(1, n - 1):
        tangents[i] = pts[i + 1] - pts[i - 1]
    
    # Normalize
    lengths = np.linalg.norm(tangents, axis=1, keepdims=True)
    lengths = np.maximum(lengths, 1e-8)
    tangents = tangents / lengths
    
    # 90-degree rotation -> normals
    normals = np.column_stack([-tangents[:, 1], tangents[:, 0]])
    return normals


def smooth_array(arr, window=5):
    """Apply simple moving average smoothing."""
    if len(arr) <= window:
        return arr
    kernel = np.ones(window) / window
    smoothed = np.copy(arr)
    for col in range(arr.shape[1]):
        smoothed[:, col] = np.convolve(arr[:, col], kernel, mode='same')
    # Re-normalize if these are direction vectors
    lengths = np.linalg.norm(smoothed, axis=1, keepdims=True)
    lengths = np.maximum(lengths, 1e-8)
    return smoothed / lengths


# ── Stitch generation ─────────────────────────────────────────────────

def generate_underlay(points, stitch_length_mm=2.5):
    """Center-walk underlay: walk the stroke centerline forward and back.
    This stabilizes the fabric before the top satin stitches."""
    line = LineString(points)
    num = max(2, int(line.length / stitch_length_mm))
    
    forward = []
    for i in range(num + 1):
        pt = line.interpolate(i / num, normalized=True)
        forward.append((pt.x, pt.y))
    
    # Walk back (offset slightly to avoid exact overlap)
    back = list(reversed(forward))
    return forward + back


def generate_satin(points, width_mm=1.2, spacing_mm=0.35, pull_comp_mm=0.1):
    """Generate satin column stitches along a stroke path.
    
    Creates a zigzag pattern by alternating between left and right sides
    of the stroke, perpendicular to the path direction.
    
    Args:
        points: Stroke centerline as (N, 2) array in mm
        width_mm: Total satin column width
        spacing_mm: Distance between stitch points along the path
        pull_comp_mm: Extra width to compensate for thread tension
    """
    # Resample for even stitch spacing
    pts = resample_line(points, spacing_mm)
    if len(pts) < 3:
        return []
    
    half_w = (width_mm / 2.0) + pull_comp_mm
    
    # Compute and smooth normals
    normals = compute_normals(pts)
    normals = smooth_array(normals, window=5)
    
    # Adaptive width: reduce at tight curves to prevent crowding
    curvature = np.zeros(len(pts))
    for i in range(1, len(pts) - 1):
        # Angle change between consecutive segments
        v1 = pts[i] - pts[i-1]
        v2 = pts[i+1] - pts[i]
        dot = np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8), -1, 1)
        curvature[i] = np.arccos(dot)
    
    # Smooth curvature and compute width scale (reduce width at sharp bends)
    if len(curvature) > 3:
        kernel = np.ones(3) / 3
        curvature = np.convolve(curvature, kernel, mode='same')
    width_scale = np.clip(1.0 - curvature * 0.5, 0.5, 1.0)
    
    # Generate zigzag stitches
    stitches = []
    for i in range(len(pts)):
        x, y = pts[i]
        nx, ny = normals[i]
        w = half_w * width_scale[i]
        
        if i % 2 == 0:
            stitches.append((x + nx * w, y + ny * w))
        else:
            stitches.append((x - nx * w, y - ny * w))
    
    return stitches


# ── Pattern assembly ──────────────────────────────────────────────────

def text_to_pattern(text, font_name='script', height_mm=15.0,
                    satin_width_mm=1.2, density_mm=0.35,
                    thread_color=0xFF0000):
    """Convert a single line of text to an EmbPattern.
    
    Returns (pattern, width_mm, height_mm).
    """
    strokes = get_text_strokes(text, font_name, height_mm)
    if not strokes:
        return None, 0, 0
    
    pattern = pyembroidery.EmbPattern()
    pattern.add_thread(pyembroidery.EmbThread(thread_color))
    
    first = True
    for stroke_pts in strokes:
        if len(stroke_pts) < 2:
            continue
        
        # Underlay
        underlay = generate_underlay(stroke_pts, stitch_length_mm=2.5)
        for j, (x, y) in enumerate(underlay):
            x10, y10 = round(x * 10), round(y * 10)
            if first:
                pattern.add_stitch_absolute(pyembroidery.STITCH, x10, y10)
                first = False
            elif j == 0:
                pattern.add_stitch_absolute(pyembroidery.TRIM, x10, y10)
            else:
                pattern.add_stitch_absolute(pyembroidery.STITCH, x10, y10)
        
        # Top satin
        satin = generate_satin(stroke_pts, satin_width_mm, density_mm)
        for j, (x, y) in enumerate(satin):
            x10, y10 = round(x * 10), round(y * 10)
            pattern.add_stitch_absolute(pyembroidery.STITCH, x10, y10)
        
        pattern.add_command(pyembroidery.TRIM)
    
    pattern.add_command(pyembroidery.END)
    
    bounds = pattern.bounds()
    w = (bounds[2] - bounds[0]) / 10.0
    h = (bounds[3] - bounds[1]) / 10.0
    return pattern, w, h


def multiline_to_pattern(lines, font_name='script', height_mm=15.0,
                         line_spacing_factor=1.6, align='center',
                         satin_width_mm=1.2, density_mm=0.35,
                         thread_color=0xFF0000):
    """Convert multiple lines of text to a single centered EmbPattern.
    
    Args:
        lines: List of text strings, one per line
        align: 'left', 'center', or 'right'
        line_spacing_factor: Multiplier on height_mm for line spacing
    """
    line_spacing = height_mm * line_spacing_factor
    
    # First pass: get widths for alignment
    widths = [get_text_width(line, font_name, height_mm) for line in lines]
    max_width = max(widths) if widths else 0
    
    combined = pyembroidery.EmbPattern()
    combined.add_thread(pyembroidery.EmbThread(thread_color))
    
    first_stitch = True
    
    for line_idx, text in enumerate(lines):
        if not text.strip():
            continue
        
        strokes = get_text_strokes(text, font_name, height_mm)
        if not strokes:
            continue
        
        # Compute offset for this line
        y_offset = line_idx * line_spacing
        
        if align == 'center':
            x_offset = (max_width - widths[line_idx]) / 2.0
        elif align == 'right':
            x_offset = max_width - widths[line_idx]
        else:
            x_offset = 0.0
        
        for stroke_pts in strokes:
            if len(stroke_pts) < 2:
                continue
            
            # Apply offsets
            shifted = stroke_pts.copy()
            shifted[:, 0] += x_offset
            shifted[:, 1] += y_offset
            
            # Underlay
            underlay = generate_underlay(shifted, stitch_length_mm=2.5)
            for j, (x, y) in enumerate(underlay):
                x10, y10 = round(x * 10), round(y * 10)
                if first_stitch:
                    combined.add_stitch_absolute(pyembroidery.STITCH, x10, y10)
                    first_stitch = False
                elif j == 0:
                    combined.add_stitch_absolute(pyembroidery.TRIM, x10, y10)
                else:
                    combined.add_stitch_absolute(pyembroidery.STITCH, x10, y10)
            
            # Top satin
            satin = generate_satin(shifted, satin_width_mm, density_mm)
            for j, (x, y) in enumerate(satin):
                x10, y10 = round(x * 10), round(y * 10)
                combined.add_stitch_absolute(pyembroidery.STITCH, x10, y10)
            
            combined.add_command(pyembroidery.TRIM)
    
    combined.add_command(pyembroidery.END)
    return combined


def generate_preview_svg(lines_text, font_name='script', height_mm=15.0,
                         line_spacing_factor=1.6, align='center',
                         satin_width_mm=1.2, density_mm=0.35,
                         thread_color='#cc0000', width_px=700):
    """Generate an SVG preview that simulates the stitched appearance."""
    line_spacing = height_mm * line_spacing_factor
    
    # Gather all strokes with offsets
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
        normals = smooth_array(normals, window=5)
        
        for i in range(len(pts)):
            x, y = pts[i]
            nx, ny = normals[i]
            x1 = (x + nx * half_w - x_min) * scale
            y1 = (y + ny * half_w - y_min) * scale
            x2 = (x - nx * half_w - x_min) * scale
            y2 = (y - ny * half_w - y_min) * scale
            svg_lines.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
                f'x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{thread_color}" stroke-width="0.8" '
                f'stroke-linecap="round"/>'
            )
    
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width_px:.0f} {height_px:.0f}" '
        f'width="{width_px}" height="{height_px:.0f}">\n'
        f'  <rect width="100%" height="100%" fill="#f5f0e8" rx="6"/>\n'
        f'  {"".join(svg_lines)}\n'
        f'</svg>'
    )
    return svg


def save_pattern(pattern, output_path):
    """Save pattern as JEF (and PNG preview)."""
    # Normalize (center on origin)
    pattern = pyembroidery.EmbPattern.get_normalized_pattern(pattern)
    
    pyembroidery.write_jef(pattern, output_path)
    
    # Also generate PNG preview
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
