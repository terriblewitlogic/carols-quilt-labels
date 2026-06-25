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
import hashlib
import warnings
from typing import List, Tuple, Optional

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans          # type: ignore
from PIL import ImageDraw                   # type: ignore  (ImageDraw for rasterization)
from skimage import morphology, measure     # type: ignore
from skimage.morphology import skeletonize  # type: ignore
from shapely import affinity                # type: ignore
from shapely.geometry import Polygon, LineString, MultiLineString  # type: ignore


# ─── Constants ────────────────────────────────────────────────────────────────
PX_PER_MM          = 10     # working resolution
EMB_PER_MM         = 10     # pyembroidery 0.1 mm units
PX_TO_EMB          = EMB_PER_MM / PX_PER_MM   # 1.0 at 10 px/mm

# Stitch length caps by role (mm). Lower caps = denser, more uniform output.
# Calibrated from professional Hatch-digitized examples (Find Joy, Faithful
# Friends, Z for Zebra) where p99 stitch lengths cluster around 4–4.5 mm.
MAX_STITCH_FILL_MM     = 4.0    # tatami / contour / medial fills
MAX_STITCH_UNDERLAY_MM = 2.5    # underlay running stitches
MAX_STITCH_OUTLINE_MM  = 2.5    # running outline
MAX_STITCH_TRAVEL_MM   = 12.0   # explicit travel runs and jumps only
MIN_STITCH_PX          = 1.5    # below this → drop as a duplicate
                                # (1.5 px @ 10 px/mm = 0.15 mm)

# Legacy alias kept for any callers we missed; treat as fill cap.
MAX_STITCH_MM      = MAX_STITCH_FILL_MM

TATAMI_CYCLE       = 3      # rows per tatami phase cycle
COMPACTNESS_THRESH  = 0.60   # above → contour fill; below → directional/medial
UNDERLAY_DENSITY    = 3      # underlay row spacing = density × this factor
MEDIAL_EIGEN_THRESH = 3.0    # eigenvalue ratio above this → use medial fill
                             # (≈ aspect ratio² — 3.0 ≈ 1.7× longer than wide;
                             # catches petals, leaves, feathers naturally)
SATIN_WIDTH_MM     = 6.0    # shapes narrower than this use medial/satin fill
                             # regardless of aspect ratio (petal tips, thin stems)
MAX_SATIN_BAR_MM   = 8.0    # max length of a single-stitch satin bar; bars
                             # wider than this get interpolated like tatami so
                             # the stitch doesn't snag on use
MIN_BRANCH_LENGTH_MM = 3.0   # medial-axis branches shorter than this are
                              # treated as Voronoi noise and ignored. Lets us
                              # walk T/Y/F-style letter branches while skipping
                              # petal-tip corner artefacts. The longest-trail
                              # fallback ensures very small shapes still produce
                              # at least one trail of bars.
PULL_COMP_MM       = 0.3    # outward expansion on fill polygon to compensate
                             # for fabric pull; keeps filled shapes full-size on cloth
STITCH_JITTER      = 0.08   # ±fraction random variation on stitch length
                             # breaks the mechanical uniform look; ~8% feels hand-stitched

# ── Tier 2 multi-pass colour sequencing ──────────────────────────────────────
# Per-colour, components are classified as either "foundation fill" (large)
# or "detail" (small accent). Foundation fills go in pass 1, details in
# pass 2, outlines and dark accents in pass 3 — matching the layer order
# pros use in Hatch.
DETAIL_AREA_MAX_MM2   = 20.0   # absolute area below which a component is a detail
                                # (~5 mm dia circle — covers eye dots, accent
                                # marks, period punctuation, small highlights)
DETAIL_AREA_MIN_MM2   = 1.2    # smaller specks are usually posterization noise;
                                # true pin-dot accents survive because the
                                # caller's min_feature_mm still controls the
                                # first-pass extraction threshold.
DETAIL_REL_THRESHOLD  = 0.15   # relative-area threshold (vs largest in colour)
MAX_DETAIL_COMPONENTS = 24     # cap micro-component count to avoid jump explosion
ACCENT_LUMINANCE_MAX  = 30     # luminance below which a colour is "dark"
ACCENT_PIXEL_FRAC_MAX = 0.08   # pixel fraction below which a dark colour
                                # is treated as an accent (final pass)

# Selective outlines: professional digitizers outline intentional dark/accent
# detail, not every posterized colour boundary. Keeping this conservative cuts
# hundreds of trims on large raster conversions while preserving definition.
OUTLINE_LUMINANCE_MAX = 115
OUTLINE_PIXEL_FRAC_MAX = 0.35
MAX_SELECTIVE_OUTLINE_COLORS = 1


# ─── Layer info (fast, no stitch generation) ─────────────────────────────────
def posterize_image(
    image_base64: str,
    hoop_w_mm: float,
    hoop_h_mm: float,
    num_colors: int = 4,
) -> List[dict]:
    """
    Posterize the image and return layer metadata without generating stitches.
    Used by the UI layer-ordering step before full conversion.

    Returns a list (already in default stitch order — dark first) of:
      { label_idx, hex, pixel_fraction, is_background }
    """
    img = _decode_image(image_base64, hoop_w_mm, hoop_h_mm)
    posterized, palette = _posterize(img, num_colors)

    pixel_counts = [int(np.sum(posterized == i)) for i in range(len(palette))]
    total_px = max(sum(pixel_counts), 1)

    layers = []
    for i, rgb in enumerate(palette):
        r, g, b = rgb
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        is_bg = (lum > 230) and ((pixel_counts[i] / total_px) > 0.20)
        layers.append({
            'label_idx':      i,
            'hex':            _rgb_to_hex(rgb),
            'pixel_fraction': round(pixel_counts[i] / total_px, 3),
            'is_background':  is_bg,
        })
    return layers


