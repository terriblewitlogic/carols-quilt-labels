import json
import base64
import tempfile
import os
import re
import pyembroidery
from engine import text_to_pattern, multiline_to_pattern, generate_preview_svg, FONT_ALIASES


# Canvas pixels → pyembroidery units (0.1 mm)
# Canvas is 4 px/mm; pyembroidery uses 0.1 mm units → multiply px by 2.5
PX2EMB = 10.0 / 4.0

SUPPORTED_FORMATS = {'jef', 'pes', 'dst', 'vp3', 'exp', 'xxx', 'hus'}

MIME = 'application/octet-stream'


def handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 204, 'headers': _cors(), 'body': ''}

    try:
        body = json.loads(event.get('body') or '{}')
    except json.JSONDecodeError as e:
        return _error(400, f'Invalid JSON: {e}')

    groups        = body.get('groups', [])
    text_elements = body.get('textElements', [])
    canvas_w      = body.get('canvasW', 0)
    canvas_h      = body.get('canvasH', 0)
    fmt           = body.get('format', 'jef').lower().lstrip('.')

    if fmt not in SUPPORTED_FORMATS:
        return _error(400, f'Unsupported format "{fmt}". Supported: {sorted(SUPPORTED_FORMATS)}')
    if not groups and not text_elements:
        return _error(400, 'No stitch data provided')

    try:
        pattern = _build_pattern(groups, text_elements, canvas_w, canvas_h)
        file_bytes = _write_pattern(pattern, fmt)
    except Exception as e:
        import traceback
        return _error(500, f'Export failed: {e}\n{traceback.format_exc()}')

    headers = {
        **_cors(),
        'Content-Type': MIME,
        'Content-Disposition': f'attachment; filename="quilt-label.{fmt}"',
    }
    return {
        'statusCode': 200,
        'headers': headers,
        'body': base64.b64encode(file_bytes).decode('utf-8'),
        'isBase64Encoded': True,
    }


def _build_pattern(groups, text_elements, canvas_w, canvas_h):
    pattern = pyembroidery.EmbPattern()
    any_added = False

    # ── Text elements via Hershey engine ──────────────────────────────
    for text_el in text_elements:
        raw = text_el.get('text', '')
        lines = [l for l in raw.split('\n') if l.strip()]
        if not lines:
            continue

        font_name    = text_el.get('font', 'sans')
        height_mm    = float(text_el.get('size_mm', 12.0))
        satin_width  = text_el.get('satin_width_mm')   # None = auto
        _d           = text_el.get('density_mm')
        density      = float(_d) if _d is not None else None  # None → auto_density in engine
        color_hex    = text_el.get('color', '#000000')
        color_int    = _hex_to_int(color_hex)
        align        = text_el.get('align', 'center')

        if satin_width is not None:
            satin_width = float(satin_width)

        if len(lines) == 1:
            text_pat, _, _ = text_to_pattern(
                lines[0], font_name, height_mm,
                satin_width_mm=satin_width,
                density_mm=density,
                thread_color=color_int,
            )
        else:
            text_pat = multiline_to_pattern(
                lines, font_name, height_mm,
                align=align,
                satin_width_mm=satin_width,
                density_mm=density,
                thread_color=color_int,
            )

        if not text_pat:
            continue

        # Compute offset to position pattern at target canvas coords
        bounds = text_pat.bounds()
        if bounds[0] == bounds[2] and bounds[1] == bounds[3]:
            continue  # empty pattern

        pat_cx = (bounds[0] + bounds[2]) / 2.0
        pat_cy = (bounds[1] + bounds[3]) / 2.0

        # x_px/y_px are canvas pixel coords (origin = top-left of canvas)
        x_px = float(text_el.get('x_px', canvas_w / 2.0))
        y_px = float(text_el.get('y_px', canvas_h / 2.0))
        target_x = (x_px - canvas_w / 2.0) * PX2EMB
        target_y = (y_px - canvas_h / 2.0) * PX2EMB

        dx = target_x - pat_cx
        dy = target_y - pat_cy

        # Add thread
        thread = pyembroidery.EmbThread()
        thread.color = color_int
        thread.name  = color_hex
        pattern.add_thread(thread)

        if any_added:
            pattern.add_command(pyembroidery.COLOR_BREAK)
        any_added = True

        for s in text_pat.stitches:
            cmd = s[2]
            if cmd == pyembroidery.END:
                continue
            pattern.add_stitch_absolute(cmd, s[0] + dx, s[1] + dy)

    # ── Pre-computed stitch groups (borders, decorative elements) ─────
    for i, group in enumerate(groups):
        thread = pyembroidery.EmbThread()
        thread.color = _hex_to_int(group.get('color', '#000000'))
        thread.name  = group.get('color', '#000000')
        pattern.add_thread(thread)

        stitches = group.get('stitches', [])
        if not stitches:
            continue

        if any_added:
            pattern.add_command(pyembroidery.COLOR_BREAK)
        any_added = True

        for j, s in enumerate(stitches):
            ex = (s['x'] - canvas_w / 2.0) * PX2EMB
            ey = (s['y'] - canvas_h / 2.0) * PX2EMB
            cmd = pyembroidery.STITCH if j > 0 else pyembroidery.JUMP
            pattern.add_stitch_absolute(cmd, ex, ey)
            if j == 0:
                pattern.add_stitch_absolute(pyembroidery.STITCH, ex, ey)

    pattern.add_command(pyembroidery.END)
    return pattern


