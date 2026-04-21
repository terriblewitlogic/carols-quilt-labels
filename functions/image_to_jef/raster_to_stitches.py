"""
Core image-to-embroidery conversion pipeline.

Improvements over v1:
  - Each colour mask is split into connected components (skimage.measure.label)
    so isolated blobs get independent treatment instead of sharing one fill angle.
  - Fill angle per polygon is computed via PCA on the polygon's vertices so each
    shape fills along its own major axis (petals along their spine, etc.)
  - Tatami row offset: each row is phase-shifted by 1/3 stitch length so row
    endpoints don't stack into a visible seam through the fabric.

Data model
----------
groups = [
    {
        'color': '#rrggbb',
        'segments': [
            [{'x': float, 'y': float}, ...],   # one connected stitch run
            ...
        ]
    },
    ...
]
All coordinates in pyembroidery units (0.1 mm), origin at image centre.
"""

import math
import base64
import io
from typing import List, Tuple, Optional

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans          # type: ignore
from PIL import ImageDraw                   # type: ignore  (ImageDraw for rasterization)
from skimage import morphology, measure     # type: ignore
from skimage.morphology import skeletonize  # type: ignore
from shapely.geometry import Polygon, LineString, MultiLineString  # type: ignore


# ─── Constants ────────────────────────────────────────────────────────────────
PX_PER_MM          = 10     # working resolution
EMB_PER_MM         = 10     # pyembroidery 0.1 mm units
PX_TO_EMB          = EMB_PER_MM / PX_PER_MM   # 1.0 at 10 px/mm
MAX_STITCH_MM      = 12.0   # break long stitches
TATAMI_CYCLE       = 3      # rows per tatami phase cycle
COMPACTNESS_THRESH  = 0.60   # above → contour fill; below → directional/medial
UNDERLAY_DENSITY    = 3      # underlay row spacing = density × this factor
MEDIAL_EIGEN_THRESH = 6.0    # eigenvalue ratio above this → use medial fill
                             # (≈ aspect ratio² so 6 ≈ 2.5× longer than wide)