# ─── Public entry point ───────────────────────────────────────────────────────
def raster_to_stitch_groups(
    image_base64: str,
    hoop_w_mm: float,
    hoop_h_mm: float,
    num_colors: int = 4,
    density_mm: float = 0.4,
    fill_angle_deg: Optional[float] = None,   # None = auto PCA per region
    min_feature_mm: float = 0.8,
    outline: str = 'running',
    outline_width_mm: float = 1.0,
    outline_policy: str = 'selective',          # 'selective'|'all'|'dark'|'none'
    color_order: Optional[List[int]] = None,  # explicit label_idx ordering from UI
    thread_brand: Optional[str] = None,        # snap palette to this brand
) -> Tuple[List[dict], str, List[str]]:
    """
    Returns (groups, preview_svg, palette_hex_list).

    Stitch order follows the video lesson:
      1. All fill groups in colour order (background→foreground, large→small)
      2. All outline groups last — so outlines always sit on top of every fill
         regardless of colour, exactly as a professional digitizer would arrange it.

    If color_order is supplied (from the UI layer panel), fills are stitched in
    that sequence instead of the default brightness sort.
    """
    img = _decode_image(image_base64, hoop_w_mm, hoop_h_mm)
    w, h = img.size

    posterized, palette = _posterize(img, num_colors, brand=thread_brand)

    min_area_px2 = (min_feature_mm * PX_PER_MM) ** 2
    density_px   = density_mm * PX_PER_MM
    outline_w_px = outline_width_mm * PX_PER_MM
    cx_px, cy_px = w / 2.0, h / 2.0

    # ── Background filter ─────────────────────────────────────────────────────
    pixel_counts = [int(np.sum(posterized == i)) for i in range(len(palette))]
    total_px     = max(sum(pixel_counts), 1)

    def _is_background(label_idx, rgb):
        r, g, b = rgb
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        return (lum > 230) and ((pixel_counts[label_idx] / total_px) > 0.20)

    # ── Determine iteration order ─────────────────────────────────────────────
    # Default: palette is already brightness-sorted (dark first) by _posterize.
    # If the UI supplied an explicit order, honour it (skip background indices).
    if color_order is not None:
        indices = [i for i in color_order if 0 <= i < len(palette)
                   and not _is_background(i, palette[i])]
    else:
        indices = [i for i in range(len(palette))
                   if not _is_background(i, palette[i])]

    def _to_emb(raw_components):
        """Sort + offset segments to centred mm units; return ({segments}, [comp_ids])."""
        ordered, component_ids = _route_components(raw_components)
        segments = [
            [{'x': (x - cx_px) * PX_TO_EMB, 'y': (y - cy_px) * PX_TO_EMB}
             for x, y in seg]
            for seg in ordered
        ]
        return segments, component_ids

    # ── Phase A — collect per-component data per colour ──────────────────────
    # color_components[label_idx] = [
    #   { 'area_px2': float,
    #     'fill_per_poly':    [[seg, seg, ...], ...],  # one inner list per polygon
    #     'outline_per_poly': [[seg, seg, ...], ...] },
    #   ...
    # ]
    color_components: dict = {}

    for label_idx in indices:
        mask = (posterized == label_idx)
        mask = morphology.binary_opening(mask, footprint=morphology.disk(1))
        mask = morphology.remove_small_objects(mask, min_size=int(min_area_px2))
        if not mask.any():
            continue

        labeled_mask = measure.label(mask)
        components: List[dict] = []

        for comp_id in range(1, labeled_mask.max() + 1):
            comp_mask = (labeled_mask == comp_id)
            comp_area = float(comp_mask.sum())
            if comp_area < min_area_px2:
                continue

            polys = _mask_to_polygons(comp_mask, min_area_px2)
            comp = {
                'area_px2':         comp_area,
                'fill_per_poly':    [],
                'outline_per_poly': [],
            }
            for poly in polys:
                fill_raw, outline_raw = _process_polygon(
                    poly, density_px, fill_angle_deg, outline, outline_w_px,
                )
                if fill_raw:
                    comp['fill_per_poly'].append(fill_raw)
                if outline_raw:
                    comp['outline_per_poly'].append(outline_raw)
            if comp['fill_per_poly'] or comp['outline_per_poly']:
                components.append(comp)

        if components:
            color_components[label_idx] = components

    # ── Phase B — classify components into fill (foundation) vs detail ───────
    color_classified: dict = {
        idx: _classify_color_components(comps)
        for idx, comps in color_components.items()
    }

    # ── Phase C — detect accent colour (dark + minor pixel fraction) ─────────
    accent_idx = _detect_accent_color(palette, pixel_counts, total_px, indices)

    # ── Phase D — build layer plan ───────────────────────────────────────────
    # Pass 1 — Foundation fills (large components, dark→light by palette order)
    # Pass 2 — Detail regions (small components, dark→light)
    # Pass 3 — Outlines for non-accent colours, then accent colour combined
    groups: List[dict] = []
    foundation_indices = [i for i in indices if i != accent_idx]

    def _emit(comp_list, color_hex, gtype, role, pass_n, key):
        """Flatten polys from a list of components, route, and append a group."""
        flat: List[List[List[Tuple[float, float]]]] = []
        for c in comp_list:
            flat.extend(c[key])
        if not flat:
            return
        segments, component_ids = _to_emb(flat)
        groups.append({
            'color':         color_hex,
            'segments':      segments,
            'componentIds':  component_ids,
            'type':          gtype,
            'role':          role,
            'pass':          pass_n,
        })

    # Pass 1 — foundation fills
    for label_idx in foundation_indices:
        cls = color_classified.get(label_idx)
        if not cls or not cls['fill']:
            continue
        _emit(cls['fill'], _rgb_to_hex(palette[label_idx]),
              'fill', 'foundation', 1, 'fill_per_poly')

    # Pass 2 — detail regions
    for label_idx in foundation_indices:
        cls = color_classified.get(label_idx)
        if not cls or not cls['detail']:
            continue
        _emit(cls['detail'], _rgb_to_hex(palette[label_idx]),
              'fill', 'detail', 2, 'fill_per_poly')

    outline_indices = _select_outline_indices(
        foundation_indices,
        palette,
        pixel_counts,
        total_px,
        outline_policy,
    )

    # Pass 3 — selective outlines for non-accent colours
    for label_idx in outline_indices:
        cls = color_classified.get(label_idx)
        if not cls:
            continue
        all_comps = cls['fill'] + cls['detail']
        _emit(all_comps, _rgb_to_hex(palette[label_idx]),
              'outline', 'outline', 3, 'outline_per_poly')

    # Pass 3 final — accent colour all in one stop (fill + detail + outline)
    if accent_idx is not None:
        cls = color_classified.get(accent_idx)
        if cls:
            all_comps = cls['fill'] + cls['detail']
            color_hex = _rgb_to_hex(palette[accent_idx])
            _emit(all_comps, color_hex, 'fill', 'accent', 3, 'fill_per_poly')
            if outline_policy != 'none':
                _emit(all_comps, color_hex, 'outline', 'accent', 3, 'outline_per_poly')

    palette_hex = [_rgb_to_hex(palette[i]) for i in indices]
    preview_svg = _build_preview_svg(groups, w, h)
    return groups, preview_svg, palette_hex


