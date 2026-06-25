"""
Netlify function: POST /api/generate
Proxies a prompt to Imagen and returns a PNG as base64.

Environment variable required: GEMINI_API_KEY
"""
import json
import os
import base64
import urllib.request
import urllib.error
from io import BytesIO

from PIL import Image

from stitch_prompt import (
    STRICT_RETRY_SUFFIX,
    STITCHABLE_SOURCE_SYSTEM_PROMPT,
    build_user_prompt,
    compose_text_prompt,
)


DEFAULT_IMAGEN_MODEL = 'imagen-4.0-generate-001'


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

    user_request = (body.get('userPrompt') or body.get('prompt') or '').strip()
    if not user_request:
        return _error(400, 'prompt is required')
    use_system_prompt = _as_bool(body.get('useSystemPrompt', True))
    raw_prompt = _as_bool(body.get('rawPrompt', False))
    system_prompt = (body.get('systemPrompt') or STITCHABLE_SOURCE_SYSTEM_PROMPT).strip()
    allow_retry = _as_bool(body.get('allowRetry', False))

    if raw_prompt:
        user_prompt = user_request
        final_text_prompt = user_request
        request_system_prompt = None
    else:
        user_prompt = build_user_prompt(user_request)
        request_system_prompt = system_prompt if use_system_prompt else None
        final_text_prompt = (
            user_prompt
            if request_system_prompt
            else compose_text_prompt(user_request, system_prompt)
        )

    model = str(body.get('model') or os.environ.get('IMAGEN_MODEL') or DEFAULT_IMAGEN_MODEL).strip()
    aspect_ratio = str(body.get('aspectRatio') or '1:1').strip() or '1:1'
    sample_count = int(body.get('sampleCount') or 1)
    sample_count = max(1, min(4, sample_count))

    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:predict?key={api_key}'

    imagen_prompt = _compose_imagen_prompt(raw_prompt, final_text_prompt, user_prompt, system_prompt, request_system_prompt)
    candidates, retry_used, retry_reason = _generate_candidates(url, imagen_prompt, sample_count, aspect_ratio)
    if not candidates:
        return _error(502, retry_reason or 'No image in Imagen response')
    selected_index, selected_quality = _select_best_candidate(candidates)
    if allow_retry and sample_count == 1 and _needs_strict_retry(selected_quality):
        strict_prompt = _compose_imagen_prompt(
            raw_prompt,
            final_text_prompt + STRICT_RETRY_SUFFIX,
            user_prompt,
            system_prompt + STRICT_RETRY_SUFFIX,
            request_system_prompt,
        )
        retry_candidates, retry_used, retry_reason = _generate_candidates(url, strict_prompt, 1, aspect_ratio)
        if retry_candidates:
            retry_index, retry_quality = _select_best_candidate(retry_candidates)
            if retry_quality.get('score', 0) >= selected_quality.get('score', 0):
                candidates = retry_candidates
                selected_index = retry_index
                selected_quality = retry_quality
        else:
            retry_used = False
    else:
        retry_used = False
        retry_reason = None
    image_b64 = candidates[selected_index]['data']

    return {
        'statusCode': 200,
        'headers': {**_cors(), 'Content-Type': 'application/json'},
        'body': json.dumps({
            'imageBase64': image_b64,
            'contentType': candidates[selected_index].get('mimeType') or 'image/png',
            'candidates': candidates,
            'selectedCandidateIndex': selected_index,
            'sourceQuality': selected_quality,
            'userPrompt': user_request,
            'generationPrompt': final_text_prompt,
            'systemPrompt': request_system_prompt,
            'provider': model,
            'aspectRatio': aspect_ratio,
            'sampleCount': sample_count,
            'retryUsed': retry_used,
            'retryReason': retry_reason,
        }),
    }


