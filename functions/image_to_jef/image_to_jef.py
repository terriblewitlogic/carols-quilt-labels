"""
Netlify function: POST /api/image_to_jef

Accepts:
  {
    imageBase64:     string,   // PNG, no data: prefix
    hoop_w_mm:       number,
    hoop_h_mm:       number,
    num_colors:      number,   // 2–6, default 4
    density_mm:      number,   // default 0.4
    fill_angle_deg:  number,   // default 45
    min_feature_mm:  number,   // default 1.5
    outline:         string,   // 'none'|'running'|'satin', default 'running'
    outline_width_mm:number,   // default 1.0
    outline_policy:  string,   // 'selective'|'all'|'dark'|'none', default 'selective'
    format:          string,   // 'jef'|'pes'|'dst'|'vp3'|'exp'|'xxx', default 'jef'
  }

Returns:
  {
    jefBase64:       string,
    previewSvg:      string,
    stitchCount:     number,
    colors:          string[],   // hex palette
  }
"""
import json
import base64
import math
import tempfile
import os
import traceback

import pyembroidery
from raster_to_stitches import raster_to_stitch_groups
from thread_palette import snap_palette
from instruction_sheet import build_pdf as build_instruction_pdf

SUPPORTED_FORMATS = {'jef', 'pes', 'dst', 'vp3', 'exp', 'xxx'}
READ_ONLY_FORMATS = {'hus', 'vip'}


def handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 204, 'headers': _cors(), 'body': ''}

    try:
        body = json.loads(event.get('body') or '{}')
    except json.JSONDecodeError as e:
        return _error(400, f'Invalid JSON: {e}')

    image_b64 = body.get('imageBase64', '')
    if not image_b64:
        return _error(400, 'imageBase64 is required')

    hoop_w       = float(body.get('hoop_w_mm', 100))
    hoop_h       = float(body.get('hoop_h_mm', 100))
    n_colors     = int(body.get('num_colors', 4))
    density      = float(body.get('density_mm', 0.4))
    _angle_raw   = body.get('fill_angle_deg', None)
    angle        = float(_angle_raw) if _angle_raw is not None else None
    min_feat     = float(body.get('min_feature_mm', 0.8))
    outline      = body.get('outline', 'running')
    out_w        = float(body.get('outline_width_mm', 1.0))
    outline_policy = body.get('outline_policy', 'selective')
    fmt          = body.get('format', 'jef').lower().lstrip('.')
    brand        = body.get('thread_brand', 'madeira')
    color_order  = body.get('color_order', None)   # optional list[int] from UI layer panel

    if fmt not in SUPPORTED_FORMATS:
        if fmt in READ_ONLY_FORMATS:
            return _error(
                400,
                f'Format "{fmt}" can be read for analysis but is not exportable '
                'with the current pyembroidery writer.',
            )
        return _error(400, f'Unsupported format "{fmt}"')
    if outline_policy not in {'selective', 'all', 'dark', 'none'}:
        return _error(400, f'Unsupported outline_policy "{outline_policy}"')

    try:
        groups, preview_svg, palette_hex = raster_to_stitch_groups(
            image_b64,
            hoop_w_mm=hoop_w,
            hoop_h_mm=hoop_h,
            num_colors=max(2, min(6, n_colors)),
            density_mm=density,
            fill_angle_deg=angle,
            min_feature_mm=min_feat,
            outline=outline,
            outline_width_mm=out_w,
            outline_policy=outline_policy,
            color_order=color_order,
            thread_brand=brand,
        )
    except Exception as e:
        return _error(500, f'Conversion failed: {e}\n{traceback.format_exc()}')

    if not groups:
        return _error(422, 'No stitch regions found. Try reducing min feature size or increasing num_colors.')

    total_segs = sum(len(g.get('segments', [])) for g in groups)
    if total_segs == 0:
        return _error(422, 'No stitch segments generated. Try adjusting fill settings.')

    try:
        pattern, stitch_count = _build_pattern(groups)
        file_bytes = _write_pattern(pattern, fmt)
    except Exception as e:
        return _error(500, f'Export failed: {e}\n{traceback.format_exc()}')

    threads = snap_palette(palette_hex, brand=brand)
    suggestions = _stitch_suggestions(stitch_count, density, min_feat, n_colors)

    # Map per-group thread metadata so the instruction sheet shows the right
    # thread code at every colour stop (multi-pass groups can repeat colours).
    color_to_thread = {t['original_hex'].lower(): t for t in threads}
    per_stop_threads = []
    for g in groups:
        meta = color_to_thread.get(g.get('color', '').lower(), {})
        per_stop_threads.append({
            'code': meta.get('code', '—'),
            'name': meta.get('name', '—'),
            'hex':  meta.get('thread_hex', g.get('color', '#000000')),
        })

    try:
        from thread_palette import PALETTE_LABELS
        brand_label = PALETTE_LABELS.get(brand, brand.title())
    except Exception:
        brand_label = brand.title()

    instruction_pdf_b64 = ''
    try:
        pdf_bytes = build_instruction_pdf(
            pattern, groups,
            design_name=body.get('design_name', 'Untitled Design'),
            hoop_w_mm=hoop_w, hoop_h_mm=hoop_h,
            format=fmt,
            thread_brand=brand_label,
            thread_codes=per_stop_threads,
        )
        instruction_pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
    except Exception as e:
        # Don't block the export if PDF generation fails — log and continue.
        print(f'[image_to_jef] PDF generation failed: {e}')

    return {
        'statusCode': 200,
        'headers': {**_cors(), 'Content-Type': 'application/json'},
        'body': json.dumps({
            'jefBase64':         base64.b64encode(file_bytes).decode('utf-8'),
            'previewSvg':        preview_svg,
            'stitchCount':       stitch_count,
            'colors':            palette_hex,
            'threads':           threads,
            'suggestions':       suggestions,
            'instructionPdfBase64': instruction_pdf_b64,
        }),
    }