# ─── Public entry point ───────────────────────────────────────────────────────
def raster_to_stitch_groups(
    image_base64: str,
    hoop_w_mm: float,
    hoop_h_mm: float,
    num_colors: int = 4,
    density_mm: float = 0.4,
    fill_angle_deg: Optional[float] = None,   # None = auto PCA per region
    min_feature_mm: float = 1.5,
    outline: str = 'running',
    outline_width_mm: float = 1.0,
) -> Tuple[List[dict], str, List[str]]:
    """Returns (groups, preview_svg, palette_hex_list)."""
    img = _decode_image(image_base64, hoop_w_mm, hoop_h_mm)
    w, h = img.size

    posterized, palette = _posterize(img, num_colors)

    min_area_px2 = (min_feature_mm * PX_PER_MM) ** 2
    density_px   = density_mm * PX_PER_MM
    outline_w_px = outline_width_mm * PX_PER_MM
    cx_px, cy_px = w / 2.0, h / 2.0

    groups: List[dict] = []

    # ── Background filter ─────────────────────────────────────────────────────
    # Skip near-white colours ONLY when they are also the dominant colour by
    # pixel area — that combination reliably identifies the image background.
    # White that isn't dominant is intentional (daisy petals, owl faces, etc.)
    pixel_counts = [int(np.sum(posterized == i)) for i in range(len(palette))]
    total_px     = max(sum(pixel_counts), 1)
    dominant_idx = int(np.argmax(pixel_counts))

    def _is_background(label_idx, rgb):
        r, g, b = rgb
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        is_near_white = lum > 230
        is_dominant   = (pixel_counts[label_idx] / total_px) > 0.20
        return is_near_white and is_dominant

    for label_idx, rgb in enumerate(palette):
        if _is_background(label_idx, rgb):
            continue
        color_hex = _rgb_to_hex(rgb)
        mask = (posterized == label_idx)

        # Light cleanup at full mask level
        mask = morphology.binary_opening(mask, footprint=morphology.disk(1))
        mask = morphology.remove_small_objects(mask, min_size=int(min_area_px2))
        if not mask.any():
            continue

        # ── Split into connected components ───────────────────────────────
        # Each isolated blob gets its own fill angle instead of sharing one.
        labeled_mask = measure.label(mask)
        raw_segments: List[List[Tuple[float, float]]] = []

        for comp_id in range(1, labeled_mask.max() + 1):
            comp_mask = (labeled_mask == comp_id)
            if comp_mask.sum() < min_area_px2:
                continue

            polys = _mask_to_polygons(comp_mask, min_area_px2)
            for poly in polys:
                # ── Simplify for fill (keeps outline at full res) ─────────
                fill_poly = poly.simplify(1.5, preserve_topology=True)
                if not fill_poly.is_valid or fill_poly.is_empty:
                    fill_poly = poly

                # ── Underlay (sparse, perpendicular) ─────────────────────
                raw_segments.extend(
                    _underlay_segments(fill_poly, density_px)
                )

                # ── Top fill: contour / medial / directional ─────────────
                compactness   = _compactness(fill_poly)
                eigen_ratio   = _eigenvalue_ratio(fill_poly)
                user_angle    = fill_angle_deg is not None

                if compactness >= COMPACTNESS_THRESH:
                    # Round/compact → concentric inward rings
                    raw_segments.extend(
                        _contour_fill_segments(fill_poly, density_px)
                    )
                elif not user_angle and eigen_ratio >= MEDIAL_EIGEN_THRESH:
                    # Clearly elongated → follow the spine with perpendicular cross-sections
                    segs = _medial_fill_segments(fill_poly, density_px)
                    if segs:
                        raw_segments.extend(segs)
                    else:
                        # Fallback if skeleton fails
                        raw_segments.extend(
                            _fill_polygon_segments(fill_poly, density_px,
                                                   _pca_angle(fill_poly))
                        )
                else:
                    # General shape → directional scan lines along PCA axis
                    angle = fill_angle_deg if user_angle else _pca_angle(fill_poly)
                    raw_segments.extend(
                        _fill_polygon_segments(fill_poly, density_px, angle)
                    )

                # ── Edge walk (boundary density gradient) ────────────────
                # Two tight inset passes give crisp edges and compensate for
                # fabric pull — stitched last so they sit on top of the fill.
                raw_segments.extend(
                    _edge_walk_segments(fill_poly, density_px)
                )

                # ── Outline ───────────────────────────────────────────────
                if outline != 'none':
                    raw_segments.extend(
                        _outline_segments(poly, outline, outline_w_px)
                    )

        if not raw_segments:
            continue

        ordered = _greedy_sort(raw_segments)

        emb_segments = [
            [{'x': (x - cx_px) * PX_TO_EMB, 'y': (y - cy_px) * PX_TO_EMB}
             for x, y in seg]
            for seg in ordered
        ]
        groups.append({'color': color_hex, 'segments': emb_segments})

    palette_hex = [_rgb_to_hex(rgb) for i, rgb in enumerate(palette)
                   if not _is_background(i, rgb)]
    preview_svg = _build_preview_svg(groups, w, h)
    return groups, preview_svg, palette_hex


# ─── Image decode + resize ────────────────────────────────────────────────────
def _decode_image(image_base64: str, hoop_w_mm: float, hoop_h_mm: float) -> Image.Image:
    img = Image.open(io.BytesIO(base64.b64decode(image_base64))).convert('RGB')
    tw = int(hoop_w_mm * PX_PER_MM)
    th = int(hoop_h_mm * PX_PER_MM)
    scale = min(tw / img.width, th / img.height)
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    return img


# ─── Color quantization ───────────────────────────────────────────────────────
def _posterize(img: Image.Image, n: int) -> Tuple[np.ndarray, list]:
    arr = np.array(img).reshape(-1, 3).astype(np.float32)
    km  = KMeans(n_clusters=n, n_init=6, random_state=42)
    labels  = km.fit_predict(arr)
    centers = km.cluster_centers_.astype(np.uint8)
    palette = [tuple(int(c) for c in rgb) for rgb in centers]

    # Sort by brightness (darker first — better stitch layering)
    order = sorted(range(n), key=lambda i: sum(palette[i]))
    remap = {old: new for new, old in enumerate(order)}
    sorted_pal = [palette[i] for i in order]
    new_labels = np.vectorize(remap.get)(labels.reshape(img.height, img.width))
    return new_labels.astype(np.uint8), sorted_pal


