import { PX_PER_MM, TATAMI_ROW_MM, TATAMI_LEN_MM, SATIN_DENSITY_MM, MIN_STITCH_MM, PULL_COMP_MM, MAX_SATIN_WIDTH_MM } from './constants.js';
import { LETTER_SPACING } from './fonts.js';

const ROW_PX = Math.round(TATAMI_ROW_MM * PX_PER_MM);
const STITCH_PX = Math.round(TATAMI_LEN_MM * PX_PER_MM);
const SATIN_PX = Math.round(SATIN_DENSITY_MM * PX_PER_MM);
const MIN_PX = Math.round(MIN_STITCH_MM * PX_PER_MM);
const PULL_PX = Math.round(PULL_COMP_MM * PX_PER_MM);
const MAX_SATIN_PX = Math.round(MAX_SATIN_WIDTH_MM * PX_PER_MM);

// ─── Canvas rendering for stitch extraction ──────────────────────────────────
export function makeCanvas(el, mode = 'fill') {
  const pad = 28;
  const tmp = document.createElement('canvas');
  tmp.width = 4; tmp.height = 4;
  const tc = tmp.getContext('2d');
  tc.font = `bold ${el.fontSize}px "${el.font}"`;
  const m = tc.measureText(el.content);
  const spacing = (el.fontSize * 0.05 * (LETTER_SPACING - 1));
  const extraW = spacing * Math.max(0, el.content.length - 1);
  const w = Math.max(4, Math.ceil(m.width + extraW) + pad * 2);
  const h = Math.max(4, Math.ceil(el.fontSize * 1.6) + pad * 2);

  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  const ctx = c.getContext('2d');
  ctx.font = `bold ${el.fontSize}px "${el.font}"`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  try { ctx.letterSpacing = `${spacing}px`; } catch(e) { /* older browsers */ }

  if (mode === 'outline') {
    ctx.strokeStyle = '#000';
    ctx.lineWidth = Math.max(3, el.fontSize / 10);
    ctx.strokeText(el.content, w / 2, h / 2);
  } else if (mode === 'satin-edges') {
    ctx.strokeStyle = '#000';
    ctx.lineWidth = Math.max(4, el.fontSize / 4);
    ctx.strokeText(el.content, w / 2, h / 2);
  } else {
    ctx.fillStyle = '#000';
    ctx.fillText(el.content, w / 2, h / 2);
  }
  return { canvas: c, ox: el.x - w / 2, oy: el.y - h / 2 };
}

// ─── SVG Element canvas rendering ────────────────────────────────────────────
export function makeSvgCanvas(el) {
  if (!el.paths || !el.paths.length) return makeCanvas(el, 'fill');
  const pad = 8;
  const scale = (el.fontSize / el.baseH) * (el.scale || 1);
  const w = Math.ceil(el.baseW * scale) + pad * 2;
  const h = Math.ceil(el.baseH * scale) + pad * 2;
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  const ctx = c.getContext('2d');
  ctx.translate(pad, pad);
  ctx.scale(scale, scale);
  for (const p of el.paths) {
    const p2d = new Path2D(p.d);
    if (p.fill !== false) { ctx.fillStyle = '#000'; ctx.fill(p2d); }
    if (p.stroke) { ctx.strokeStyle = '#000'; ctx.lineWidth = p.strokeWidth || 1; ctx.stroke(p2d); }
  }
  return { canvas: c, ox: el.x - w / 2, oy: el.y - h / 2 };
}

