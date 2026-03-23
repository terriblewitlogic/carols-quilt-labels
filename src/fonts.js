// ─── Embroidery fonts ────────────────────────────────────────────────────────

// Embroidery letter spacing multiplier (130% of normal)
export const LETTER_SPACING = 1.30;
// value:         Hershey font name sent to the backend engine for export
// previewFont:   CSS font family used for canvas design-view rendering
// previewStyle:  optional CSS font-style ('italic')
// previewWeight: CSS font-weight to approximate Hershey stroke weight
//                Hershey fonts are single-stroke — most map to 300-400 (thin/normal)

export const FONT_CATEGORIES = [
  {
    id: 'script',
    label: 'Script / Cursive',
    minHeight_mm: 8.0,
    fonts: [
      { label: 'Script',        value: 'script',   previewFont: '"Brush Script MT", "Segoe Script", cursive', previewWeight: '500' },
      { label: 'Script Light',  value: 'script2',  previewFont: '"Brush Script MT", cursive',                 previewWeight: '400' },
      { label: 'Times Italic',  value: 'cursive',  previewFont: '"Times New Roman", Georgia, serif',          previewWeight: '700', previewStyle: 'italic' },
    ],
  },
  {
    id: 'sans-serif',
    label: 'Sans-Serif (Block)',
    minHeight_mm: 6.35,
    fonts: [
      { label: 'Sans-Serif',    value: 'sans',      previewFont: 'Arial, "Helvetica Neue", sans-serif', previewWeight: '300' },
      { label: 'Sans Bold',     value: 'sans-bold', previewFont: 'Arial, "Helvetica Neue", sans-serif', previewWeight: '600' },
    ],
  },
  {
    id: 'serif',
    label: 'Serif',
    minHeight_mm: 7.0,
    fonts: [
      { label: 'Serif',         value: 'serif',        previewFont: 'Georgia, serif',                          previewWeight: '400' },
      { label: 'Serif Medium',  value: 'serif-medium', previewFont: 'Georgia, serif',                          previewWeight: '500' },
      { label: 'Serif Bold',    value: 'serif-bold',   previewFont: 'Georgia, serif',                          previewWeight: '700' },
      { label: 'Italic Serif',  value: 'italic',       previewFont: 'Palatino, "Book Antiqua", serif',         previewWeight: '400', previewStyle: 'italic' },
      { label: 'Times',         value: 'times',        previewFont: '"Times New Roman", Georgia, serif',        previewWeight: '400' },
      { label: 'Times Bold',    value: 'times-bold',   previewFont: '"Times New Roman", Georgia, serif',        previewWeight: '700' },
    ],
  },
  {
    id: 'display',
    label: 'Display',
    minHeight_mm: 10.0,
    fonts: [
      { label: 'Gothic',        value: 'gothic',        previewFont: '"Palatino Linotype", Palatino, serif', previewWeight: '400' },
      { label: 'Gothic Italic', value: 'gothic-italic', previewFont: '"Palatino Linotype", Palatino, serif', previewWeight: '400', previewStyle: 'italic' },
    ],
  },
];

// Flat list for dropdowns and lookups
export const ALL_FONTS = FONT_CATEGORIES.flatMap(cat =>
  cat.fonts.map(f => ({ ...f, category: cat.id, minHeight_mm: cat.minHeight_mm }))
);

// Get min height for a font value
export function getMinHeight(fontValue) {
  const f = ALL_FONTS.find(f => f.value === fontValue);
  return f ? f.minHeight_mm : 6.35;
}

// Build CSS font string for canvas preview rendering
// Weights approximate Hershey single-stroke visual weight (mostly thin/normal)
export function getPreviewCSS(fontValue, fontSize) {
  const f = ALL_FONTS.find(f => f.value === fontValue);
  const family = f?.previewFont || 'Georgia, serif';
  const style  = f?.previewStyle || 'normal';
  const weight = f?.previewWeight || '400';
  return `${style} ${weight} ${fontSize}px ${family}`;
}