def preview_handler(event, context):
    """Return an SVG stitch-simulation for the text elements in the request."""
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 204, 'headers': _cors(), 'body': ''}

    try:
        body = json.loads(event.get('body') or '{}')
    except json.JSONDecodeError as e:
        return _error(400, f'Invalid JSON: {e}')

    text_elements = body.get('textElements', [])
    if not text_elements:
        return _error(400, 'No textElements provided')

    # Generate a preview SVG per text element, then composite vertically
    WIDTH_PX = 600
    GAP_PX   = 12
    parts = []  # list of (svg_str, vb_w, vb_h)

    for el in text_elements:
        lines = [l for l in el.get('text', '').split('\n') if l.strip()]
        if not lines:
            continue
        font_name  = el.get('font', 'script')
        height_mm  = float(el.get('size_mm', 12.0))
        color_hex  = el.get('color', '#cc0000')
        align      = el.get('align', 'center')
        _d         = el.get('density_mm')
        density_mm = float(_d) if _d is not None else None

        el_svg = generate_preview_svg(
            lines, font_name, height_mm,
            align=align,
            thread_color=color_hex,
            density_mm=density_mm,
            width_px=WIDTH_PX,
        )
        m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', el_svg)
        vb_w = float(m.group(1)) if m else WIDTH_PX
        vb_h = float(m.group(2)) if m else 80
        parts.append((el_svg, vb_w, vb_h))

    if not parts:
        return _error(400, 'No text provided')

    if len(parts) == 1:
        svg = parts[0][0]
    else:
        # Stack element SVGs vertically inside one wrapper SVG
        total_h = sum(h for _, _, h in parts) + GAP_PX * (len(parts) - 1)
        rows = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH_PX} {total_h:.0f}" width="100%" preserveAspectRatio="xMidYMid meet">']
        y = 0.0
        for el_svg, vb_w, vb_h in parts:
            inner = re.sub(r'<svg[^>]*>', '', el_svg, count=1).replace('</svg>', '').strip()
            rows.append(f'<svg x="0" y="{y:.0f}" width="{WIDTH_PX}" height="{vb_h:.0f}" viewBox="0 0 {vb_w:.0f} {vb_h:.0f}">')
            rows.append(inner)
            rows.append('</svg>')
            y += vb_h + GAP_PX
        rows.append('</svg>')
        svg = '\n'.join(rows)

    return {
        'statusCode': 200,
        'headers': {**_cors(), 'Content-Type': 'application/json'},
        'body': json.dumps({'svg': svg}),
    }


def font_samples_handler(event, context):
    """Return small stitch-preview SVGs for every available font.

    Returns: { samples: { fontValue: svgString, ... } }
    Each SVG shows the word 'Abc' stitched at 12mm so the picker can display
    accurate thumbnails of what each Hershey font actually looks like.
    """
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 204, 'headers': _cors(), 'body': ''}

    sample_text = 'Abc'
    height_mm   = 12.0
    samples     = {}

    for font_value in FONT_ALIASES.keys():
        try:
            svg = generate_preview_svg(
                [sample_text], font_value, height_mm,
                thread_color='#4A3820',
                width_px=180,
            )
            samples[font_value] = svg
        except Exception:
            samples[font_value] = ''   # font failed silently

    return {
        'statusCode': 200,
        'headers': {**_cors(), 'Content-Type': 'application/json'},
        'body': json.dumps({'samples': samples}),
    }


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


def _hex_to_int(hex_color):
    h = hex_color.lstrip('#')
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return (r << 16) | (g << 8) | b


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