// ─── Tatami Fill (brick-pattern, configurable angle) ─────────────────────────
export function tatamiStitches(el, angle = 45) {
  const isSvg = el.type === 'decorative' && el.paths;
  const { canvas, ox, oy } = isSvg ? makeSvgCanvas(el) : makeCanvas(el, 'fill');
  const { width: w, height: h } = canvas;
  const data = canvas.getContext('2d').getImageData(0, 0, w, h).data;

  const rad = (angle * Math.PI) / 180;
  const cosA = Math.cos(rad), sinA = Math.sin(rad);
  const cx = w / 2, cy = h / 2;

  // Compute bounding box in rotated space
  const corners = [[0,0],[w,0],[0,h],[w,h]];
  let rMinX = Infinity, rMaxX = -Infinity, rMinY = Infinity, rMaxY = -Infinity;
  for (const [px, py] of corners) {
    const rx = (px - cx) * cosA + (py - cy) * sinA;
    const ry = -(px - cx) * sinA + (py - cy) * cosA;
    rMinX = Math.min(rMinX, rx); rMaxX = Math.max(rMaxX, rx);
    rMinY = Math.min(rMinY, ry); rMaxY = Math.max(rMaxY, ry);
  }

  const pts = [];
  let dir = 1;
  const brickOffset = STITCH_PX / 3;
  let rowIdx = 0;

  for (let ry = rMinY; ry <= rMaxY; ry += ROW_PX) {
    const rp = [];
    const offset = (rowIdx % 3) * brickOffset;
    let start = null;

    for (let rx = rMinX - brickOffset; rx <= rMaxX + brickOffset; rx += 1) {
      // Rotate back to image space
      const imgX = Math.round(rx * cosA - ry * sinA + cx);
      const imgY = Math.round(rx * sinA + ry * cosA + cy);
      const inBounds = imgX >= 0 && imgX < w && imgY >= 0 && imgY < h;
      const filled = inBounds && data[(imgY * w + imgX) * 4 + 3] > 80;

      if (filled && start === null) start = rx;
      if (!filled && start !== null) {
        if (rp.length > 0) rp.push(null); // jump marker between separate fill runs
        for (let sx = start + offset; sx <= rx - 1; sx += STITCH_PX) {
          const px = sx * cosA - ry * sinA + cx;
          const py = sx * sinA + ry * cosA + cy;
          rp.push({ x: ox + px, y: oy + py });
        }
        const px = (rx - 1) * cosA - ry * sinA + cx;
        const py = (rx - 1) * sinA + ry * cosA + cy;
        rp.push({ x: ox + px, y: oy + py });
        start = null;
      }
    }
    if (rp.length) { if (dir < 0) rp.reverse(); pts.push(...rp); dir *= -1; }
    rowIdx++;
  }
  return pts;
}

// ─── Legacy fill (horizontal scanline, 0° angle) ────────────────────────────
export function fillStitches(el) {
  return tatamiStitches(el, 0);
}

// ─── Satin Stitch (shared column-scan logic) ─────────────────────────────────
function satinFromCanvas(canvas, ox, oy) {
  const { width: w, height: h } = canvas;
  const data = canvas.getContext('2d').getImageData(0, 0, w, h).data;
  const pts = [];
  const underlayPts = [];

  for (let col = 0; col < w; col += Math.max(1, SATIN_PX)) {
    let top = -1, bot = -1;
    for (let row = 0; row < h; row++) {
      if (data[(row * w + col) * 4 + 3] > 80) {
        if (top < 0) top = row;
        bot = row;
      }
    }
    if (top >= 0 && bot > top) {
      const width = bot - top;
      const topAdj = Math.max(0, top - PULL_PX);
      const botAdj = Math.min(h - 1, bot + PULL_PX);

      if (width > MAX_SATIN_PX) {
        const mid = (top + bot) / 2;
        const overlap = 3;
        if (pts.length % 2 === 0) {
          pts.push({ x: ox + col, y: oy + topAdj });
          pts.push({ x: ox + col, y: oy + mid + overlap });
          pts.push({ x: ox + col, y: oy + mid - overlap });
          pts.push({ x: ox + col, y: oy + botAdj });
        } else {
          pts.push({ x: ox + col, y: oy + mid + overlap });
          pts.push({ x: ox + col, y: oy + topAdj });
          pts.push({ x: ox + col, y: oy + botAdj });
          pts.push({ x: ox + col, y: oy + mid - overlap });
        }
      } else {
        if (pts.length % 2 === 0) {
          pts.push({ x: ox + col, y: oy + topAdj });
          pts.push({ x: ox + col, y: oy + botAdj });
        } else {
          pts.push({ x: ox + col, y: oy + botAdj });
          pts.push({ x: ox + col, y: oy + topAdj });
        }
      }

      const widthMm = width / PX_PER_MM;
      if (widthMm >= 5 && widthMm < 10) {
        underlayPts.push({ x: ox + col, y: oy + (top + bot) / 2 });
      } else if (widthMm >= 10) {
        underlayPts.push({ x: ox + col, y: oy + top + 2 });
        underlayPts.push({ x: ox + col, y: oy + bot - 2 });
      }
    }
  }

  return [...underlayPts, ...pts];
}

