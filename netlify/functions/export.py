import json
import base64
import tempfile
import os
import pyembroidery


# Canvas pixels → pyembroidery units (0.1 mm)
PX2EMB = 10.0 / 4.0  # JEF_PER_MM / PX_PER_MM

SUPPORTED_FORMATS = {'jef', 'pes', 'dst', 'vp3', 'exp', 'xxx', 'hus'}

MIME = 'application/octet-stream'


def handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 204, 'headers': _cors(), 'body': ''}

    try:
        body = json.loads(event.get('body') or '{}')
    except json.JSONDecodeError as e:
        return _error(400, f'Invalid JSON: {e}')

    groups = body.get('groups', [])
    canvas_w = body.get('canvasW', 0)
    canvas_h = body.get('canvasH', 0)
    fmt = body.get('format', 'jef').lower().lstrip('.')

    if fmt not in SUPPORTED_FORMATS:
        return _error(400, f'Unsupported format "{fmt}". Supported: {sorted(SUPPORTED_FORMATS)}')
    if not groups:
        return _error(400, 'No stitch groups provided')

    try:
        pattern = _build_pattern(groups, canvas_w, canvas_h)
        file_bytes = _write_pattern(pattern, fmt)
    except Exception as e:
        return _error(500, f'Export failed: {e}')

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


def _build_pattern(groups, canvas_w, canvas_h):
    pattern = pyembroidery.EmbPattern()

    for i, group in enumerate(groups):
        thread = pyembroidery.EmbThread()
        thread.color = _hex_to_int(group.get('color', '#000000'))
        thread.name = group.get('color', '#000000')
        pattern.add_thread(thread)

        stitches = group.get('stitches', [])
        if not stitches:
            continue

        # Convert canvas coords (px, Y-down, origin top-left) to pyembroidery
        # units (0.1 mm, Y-down, origin at hoop center)
        for j, s in enumerate(stitches):
            ex = (s['x'] - canvas_w / 2.0) * PX2EMB
            ey = (s['y'] - canvas_h / 2.0) * PX2EMB
            cmd = pyembroidery.STITCH if j > 0 else pyembroidery.JUMP
            pattern.add_stitch_absolute(cmd, ex, ey)
            if j == 0:
                # Stitch in place after jump to anchor thread
                pattern.add_stitch_absolute(pyembroidery.STITCH, ex, ey)

        if i < len(groups) - 1:
            pattern.add_command(pyembroidery.COLOR_BREAK)

    pattern.add_command(pyembroidery.END)
    return pattern


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