# ─── Per-polygon stitch generation (extracted from main loop) ────────────────
def _process_polygon(
    poly: Polygon,
    density_px: float,
    fill_angle_deg: Optional[float],
    outline: str,
    outline_w_px: float,
) -> Tuple[List[List[Tuple[float, float]]], List[List[Tuple[float, float]]]]:
    """
    Generate the fill and outline raw stitch segments for a single polygon.

    Returns (fill_raw, outline_raw). Either may be empty depending on shape
    properties (thin stripes get no fill; outline='none' gets no outline).
    """
    fill_poly = poly.simplify(1.5, preserve_topology=True)
    if not fill_poly.is_valid or fill_poly.is_empty:
        fill_poly = poly

    fill_raw: List[List[Tuple[float, float]]] = []
    outline_raw: List[List[Tuple[float, float]]] = []

    # Thin-stripe guard
    eroded_test = fill_poly.buffer(-density_px * 0.6)
    is_thin_stripe = eroded_test.is_empty or eroded_test.area < (density_px ** 2)

    # Outline-network guard — connected ring of outline strokes that has very
    # low compactness (perimeter dwarfs filled area). Filling it makes a
    # visible crosshatch grid — skip fill, only run the outline pass.
    is_outline_network = _compactness(fill_poly) < 0.08

    if not is_thin_stripe and not is_outline_network:
        # Pull compensation
        pull_px   = PULL_COMP_MM * PX_PER_MM
        direction = fill_angle_deg if fill_angle_deg is not None else _pca_angle(fill_poly)
        fill_comp = _directional_pull_compensation(fill_poly, pull_px, direction)
        if not fill_comp.is_valid or fill_comp.is_empty:
            fill_comp = fill_poly

        # Satin zone: shape so narrow that a half-satin buffer empties it
        half_satin_px = (SATIN_WIDTH_MM * PX_PER_MM) / 2
        is_satin_zone = fill_comp.buffer(-half_satin_px).is_empty

        # Underlay
        fill_raw.extend(_underlay_segments(fill_comp, density_px))

        # Top fill
        compactness = _compactness(fill_comp)
        eigen_ratio = _eigenvalue_ratio(fill_comp)
        user_angle  = fill_angle_deg is not None
        strategy    = _choose_fill_strategy(fill_comp, user_angle)

        if strategy == 'medial' or is_satin_zone or (not user_angle and eigen_ratio >= MEDIAL_EIGEN_THRESH):
            # Very narrow shapes get true satin columns (single-stitch bars
            # rail to rail). Mid-narrow shapes still use the skeleton-based
            # medial fill which interpolates each bar.
            segs = None
            if is_satin_zone:
                segs = _satin_column_segments(fill_comp, density_px)
            if not segs:
                segs = _medial_fill_segments(fill_comp, density_px)
            if segs:
                fill_raw.extend(segs)
            else:
                fill_raw.extend(_fill_polygon_segments(
                    fill_comp, density_px, _pca_angle(fill_comp)))
        elif strategy == 'contour' or compactness >= COMPACTNESS_THRESH:
            fill_raw.extend(_contour_fill_segments(fill_comp, density_px))
        else:
            angle = fill_angle_deg if user_angle else _pca_angle(fill_comp)
            fill_raw.extend(_fill_polygon_segments(fill_comp, density_px, angle))

        # Edge walk
        fill_raw.extend(_edge_walk_segments(fill_comp, density_px))

    # Outline (gets stitched in pass 3 — last layer always)
    if outline != 'none':
        outline_raw.extend(_outline_segments(poly, outline, outline_w_px))

    return fill_raw, outline_raw


# ─── Component classification (Tier 2 multi-pass) ────────────────────────────
def _classify_color_components(components: List[dict]) -> dict:
    """
    Split a colour's components into 'fill' (foundation) and 'detail' (accent).

    A component is a detail if:
      • its area is below DETAIL_AREA_MAX_MM2 (absolute) AND
      • its area is below DETAIL_REL_THRESHOLD × the largest component
        for the same colour.

    Detail count is capped at MAX_DETAIL_COMPONENTS (largest first) to prevent
    a noisy posterization from blowing up the jump count with tiny specks.
    """
    if not components:
        return {'fill': [], 'detail': []}

    max_area_px2 = max(c['area_px2'] for c in components)
    threshold_abs_px2 = DETAIL_AREA_MAX_MM2 * (PX_PER_MM ** 2)
    min_detail_px2 = DETAIL_AREA_MIN_MM2 * (PX_PER_MM ** 2)
    threshold_rel_px2 = max_area_px2 * DETAIL_REL_THRESHOLD
    threshold = min(threshold_abs_px2, threshold_rel_px2)

    fill_list: List[dict]   = []
    detail_list: List[dict] = []
    for c in components:
        if min_detail_px2 <= c['area_px2'] <= threshold:
            detail_list.append(c)
        else:
            fill_list.append(c)

    # Cap detail components — keep the largest if too many
    if len(detail_list) > MAX_DETAIL_COMPONENTS:
        detail_list.sort(key=lambda c: -c['area_px2'])
        detail_list = detail_list[:MAX_DETAIL_COMPONENTS]

    return {'fill': fill_list, 'detail': detail_list}


def _select_outline_indices(
    indices: list,
    palette: list,
    pixel_counts: list,
    total_px: int,
    outline_policy: str,
) -> List[int]:
    """
    Choose which non-accent colours deserve an outline pass.

    `all` preserves the older behaviour. The default `selective` policy follows
    the professional samples: final outlines are dark/accent/detail colours,
    not every light fill boundary created by posterization.
    """
    if outline_policy == 'none':
        return []
    if outline_policy == 'all':
        return list(indices)

    candidates = []
    for label_idx in indices:
        rgb = palette[label_idx]
        lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        frac = pixel_counts[label_idx] / max(total_px, 1)
        if lum <= OUTLINE_LUMINANCE_MAX and (
            outline_policy == 'dark' or frac <= OUTLINE_PIXEL_FRAC_MAX
        ):
            candidates.append((lum, -frac, label_idx))

    candidates.sort()
    return [idx for _lum, _frac, idx in candidates[:MAX_SELECTIVE_OUTLINE_COLORS]]