export function satinStitches(el) {
  const isSvg = el.type === 'decorative' && el.paths;
  const { canvas, ox, oy } = isSvg ? makeSvgCanvas(el) : makeCanvas(el, 'fill');
  return satinFromCanvas(canvas, ox, oy);
}

// ─── Border (running stitch tracing letter perimeter) ────────────────────────
// Column-based satin cannot be used here — for letters like T, E, L the scan
// bridges across stroke gaps, creating stitches spanning the full letter height.
// Outline tracing is geometrically correct for all letter shapes.
export function borderStitches(el) {
  return outlineStitches(el);
}

// ─── Running / Outline Stitch ────────────────────────────────────────────────
export function outlineStitches(el) {
  const isSvg = el.type === 'decorative' && el.paths;
  const { canvas, ox, oy } = isSvg ? makeSvgCanvas(el) : makeCanvas(el, 'outline');
  const { width: w, height: h } = canvas;
  const data = canvas.getContext('2d').getImageData(0, 0, w, h).data;
  const all = [];
  for (let row = 0; row < h; row++) {
    const rp = [];
    for (let col = 0; col < w; col++)
      if (data[(row * w + col) * 4 + 3] > 80) rp.push({ x: ox + col, y: oy + row });
    if (row % 2) rp.reverse();
    all.push(...rp);
  }
  if (!all.length) return [];
  const sts = [all[0]];
  let acc = 0;
  for (let i = 1; i < all.length; i++) {
    acc += Math.hypot(all[i].x - all[i - 1].x, all[i].y - all[i - 1].y);
    if (acc >= STITCH_PX) { sts.push(all[i]); acc = 0; }
  }
  return sts;
}

// ─── Bean Stitch (triple-run) ────────────────────────────────────────────────
export function beanStitches(el) {
  const outline = outlineStitches(el);
  if (outline.length < 2) return outline;
  const pts = [];
  for (let i = 0; i < outline.length - 1; i++) {
    pts.push(outline[i], outline[i + 1], outline[i]);
  }
  pts.push(outline[outline.length - 1]);
  return pts;
}

// ─── Post-process: merge stitches < MIN_STITCH_MM ────────────────────────────
export function postProcess(pts) {
  if (pts.length < 2) return pts;
  const out = [pts[0]];
  for (let i = 1; i < pts.length; i++) {
    const last = out[out.length - 1];
    const d = Math.hypot(pts[i].x - last.x, pts[i].y - last.y);
    if (d >= MIN_PX || i === pts.length - 1) out.push(pts[i]);
  }
  return out;
}

// ─── Main dispatch ───────────────────────────────────────────────────────────
export function generateStitches(el) {
  switch (el.stitchType) {
    // Satin and tatami have their own well-defined spacing; postProcess would
    // incorrectly remove the short between-column/between-row transitions.
    case 'satin':   return satinStitches(el);
    case 'tatami':  return tatamiStitches(el, el.stitchAngle || 45);
    case 'fill':    return tatamiStitches(el, 0);
    // Outline/bean are sampled at STITCH_PX intervals already; postProcess
    // only removes any sub-MIN_PX artefacts from sharp corners.
    case 'outline': return postProcess(outlineStitches(el));
    case 'bean':    return postProcess(beanStitches(el));
    default:        return tatamiStitches(el, 45);
  }
}
