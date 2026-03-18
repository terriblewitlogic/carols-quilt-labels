// ─── Auto-layout engine for structured label fields ──────────────────────────
import { PX_PER_MM } from './constants.js';

// Given active fields with content, compute element positions within design area
export function autoLayout(fields, template, designW, designH, baseFontSize = 32) {
  const layout = template?.layout || [];
  const elements = [];
  const cx = designW / 2;
  const spacing = baseFontSize * 0.6;
  let uid = 100;

  // Collect fields that have content, in layout order
  const activeItems = [];
  for (const item of layout) {
    const text = item.fixedText || fields[item.field];
    if (text && text.trim()) {
      activeItems.push({ ...item, text: text.trim() });
    }
  }

  // Also add fields not in layout that have content
  for (const [key, val] of Object.entries(fields)) {
    if (val && val.trim() && !activeItems.find(a => a.field === key)) {
      activeItems.push({ field: key, text: val.trim(), fontScale: 0.75, font: 'Arial' });
    }
  }

  if (!activeItems.length) return [];

  // Calculate total height needed
  const totalItems = activeItems.length;
  const itemHeights = activeItems.map(item => baseFontSize * (item.fontScale || 1));
  const totalHeight = itemHeights.reduce((s, h) => s + h, 0) + spacing * (totalItems - 1);

  // Start Y to center vertically
  let y = (designH - totalHeight) / 2 + itemHeights[0] / 2;

  for (let i = 0; i < activeItems.length; i++) {
    const item = activeItems[i];
    const fontSize = Math.round(baseFontSize * (item.fontScale || 1));
    elements.push({
      id: uid++,
      type: 'text',
      content: item.text,
      x: cx,
      y: y,
      fontSize,
      font: item.font || 'Georgia',
      color: '#111111',
      stitchType: fontSize > 25 * PX_PER_MM ? 'fill' : 'satin',
      fieldKey: item.field,
    });
    y += itemHeights[i] + spacing;
  }

  return elements;
}
