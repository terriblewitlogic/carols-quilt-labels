// API client for image embroidery endpoints.
// Both endpoints live in /api/* (Vercel) which proxies to netlify/functions/* on Netlify.

const BASE = import.meta.env.VITE_API_BASE || '';

/**
 * Generate an image from a prompt via the Gemini proxy.
 * Returns { imageBase64: string (PNG, no data: prefix) }
 */
export async function generateImage(prompt) {
  const res = await fetch(`${BASE}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch {
    throw new Error(`Server returned non-JSON (${res.status}): ${text.slice(0, 200) || '(empty)'}`);
  }
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

/**
 * Convert a PNG (base64, no prefix) to embroidery stitches.
 * opts: {
 *   hoop_w_mm, hoop_h_mm,   // target dimensions
 *   num_colors,              // 2–6
 *   density_mm,              // row spacing
 *   fill_angle_deg,          // global fill angle
 *   min_feature_mm,          // smallest region to keep
 *   outline,                 // 'none' | 'running' | 'satin'
 *   outline_width_mm,        // only used when outline === 'satin'
 *   format,                  // 'jef' (default)
 * }
 * Returns { jefBase64, previewSvg, stitchCount, estimatedTimeSec, colors }
 */
export async function convertToStitches(imageBase64, opts = {}) {
  const res = await fetch(`${BASE}/api/image_to_jef`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ imageBase64, ...opts }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data; // { jefBase64, previewSvg, stitchCount, estimatedTimeSec, colors }
}

/**
 * Posterize an image and return layer metadata (no stitch generation).
 * Used to populate the layer ordering panel before full conversion.
 * Returns { layers: [{ label_idx, hex, pixel_fraction, is_background }] }
 */
export async function posterizeImage(imageBase64, opts = {}) {
  const res = await fetch(`${BASE}/api/posterize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ imageBase64, ...opts }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

/**
 * Save a generated design to the local library (dev only).
 * payload: { id, name, category, description, imageBase64, previewSvg,
 *            jefBase64, format, stitchCount, colors, threads, writeKey? }
 * Returns { saved: true, id: string }
 */
export async function saveToLibrary(payload) {
  const res = await fetch(`${BASE}/api/save_to_library`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch {
    throw new Error(`Server returned non-JSON (${res.status}): ${text.slice(0, 200) || '(empty)'}`);
  }
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

/** Trigger a browser download of base64 bytes. */
export function downloadBase64(base64, filename, mime = 'application/octet-stream') {
  const bytes = atob(base64);
  const buf = new Uint8Array(bytes.length);
  for (let i = 0; i < bytes.length; i++) buf[i] = bytes.charCodeAt(i);
  const url = URL.createObjectURL(new Blob([buf], { type: mime }));
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