def _detect_accent_color(
    palette: list,
    pixel_counts: list,
    total_px: int,
    indices: list,
) -> Optional[int]:
    """
    Find a palette entry that is dark enough AND minor enough in pixel count
    to be an "accent" colour (final pass) rather than a foundation fill.

    Returns the label_idx of the accent colour, or None if no palette entry
    qualifies. Black at < 8 % of pixels is the canonical case — Z for Zebra
    runs four black stops at the very end.
    """
    for label_idx in indices:
        rgb = palette[label_idx]
        lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        frac = pixel_counts[label_idx] / total_px
        if lum < ACCENT_LUMINANCE_MAX and frac < ACCENT_PIXEL_FRAC_MAX:
            return label_idx
    return None


# ─── Image decode + resize ────────────────────────────────────────────────────
def _decode_image(image_base64: str, hoop_w_mm: float, hoop_h_mm: float) -> Image.Image:
    img = Image.open(io.BytesIO(base64.b64decode(image_base64))).convert('RGB')
    tw = int(hoop_w_mm * PX_PER_MM)
    th = int(hoop_h_mm * PX_PER_MM)
    scale = min(tw / img.width, th / img.height)
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    return img


# ─── Color quantization ───────────────────────────────────────────────────────
def _posterize(
    img: Image.Image,
    n: int,
    brand: Optional[str] = None,
) -> Tuple[np.ndarray, list]:
    """
    KMeans-cluster the image into n colours. If `brand` is given, each cluster
    centre is then snapped to its nearest entry in the named thread palette
    (e.g. 'madeira', 'isacord', 'robison-anton') so the preview, stitch
    file, and exported palette all use real stockable thread colours
    instead of arbitrary RGB centroids.
    """
    arr = np.array(img).reshape(-1, 3).astype(np.float32)
    km  = KMeans(n_clusters=n, n_init=6, random_state=42)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        labels  = km.fit_predict(arr)
    centers = km.cluster_centers_.astype(np.uint8)
    palette = [tuple(int(c) for c in rgb) for rgb in centers]

    # Snap each centre to the nearest thread in the chosen palette
    if brand:
        try:
            from thread_palette import nearest_thread
            snapped = []
            for rgb in palette:
                t = nearest_thread(rgb, brand=brand)
                snapped.append(t['rgb'])
            palette = snapped
        except Exception:
            pass  # fall back to raw KMeans centres on any error

    # Sort by brightness (darker first — better stitch layering)
    order = sorted(range(n), key=lambda i: sum(palette[i]))
    remap = {old: new for new, old in enumerate(order)}
    sorted_pal = [palette[i] for i in order]
    new_labels = np.vectorize(remap.get)(labels.reshape(img.height, img.width))
    return new_labels.astype(np.uint8), sorted_pal


# ─── Mask → polygons ─────────────────────────────────────────────────────────
def _mask_to_polygons(mask: np.ndarray, min_area: float) -> List[Polygon]:
    rings = []
    for contour in measure.find_contours(mask.astype(np.float32), 0.5):
        coords = [(c[1], c[0]) for c in contour]
        if len(coords) < 4:
            continue
        try:
            poly = Polygon(coords)
            if not poly.is_valid:
                poly = poly.buffer(0)
            if poly.area >= min_area and not poly.is_empty:
                rings.append(poly)
        except Exception:
            pass
    if not rings:
        return []

    rings.sort(key=lambda p: p.area, reverse=True)
    shells = []
    holes_by_shell = {}

    for i, ring in enumerate(rings):
        parent = None
        parent_area = float('inf')
        point = ring.representative_point()
        for j, candidate in enumerate(rings):
            if i == j or candidate.area <= ring.area:
                continue
            if candidate.contains(point) and candidate.area < parent_area:
                parent, parent_area = j, candidate.area

        if parent is None:
            holes_by_shell[i] = []
            shells.append((i, ring))
        else:
            holes_by_shell.setdefault(parent, []).append(list(ring.exterior.coords))

    polys: List[Polygon] = []
    for shell_idx, shell in shells:
        poly = Polygon(shell.exterior.coords, holes_by_shell.get(shell_idx, []))
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.area >= min_area and not poly.is_empty:
            if poly.geom_type == 'MultiPolygon':
                polys.extend([p for p in poly.geoms if p.area >= min_area])
            else:
                polys.append(poly)
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
    max_stitch_px: Optional[float] = None,
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

    # ── Order by skeleton graph, with PCA projection as a stable fallback ──
    angle_rad = math.radians(_pca_angle(poly))
    axis      = np.array([math.cos(angle_rad), math.sin(angle_rad)])
    ordered_points = _order_skeleton_points(rows, cols, ox, oy, axis)
    if len(ordered_points) < 3:
        return []
    wx_o = np.array([p[0] for p in ordered_points])
    wy_o = np.array([p[1] for p in ordered_points])

    # Use cumulative path distance for sampling; projection alone falls apart
    # on curved or branched skeletons.
    path_d = [0.0]
    for i in range(1, len(ordered_points)):
        path_d.append(path_d[-1] + math.hypot(wx_o[i] - wx_o[i-1], wy_o[i] - wy_o[i-1]))
    path_d_o = np.array(path_d)

    # ── Sample at density_px intervals ────────────────────────────────────
    max_px   = max_stitch_px if max_stitch_px is not None else MAX_STITCH_FILL_MM * PX_PER_MM
    segments = []
    last_p   = path_d_o[0] - density_px  # ensure first sample is included

    for i in range(len(wx_o)):
        if path_d_o[i] - last_p < density_px:
            continue
        last_p = path_d_o[i]
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

        # Pick the segment closest to the skeleton point.
        raw = _linear_parts(inter)
        if not raw:
            continue

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


