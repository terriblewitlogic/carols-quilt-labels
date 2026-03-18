// ─── Pre-defined SVG decorative elements for quilt labels ────────────────────
// Each element: { id, label, baseW, baseH, paths: [{ d, fill?, stroke?, strokeWidth? }] }

export const DECORATIVE_ELEMENTS = {
  floral: {
    label: 'Floral',
    items: [
      {
        id: 'flower-rose', label: 'Rose', baseW: 40, baseH: 40,
        paths: [
          { d: 'M20 8 C14 8 8 14 8 20 C8 26 12 32 20 36 C28 32 32 26 32 20 C32 14 26 8 20 8Z', fill: true },
          { d: 'M20 12 C16 14 14 18 16 22 C18 26 22 26 24 22 C26 18 24 14 20 12Z', fill: true },
          { d: 'M20 16 Q18 20 20 24 Q22 20 20 16Z', fill: true },
          { d: 'M16 36 Q14 42 12 38 M24 36 Q26 42 28 38', stroke: true, fill: false, strokeWidth: 1.5 },
        ],
      },
      {
        id: 'flower-daisy', label: 'Daisy', baseW: 36, baseH: 36,
        paths: [
          { d: 'M18 4 Q16 10 18 14 Q20 10 18 4Z M30 10 Q24 12 22 16 Q26 14 30 10Z M34 22 Q28 20 24 22 Q28 24 34 22Z M30 32 Q24 28 22 26 Q26 30 30 32Z M18 36 Q20 30 18 26 Q16 30 18 36Z M6 32 Q12 28 14 26 Q10 30 6 32Z M2 22 Q8 20 12 22 Q8 24 2 22Z M6 10 Q12 12 14 16 Q10 14 6 10Z', fill: true },
          { d: 'M15 15 A4 4 0 1 1 23 15 A4 4 0 1 1 15 15Z', fill: true },
        ],
      },
      {
        id: 'flower-tulip', label: 'Tulip', baseW: 28, baseH: 44,
        paths: [
          { d: 'M14 4 Q8 12 8 20 Q10 16 14 14 Q12 20 14 24 L14 4Z', fill: true },
          { d: 'M14 4 Q20 12 20 20 Q18 16 14 14 Q16 20 14 24 L14 4Z', fill: true },
          { d: 'M14 24 L14 40', stroke: true, fill: false, strokeWidth: 2 },
          { d: 'M14 32 Q8 28 4 30 M14 34 Q20 30 24 32', stroke: true, fill: false, strokeWidth: 1.5 },
        ],
      },
      {
        id: 'vine-trail', label: 'Vine Trail', baseW: 80, baseH: 20,
        paths: [
          { d: 'M4 10 Q20 2 40 10 Q60 18 76 10', stroke: true, fill: false, strokeWidth: 1.5 },
          { d: 'M16 6 Q14 2 10 4 Q14 6 16 6Z M32 12 Q30 16 26 14 Q30 12 32 12Z M48 6 Q46 2 42 4 Q46 6 48 6Z M64 12 Q62 16 58 14 Q62 12 64 12Z', fill: true },
        ],
      },
      {
        id: 'wreath', label: 'Wreath', baseW: 50, baseH: 50,
        paths: [
          { d: 'M25 5 Q38 5 43 15 Q48 25 43 35 Q38 45 25 45 Q12 45 7 35 Q2 25 7 15 Q12 5 25 5Z', stroke: true, fill: false, strokeWidth: 2 },
          { d: 'M15 8 Q13 5 10 7 Q13 9 15 8Z M33 8 Q35 5 38 7 Q35 9 33 8Z M8 20 Q5 18 4 21 Q7 21 8 20Z M42 20 Q45 18 46 21 Q43 21 42 20Z M10 36 Q7 38 9 40 Q11 38 10 36Z M40 36 Q43 38 41 40 Q39 38 40 36Z M20 44 Q18 47 21 47 Q20 45 20 44Z M30 44 Q32 47 29 47 Q30 45 30 44Z', fill: true },
        ],
      },
    ],
  },
  geometric: {
    label: 'Geometric / Symbolic',
    items: [
      {
        id: 'heart-simple', label: 'Heart', baseW: 36, baseH: 34,
        paths: [{ d: 'M18 30 C6 22 0 14 4 8 C8 2 14 2 18 8 C22 2 28 2 32 8 C36 14 30 22 18 30Z', fill: true }],
      },
      {
        id: 'heart-double', label: 'Double Heart', baseW: 44, baseH: 36,
        paths: [
          { d: 'M16 28 C6 20 0 14 4 8 C8 2 12 2 16 8 C20 2 24 2 28 8 C32 14 26 20 16 28Z', stroke: true, fill: false, strokeWidth: 1.5 },
          { d: 'M28 32 C18 24 12 18 16 12 C20 6 24 6 28 12 C32 6 36 6 40 12 C44 18 38 24 28 32Z', stroke: true, fill: false, strokeWidth: 1.5 },
        ],
      },
      {
        id: 'star-simple', label: 'Star', baseW: 36, baseH: 36,
        paths: [{ d: 'M18 2 L22 14 L34 14 L24 22 L28 34 L18 26 L8 34 L12 22 L2 14 L14 14Z', fill: true }],
      },
      {
        id: 'butterfly', label: 'Butterfly', baseW: 44, baseH: 32,
        paths: [
          { d: 'M22 16 Q12 4 4 8 Q0 16 10 22 Q16 26 22 22Z', fill: true },
          { d: 'M22 16 Q32 4 40 8 Q44 16 34 22 Q28 26 22 22Z', fill: true },
          { d: 'M22 10 L22 28', stroke: true, fill: false, strokeWidth: 1.5 },
          { d: 'M22 10 Q18 4 16 2 M22 10 Q26 4 28 2', stroke: true, fill: false, strokeWidth: 1 },
        ],
      },
      {
        id: 'dove', label: 'Dove', baseW: 44, baseH: 32,
        paths: [
          { d: 'M8 20 Q4 14 8 10 Q14 4 22 8 Q30 4 36 8 Q42 12 40 18 Q38 16 34 18 Q30 14 22 16 Q16 14 8 20Z', fill: true },
          { d: 'M8 20 Q6 24 10 26 Q14 22 16 20', stroke: true, fill: false, strokeWidth: 1.5 },
        ],
      },
      {
        id: 'patchwork-block', label: 'Quilt Block', baseW: 32, baseH: 32,
        paths: [
          { d: 'M0 0 L16 16 L0 32Z M32 0 L16 16 L32 32Z', fill: true },
          { d: 'M0 0 L32 0 L16 16Z M0 32 L32 32 L16 16Z', stroke: true, fill: false, strokeWidth: 1.5 },
        ],
      },
    ],
  },
  frames: {
    label: 'Frames',
    items: [
      {
        id: 'frame-simple', label: 'Simple Frame', baseW: 80, baseH: 60,
        paths: [{ d: 'M4 4 L76 4 L76 56 L4 56Z', stroke: true, fill: false, strokeWidth: 2 }],
      },
      {
        id: 'frame-double', label: 'Double Frame', baseW: 80, baseH: 60,
        paths: [
          { d: 'M4 4 L76 4 L76 56 L4 56Z', stroke: true, fill: false, strokeWidth: 1.5 },
          { d: 'M8 8 L72 8 L72 52 L8 52Z', stroke: true, fill: false, strokeWidth: 1 },
        ],
      },
      {
        id: 'frame-scalloped', label: 'Scalloped Frame', baseW: 80, baseH: 60,
        paths: [
          { d: 'M10 4 Q20 0 30 4 Q40 0 50 4 Q60 0 70 4 L76 10 Q80 20 76 30 Q80 40 76 50 L70 56 Q60 60 50 56 Q40 60 30 56 Q20 60 10 56 L4 50 Q0 40 4 30 Q0 20 4 10Z', stroke: true, fill: false, strokeWidth: 1.5 },
        ],
      },
    ],
  },
  corners: {
    label: 'Corner Ornaments',
    items: [
      {
        id: 'corner-floral', label: 'Floral Corner', baseW: 30, baseH: 30,
        paths: [
          { d: 'M4 26 Q8 18 14 14 Q18 8 26 4', stroke: true, fill: false, strokeWidth: 1.5 },
          { d: 'M8 22 Q6 18 10 16 Q8 14 12 12Z', fill: true },
          { d: 'M16 12 Q14 8 18 6 Q16 4 20 4Z', fill: true },
        ],
      },
      {
        id: 'corner-scroll', label: 'Scroll Corner', baseW: 30, baseH: 30,
        paths: [
          { d: 'M4 26 Q4 14 14 4 Q10 10 8 16 Q8 20 12 18 Q16 16 14 12 Q14 8 18 6', stroke: true, fill: false, strokeWidth: 1.5 },
        ],
      },
    ],
  },
  holiday: {
    label: 'Holiday / Occasion',
    items: [
      {
        id: 'snowflake', label: 'Snowflake', baseW: 36, baseH: 36,
        paths: [
          { d: 'M18 2 L18 34 M4 10 L32 26 M4 26 L32 10', stroke: true, fill: false, strokeWidth: 1.5 },
          { d: 'M18 6 L15 8 M18 6 L21 8 M18 30 L15 28 M18 30 L21 28 M8 12 L8 16 M8 12 L12 12 M28 24 L28 20 M28 24 L24 24 M8 24 L12 24 M8 24 L8 20 M28 12 L24 12 M28 12 L28 16', stroke: true, fill: false, strokeWidth: 1 },
        ],
      },
      {
        id: 'holly', label: 'Holly', baseW: 36, baseH: 28,
        paths: [
          { d: 'M8 14 Q4 8 8 4 Q12 2 16 6 Q14 10 10 14 Q14 18 16 22 Q12 26 8 24 Q4 20 8 14Z', fill: true },
          { d: 'M20 14 Q24 8 28 4 Q32 2 34 6 Q30 10 26 14 Q30 18 34 22 Q32 26 28 24 Q24 20 20 14Z', fill: true },
          { d: 'M16 12 A3 3 0 1 1 22 12 A3 3 0 1 1 16 12Z M14 16 A3 3 0 1 1 20 16 A3 3 0 1 1 14 16Z', fill: true },
        ],
      },
      {
        id: 'baby-rattle', label: 'Baby Rattle', baseW: 24, baseH: 40,
        paths: [
          { d: 'M8 4 A8 8 0 1 1 8 20 A8 8 0 1 1 8 4Z', stroke: true, fill: false, strokeWidth: 1.5 },
          { d: 'M12 20 L12 36 Q12 40 16 40 Q20 40 20 36 L20 20', stroke: true, fill: false, strokeWidth: 2 },
          { d: 'M8 28 L24 28', stroke: true, fill: false, strokeWidth: 1.5 },
        ],
      },
    ],
  },
};

export const ALL_ELEMENT_CATEGORIES = Object.keys(DECORATIVE_ELEMENTS);