# ─── Mask → polygons ─────────────────────────────────────────────────────────
def _mask_to_polygons(mask: np.ndarray, min_area: float) -> List[Polygon]:
    polys = []
    for contour in measure.find_contours(mask.astype(np.float32), 0.5):
        coords = [(c[1], c[0]) for c in contour]
        if len(coords) < 4:
            continue
        try:
            poly = Polygon(coords)
            if not poly.is_valid:
                poly = poly.buffer(0)
            if poly.area >= min_area:
                polys.append(poly)
        except Exception:
            pass
    return polys


# ─── PCA fill angle ───────────────────────────────────────────────────────────
def _pca_angle(poly: Polygon) -> float:
    """
    Compute the fill angle for a polygon by PCA on its exterior vertices.
    Returns the angle (degrees) of the major axis, normalised to 0–180.
    Falls back to 45° for degenerate shapes.
    """
    pts = np.array(poly.exterior.coords[:-1])   # drop repeated closing point
    if len(pts) < 3:
        return 45.0
    centered = pts - pts.mean(axis=0)
    cov = np.cov(centered.T)
    if cov.ndim < 2:
        return 45.0
    _, vecs = np.linalg.eigh(cov)
    major = vecs[:, -1]                         # eigenvector of largest eigenvalue
    angle = math.degrees(math.atan2(major[1], major[0])) % 180
    return angle


# ─── Eigenvalue ratio (aspect measure) ───────────────────────────────────────
def _eigenvalue_ratio(poly: Polygon) -> float:
    """Ratio of largest to smallest PCA eigenvalue. Elongated → high value."""
    pts = np.array(poly.exterior.coords[:-1])
    if len(pts) < 3:
        return 1.0
    centered = pts - pts.mean(axis=0)
    vals, _ = np.linalg.eigh(np.cov(centered.T))
    return float(vals[-1] / (vals[0] + 1e-6))


# ─── Medial axis fill ─────────────────────────────────────────────────────────
def _medial_fill_segments(
    poly: Polygon,
    density_px: float,
) -> List[List[Tuple[float, float]]]:
    """
    Fill by shooting stitch segments perpendicular to the shape's medial axis.

    1. Rasterise the polygon to a local binary mask.
    2. Skeletonise with skimage.
    3. Order skeleton pixels by projection onto the PCA major axis — avoids
       complex graph traversal while giving a smooth path along the spine.
    4. Sample at density_px intervals.
    5. At each sample compute the local tangent from nearby skeleton points,
       shoot a perpendicular line through the polygon (shapely intersection),
       and yield the clipped segment as a stitch run.

    Result: fill lines that curve naturally to follow petals, stems and leaves
    rather than being cut at a fixed global angle.
    """
    minx, miny, maxx, maxy = poly.bounds
    W = int(maxx - minx) + 8
    H = int(maxy - miny) + 8
    ox, oy = minx - 4, miny - 4

    # ── Rasterise ──────────────────────────────────────────────────────────
    mask = _rasterize_poly_local(poly, W, H, ox, oy)
    if not mask.any():
        return []

    # ── Skeletonise ────────────────────────────────────────────────────────
    skel = skeletonize(mask)
    rows, cols = np.where(skel)
    if len(rows) < 3:
        return []

    # World-space skeleton coordinates
    wx = cols.astype(float) + ox
    wy = rows.astype(float) + oy

    # ── Order by projection onto PCA major axis ────────────────────────────
    angle_rad = math.radians(_pca_angle(poly))
    axis      = np.array([math.cos(angle_rad), math.sin(angle_rad)])
    pts_arr   = np.column_stack([wx, wy])
    proj      = pts_arr @ axis
    order     = np.argsort(proj)
    wx_o      = wx[order]
    wy_o      = wy[order]
    proj_o    = proj[order]

    # ── Sample at density_px intervals ────────────────────────────────────
    max_px   = MAX_STITCH_MM * PX_PER_MM
    segments = []
    last_p   = proj_o[0] - density_px  # ensure first sample is included

    for i in range(len(wx_o)):
        if proj_o[i] - last_p < density_px:
            continue
        last_p = proj_o[i]
        x, y   = wx_o[i], wy_o[i]

        # Local tangent from a ±3-pixel window in the ordered list
        i0 = max(0, i - 3)
        i1 = min(len(wx_o) - 1, i + 3)
        tdx = wx_o[i1] - wx_o[i0]
        tdy = wy_o[i1] - wy_o[i0]
        td  = math.hypot(tdx, tdy)
        if td < 1e-6:
            tdx, tdy = axis[0], axis[1]
        else:
            tdx, tdy = tdx / td, tdy / td

        # Perpendicular direction
        px, py = -tdy, tdx

        # Intersect perpendicular line with polygon
        far  = float(max(W, H) + 20)
        line = LineString([
            (x + px * far, y + py * far),
            (x - px * far, y - py * far),
        ])
        inter = poly.intersection(line)
        if inter.is_empty:
            continue

        # Pick the segment closest to the skeleton point
        # inter can be LineString, MultiLineString, Point, GeometryCollection, etc.
        if isinstance(inter, LineString):
            raw = [list(inter.coords)]
        elif hasattr(inter, 'geoms'):
            raw = [list(s.coords) for s in inter.geoms if isinstance(s, LineString)]
        else:
            continue  # Point or other non-linear geometry — skip

        best, best_d = None, float('inf')
        for seg in raw:
            if len(seg) < 2:
                continue
            mx = (seg[0][0] + seg[-1][0]) / 2
            my = (seg[0][1] + seg[-1][1]) / 2
            d  = math.hypot(mx - x, my - y)
            if d < best_d:
                best_d, best = d, seg

        if best:
            row_i = len(segments)
            pts   = _interpolate_tatami(
                best[0][0], best[0][1], best[-1][0], best[-1][1],
                (row_i % TATAMI_CYCLE) / TATAMI_CYCLE, max_px,
            )
            if row_i % 2 == 1:
                pts = list(reversed(pts))
            if pts:
                segments.append(pts)

    return segments