# Travel-run thresholds (in pyembroidery units = 0.1 mm).
#
# Within a single colour group the encoder takes one of four paths based on
# the gap between the previous segment's end and the next segment's start:
#
#   gap < 2 mm:                            single plain stitch
#   role-dependent same-colour fill gaps:  travel run (stitches under fill)
#   gap < 4 mm same outline component:     short carry
#   anything else:                         JUMP, with role-aware TRIM thresholds
#
# Pro embroidery files (Hatch-digitized examples) sit at ~0.8% jumps; before
# this change ours hit 6.7% and after the first cut 3.5%.
_SHORT_JUMP_EMB         = 20    # 2 mm — plain stitch
_TRAVEL_GAP_FOUNDATION_EMB = 1200 # 120 mm — foundation travel is usually buried
_TRAVEL_GAP_DETAIL_EMB     = 800  # 80 mm — detail travel avoids trim storms
_TRAVEL_GAP_FILL_EMB       = 500  # 50 mm — fallback for uncategorized fills
_OUTLINE_CONNECT_EMB    = 40    # 4 mm — short same-component outline carries
_TRIM_GAP_FOUNDATION_EMB = 1200 # 120 mm — foundation carries are usually buried
_TRIM_GAP_DETAIL_EMB     = 1200 # 120 mm — detail islands can jump without knot storms
_TRIM_GAP_OUTLINE_EMB    = 800  # 80 mm — outline carries are easiest to notice
_TRAVEL_STEP_EMB        = 25    # travel stitches every 2.5 mm (matches OUTLINE cap)


def _build_pattern(groups):
    """
    Convert stitch groups to a pyembroidery pattern.

    Travel runs: short moves inside the same source component are stitched as
    connectors. Moves between components or across obvious whitespace use
    trim/jump so they do not leave visible threads on the fabric.
    """
    pattern = pyembroidery.EmbPattern()
    stitch_count = 0
    any_added = False

    for group in groups:
        color_hex = group['color']
        segments = group.get('segments', [])
        component_ids = group.get('componentIds') or [0] * len(segments)
        group_type = group.get('type', 'fill')
        if not segments:
            continue

        thread = pyembroidery.EmbThread()
        thread.color = _hex_to_int(color_hex)
        thread.name = color_hex
        pattern.add_thread(thread)

        if any_added:
            pattern.add_command(pyembroidery.COLOR_BREAK)
        any_added = True

        prev_end = None   # (x, y) of last stitched point in this colour block
        prev_component = None
        group_role = group.get('role', '')
        trim_gap = _trim_gap_for_group(group_type, group_role)

        def add_stitch(x, y):
            nonlocal stitch_count
            pattern.add_stitch_absolute(pyembroidery.STITCH, x, y)
            stitch_count += 1

        for seg_i, seg in enumerate(segments):
            if not seg:
                continue

            x0, y0 = seg[0]['x'], seg[0]['y']
            component_id = component_ids[seg_i] if seg_i < len(component_ids) else 0

            if prev_end is not None:
                px, py = prev_end
                gap = math.hypot(x0 - px, y0 - py)
                same_component = component_id == prev_component

                # Decide jump / travel / plain-stitch — see threshold block above.
                travel_limit = _travel_gap_for_group(group_type, group_role)

                if gap <= _SHORT_JUMP_EMB:
                    # < 2 mm — emit a plain stitch and continue
                    add_stitch(x0, y0)
                elif (
                    (group_type != 'outline' and gap <= travel_limit)
                    or (group_type == 'outline' and same_component and gap <= _OUTLINE_CONNECT_EMB)
                ):
                    # ── Travel run ──────────────────────────────────────
                    # Walk across the gap at _TRAVEL_STEP_EMB intervals.
                    # Same-colour thread blends with whatever fill it crosses.
                    steps = max(1, int(gap / _TRAVEL_STEP_EMB))
                    for i in range(1, steps + 1):
                        t  = i / steps
                        tx = px + (x0 - px) * t
                        ty = py + (y0 - py) * t
                        add_stitch(tx, ty)
                else:
                    # ── Jump to next segment ─────────────────────────────
                    # TRIM only on genuinely long carries. Professional files
                    # routinely leave shorter same-colour jumps untrimmed to
                    # avoid stop-start knots and trim storms.
                    if gap > trim_gap:
                        pattern.add_command(pyembroidery.TRIM)
                    pattern.add_stitch_absolute(pyembroidery.JUMP, x0, y0)
                    add_stitch(x0, y0)
            else:
                # First segment of this colour block
                pattern.add_stitch_absolute(pyembroidery.JUMP, x0, y0)
                add_stitch(x0, y0)

            for s in seg[1:]:
                add_stitch(s['x'], s['y'])

            prev_end = (seg[-1]['x'], seg[-1]['y'])
            prev_component = component_id

    pattern.add_command(pyembroidery.END)
    return pattern, stitch_count


