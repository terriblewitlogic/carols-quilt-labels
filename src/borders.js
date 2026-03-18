// ─── Border System ───────────────────────────────────────────────────────────

export const BORDER_TYPES = [
  {
    id: 'none', label: 'None',
  },
  {
    id: 'running', label: 'Running Stitch',
    isStitchOnly: true, inset: 2,
  },
  {
    id: 'double-line', label: 'Double Line',
    isStitchOnly: true, inset: 4,
  },
  {
    id: 'satin-outline', label: 'Satin Outline',
    isStitchOnly: true, width: 3, inset: 4,
  },
  {
    id: 'scallop', label: 'Scalloped',
    motifW: 14, motifH: 6,
    motif: 'M0 6 Q7 -2 14 6',
    cornerMotif: 'M0 6 Q3 3 6 0',
    inset: 8,
  },
  {
    id: 'vine', label: 'Vine & Leaf',
    motifW: 20, motifH: 8,
    motif: 'M0 4 Q5 0 10 4 Q15 8 20 4',
    leaf: 'M10 4 Q8 0 6 2 Q8 4 10 4Z',
    cornerMotif: 'M0 6 Q3 3 6 0',
    inset: 10,
  },
  {
    id: 'scrollwork', label: 'Scrollwork',
    motifW: 24, motifH: 10,
    motif: 'M0 5 Q4 0 8 5 Q12 10 16 5 Q20 0 24 5',
    cornerMotif: 'M0 8 Q4 4 8 0 Q4 4 0 8',
    inset: 12,
  },
];

// Calculate how many motif repeats fit an edge, with adjusted spacing
export function calculateRepeats(edgeLengthMm, motifWidthMm) {
  if (!motifWidthMm || motifWidthMm <= 0) return { count: 0, scale: 1 };
  const raw = edgeLengthMm / motifWidthMm;
  const count = Math.max(1, Math.round(raw));
  const scale = edgeLengthMm / (count * motifWidthMm);
  return { count, scale };
}

// Generate border stitch points for a rectangular label
export function generateBorderStitches(borderType, designW, designH, px_per_mm) {
  const border = BORDER_TYPES.find(b => b.id === borderType);
  if (!border || border.id === 'none') return [];

  const pts = [];
  const inset = (border.inset || 2) * px_per_mm;
  const x0 = inset, y0 = inset;
  const x1 = designW - inset, y1 = designH - inset;
  const spacing = 2 * px_per_mm; // 2mm stitch spacing

  if (border.isStitchOnly) {
    // Running stitch or satin outline along rectangle
    const perimeter = [];
    // Top edge
    for (let x = x0; x <= x1; x += spacing) perimeter.push({ x, y: y0 });
    // Right edge
    for (let y = y0; y <= y1; y += spacing) perimeter.push({ x: x1, y });
    // Bottom edge (reverse)
    for (let x = x1; x >= x0; x -= spacing) perimeter.push({ x, y: y1 });
    // Left edge (reverse)
    for (let y = y1; y >= y0; y -= spacing) perimeter.push({ x: x0, y });
    // Close
    perimeter.push({ x: x0, y: y0 });
    pts.push(...perimeter);

    // Double-line: add inner rectangle
    if (border.id === 'double-line') {
      const gap = 3 * px_per_mm;
      const ix0 = x0 + gap, iy0 = y0 + gap, ix1 = x1 - gap, iy1 = y1 - gap;
      for (let x = ix0; x <= ix1; x += spacing) pts.push({ x, y: iy0 });
      for (let y = iy0; y <= iy1; y += spacing) pts.push({ x: ix1, y });
      for (let x = ix1; x >= ix0; x -= spacing) pts.push({ x, y: iy1 });
      for (let y = iy1; y >= iy0; y -= spacing) pts.push({ x: ix0, y });
      pts.push({ x: ix0, y: iy0 });
    }

    // Satin outline: add zigzag along the path
    if (border.id === 'satin-outline') {
      const w = (border.width || 3) * px_per_mm / 2;
      const satinPts = [];
      for (let i = 0; i < perimeter.length - 1; i++) {
        const p = perimeter[i], q = perimeter[i + 1];
        const dx = q.x - p.x, dy = q.y - p.y;
        const len = Math.hypot(dx, dy);
        if (len < 0.5) continue;
        const nx = -dy / len * w, ny = dx / len * w;
        satinPts.push({ x: p.x + nx, y: p.y + ny });
        satinPts.push({ x: p.x - nx, y: p.y - ny });
      }
      pts.push(...satinPts);
    }
  } else if (border.motif) {
    // Motif-based borders
    const motifW = border.motifW * px_per_mm;
    const motifH = border.motifH * px_per_mm;
    const edgeW = x1 - x0;
    const edgeH = y1 - y0;

    // Generate scallop/vine points along each edge
    const genEdge = (startX, startY, length, angle) => {
      const { count } = calculateRepeats(length / px_per_mm, border.motifW);
      const segW = length / count;
      const cos = Math.cos(angle), sin = Math.sin(angle);
      for (let i = 0; i < count; i++) {
        const steps = 8;
        for (let s = 0; s <= steps; s++) {
          const t = s / steps;
          const lx = i * segW + t * segW;
          const ly = Math.sin(t * Math.PI) * motifH * 0.5;
          pts.push({
            x: startX + lx * cos - ly * sin,
            y: startY + lx * sin + ly * cos,
          });
        }
      }
    };

    genEdge(x0, y0, edgeW, 0);
    genEdge(x1, y0, edgeH, Math.PI / 2);
    genEdge(x1, y1, edgeW, Math.PI);
    genEdge(x0, y1, edgeH, -Math.PI / 2);
  }

  return pts;
}