# ─── Satin column fill (Tier 4.1 — vector medial axis) ───────────────────────
def _satin_column_segments(
    poly: Polygon,
    density_px: float,
) -> Optional[List[List[Tuple[float, float]]]]:
    """
    Generate true satin column stitches for a narrow shape.

    Uses trimesh's vector medial axis (a Voronoi-based graph) rather than
    skimage's bitmap skeleton, so the spine of the shape is traced
    accurately and tangent directions don't suffer from rasterisation
    artefacts.

    Decomposes the medial axis into trails — non-branching paths between
    endpoints (degree 1) and junctions (degree ≥ 3) — and walks each trail
    independently. This handles letter-form glyphs ("T", "Y", "F", "K")
    where the medial axis has multiple branches; the previous longest-path
    approach captured only the main spine and missed side strokes.

    Each "bar" is a single rail-to-rail stitch when the column width is
    ≤ MAX_SATIN_BAR_MM — that's the defining feature of a satin column:
    one long shiny stitch across the column, not interpolated. Bars wider
    than the cap fall back to tatami-style interpolation so we don't end
    up with snag-prone 12 mm stitches.

    Returns None if the shape is unsuitable (degenerate medial axis,
    trimesh not available, etc.) so the caller can fall back to the
    skeleton-based _medial_fill_segments.
    """
    try:
        from trimesh.path import polygons as _tp
    except ImportError:
        return None

    if poly.is_empty or not poly.is_valid:
        return None

    try:
        result = _tp.medial_axis(poly)
    except Exception:
        return None
    if result is None or len(result) != 2:
        return None
    edges, vertices = result
    if len(vertices) < 2 or len(edges) == 0:
        return None

    # Build adjacency: vertex_index -> [neighbour_index, ...]
    n_verts = len(vertices)
    adj: List[List[int]] = [[] for _ in range(n_verts)]
    for a, b in edges:
        ai, bi = int(a), int(b)
        if 0 <= ai < n_verts and 0 <= bi < n_verts and ai != bi:
            adj[ai].append(bi)
            adj[bi].append(ai)

    # ── Decompose graph into trails ──────────────────────────────────────
    # A "trail" is a non-branching path between two notable vertices —
    # endpoints (degree 1) and junctions (degree ≥ 3). Intermediate
    # vertices have exactly degree 2 (they are smooth-spine nodes).
    trails = _decompose_medial_trails(adj, n_verts)
    if not trails:
        return None

    minx, miny, maxx, maxy = poly.bounds
    far = max(maxx - minx, maxy - miny) + 20.0

    fill_max_px  = MAX_STITCH_FILL_MM * PX_PER_MM
    satin_cap_px = MAX_SATIN_BAR_MM * PX_PER_MM

    # Stitch trails longest-first so the main spine lays down first; smaller
    # branches stitch on top. _route_components will smooth inter-trail
    # ordering further.
    #
    # Trimesh's Voronoi-based medial axis produces small noise trails near
    # convex corners and shape ends — branches a few pixels long that fork
    # off and quickly rejoin. Filtering by minimum trail length removes the
    # noise while keeping legitimate branches like the T-crossbar / Y-stem.
    min_trail_px = max(density_px * 3.0, MIN_BRANCH_LENGTH_MM * PX_PER_MM)
    trail_paths = []
    for trail_indices in trails:
        path_pts = [(float(vertices[i][0]), float(vertices[i][1])) for i in trail_indices]
        if len(path_pts) < 2:
            continue
        cum = [0.0]
        for i in range(1, len(path_pts)):
            dx = path_pts[i][0] - path_pts[i-1][0]
            dy = path_pts[i][1] - path_pts[i-1][1]
            cum.append(cum[-1] + math.hypot(dx, dy))
        if cum[-1] < min_trail_px:
            continue
        trail_paths.append((path_pts, cum))

    # If filtering removed every trail (very small shape), keep the longest
    # one so we still produce some output.
    if not trail_paths and trails:
        all_paths = []
        for trail_indices in trails:
            path_pts = [(float(vertices[i][0]), float(vertices[i][1])) for i in trail_indices]
            if len(path_pts) < 2:
                continue
            cum = [0.0]
            for i in range(1, len(path_pts)):
                dx = path_pts[i][0] - path_pts[i-1][0]
                dy = path_pts[i][1] - path_pts[i-1][1]
                cum.append(cum[-1] + math.hypot(dx, dy))
            if cum[-1] >= density_px:
                all_paths.append((path_pts, cum))
        if all_paths:
            all_paths.sort(key=lambda tp: tp[1][-1], reverse=True)
            trail_paths = all_paths[:1]

    trail_paths.sort(key=lambda tp: tp[1][-1], reverse=True)

    segments: List[List[Tuple[float, float]]] = []
    bar_idx = 0
    seen_bars: set = set()  # dedupe bars from adjacent trails meeting at junctions

    for path_pts, cum in trail_paths:
        total = cum[-1]
        seg_idx = 0
        # First bar half-step into the trail so junction overlap is reduced
        d = density_px / 2.0
        while d <= total:
            while seg_idx + 1 < len(cum) and cum[seg_idx + 1] < d:
                seg_idx += 1
            if seg_idx + 1 >= len(cum):
                break
            seg_len = cum[seg_idx + 1] - cum[seg_idx]
            if seg_len < 1e-6:
                d += density_px
                continue
            t = (d - cum[seg_idx]) / seg_len
            x = path_pts[seg_idx][0] + t * (path_pts[seg_idx + 1][0] - path_pts[seg_idx][0])
            y = path_pts[seg_idx][1] + t * (path_pts[seg_idx + 1][1] - path_pts[seg_idx][1])

            # Tangent — use a small window for stability
            i0 = max(0, seg_idx - 1)
            i1 = min(len(path_pts) - 1, seg_idx + 2)
            tdx = path_pts[i1][0] - path_pts[i0][0]
            tdy = path_pts[i1][1] - path_pts[i0][1]
            tlen = math.hypot(tdx, tdy)
            if tlen < 1e-6:
                d += density_px
                continue
            tdx /= tlen
            tdy /= tlen
            nx, ny = -tdy, tdx   # perpendicular

            bar = LineString([(x + nx * far, y + ny * far),
                              (x - nx * far, y - ny * far)])
            try:
                inter = poly.intersection(bar)
            except Exception:
                d += density_px
                continue
            if inter.is_empty:
                d += density_px
                continue

            raw = _linear_parts(inter)
            if not raw:
                d += density_px
                continue

            best = None
            best_score = float('inf')
            for s in raw:
                if len(s) < 2:
                    continue
                mx = (s[0][0] + s[-1][0]) / 2
                my = (s[0][1] + s[-1][1]) / 2
                score = math.hypot(mx - x, my - y)
                if score < best_score:
                    best_score = score
                    best = s
            if best is None:
                d += density_px
                continue

            x0, y0 = best[0]
            x1, y1 = best[-1]
            bar_len = math.hypot(x1 - x0, y1 - y0)
            if bar_len < MIN_STITCH_PX:
                d += density_px
                continue

            # Dedupe near-identical bars across trails (junction overlap).
            # Bucket by midpoint at MIN_STITCH_PX granularity.
            mid_bx = round((x0 + x1) / 2.0 / MIN_STITCH_PX)
            mid_by = round((y0 + y1) / 2.0 / MIN_STITCH_PX)
            bar_key = (mid_bx, mid_by)
            if bar_key in seen_bars:
                d += density_px
                continue
            seen_bars.add(bar_key)

            if bar_len <= satin_cap_px:
                pts = [(x0, y0), (x1, y1)]
            else:
                phase = (bar_idx % TATAMI_CYCLE) / TATAMI_CYCLE
                pts = _interpolate_tatami(x0, y0, x1, y1, phase, fill_max_px)

            # Alternate direction so consecutive bars zig-zag cleanly
            if bar_idx % 2 == 1:
                pts = list(reversed(pts))

            segments.append(pts)
            d += density_px
            bar_idx += 1

    return segments if segments else None


