"""
Netlify function: POST /api/save_to_library

Dev-only endpoint that saves a generated embroidery design to the local
public/library/ directory and updates the manifest.json index.

This runs fine under scripts/dev-functions.py.  On Netlify/Vercel the
filesystem is read-only after deploy, so this endpoint is intentionally
blocked unless the LIBRARY_WRITE_KEY env var is set — set it in .env for
local dev and leave it unset in production.

Request body:
  {
    id:           string,   // e.g. "sunflower"
    name:         string,
    category:     string,   // must match one of the 6 category ids
    description:  string,
    imageBase64:  string,   // original PNG (no data: prefix)
    previewSvg:   string,   // stitch-preview SVG markup
    jefBase64:    string,   // embroidery file bytes
    format:       string,   // 'jef'|'pes'|...
    stitchCount:  number,
    colors:       string[],
    threads:      object[],
    writeKey:     string,   // optional — must match LIBRARY_WRITE_KEY if set
  }

Returns:
  { saved: true, id: string }   on success
  { error: string }             on failure
"""

import json
import base64
import os
import re
from datetime import datetime, timezone

# ─── Locate public/library relative to this file ──────────────────────────────
_HERE      = os.path.dirname(os.path.abspath(__file__))
_PROJ_ROOT = os.path.normpath(os.path.join(_HERE, '..', '..', '..'))
_LIB_DIR   = os.path.join(_PROJ_ROOT, 'public', 'library')
_MANIFEST  = os.path.join(_LIB_DIR, 'manifest.json')

VALID_CATEGORIES = {
    'florals', 'birds-insects', 'animals',
    'botanicals', 'folk-art', 'geometric', 'custom',
}


def handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 204, 'headers': _cors(), 'body': ''}

    # ── Auth: optional LIBRARY_WRITE_KEY guard ────────────────────────────────
    required_key = os.environ.get('LIBRARY_WRITE_KEY', '')
    if required_key:
        try:
            body_for_key = json.loads(event.get('body') or '{}')
        except Exception:
            body_for_key = {}
        provided_key = (
            event.get('headers', {}).get('x-library-write-key', '') or
            body_for_key.get('writeKey', '')
        )
        if provided_key != required_key:
            return _error(403, 'Invalid or missing write key.')

    # ── Parse body ────────────────────────────────────────────────────────────
    try:
        body = json.loads(event.get('body') or '{}')
    except json.JSONDecodeError as e:
        return _error(400, f'Invalid JSON: {e}')

    entry_id    = _slugify(body.get('id', '').strip())
    name        = body.get('name', '').strip()
    category    = body.get('category', 'custom').strip().lower()
    description = body.get('description', '').strip()
    image_b64   = body.get('imageBase64', '')
    preview_svg = body.get('previewSvg', '')
    jef_b64     = body.get('jefBase64', '')
    fmt         = body.get('format', 'jef').lower().lstrip('.')
    stitch_count = int(body.get('stitchCount', 0))
    colors      = body.get('colors', [])
    threads     = body.get('threads', [])

    # ── Validate ──────────────────────────────────────────────────────────────
    if not entry_id:
        return _error(400, 'id is required')
    if not name:
        return _error(400, 'name is required')
    if category not in VALID_CATEGORIES:
        category = 'custom'
    if not preview_svg:
        return _error(400, 'previewSvg is required')
    if not jef_b64:
        return _error(400, 'jefBase64 is required')

    # ── Write files ───────────────────────────────────────────────────────────
    entry_dir = os.path.join(_LIB_DIR, entry_id)
    os.makedirs(entry_dir, exist_ok=True)

    # Stitch-preview SVG
    with open(os.path.join(entry_dir, 'preview.svg'), 'w', encoding='utf-8') as f:
        f.write(preview_svg)

    # Original generated image (PNG)
    if image_b64:
        try:
            img_bytes = base64.b64decode(image_b64)
            with open(os.path.join(entry_dir, 'image.png'), 'wb') as f:
                f.write(img_bytes)
        except Exception as e:
            return _error(500, f'Failed to decode imageBase64: {e}')

    # Embroidery file
    try:
        emb_bytes = base64.b64decode(jef_b64)
        with open(os.path.join(entry_dir, f'embroidery.{fmt}'), 'wb') as f:
            f.write(emb_bytes)
    except Exception as e:
        return _error(500, f'Failed to decode jefBase64: {e}')

    # Per-entry meta.json
    meta = {
        'id':          entry_id,
        'name':        name,
        'category':    category,
        'description': description,
        'stitchCount': stitch_count,
        'colors':      colors,
        'threads':     threads,
        'format':      fmt,
        'savedAt':     datetime.now(timezone.utc).isoformat(),
    }
    with open(os.path.join(entry_dir, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)

    # ── Update manifest.json ──────────────────────────────────────────────────
    manifest = _read_manifest()
    # Replace existing entry with same id, or append
    manifest = [m for m in manifest if m.get('id') != entry_id]
    manifest.append(meta)
    manifest.sort(key=lambda m: m.get('category', '') + m.get('name', ''))

    with open(_MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f'[save_to_library] Saved "{name}" ({entry_id}) → {entry_dir}')

    return {
        'statusCode': 200,
        'headers': {**_cors(), 'Content-Type': 'application/json'},
        'body': json.dumps({'saved': True, 'id': entry_id}),
    }


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _read_manifest():
    if os.path.exists(_MANIFEST):
        try:
            with open(_MANIFEST, encoding='utf-8') as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            pass
    return []


def _slugify(text):
    """Convert a name/id to a safe filesystem slug."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\-]', '-', text)
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-') or 'design'


def _cors():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, x-library-write-key',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
    }


def _error(status, message):
    return {
        'statusCode': status,
        'headers': {**_cors(), 'Content-Type': 'application/json'},
        'body': json.dumps({'error': message}),
    }