def _rasterize_poly_local(
    poly: Polygon, W: int, H: int, ox: float, oy: float
) -> np.ndarray:
    """Rasterise a polygon into a W×H binary numpy array at 1 px/unit."""
    from PIL import Image as _PILImage
    img  = _PILImage.new('L', (W, H), 0)
    draw = ImageDraw.Draw(img)
    coords_px = [(int(x - ox), int(y - oy)) for x, y in poly.exterior.coords]
    if len(coords_px) >= 3:
        draw.polygon(coords_px, fill=255)
    return np.array(img) > 0


# ─── Fill: return list of segments (with tatami offset) ──────────────────────
def _fill_polygon_segments(
    poly: Polygon,
    density_px: float,
    angle_deg: float,
) -> List[List[Tuple[float, float]]]:
    """
    Parallel-line fill with tatami row offset.
    Returns one segment per scan-line intersection (jumps between segments
    are handled by the caller / pyembroidery).
    """
    a   = math.radians(angle_deg)
    ca, sa = math.cos(-a), math.sin(-a)
    cb, sb = math.cos( a), math.sin( a)

    def rot(x, y):   return x*ca - y*sa, x*sa + y*ca
    def unrot(x, y): return x*cb - y*sb, x*sb + y*cb

    rot_poly = Polygon([rot(x, y) for x, y in poly.exterior.coords])
    if not rot_poly.is_valid:
        rot_poly = rot_poly.buffer(0)

    minx, miny, maxx, maxy = rot_poly.bounds
    max_px   = MAX_STITCH_MM * PX_PER_MM
    segments = []
    row = 0
    y   = miny + density_px / 2

    while y <= maxy:
        # Tatami phase: shift stitch start by 0, 1/3, 2/3 of max stitch length
        phase = (row % TATAMI_CYCLE) / TATAMI_CYCLE

        inter = rot_poly.intersection(LineString([(minx-1, y), (maxx+1, y)]))
        if not inter.is_empty:
            raw = ([list(inter.coords)] if isinstance(inter, LineString)
                   else [list(s.coords) for s in inter.geoms])
            raw.sort(key=lambda s: s[0][0])
            if row % 2 == 1:
                raw = [list(reversed(s)) for s in reversed(raw)]

            for seg in raw:
                if len(seg) < 2:
                    continue
                x0, y0 = seg[0]
                x1, y1 = seg[-1]
                pts = _interpolate_tatami(*unrot(x0, y0), *unrot(x1, y1),
                                         phase, max_px)
                if pts:
                    segments.append(pts)

        y   += density_px
        row += 1

    return segments