def _decompose_medial_trails(adj: List[List[int]], n_verts: int) -> List[List[int]]:
    """
    Decompose a medial-axis graph into non-branching trails.

    A trail starts at a notable vertex (degree 1 = endpoint, or degree
    ≥ 3 = junction) and follows degree-2 intermediate vertices to the
    next notable vertex. Each undirected edge appears in exactly one trail.

    Returns a list of vertex-index sequences. Internal cycles (purely
    degree-2 loops) are also captured as single trails that revisit the
    starting vertex at the end.
    """
    visited_edges: set = set()
    trails: List[List[int]] = []

    def edge_key(a: int, b: int) -> Tuple[int, int]:
        return (a, b) if a < b else (b, a)

    def trace(start: int, first_step: int) -> List[int]:
        trail = [start]
        prev, cur = start, first_step
        while True:
            visited_edges.add(edge_key(prev, cur))
            trail.append(cur)
            # Stop at endpoints and junctions
            if len(adj[cur]) != 2:
                return trail
            # Continue along the only unvisited neighbour
            a, b = adj[cur]
            nxt = a if a != prev else b
            if edge_key(cur, nxt) in visited_edges:
                return trail   # cycle / already-walked edge
            prev, cur = cur, nxt

    # Pass 1 — start every trail from an endpoint or junction
    for v in range(n_verts):
        deg = len(adj[v])
        if deg == 1 or deg >= 3:
            for nb in adj[v]:
                if edge_key(v, nb) in visited_edges:
                    continue
                trail = trace(v, nb)
                if len(trail) >= 2:
                    trails.append(trail)

    # Pass 2 — pure degree-2 cycles (no notable vertex). Pick any unvisited
    # edge and trace; trail loops back to the start vertex.
    for v in range(n_verts):
        if len(adj[v]) != 2:
            continue
        for nb in adj[v]:
            if edge_key(v, nb) in visited_edges:
                continue
            trail = trace(v, nb)
            if len(trail) >= 2:
                trails.append(trail)

    return trails


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
    for ring in poly.interiors:
        hole_px = [(int(x - ox), int(y - oy)) for x, y in ring.coords]
        if len(hole_px) >= 3:
            draw.polygon(hole_px, fill=0)
    return np.array(img) > 0


