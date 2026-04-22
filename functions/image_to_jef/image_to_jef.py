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
    format:          string,   // 'jef'|'pes'|..., default 'jef'
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

SUPPORTED_FORMATS = {'jef', 'pes', 'dst', 'vp3', 'exp', 'xxx', 'hus'}


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

    hoop_w  = float(body.get('hoop_w_mm', 100))
    hoop_h  = float(body.get('hoop_h_mm', 100))
    n_colors = int(body.get('num_colors', 4))
    density  = float(body.get('density_mm', 0.4))
    _angle_raw = body.get('fill_angle_deg', None)
    angle    = float(_angle_raw) if _angle_raw is not None else None
    min_feat = float(body.get('min_feature_mm', 1.5))
    outline  = body.get('outline', 'running')
    out_w    = float(body.get('outline_width_mm', 1.0))
    fmt      = body.get('format', 'jef').lower().lstrip('.')
    brand    = body.get('thread_brand', 'madeira')

    if fmt not in SUPPORTED_FORMATS:
        return _error(400, f'Unsupported format "{fmt}"')

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

    return {
        'statusCode': 200,
        'headers': {**_cors(), 'Content-Type': 'application/json'},
        'body': json.dumps({
            'jefBase64':   base64.b64encode(file_bytes).decode('utf-8'),
            'previewSvg':  preview_svg,
            'stitchCount': stitch_count,
            'colors':      palette_hex,
            'threads':     threads,
            'suggestions': suggestions,  # [] when count is fine
        }),
    }


# Travel-run thresholds (in pyembroidery units = 0.1 mm)
_TRAVEL_MAX_EMB  = 120   # gaps < 12 mm get a travel run instead of a jump
_TRAVEL_STEP_EMB =  30   # travel stitches every 3 mm


def _build_pattern(groups):
    """
    Convert stitch groups to a pyembroidery pattern.

    Travel runs: within a single colour block, if two consecutive segments are
    < _TRAVEL_MAX_EMB apart, connect them with short running stitches instead
    of a JUMP.  This reduces trim count (the video calls these "connector
    stitches") and mirrors what Hatch's auto-digitizer does automatically.
    """
    pattern = pyembroidery.EmbPattern()
    stitch_count = 0
    any_added = False

    for group in groups:
        color_hex = group['color']
        segments = group.get('segments', [])
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

        for seg in segments:
            if not seg:
                continue

            x0, y0 = seg[0]['x'], seg[0]['y']

            if prev_end is not None:
                px, py = prev_end
                gap = math.hypot(x0 - px, y0 - py)

                if gap < _TRAVEL_MAX_EMB:
                    # ── Travel run ──────────────────────────────────────
                    # Stitch straight across the gap at _TRAVEL_STEP_EMB
                    # intervals.  Thread stays on top but the same colour
                    # makes it invisible from the front; no trim needed.
                    steps = max(1, int(gap / _TRAVEL_STEP_EMB))
                    for i in range(1, steps + 1):
                        t  = i / steps
                        tx = px + (x0 - px) * t
                        ty = py + (y0 - py) * t
                        pattern.add_stitch_absolute(pyembroidery.STITCH, tx, ty)
                    # Arrive at segment start — no JUMP needed
                    pattern.add_stitch_absolute(pyembroidery.STITCH, x0, y0)
                else:
                    # ── Jump to next segment ─────────────────────────────
                    pattern.add_stitch_absolute(pyembroidery.JUMP,   x0, y0)
                    pattern.add_stitch_absolute(pyembroidery.STITCH, x0, y0)
            else:
                # First segment of this colour block
                pattern.add_stitch_absolute(pyembroidery.JUMP,   x0, y0)
                pattern.add_stitch_absolute(pyembroidery.STITCH, x0, y0)

            for s in seg[1:]:
                pattern.add_stitch_absolute(pyembroidery.STITCH, s['x'], s['y'])
                stitch_count += 1

            prev_end = (seg[-1]['x'], seg[-1]['y'])

    pattern.add_command(pyembroidery.END)
    return pattern, stitch_count


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