def _interpolate_tatami(
    x0: float, y0: float,
    x1: float, y1: float,
    phase: float,
    max_px: float,
) -> List[Tuple[float, float]]:
    """
    Walk from (x0,y0) to (x1,y1) in steps of max_px, with the first step
    starting at phase * max_px so consecutive rows don't align.
    """
    dx, dy = x1 - x0, y1 - y0
    dist   = math.hypot(dx, dy)
    if dist < 1e-6:
        return [(x0, y0)]

    pts   = [(x0, y0)]
    d     = phase * max_px   # first stitch offset
    while d < dist:
        t = d / dist
        pts.append((x0 + dx*t, y0 + dy*t))
        d += max_px
    if math.hypot(pts[-1][0]-x1, pts[-1][1]-y1) > 0.5:
        pts.append((x1, y1))
    return pts


# ─── Shape compactness ───────────────────────────────────────────────────────
def _compactness(poly: Polygon) -> float:
    """4π·area / perimeter² — 1.0 for circle, ~0 for thin spike."""
    p = poly.length
    if p < 1e-6:
        return 0.0
    return min(1.0, (4 * math.pi * poly.area) / (p * p))


# ─── Contour fill (inward concentric rings) ───────────────────────────────────
def _contour_fill_segments(
    poly: Polygon,
    density_px: float,
) -> List[List[Tuple[float, float]]]:
    """
    Fill by repeatedly shrinking the polygon inward by density_px.
    Produces concentric rings that follow the shape boundary — great for
    circles, ovals, flower centres, rounded leaves.
    Alternates CW/CCW so consecutive rings connect cleanly.
    """
    max_px   = MAX_STITCH_MM * PX_PER_MM
    segments = []
    current  = poly
    ring     = 0

    while True:
        shrunk = current.buffer(-density_px)
        if shrunk.is_empty or shrunk.area < density_px ** 2:
            break

        # Handle MultiPolygon (shape may split as it shrinks)
        parts = (list(shrunk.geoms)
                 if shrunk.geom_type == 'MultiPolygon'
                 else [shrunk])

        for part in parts:
            if part.is_empty:
                continue
            coords = list(part.exterior.coords)
            # Alternate direction so the needle travels ring-to-ring efficiently
            if ring % 2 == 1:
                coords = list(reversed(coords))

            pts: List[Tuple[float, float]] = []
            for i in range(len(coords) - 1):
                pts.extend(_interpolate_tatami(
                    coords[i][0], coords[i][1],
                    coords[i+1][0], coords[i+1][1],
                    (ring % TATAMI_CYCLE) / TATAMI_CYCLE,
                    max_px,
                ))
            if pts:
                segments.append(pts)

        current = shrunk
        ring   += 1

    return segments


# ─── Underlay pass ────────────────────────────────────────────────────────────
def _underlay_segments(
    poly: Polygon,
    density_px: float,
) -> List[List[Tuple[float, float]]]:
    """
    Sparse scan-line pass at 90° to the dominant fill angle, stitched before
    the top fill. Stabilises the fabric and improves how the top fill sits.
    Uses UNDERLAY_DENSITY × normal density (wider row spacing = fewer stitches).
    """
    # Underlay always runs at the PCA angle + 90° (cross-grain)
    base_angle = _pca_angle(poly)
    underlay_angle = (base_angle + 90) % 180
    underlay_density = density_px * UNDERLAY_DENSITY
    return _fill_polygon_segments(poly, underlay_density, underlay_angle)


# ─── Edge walk (boundary density gradient) ───────────────────────────────────
def _edge_walk_segments(
    poly: Polygon,
    density_px: float,
    n_passes: int = 2,
) -> List[List[Tuple[float, float]]]:
    """
    Stitch N tight inset rings just inside the polygon boundary.
    Each ring is spaced density_px * 0.45 inward from the previous,
    so the outermost ~1mm of fill is denser than the interior — giving
    sharp-looking edges without changing the bulk fill spacing.
    Rings alternate direction (CW/CCW) for efficient needle travel.
    """
    max_px   = MAX_STITCH_MM * PX_PER_MM
    step     = density_px * 0.45      # tight inset spacing
    segments = []

    for i in range(n_passes):
        inset = poly.buffer(-(step * (i + 1)))
        if inset.is_empty or inset.area < step ** 2:
            break

        parts = (list(inset.geoms)
                 if inset.geom_type == 'MultiPolygon'
                 else [inset])

        for part in parts:
            if part.is_empty:
                continue
            coords = list(part.exterior.coords)
            if i % 2 == 1:
                coords = list(reversed(coords))

            pts: List[Tuple[float, float]] = []
            for j in range(len(coords) - 1):
                pts.extend(_interpolate_tatami(
                    coords[j][0], coords[j][1],
                    coords[j+1][0], coords[j+1][1],
                    0.0, max_px,
                ))
            if pts:
                segments.append(pts)

    return segments