def _order_skeleton_points(
    rows: np.ndarray,
    cols: np.ndarray,
    ox: float,
    oy: float,
    fallback_axis: np.ndarray,
) -> List[Tuple[float, float]]:
    """Trace the longest skeleton path first, then append side branches stably."""
    pixels = [(int(r), int(c)) for r, c in zip(rows, cols)]
    index = {p: i for i, p in enumerate(pixels)}
    if not pixels:
        return []

    neighbors = {i: [] for i in range(len(pixels))}
    for i, (r, c) in enumerate(pixels):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                j = index.get((r + dr, c + dc))
                if j is not None:
                    neighbors[i].append(j)

    def farthest_from(start):
        seen = {start}
        parent = {start: None}
        queue = [start]
        for node in queue:
            for nxt in neighbors[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    parent[nxt] = node
                    queue.append(nxt)
        return queue[-1], parent, seen

    endpoints = [i for i, ns in neighbors.items() if len(ns) <= 1]
    start = endpoints[0] if endpoints else 0
    a, _, _ = farthest_from(start)
    b, parent, _ = farthest_from(a)

    path = []
    cur = b
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()

    # Append branch pixels by projection so branch handling remains
    # deterministic without pretending a branched skeleton is one continuous line.
    path_set = set(path)
    remaining = [i for i in range(len(pixels)) if i not in path_set]
    remaining.sort(key=lambda i: (np.array([pixels[i][1] + ox, pixels[i][0] + oy]) @ fallback_axis))
    ordered = path + remaining
    return [(pixels[i][1] + ox, pixels[i][0] + oy) for i in ordered]


# ─── Fill: return list of segments (with tatami offset) ──────────────────────
def _fill_polygon_segments(
    poly: Polygon,
    density_px: float,
    angle_deg: float,
    max_stitch_px: Optional[float] = None,
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

    rot_poly = affinity.rotate(poly, -angle_deg, origin=(0, 0), use_radians=False)
    if not rot_poly.is_valid:
        rot_poly = rot_poly.buffer(0)

    minx, miny, maxx, maxy = rot_poly.bounds
    max_px   = max_stitch_px if max_stitch_px is not None else MAX_STITCH_FILL_MM * PX_PER_MM
    segments = []
    row = 0
    y   = miny + density_px / 2

    while y <= maxy:
        # Tatami phase: shift stitch start by 0, 1/3, 2/3 of max stitch length
        phase = (row % TATAMI_CYCLE) / TATAMI_CYCLE

        inter = rot_poly.intersection(LineString([(minx-1, y), (maxx+1, y)]))
        if not inter.is_empty:
            raw = _linear_parts(inter)
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
    Walk from (x0,y0) to (x1,y1) in steps of max_px.

    The first interior stitch is placed at distance `(phase + 1) * max_px / cycle`
    along the segment so consecutive rows don't align — a phase of 0 still
    yields a *full step* away from the start (not a duplicate of (x0,y0)).
    Subsequent stitches are spaced by max_px with ±STITCH_JITTER variation.

    Returns a list of points starting with (x0,y0) and ending at or near (x1,y1).
    Consecutive duplicates within MIN_STITCH_PX are removed — defensive against
    polygon intersections that hand us coincident endpoints.
    """
    dx, dy = x1 - x0, y1 - y0
    dist   = math.hypot(dx, dy)
    if dist < MIN_STITCH_PX:
        return [(x0, y0)]

    pts   = [(x0, y0)]
    # Offset the first interior step by phase * max_px so adjacent rows are
    # phase-shifted, but keep d > 0 so we never re-emit (x0, y0).
    d     = max_px * (1.0 - phase * (1.0 - 1.0 / TATAMI_CYCLE))
    step_i = 0
    while d < dist:
        t = d / dist
        pts.append((x0 + dx*t, y0 + dy*t))
        # Deterministic jitter keeps output reproducible while avoiding rigid rows.
        d += max_px * (1.0 + _stable_jitter(x0, y0, x1, y1, phase, step_i))
        step_i += 1
    # Always end exactly at (x1, y1) — but only if it isn't already there.
    if math.hypot(pts[-1][0]-x1, pts[-1][1]-y1) > MIN_STITCH_PX:
        pts.append((x1, y1))

    # Defensive dedupe: drop any consecutive points within MIN_STITCH_PX.
    # In practice this catches degenerate polygon edges and rounding issues.
    if len(pts) > 1:
        out = [pts[0]]
        for p in pts[1:]:
            if math.hypot(p[0]-out[-1][0], p[1]-out[-1][1]) >= MIN_STITCH_PX:
                out.append(p)
        pts = out
    return pts


def _stable_jitter(
    x0: float, y0: float,
    x1: float, y1: float,
    phase: float,
    step_i: int,
) -> float:
    key = f'{x0:.2f},{y0:.2f},{x1:.2f},{y1:.2f},{phase:.3f},{step_i}'.encode('utf-8')
    raw = hashlib.blake2b(key, digest_size=4).digest()
    unit = int.from_bytes(raw, 'little') / 0xFFFFFFFF
    return (unit * 2.0 - 1.0) * STITCH_JITTER


def _interpolate_polyline(
    coords: List[Tuple[float, float]],
    max_px: float,
    phase: float = 0.0,
) -> List[Tuple[float, float]]:
    """
    Walk a multi-point polyline and emit stitches every max_px along its
    cumulative arc length. Avoids the corner-duplication problem of calling
    _interpolate_tatami once per edge and extending the result list.

    `phase` (0..1) shifts the first interior stitch; pass per-row phase to
    desynchronise consecutive rows in fill scans. The first emitted stitch
    is always exactly at coords[0]; the last is exactly at coords[-1].

    Buffered polygons can carry thousands of near-duplicate vertices around
    rounded corners; we collapse them to a clean polyline up front so the
    arc-length walk is well-behaved.
    """
    if len(coords) < 2:
        return list(coords)

    # ── Preprocess: drop near-duplicate consecutive points ───────────────
    # Shapely's negative buffer produces densely-spaced vertices around
    # rounded corners. We need a polyline whose edges are at least
    # MIN_STITCH_PX long so the arc-length walk doesn't get hung up on
    # microscopic edges.
    clean = [coords[0]]
    for p in coords[1:]:
        if math.hypot(p[0] - clean[-1][0], p[1] - clean[-1][1]) >= MIN_STITCH_PX:
            clean.append(p)
    if len(clean) < 2:
        return [coords[0]]
    coords = clean

    # Cumulative arc length over the cleaned polyline
    cum = [0.0]
    for i in range(1, len(coords)):
        dx = coords[i][0] - coords[i-1][0]
        dy = coords[i][1] - coords[i-1][1]
        cum.append(cum[-1] + math.hypot(dx, dy))
    total = cum[-1]
    if total < MIN_STITCH_PX:
        return [coords[0]]

    # Sample positions: start, then phase-shifted first interior, then max_px
    # increments with jitter, then exact end.
    out = [coords[0]]
    d = max_px * (1.0 - phase * (1.0 - 1.0 / TATAMI_CYCLE))
    step_i = 0
    seg_idx = 0
    while d < total - MIN_STITCH_PX:
        # Advance seg_idx so coords[seg_idx]..coords[seg_idx+1] contains d
        while seg_idx + 1 < len(cum) and cum[seg_idx + 1] < d:
            seg_idx += 1
        if seg_idx + 1 >= len(cum):
            break
        seg_len = cum[seg_idx + 1] - cum[seg_idx]
        # All edges are >= MIN_STITCH_PX after the preprocess pass, so
        # division is safe.
        t = (d - cum[seg_idx]) / seg_len
        x = coords[seg_idx][0] + t * (coords[seg_idx + 1][0] - coords[seg_idx][0])
        y = coords[seg_idx][1] + t * (coords[seg_idx + 1][1] - coords[seg_idx][1])
        if math.hypot(x - out[-1][0], y - out[-1][1]) >= MIN_STITCH_PX:
            out.append((x, y))
        d += max_px * (1.0 + _stable_jitter(coords[0][0], coords[0][1],
                                            coords[-1][0], coords[-1][1],
                                            phase, step_i))
        step_i += 1

    # End exactly at coords[-1]
    if math.hypot(coords[-1][0] - out[-1][0], coords[-1][1] - out[-1][1]) >= MIN_STITCH_PX:
        out.append(coords[-1])
    return out


# ─── Shape compactness ───────────────────────────────────────────────────────
def _compactness(poly: Polygon) -> float:
    """4π·area / perimeter² — 1.0 for circle, ~0 for thin spike."""
    p = poly.length
    if p < 1e-6:
        return 0.0
    return min(1.0, (4 * math.pi * poly.area) / (p * p))


def _directional_pull_compensation(
    poly: Polygon,
    pull_px: float,
    stitch_angle_deg: float,
) -> Polygon:
    """
    Compensate mostly across the stitch direction, where fabric pull is strongest.
    A tiny along-stitch expansion prevents pointed ends from shrinking too much.
    """
    if pull_px <= 0 or poly.is_empty:
        return poly

    minx, miny, maxx, maxy = poly.bounds
    w = max(maxx - minx, 1.0)
    h = max(maxy - miny, 1.0)
    cx, cy = poly.centroid.x, poly.centroid.y

    rotated = affinity.rotate(poly, -stitch_angle_deg, origin=(cx, cy), use_radians=False)
    # X is stitch direction, Y is cross-pull after rotation.
    xfact = 1.0 + min(0.03, (pull_px * 0.25) / w)
    yfact = 1.0 + min(0.12, pull_px / h)
    scaled = affinity.scale(rotated, xfact=xfact, yfact=yfact, origin=(cx, cy))
    restored = affinity.rotate(scaled, stitch_angle_deg, origin=(cx, cy), use_radians=False)
    return restored.buffer(0)


def _choose_fill_strategy(poly: Polygon, user_angle: bool) -> str:
    """Return medial, contour, or scan using a few cheap shape-quality signals."""
    if poly.is_empty:
        return 'scan'
    compactness = _compactness(poly)
    eigen_ratio = _eigenvalue_ratio(poly)
    minx, miny, maxx, maxy = poly.bounds
    width = max(maxx - minx, 1.0)
    height = max(maxy - miny, 1.0)
    bbox_area = width * height
    extent = poly.area / bbox_area
    hole_count = len(getattr(poly, 'interiors', []))

    if not user_angle and hole_count == 0 and eigen_ratio >= MEDIAL_EIGEN_THRESH:
        return 'medial'
    if hole_count == 0 and compactness >= COMPACTNESS_THRESH and extent > 0.45:
        return 'contour'
    return 'scan'


def _linear_parts(geom) -> List[List[Tuple[float, float]]]:
    if geom.is_empty:
        return []
    if isinstance(geom, LineString):
        coords = list(geom.coords)
        return [coords] if len(coords) >= 2 else []
    if isinstance(geom, MultiLineString) or hasattr(geom, 'geoms'):
        parts: List[List[Tuple[float, float]]] = []
        for g in geom.geoms:
            if isinstance(g, LineString):
                coords = list(g.coords)
                if len(coords) >= 2:
                    parts.append(coords)
        return parts
    return []


# ─── Contour fill (inward concentric rings) ───────────────────────────────────
def _contour_fill_segments(
    poly: Polygon,
    density_px: float,
    max_stitch_px: Optional[float] = None,
) -> List[List[Tuple[float, float]]]:
    """
    Fill by repeatedly shrinking the polygon inward by density_px.
    Produces concentric rings that follow the shape boundary — great for
    circles, ovals, flower centres, rounded leaves.
    Alternates CW/CCW so consecutive rings connect cleanly.
    """
    max_px   = max_stitch_px if max_stitch_px is not None else MAX_STITCH_FILL_MM * PX_PER_MM
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

            phase = (ring % TATAMI_CYCLE) / TATAMI_CYCLE
            pts = _interpolate_polyline(coords, max_px, phase)
            if len(pts) >= 2:
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
    Adaptive stabilising pass stitched before the top fill.
    Small pieces get a light center walk, narrow pieces get medial support,
    and broad fills get sparse cross-grain scan lines.

    Underlay uses MAX_STITCH_UNDERLAY_MM (2.5 mm) rather than the 4 mm fill
    cap — pros use shorter stitches under the top layer for stability.
    """
    area_mm2 = poly.area / (PX_PER_MM * PX_PER_MM)
    minx, miny, maxx, maxy = poly.bounds
    narrow_mm = min(maxx - minx, maxy - miny) / PX_PER_MM

    underlay_max_px = MAX_STITCH_UNDERLAY_MM * PX_PER_MM

    if area_mm2 < 18:
        return _contour_fill_segments(poly, density_px * 1.8,
                                      max_stitch_px=underlay_max_px)[:1]
    if narrow_mm < SATIN_WIDTH_MM * 1.4:
        medial = _medial_fill_segments(poly, density_px * UNDERLAY_DENSITY,
                                       max_stitch_px=underlay_max_px)
        if medial:
            return medial

    # Broad fills use PCA + 90° (cross-grain)
    base_angle = _pca_angle(poly)
    underlay_angle = (base_angle + 90) % 180
    underlay_density = density_px * UNDERLAY_DENSITY
    return _fill_polygon_segments(poly, underlay_density, underlay_angle,
                                  max_stitch_px=underlay_max_px)


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
    max_px   = MAX_STITCH_FILL_MM * PX_PER_MM
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

            pts = _interpolate_polyline(coords, max_px, phase=0.0)
            if len(pts) >= 2:
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
        max_px = MAX_STITCH_OUTLINE_MM * PX_PER_MM
        rings = [coords] + [list(r.coords) for r in simplified.interiors]
        segs = []
        for ring in rings:
            pts = _interpolate_polyline(ring, max_px, phase=0.0)
            if len(pts) >= 2:
                segs.append(pts)
        return segs

    if mode == 'satin':
        half = width_px / 2.0
        segs: List[List[Tuple[float, float]]] = []
        rings = [coords] + [list(r.coords) for r in simplified.interiors]
        STEP = max(2.0, width_px * 0.8)
        for ring_idx, ring in enumerate(rings):
            n = len(ring) - 1
            for i in range(n):
                x0, y0 = ring[i]
                x1, y1 = ring[(i+1) % n]
                elen = math.hypot(x1-x0, y1-y0)
                if elen < 1e-6:
                    continue
                ex, ey = (x1-x0)/elen, (y1-y0)/elen
                normal_sign = -1 if ring_idx == 0 else 1
                nx, ny = ey * normal_sign, -ex * normal_sign
                steps = max(1, int(elen / STEP))
                for s in range(steps):
                    t  = (s + 0.5) / steps
                    mx = x0 + t*(x1-x0)
                    my = y0 + t*(y1-y0)
                    # Clamp each bar to the buffered outline band. This softens
                    # concave corners and keeps inner holes from throwing long bars.
                    bar = LineString([(mx+nx*half, my+ny*half),
                                      (mx-nx*half, my-ny*half)])
                    clipped = _linear_parts(bar.intersection(poly.buffer(half)))
                    if clipped:
                        best = max(clipped, key=lambda p: math.hypot(p[-1][0]-p[0][0], p[-1][1]-p[0][1]))
                        segs.append(best)
                    else:
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


def _route_components(
    components: List[List[List[Tuple[float, float]]]],
) -> Tuple[List[List[Tuple[float, float]]], List[int]]:
    """
    Sort segments inside each connected component, then route components as
    units. Returning component ids lets the exporter trim/jump between objects.
    """
    routed = [_greedy_sort(c) for c in components if c]
    if not routed:
        return [], []

    remaining = list(range(len(routed)))
    ordered_components = []

    def d(a, b): return math.hypot(a[0]-b[0], a[1]-b[1])

    cur = min(remaining, key=lambda i: d(routed[i][0][0], (0, 0)))
    remaining.remove(cur)
    ordered_components.append((cur, routed[cur]))
    tail = routed[cur][-1][-1]

    while remaining:
        best, best_d, flip = None, float('inf'), False
        for i in remaining:
            ds = d(tail, routed[i][0][0])
            de = d(tail, routed[i][-1][-1])
            if ds < best_d:
                best, best_d, flip = i, ds, False
            if de < best_d:
                best, best_d, flip = i, de, True
        remaining.remove(best)
        comp = routed[best]
        if flip:
            comp = [list(reversed(seg)) for seg in reversed(comp)]
        ordered_components.append((best, comp))
        tail = comp[-1][-1]

    flat: List[List[Tuple[float, float]]] = []
    ids: List[int] = []
    for comp_id, comp in ordered_components:
        for seg in comp:
            flat.append(seg)
            ids.append(comp_id)
    return flat, ids


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
