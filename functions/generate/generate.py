"""
Netlify function: POST /api/generate
Proxies a prompt to Gemini 3.1 Flash Image Preview and returns a PNG as base64.

Environment variable required: GEMINI_API_KEY
"""
import json
import base64
import os
import urllib.request
import urllib.error


GEMINI_MODEL = 'gemini-3.1-flash-image-preview'
GEMINI_URL = (
    f'https://generativelanguage.googleapis.com/v1beta/models/'
    f'{GEMINI_MODEL}:generateContent'
)


def handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 204, 'headers': _cors(), 'body': ''}

    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return _error(500, 'GEMINI_API_KEY is not configured on the server.')

    try:
        body = json.loads(event.get('body') or '{}')
    except json.JSONDecodeError as e:
        return _error(400, f'Invalid JSON: {e}')

    prompt = (body.get('prompt') or '').strip()
    if not prompt:
        return _error(400, 'prompt is required')

    # Call Gemini
    request_body = {
        'contents': [
            {
                'parts': [
                    {'text': prompt}
                ]
            }
        ],
        'generationConfig': {
            'responseModalities': ['IMAGE', 'TEXT'],
        },
    }

    url = f'{GEMINI_URL}?key={api_key}'
    req = urllib.request.Request(
        url,
        data=json.dumps(request_body).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            gemini_data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode('utf-8', errors='replace')
        return _error(502, f'Gemini API error {e.code}: {body_text}')
    except urllib.error.URLError as e:
        return _error(502, f'Network error calling Gemini: {e.reason}')

    # Extract the inline image from the response
    image_b64 = _extract_image(gemini_data)
    if image_b64 is None:
        # Try to extract a useful error message from the response
        err_msg = _extract_text(gemini_data) or 'No image in Gemini response'
        return _error(502, err_msg)

    return {
        'statusCode': 200,
        'headers': {**_cors(), 'Content-Type': 'application/json'},
        'body': json.dumps({'imageBase64': image_b64}),
    }


def _extract_image(data):
    """Return base64 PNG string from a Gemini generateContent response, or None."""
    try:
        for candidate in data.get('candidates', []):
            for part in candidate.get('content', {}).get('parts', []):
                inline = part.get('inlineData', {})
                if inline.get('mimeType', '').startswith('image/'):
                    return inline['data']
    except (KeyError, TypeError):
        pass
    return None


def _extract_text(data):
    """Return any text parts from a Gemini response (useful for error messages)."""
    try:
        parts = []
        for candidate in data.get('candidates', []):
            for part in candidate.get('content', {}).get('parts', []):
                if 'text' in part:
                    parts.append(part['text'])
        return ' '.join(parts) if parts else None
    except (KeyError, TypeError):
        return None


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