def _compose_imagen_prompt(raw_prompt, final_text_prompt, user_prompt, system_prompt, request_system_prompt):
    # Imagen predict does not currently expose a separate systemInstruction
    # field, so compose the product prompt into one text prompt.
    return (
        final_text_prompt
        if raw_prompt
        else f'{user_prompt}\n\n{system_prompt}' if request_system_prompt
        else final_text_prompt
    )


def _generate_candidates(url, imagen_prompt, sample_count, aspect_ratio):
    request_body = {
        'instances': [{'prompt': imagen_prompt}],
        'parameters': {
            'sampleCount': sample_count,
            'aspectRatio': aspect_ratio,
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(request_body).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            imagen_data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode('utf-8', errors='replace')
        return [], False, f'Imagen API error {e.code}: {body_text}'
    except urllib.error.URLError as e:
        return [], False, f'Network error calling Imagen: {e.reason}'
    return _extract_imagen_images(imagen_data), True, None


def _needs_strict_retry(score):
    if not isinstance(score, dict):
        return True
    flags = set(score.get('flags') or [])
    return score.get('score', 0) < 58 or bool(flags & {'fragmented', 'tiny-fragments', 'soft-shading', 'busy-border-or-cropped'})


def _extract_imagen_images(data):
    """Return image candidates from an Imagen predict response."""
    images = []
    try:
        for prediction in data.get('predictions', []):
            if prediction.get('bytesBase64Encoded'):
                images.append({
                    'data': prediction['bytesBase64Encoded'],
                    'mimeType': prediction.get('mimeType') or 'image/png',
                })
            if prediction.get('image', {}).get('bytesBase64Encoded'):
                images.append({
                    'data': prediction['image']['bytesBase64Encoded'],
                    'mimeType': prediction['image'].get('mimeType') or 'image/png',
                })
    except (KeyError, TypeError):
        pass
    return images


def _select_best_candidate(candidates):
    scored = []
    for index, candidate in enumerate(candidates):
        score = _score_source_candidate(candidate.get('data') or '')
        scored.append((score.get('score', 0), index, score))
    scored.sort(key=lambda item: item[0], reverse=True)
    _, index, score = scored[0]
    return index, score


def _score_source_candidate(image_b64):
    try:
        image = Image.open(BytesIO(base64.b64decode(image_b64))).convert('RGBA')
    except Exception as exc:
        return {'score': 0, 'status': 'score-error', 'reason': str(exc)}

    image.thumbnail((160, 160), Image.Resampling.LANCZOS)
    width, height = image.size
    pixels = list(image.getdata())
    mask = bytearray(width * height)
    color_bins = {}
    background = dark = foreground = border_background = border_pixels = soft = 0
    for y in range(height):
        for x in range(width):
            idx = y * width + x
            r, g, b, a = pixels[idx]
            is_background = a < 32 or (r > 244 and g > 244 and b > 244)
            is_dark = (not is_background) and r < 70 and g < 70 and b < 70
            is_border = x < 8 or y < 8 or x >= width - 8 or y >= height - 8
            if is_border:
                border_pixels += 1
                if is_background:
                    border_background += 1
            if is_background:
                background += 1
                continue
            mask[idx] = 1
            foreground += 1
            if is_dark:
                dark += 1
                continue
            if max(r, g, b) - min(r, g, b) < 22 and max(r, g, b) < 235:
                soft += 1
            key = (r >> 4, g >> 4, b >> 4)
            color_bins[key] = color_bins.get(key, 0) + 1

    components = _measure_components(mask, width, height)
    total = max(1, width * height)
    foreground_ratio = foreground / total
    border_background_ratio = border_background / max(1, border_pixels)
    dark_ratio = dark / max(1, foreground)
    soft_ratio = soft / max(1, foreground)
    largest_component_ratio = components['largest'] / max(1, foreground)
    meaningful_bin_threshold = max(5, foreground * 0.004)
    color_bin_count = sum(1 for count in color_bins.values() if count >= meaningful_bin_threshold)

    score = 100.0
    score -= max(0, color_bin_count - 10) * 2.6
    score -= max(0, components['count'] - 16) * 2.8
    score -= components['tiny'] * 6.5
    score -= components['small'] * 2.4
    score -= max(0, soft_ratio - 0.08) * 90
    if border_background_ratio < 0.78:
        score -= (0.78 - border_background_ratio) * 120
    if foreground_ratio < 0.08:
        score -= (0.08 - foreground_ratio) * 180
    if foreground_ratio > 0.62:
        score -= (foreground_ratio - 0.62) * 80
    if largest_component_ratio < 0.35:
        score -= (0.35 - largest_component_ratio) * 90
    if dark_ratio > 0.42:
        score -= (dark_ratio - 0.42) * 70
    score = int(max(0, min(100, round(score))))

    flags = []
    if color_bin_count > 18:
        flags.append('too-many-tones')
    if components['tiny'] > 4:
        flags.append('tiny-fragments')
    if components['count'] > 22:
        flags.append('fragmented')
    if soft_ratio > 0.12:
        flags.append('soft-shading')
    if border_background_ratio < 0.78:
        flags.append('busy-border-or-cropped')
    if foreground_ratio < 0.08:
        flags.append('too-small')
    if foreground_ratio > 0.62:
        flags.append('too-large')

    return {
        'score': score,
        'status': 'good' if score >= 78 else 'caution' if score >= 58 else 'review',
        'flags': flags,
        'width': image.width,
        'height': image.height,
        'colorBinCount': color_bin_count,
        'foregroundRatio': round(foreground_ratio, 3),
        'backgroundRatio': round(background / total, 3),
        'borderBackgroundRatio': round(border_background_ratio, 3),
        'darkRatio': round(dark_ratio, 3),
        'softRatio': round(soft_ratio, 3),
        'componentCount': components['count'],
        'tinyComponents': components['tiny'],
        'smallComponents': components['small'],
        'largestComponentRatio': round(largest_component_ratio, 3),
    }


def _measure_components(mask, width, height):
    seen = bytearray(len(mask))
    count = tiny = small = largest = 0
    for start, value in enumerate(mask):
        if not value or seen[start]:
            continue
        count += 1
        size = 0
        seen[start] = 1
        queue = [start]
        head = 0
        while head < len(queue):
            pixel = queue[head]
            head += 1
            size += 1
            x = pixel % width
            y = pixel // width
            neighbors = []
            if x > 0:
                neighbors.append(pixel - 1)
            if x < width - 1:
                neighbors.append(pixel + 1)
            if y > 0:
                neighbors.append(pixel - width)
            if y < height - 1:
                neighbors.append(pixel + width)
            for nxt in neighbors:
                if mask[nxt] and not seen[nxt]:
                    seen[nxt] = 1
                    queue.append(nxt)
        largest = max(largest, size)
        if size < 10:
            tiny += 1
        elif size < 36:
            small += 1
    return {'count': count, 'tiny': tiny, 'small': small, 'largest': largest}


def _extract_text(data):
    """Return any text/message parts from a provider response."""
    try:
        if isinstance(data.get('error'), dict) and data['error'].get('message'):
            return data['error']['message']
        parts = []
        for candidate in data.get('candidates', []):
            for part in candidate.get('content', {}).get('parts', []):
                if 'text' in part:
                    parts.append(part['text'])
        for prediction in data.get('predictions', []):
            if prediction.get('text'):
                parts.append(prediction['text'])
        return ' '.join(parts) if parts else None
    except (KeyError, TypeError):
        return None


def _cors():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
    }


def _as_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() not in {'0', 'false', 'no', 'off', ''}
    return default


def _error(status, message):
    return {
        'statusCode': status,
        'headers': {**_cors(), 'Content-Type': 'application/json'},
        'body': json.dumps({'error': message}),
    }