# ─── Outline segments ─────────────────────────────────────────────────────────
def _outline_segments(
    poly: Polygon,
    mode: str,
    width_px: float,
) -> List[List[Tuple[float, float]]]:
    simplified = poly.simplify(2.0, preserve_topology=True)
    coords = list(simplified.exterior.coords)
    if len(coords) < 3:
        coords = list(poly.exterior.coords)

    if mode == 'running':
        pts: List[Tuple[float, float]] = []
        max_px = MAX_STITCH_MM * PX_PER_MM
        for i in range(len(coords) - 1):
            pts.extend(_interpolate_tatami(
                coords[i][0], coords[i][1],
                coords[i+1][0], coords[i+1][1],
                0.0, max_px,
            ))
        return [pts] if pts else []

    if mode == 'satin':
        half = width_px / 2.0
        segs: List[List[Tuple[float, float]]] = []
        n = len(coords) - 1
        STEP = max(2.0, width_px * 0.8)
        for i in range(n):
            x0, y0 = coords[i]
            x1, y1 = coords[(i+1) % n]
            elen = math.hypot(x1-x0, y1-y0)
            if elen < 1e-6:
                continue
            ex, ey = (x1-x0)/elen, (y1-y0)/elen
            nx, ny = ey, -ex      # inward normal (CCW exterior)
            steps = max(1, int(elen / STEP))
            for s in range(steps):
                t  = s / steps
                mx = x0 + t*(x1-x0)
                my = y0 + t*(y1-y0)
                segs.append([(mx+nx*half, my+ny*half),
                              (mx-nx*half, my-ny*half)])
        return segs

    return []


# ─── Greedy nearest-endpoint sort ────────────────────────────────────────────
def _greedy_sort(segs: List[List[Tuple]]) -> List[List[Tuple]]:
    if not segs:
        return segs
    remaining = list(range(len(segs)))
    ordered   = []

    def d(a, b): return math.hypot(a[0]-b[0], a[1]-b[1])

    cur = min(remaining, key=lambda i: d(segs[i][0], (0, 0)))
    remaining.remove(cur)
    ordered.append(segs[cur])
    tail = segs[cur][-1]

    while remaining:
        best, best_d, flip = None, float('inf'), False
        for i in remaining:
            ds = d(tail, segs[i][0])
            de = d(tail, segs[i][-1])
            if ds < best_d: best, best_d, flip = i, ds, False
            if de < best_d: best, best_d, flip = i, de, True
        remaining.remove(best)
        seg = segs[best] if not flip else list(reversed(segs[best]))
        ordered.append(seg)
        tail = seg[-1]

    return ordered


# ─── Preview SVG ─────────────────────────────────────────────────────────────
def _build_preview_svg(groups: List[dict], img_w: int, img_h: int) -> str:
    ew  = img_w * PX_TO_EMB
    eh  = img_h * PX_TO_EMB
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{-ew/2:.1f} {-eh/2:.1f} {ew:.1f} {eh:.1f}" '
        f'style="background:#f5f0eb">',
    ]
    for group in groups:
        c = group['color']
        for seg in group.get('segments', []):
            if len(seg) < 2:
                continue
            pts = ' '.join(f"{s['x']:.1f},{s['y']:.1f}" for s in seg)
            lines.append(
                f'<polyline points="{pts}" fill="none" stroke="{c}" '
                f'stroke-width="1.4" stroke-linejoin="round" stroke-linecap="round"/>'
            )
    lines.append('</svg>')
    return '\n'.join(lines)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _rgb_to_hex(rgb) -> str:
    return '#{:02x}{:02x}{:02x}'.format(*rgb)
