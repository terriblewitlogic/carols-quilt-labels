"""
Lightweight endpoint: POST /api/posterize

Posterizes the image to N colours and returns layer metadata without
generating any stitches. The UI uses this to show the layer ordering
panel so users can reorder colours before the full conversion step.

Request:
  { imageBase64, hoop_w_mm, hoop_h_mm, num_colors }

Response:
  {
    layers: [
      { label_idx, hex, pixel_fraction, is_background },
      ...  // in default stitch order (dark first)
    ]
  }
"""
import json
import sys
import os
import traceback

# Reuse the posterize helper from raster_to_stitches
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'image_to_jef'))
from raster_to_stitches import posterize_image


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

    hoop_w   = float(body.get('hoop_w_mm', 100))
    hoop_h   = float(body.get('hoop_h_mm', 100))
    n_colors = int(body.get('num_colors', 4))

    try:
        layers = posterize_image(image_b64, hoop_w, hoop_h, max(2, min(8, n_colors)))
    except Exception as e:
        return _error(500, f'Posterize failed: {e}\n{traceback.format_exc()}')

    return {
        'statusCode': 200,
        'headers': {**_cors(), 'Content-Type': 'application/json'},
        'body': json.dumps({'layers': layers}),
    }


def _cors():
    return {
        'Access-Control-Allow-Origin':  '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
    }


def _error(status, message):
    return {
        'statusCode': status,
        'headers': {**_cors(), 'Content-Type': 'application/json'},
        'body': json.dumps({'error': message}),
    }