def _trim_gap_for_group(group_type, group_role):
    """Return role-aware trim threshold in embroidery units (0.1 mm)."""
    if group_type == 'outline':
        return _TRIM_GAP_OUTLINE_EMB
    if group_role in {'foundation', 'background'}:
        return _TRIM_GAP_FOUNDATION_EMB
    return _TRIM_GAP_DETAIL_EMB


def _travel_gap_for_group(group_type, group_role):
    """Return role-aware same-colour travel-run threshold in 0.1 mm units."""
    if group_type == 'outline':
        return _OUTLINE_CONNECT_EMB
    if group_role in {'foundation', 'background'}:
        return _TRAVEL_GAP_FOUNDATION_EMB
    if group_role in {'detail', 'accent'}:
        return _TRAVEL_GAP_DETAIL_EMB
    return _TRAVEL_GAP_FILL_EMB


def _write_pattern(pattern, fmt):
    with tempfile.NamedTemporaryFile(suffix=f'.{fmt}', delete=False) as f:
        tmp_path = f.name
    try:
        pyembroidery.write(pattern, tmp_path)
        with open(tmp_path, 'rb') as f:
            return f.read()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _stitch_suggestions(stitch_count, density_mm, min_feature_mm, num_colors):
    """
    Return a list of plain-English suggestions when the stitch count is high.
    Each suggestion has: { text, param, current, suggested }
    Returns [] when count is acceptable (< 25k).
    """
    WARN  = 25_000
    HIGH  = 40_000
    if stitch_count < WARN:
        return []

    tips = []

    # Density — biggest lever, roughly linear effect on stitch count
    if density_mm < 0.55:
        suggested = round(min(density_mm + 0.15, 0.70), 2)
        reduction = int((1 - density_mm / suggested) * 100)
        tips.append({
            'text': f'Increase fill density from {density_mm} → {suggested} mm '
                    f'(~{reduction}% fewer stitches, slightly looser fill)',
            'param': 'density_mm',
            'current': density_mm,
            'suggested': suggested,
        })

    # Min feature size — removes small detail regions entirely
    if min_feature_mm < 2.5:
        suggested = round(min_feature_mm + 1.0, 1)
        tips.append({
            'text': f'Raise minimum feature size from {min_feature_mm} → {suggested} mm '
                    f'(drops small detail regions that add stitches without visible benefit)',
            'param': 'min_feature_mm',
            'current': min_feature_mm,
            'suggested': suggested,
        })

    # Colour count — fewer colours = fewer regions = less total filled area
    if num_colors > 3 and stitch_count > HIGH:
        suggested = num_colors - 1
        tips.append({
            'text': f'Reduce colours from {num_colors} → {suggested} '
                    f'(merges the two most similar colours, shrinks filled area)',
            'param': 'num_colors',
            'current': num_colors,
            'suggested': suggested,
        })

    # Always add a time estimate context line
    minutes = round(stitch_count / 400 / 60, 1)
    tips.append({
        'text': f'At 400 spm this is ~{minutes} min of machine time. '
                f'Most home machines handle up to ~50k stitches comfortably.',
        'param': None,
        'current': None,
        'suggested': None,
    })

    return tips


def _hex_to_int(hex_color):
    h = hex_color.lstrip('#')
    return (int(h[0:2], 16) << 16) | (int(h[2:4], 16) << 8) | int(h[4:6], 16)


def _cors():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
    }


def _error(status, message):
    return {
        'statusCode': status,
        'headers': {**_cors(), 'Content-Type': 'application/json'},
        'body': json.dumps({'error': message}),
    }
