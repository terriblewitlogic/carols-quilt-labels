// ─── Hoop Sizes ──────────────────────────────────────────────────────────────
// JEF hoop codes: 0=Standard A (126×110mm), 1=Free Arm C (50×50mm),
//   2=Large B (140×200mm), 3=Spring F (126×110mm), 4=Giga D (230×200mm)
export const HOOPS = {
  '4x4':  { w: 89,  h: 89,  label: '4×4"',  jefCode: 0 },
  '5x7':  { w: 114, h: 165, label: '5×7"',  jefCode: 2 },
  '6x10': { w: 140, h: 241, label: '6×10"', jefCode: 2 },
  '8x8':  { w: 178, h: 178, label: '8×8"',  jefCode: 4 },
};
export const DEFAULT_HOOP = '5x7';
export const MARGIN_MM = 25; // 1" needle clearance

// ─── Scale ───────────────────────────────────────────────────────────────────
export const PX_PER_MM = 4; // canvas pixels per mm
export const JEF_PER_MM = 10; // JEF units per mm (0.1mm)

// Derived helpers
export function getCanvasDims(hoopKey) {
  const h = HOOPS[hoopKey];
  const cw = h.w * PX_PER_MM;
  const ch = h.h * PX_PER_MM;
  const dw = (h.w - MARGIN_MM * 2) * PX_PER_MM;
  const dh = (h.h - MARGIN_MM * 2) * PX_PER_MM;
  const mx = MARGIN_MM * PX_PER_MM;
  const my = MARGIN_MM * PX_PER_MM;
  return { cw, ch, dw, dh, mx, my, hoopW: h.w, hoopH: h.h };
}

// ─── Stitch params ───────────────────────────────────────────────────────────
export const TATAMI_ROW_MM = 0.4;
export const TATAMI_LEN_MM = 4.5;
export const SATIN_DENSITY_MM = 0.38;
export const MIN_STITCH_MM = 1.0;
export const PULL_COMP_MM = 0.3;
export const MAX_SATIN_WIDTH_MM = 12.7;
export const MIN_BORDER_MM = 12; // minimum font height (mm) for satin border to work well

// Label shapes
export const SHAPES = ['rectangle', 'rectangle-h', 'square', 'oval', 'heart', 'triangle'];
export const SHAPE_LABELS = {
  'rectangle': 'Rectangle ↕',
  'rectangle-h': 'Rectangle ↔',
  'square': 'Square',
  'oval': 'Oval ↕',
  'heart': 'Heart',
  'triangle': 'Triangle',
};
