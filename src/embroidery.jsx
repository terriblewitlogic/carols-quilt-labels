import { useState, useRef, useEffect, useCallback, useReducer } from "react";
import { getCanvasDims, DEFAULT_HOOP, HOOPS, SHAPES, SHAPE_LABELS, MIN_BORDER_MM } from './constants.js';
import { PALETTES, DEFAULT_PALETTE } from './colors.js';
import { FONT_CATEGORIES, ALL_FONTS, getPreviewCSS, getMinHeight } from './fonts.js';
import { generateStitches, borderStitches } from './stitch-engine.js';
// jef-encoder.js kept for reference; export now handled by Netlify function (pyembroidery)
import { TEMPLATES } from './templates.js';
import { DECORATIVE_ELEMENTS } from './decorative-elements.js';
import { BORDER_TYPES, generateBorderStitches } from './borders.js';
import { openColorChart } from './color-chart.js';
import { PX_PER_MM } from './constants.js';

// ─── Unit conversion helpers (px ↔ display unit) ─────────────────────────────
const PX_PER_IN  = PX_PER_MM * 25.4;   // 101.6 px per inch
const PX_PER_CM  = PX_PER_MM * 10;     // 40 px per cm
const pxToUnit = (px, unit) => unit === 'in' ? px / PX_PER_IN : px / PX_PER_CM;
const unitToPx = (val, unit) => Math.round(val * (unit === 'in' ? PX_PER_IN : PX_PER_CM));
const mmToUnit = (mm, unit) => unit === 'in' ? mm / 25.4 : mm / 10;
const fmtUnit  = (val, unit) => unit === 'in'
  ? `${val.toFixed(2)}"`
  : `${val.toFixed(1)} cm`;
// Slider bounds in each unit
const UNIT_SLIDER = {
  in: { min: 0.10, max: 1.60, step: 0.05 },
  cm: { min: 0.30, max: 4.00, step: 0.10 },
};

let uid = 200;

// ─── Undo/Redo reducer ───────────────────────────────────────────────────────
function elsReducer(state, action) {
  switch (action.type) {
    case 'SET': return action.els;
    case 'ADD': return [...state, action.el];
    case 'UPD': return state.map(e => e.id === action.id ? { ...e, ...action.props } : e);
    case 'DEL': return state.filter(e => e.id !== action.id);
    default: return state;
  }
}

// ─── Styles ──────────────────────────────────────────────────────────────────
const s = {
  wrap: { display:'flex', flexDirection:'column', height:'100vh', fontFamily:'"Iowan Old Style", Georgia, serif', background:'#1A1410', color:'#E8E0D4', overflow:'hidden' },
  topBar: { display:'flex', alignItems:'center', padding:'0 16px', height:46, background:'#110E0B', borderBottom:'1px solid #2E2820', gap:10, flexShrink:0 },
  body: { display:'flex', flex:1, overflow:'hidden', minHeight:0 },
  leftSide: { width:248, background:'#110E0B', borderRight:'1px solid #2E2820', display:'flex', flexDirection:'column', flexShrink:0 },
  rightSide: { width:268, background:'#110E0B', borderLeft:'1px solid #2E2820', overflowY:'auto', padding:'12px 14px', flexShrink:0, scrollbarWidth:'thin' },
  main: { flex:1, display:'flex', alignItems:'center', justifyContent:'center', background:'#0D0B08', position:'relative', overflow:'hidden' },
  bottomBar: { height:26, background:'#0D0B08', borderTop:'1px solid #1E1C18', display:'flex', alignItems:'center', padding:'0 16px', gap:20, flexShrink:0 },
  inp: { width:'100%', padding:'6px 9px', background:'#1A1410', border:'1px solid #3A3020', borderRadius:5, color:'#E8E0D4', fontSize:12, marginBottom:6, boxSizing:'border-box', fontFamily:'inherit', outline:'none' },
  sec: { padding:'6px 12px', background:'#1E1C18', border:'1px solid #3A3020', borderRadius:5, color:'#C8A060', cursor:'pointer', fontSize:12, fontFamily:'inherit' },
  pri: { padding:'7px 16px', background:'#7A1A10', border:'none', borderRadius:5, color:'#F8E8D8', cursor:'pointer', fontWeight:700, fontSize:12, letterSpacing:'.3px', fontFamily:'inherit' },
  lbl: { fontSize:9, fontWeight:700, color:'#5A4830', letterSpacing:2, textTransform:'uppercase', marginBottom:7, marginTop:2, display:'block' },
  card: { background:'#1A1410', border:'1px solid #2E2820', borderRadius:7, padding:10, marginBottom:12 },
  pill: (active) => ({ padding:'4px 9px', borderRadius:20, border:'none', background: active ? '#3A2E1E' : 'transparent', color: active ? '#C8A060' : '#5A4830', cursor:'pointer', fontSize:11, fontFamily:'inherit', flexShrink:0 }),
  tabBtn: (active) => ({ flex:1, padding:'8px 4px', borderWidth:0, borderBottomWidth:2, borderStyle:'solid', borderBottomColor: active ? '#C8A060' : 'transparent', background:'transparent', color: active ? '#C8A060' : '#5A4830', cursor:'pointer', fontSize:11, fontFamily:'inherit', letterSpacing:.5, textTransform:'uppercase' }),
  iconBtn: { background:'transparent', border:'1px solid #2E2820', borderRadius:4, color:'#6A5840', cursor:'pointer', padding:'4px 7px', fontSize:12, fontFamily:'inherit' },
};

// ─── Helper: draw label shape clip path ─────────────────────────────────────
function applyShapeClip(ctx, shape, x, y, w, h) {
  ctx.beginPath();
  const r = Math.min(w, h) * 0.05;
  if (shape === 'rectangle') {
    ctx.roundRect(x, y, w, h, r);
  } else if (shape === 'square') {
    const sz = Math.min(w, h);
    ctx.roundRect(x + (w - sz) / 2, y + (h - sz) / 2, sz, sz, r);
  } else if (shape === 'oval') {
    ctx.ellipse(x + w / 2, y + h / 2, w / 2, h / 2, 0, 0, Math.PI * 2);
  } else if (shape === 'heart') {
    const cx = x + w / 2, cy = y + h * 0.35;
    const rx = w * 0.26, ry = h * 0.26;
    ctx.moveTo(cx, y + h * 0.92);
    ctx.bezierCurveTo(cx - w * 0.45, cy + ry * 1.2, cx - w * 0.5, cy - ry, cx, cy - ry * 0.2);
    ctx.bezierCurveTo(cx + w * 0.5, cy - ry, cx + w * 0.45, cy + ry * 1.2, cx, y + h * 0.92);
  } else if (shape === 'rectangle-h') {
    ctx.roundRect(x, y, w, h, r);
  } else if (shape === 'triangle') {
    // Equilateral-ish triangle: apex centered top, base at bottom
    ctx.moveTo(x + w / 2, y); ctx.lineTo(x + w, y + h); ctx.lineTo(x, y + h);
  } else {
    ctx.rect(x, y, w, h);
  }
  ctx.closePath();
}

// ─── Main Component ──────────────────────────────────────────────────────────
export default function QuiltLabelMaker() {
  const [hoopKey, setHoopKey] = useState(DEFAULT_HOOP);
  const [labelShape, setLabelShape] = useState('rectangle-h');
  const [border, setBorder] = useState({ type: 'none', color: '#111111' });
  const [els, dispatch] = useReducer(elsReducer, []);
  const [history, setHistory] = useState([]);
  const [future, setFuture] = useState([]);
  const [sel, setSel] = useState(1);
  const [mode, setMode] = useState('design');
  const [sGroups, setSG] = useState([]);
  const [drag, setDrag] = useState(null);
  const [snap, setSnap] = useState(false);
  const [leftTab, setLeftTab] = useState('templates');
  const [palette, setPalette] = useState(DEFAULT_PALETTE);
  const [colorFilter, setColorFilter] = useState('');
  const [activeTemplate, setActiveTemplate] = useState(null);
  const [stitchAngle, setStitchAngle] = useState(45);
  const [exportFormat, setExportFormat] = useState('jef');
  const [exporting, setExporting] = useState(false);
  const [previewSvg, setPreviewSvg] = useState(null);
  const [fontSamples, setFontSamples] = useState({});   // fontValue → svgString
  const [unit, setUnit] = useState('in');               // 'in' | 'cm'
  const cvs = useRef(null);

  const rawDims = getCanvasDims(hoopKey);
  // rectangle-h flips the canvas to landscape orientation
  const dims = labelShape === 'rectangle-h'
    ? { ...rawDims, cw: rawDims.ch, ch: rawDims.cw, dw: rawDims.dh, dh: rawDims.dw, hoopW: rawDims.hoopH, hoopH: rawDims.hoopW }
    : rawDims;
  const { cw, ch, dw, dh, mx, my } = dims;
  const selEl = els.find(e => e.id === sel);
  const totalSt = sGroups.reduce((s, g) => s + g.stitches.filter(Boolean).length, 0);
  const estMin = totalSt ? Math.ceil(totalSt / 800) : 0;
  const paletteColors = PALETTES[palette].colors;
  const filteredColors = colorFilter ? paletteColors.filter(c => c.n.toLowerCase().includes(colorFilter.toLowerCase())) : paletteColors;
  const hoop = HOOPS[hoopKey];

  // ── Undo/Redo ──
  const pushHistory = useCallback((snapshot) => {
    setHistory(h => [...h.slice(-30), snapshot]);
    setFuture([]);
  }, []);

  const undo = useCallback(() => {
    if (!history.length) return;
    setFuture(f => [els, ...f]);
    const prev = history[history.length - 1];
    setHistory(h => h.slice(0, -1));
    dispatch({ type:'SET', els: prev });
  }, [history, els]);

  const redo = useCallback(() => {
    if (!future.length) return;
    setHistory(h => [...h, els]);
    const next = future[0];
    setFuture(f => f.slice(1));
    dispatch({ type:'SET', els: next });
  }, [future, els]);

  // ── Default positions ──
  const defaultPos = useCallback(() => ({ x: cw / 2, y: ch / 2 }), [cw, ch]);

  // Re-center elements when hoop changes
  useEffect(() => {
    dispatch({ type:'SET', els: els.map((el, i) => ({
      ...el,
      x: cw / 2,
      y: my + (i + 1) * (dh / (els.length + 1)),
    }))});
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hoopKey]);

  // ── Fetch stitch SVG thumbnails for font picker (once when fonts tab opens) ──
  useEffect(() => {
    if (leftTab !== 'fonts' || Object.keys(fontSamples).length > 0) return;
    fetch('/api/font_samples', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' })
      .then(r => r.json())
      .then(d => { if (d.samples) setFontSamples(d.samples); })
      .catch(() => {});  // silently ignore — CSS fallback stays visible
  }, [leftTab]);

  // ── Drawing ──
  useEffect(() => {
    const canvas = cvs.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, cw, ch);

    // Fabric background (entire canvas)
    const bg = ctx.createLinearGradient(0, 0, cw, ch);
    bg.addColorStop(0, '#FBF7F0'); bg.addColorStop(1, '#F0E8DC');
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, cw, ch);

    // Linen weave texture
    ctx.fillStyle = 'rgba(130,105,70,.06)';
    for (let x = 6; x < cw; x += 8) for (let y = 6; y < ch; y += 8) {
      ctx.beginPath(); ctx.arc(x, y, 0.6, 0, Math.PI * 2); ctx.fill();
    }

    // Design area boundary
    ctx.save();
    applyShapeClip(ctx, labelShape, mx, my, dw, dh);
    ctx.strokeStyle = 'rgba(150,100,50,.25)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();

    // Margin guide (outer)
    ctx.strokeStyle = 'rgba(150,100,50,.12)';
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 6]);
    ctx.strokeRect(0.5, 0.5, cw - 1, ch - 1);
    ctx.setLineDash([]);

    // Clip to label shape
    ctx.save();
    applyShapeClip(ctx, labelShape, mx, my, dw, dh);
    ctx.clip();

    if (mode === 'stitch' && sGroups.length) {
      for (const grp of sGroups) {
        const st = grp.stitches;
        ctx.strokeStyle = grp.color; ctx.lineWidth = 2.5; ctx.lineCap = 'round';
        for (let i = 1; i < st.length; i++) {
          if (!st[i] || !st[i-1]) continue; // null = jump between fill runs
          const d = Math.hypot(st[i].x - st[i-1].x, st[i].y - st[i-1].y);
          if (d < 3 || d > 100) continue; // skip inter-row hops and element-to-element jumps
          ctx.beginPath();
          ctx.moveTo(st[i-1].x, st[i-1].y);
          ctx.lineTo(st[i].x, st[i].y);
          ctx.stroke();
        }
      }
    } else {
      for (const el of els) {
        ctx.save();
        if (el.type === 'decorative' && el.paths) {
          const scale = (el.fontSize / (el.baseH || 40)) * (el.scale || 1);
          const pw = (el.baseW || 40) * scale, ph = (el.baseH || 40) * scale;
          ctx.translate(el.x - pw / 2, el.y - ph / 2);
          ctx.scale(scale, scale);
          ctx.fillStyle = el.color; ctx.strokeStyle = el.color;
          for (const p of el.paths) {
            const p2d = new Path2D(p.d);
            if (p.fill !== false) ctx.fill(p2d);
            if (p.stroke) { ctx.lineWidth = p.strokeWidth || 1.5; ctx.stroke(p2d); }
          }
        } else {
          ctx.font = getPreviewCSS(el.font, el.fontSize);
          ctx.fillStyle = el.color;
          ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
          ctx.shadowColor = 'rgba(0,0,0,.18)';
          ctx.shadowBlur = 2; ctx.shadowOffsetX = 1; ctx.shadowOffsetY = 1;
          ctx.fillText(el.content, el.x, el.y);
          ctx.shadowBlur = 0; ctx.shadowOffsetX = 0; ctx.shadowOffsetY = 0;
        }
        if (el.id === sel) {
          ctx.strokeStyle = 'rgba(60,130,255,.9)'; ctx.lineWidth = 1.5; ctx.setLineDash([5,4]);
          const mw = el.type === 'decorative' ? (el.baseW || 40) * (el.fontSize / (el.baseH || 40)) : ctx.measureText(el.content).width + 16;
          const mh = el.fontSize + 12;
          ctx.strokeRect(el.x - mw / 2, el.y - mh / 2, mw, mh); ctx.setLineDash([]);
          ctx.fillStyle = '#4A90FF';
          [[el.x - mw/2, el.y - mh/2],[el.x + mw/2, el.y - mh/2],[el.x - mw/2, el.y + mh/2],[el.x + mw/2, el.y + mh/2]]
            .forEach(([px,py]) => { ctx.beginPath(); ctx.arc(px, py, 4, 0, Math.PI * 2); ctx.fill(); });
        }
        ctx.restore();
      }
    }
    ctx.restore();

    // Empty canvas hint
    if (els.length === 0 && mode === 'design') {
      ctx.save();
      ctx.fillStyle = 'rgba(139,100,56,0.22)';
      ctx.font = '13px Georgia, serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('← Select a template to start', cw / 2, ch / 2);
      ctx.restore();
    }

    // Snap grid (when enabled)
    if (snap && mode !== 'stitch') {
      const gridMm = 6.35;
      const gridPx = gridMm * PX_PER_MM;
      ctx.strokeStyle = 'rgba(200,160,80,.07)'; ctx.lineWidth = 1;
      for (let x = mx % gridPx; x < cw; x += gridPx) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, ch); ctx.stroke(); }
      for (let y = my % gridPx; y < ch; y += gridPx) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(cw, y); ctx.stroke(); }
    }

    // Hoop border (thin outer frame)
    ctx.strokeStyle = 'rgba(100,70,30,.3)'; ctx.lineWidth = 2;
    ctx.strokeRect(1, 1, cw - 2, ch - 2);
  }, [els, sel, mode, sGroups, cw, ch, dw, dh, mx, my, labelShape, snap]);

  // ── Stitch Generation ──
  const genStitches = useCallback(() => {
    const groups = [];
    for (const el of els) {
      const fillSt = generateStitches({ ...el, stitchAngle: el.stitchAngle || stitchAngle });
      if (fillSt.length) groups.push({ color: el.color, colorName: el.colorName, brandCode: el.brandCode, stitches: fillSt });
      if (el.satinBorder && (el.stitchType === 'tatami' || el.stitchType === 'fill') && (el.fontSize / 4) >= MIN_BORDER_MM) {
        const bSt = borderStitches(el);
        if (bSt.length) groups.push({ color: el.color, colorName: el.colorName, brandCode: el.brandCode, stitches: bSt });
      }
    }

    // Border stitches
    if (border.type !== 'none') {
      const bPts = generateBorderStitches(border.type, dw, dh, PX_PER_MM);
      const translated = bPts.map(p => ({ x: p.x + mx, y: p.y + my }));
      if (translated.length) groups.push({ color: border.color, colorName: 'Border', stitches: translated });
    }
    setSG(groups); return groups;
  }, [els, border, dw, dh, mx, my, stitchAngle]);

  const togglePreview = () => {
    if (mode !== 'stitch') { genStitches(); setMode('stitch'); }
    else setMode('design');
  };

  const doPreview = async () => {
    const textElements = els
      .filter(el => el.type === 'text')
      .map(el => ({
        text:       el.content,
        font:       el.font || 'script',
        size_mm:    el.fontSize / PX_PER_MM,
        x_px:       el.x,
        y_px:       el.y,
        color:      el.color,
        align:      'center',
        density_mm: el.density_mm ?? null,
      }));
    if (!textElements.length) { alert('Add some text first.'); return; }
    try {
      const res = await fetch('/api/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ textElements }),
      });
      if (res.ok) {
        const data = await res.json();
        setPreviewSvg(data.svg);
      } else {
        alert('Preview failed');
      }
    } catch (e) {
      alert(`Preview error: ${e.message}`);
    }
  };

  const doExport = async () => {
    // Build stitch groups for non-text elements (borders, decoratives)
    const groups = [];
    for (const el of els) {
      if (el.type === 'text') continue;   // text handled by backend engine
      const fillSt = generateStitches({ ...el, stitchAngle: el.stitchAngle || stitchAngle });
      if (fillSt.length) groups.push({ color: el.color, colorName: el.colorName, brandCode: el.brandCode, stitches: fillSt.filter(Boolean) });
    }
    if (border.type !== 'none') {
      const bPts = generateBorderStitches(border.type, dw, dh, PX_PER_MM);
      const translated = bPts.map(p => ({ x: p.x + mx, y: p.y + my }));
      if (translated.length) groups.push({ color: border.color, colorName: 'Border', stitches: translated });
    }

    // Build text element metadata for the backend Hershey engine
    const textElements = els
      .filter(el => el.type === 'text')
      .map(el => ({
        text:       el.content,
        font:       el.font || 'script',
        size_mm:    el.fontSize / PX_PER_MM,
        x_px:       el.x,
        y_px:       el.y,
        color:      el.color,
        align:      'center',
        density_mm: el.density_mm ?? null,
      }));

    if (!groups.length && !textElements.length) return;
    setExporting(true);
    try {
      const res = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ groups, textElements, canvasW: cw, canvasH: ch, format: exportFormat }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: res.statusText }));
        alert(`Export failed: ${err.error || res.statusText}`);
        return;
      }
      const blob = await res.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `carol-label.${exportFormat}`;
      a.click();
      URL.revokeObjectURL(a.href);
    } catch (e) {
      alert(`Export error: ${e.message}`);
    } finally {
      setExporting(false);
    }
  };

  const doColorChart = () => {
    const decorativeGroups = genStitches();

    // Collect text element colors — stitch count is estimated (backend processes text)
    // Estimate: ~30 stitches per mm of font height per non-space character
    const PX_PER_MM = 4;
    const textColorMap = new Map();
    for (const el of els.filter(e => e.type === 'text')) {
      const chars    = (el.content || '').replace(/\s/g, '').length;
      const sizeMm   = (el.fontSize || 48) / PX_PER_MM;
      const estCount = Math.round(chars * sizeMm * 30);
      const key      = el.color || '#000000';
      if (textColorMap.has(key)) {
        textColorMap.get(key).estStitches += estCount;
      } else {
        textColorMap.set(key, {
          color:       key,
          colorName:   el.colorName || 'Text',
          brandCode:   el.brandCode,
          estStitches: estCount,
          isText:      true,
        });
      }
    }
    const textGroups = [...textColorMap.values()].map(t => ({
      ...t,
      stitches: Array(t.estStitches).fill(0),  // .length used for totals
    }));

    const allGroups = [...textGroups, ...decorativeGroups];
    const dataUrl   = cvs.current?.toDataURL();
    openColorChart(allGroups, dataUrl, hoop.label, PALETTES[palette].label, exportFormat);
  };

  // ── CRUD ──
  const upd = useCallback((id, props) => {
    pushHistory(els);
    dispatch({ type:'UPD', id, props });
    setMode('design');
  }, [els, pushHistory]);

  const addText = (content, font, fontSize, color) => {
    if (!content.trim()) return;
    pushHistory(els);
    const el = { id: uid++, type:'text', content, x: cw/2, y: ch/2, fontSize: fontSize || 32, font: font || 'script', color: color || '#111111', stitchType:'tatami', stitchAngle: 45, density_mm: null };
    dispatch({ type:'ADD', el }); setSel(el.id); setMode('design');
  };

  const addDecorative = (item) => {
    pushHistory(els);
    // Stroke-only paths (frames, outlines) should trace with running stitch, not tatami fill
    const isStrokeOnly = item.paths.every(p => p.fill === false && p.stroke);
    const el = { id: uid++, type:'decorative', content: item.label, paths: item.paths, baseW: item.baseW, baseH: item.baseH, fontSize: item.baseH, x: cw/2, y: ch/2, color:'#111111', stitchType: isStrokeOnly ? 'satin' : 'fill', scale:1 };
    dispatch({ type:'ADD', el }); setSel(el.id); setMode('design');
  };

  const del = (id) => { pushHistory(els); dispatch({ type:'DEL', id }); setSel(null); };

  // ── Apply template ──
  const applyTemplate = (tpl) => {
    setActiveTemplate(tpl.id);
    pushHistory(els);
    // Create elements from layout
    const newEls = [];
    const cx = cw / 2;
    const totalItems = (tpl.layout || []).length;
    const spacing = dh / (totalItems + 1);
    tpl.layout?.forEach((item, i) => {
      const text = item.fixedText || tpl.defaults?.[item.field] || '';
      if (!text) return;
      const fontSize = Math.round(32 * (item.fontScale || 1));
      newEls.push({ id: uid++, type:'text', content: text, x: cx, y: my + spacing * (i + 1), fontSize, font: item.font || 'Georgia', color:'#111111', stitchType: 'tatami', stitchAngle: 45, density_mm: null, fieldKey: item.field });
    });
    dispatch({ type:'SET', els: newEls });
    setSel(newEls[0]?.id || null);
    setMode('design');
  };

  // ── Mouse ──
  const snapPt = (v, gridPx) => snap ? Math.round(v / gridPx) * gridPx : v;
  const GRID = 6.35 * PX_PER_MM;

  const toCanvas = e => {
    const r = cvs.current.getBoundingClientRect();
    return { x: (e.clientX - r.left) * (cw / r.width), y: (e.clientY - r.top) * (ch / r.height) };
  };
  const hitEl = ({ x, y }) => {
    const ctx = cvs.current.getContext('2d');
    for (let i = els.length - 1; i >= 0; i--) {
      const el = els[i];
      let hw, hh;
      if (el.type === 'decorative') {
        const sc = el.fontSize / (el.baseH || 40) * (el.scale || 1);
        hw = (el.baseW || 40) * sc / 2 + 8; hh = (el.baseH || 40) * sc / 2 + 8;
      } else {
        ctx.font = getPreviewCSS(el.font, el.fontSize);
        hw = ctx.measureText(el.content).width / 2 + 10; hh = el.fontSize / 2 + 8;
      }
      if (Math.abs(x - el.x) <= hw && Math.abs(y - el.y) <= hh) return el;
    }
    return null;
  };
  const onDown = e => {
    const p = toCanvas(e); const h = hitEl(p);
    if (h) { setSel(h.id); setDrag({ id:h.id, ox:p.x - h.x, oy:p.y - h.y }); }
    else setSel(null);
  };
  const onMove = e => {
    if (!drag) return;
    const p = toCanvas(e);
    dispatch({ type:'UPD', id:drag.id, props: { x: snapPt(p.x - drag.ox, GRID), y: snapPt(p.y - drag.oy, GRID) } });
  };
  const onUp = () => { if (drag) { pushHistory(els.map(e => e.id === drag.id ? { ...e } : e)); setDrag(null); } };

  // ── Keyboard ──
  useEffect(() => {
    const handler = e => {
      if (!selEl) return;
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') del(selEl.id);
      }
      if (e.key === 'Escape') setSel(null);
      if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key) && document.activeElement.tagName === 'CANVAS') {
        e.preventDefault();
        const step = snap ? GRID : 2;
        const dx = e.key==='ArrowLeft' ? -step : e.key==='ArrowRight' ? step : 0;
        const dy = e.key==='ArrowUp' ? -step : e.key==='ArrowDown' ? step : 0;
        upd(selEl.id, { x: selEl.x + dx, y: selEl.y + dy });
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) { e.preventDefault(); undo(); }
      if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) { e.preventDefault(); redo(); }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [selEl, sel, snap, undo, redo, GRID]);

  const [newText, setNewText] = useState('');
  const [newColor, setNewColor] = useState('#111111');

  // Canvas CSS size
  const maxCanvasH = 'calc(100vh - 80px)';
  const maxCanvasW = 'calc(100vw - 540px)';
  const canvasAspect = ch / cw;

  return (
    <div style={s.wrap}>

      {/* ─── Stitch Preview Modal ─── */}
      {previewSvg && (
        <div onClick={() => setPreviewSvg(null)}
          style={{ position:'fixed', inset:0, background:'rgba(0,0,0,.75)', zIndex:999,
                   display:'flex', alignItems:'center', justifyContent:'center', cursor:'pointer' }}>
          <div onClick={e => e.stopPropagation()}
            style={{ background:'#f5f0e8', borderRadius:12, padding:24, maxWidth:'80vw', maxHeight:'80vh',
                     overflow:'auto', boxShadow:'0 20px 60px rgba(0,0,0,.6)' }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12 }}>
              <span style={{ fontFamily:'Georgia, serif', fontSize:14, color:'#2c2418' }}>Stitch Preview</span>
              <button onClick={() => setPreviewSvg(null)}
                style={{ background:'none', border:'none', cursor:'pointer', fontSize:18, color:'#8a7e6e' }}>✕</button>
            </div>
            <div dangerouslySetInnerHTML={{ __html: previewSvg }} />
            <div style={{ marginTop:10, fontSize:11, color:'#8a7e6e', textAlign:'center' }}>
              This shows how the stitches will look on the machine. Click anywhere to close.
            </div>
          </div>
        </div>
      )}

      {/* ─── Top Bar ─── */}
      <div style={s.topBar}>
        <span style={{ fontSize:15, fontWeight:700, color:'#D4A060', letterSpacing:.3 }}>✂ Carol's Quilt Labels</span>
        <div style={{ width:1, height:20, background:'#2E2820', margin:'0 4px' }} />

        {/* Hoop size */}
        <select value={hoopKey} onChange={e => setHoopKey(e.target.value)}
          style={{ ...s.inp, width:'auto', marginBottom:0, fontSize:11, padding:'3px 6px' }}>
          {Object.entries(HOOPS).map(([k, v]) => <option key={k} value={k}>{v.label} ({v.w}×{v.h}mm)</option>)}
        </select>

        {/* Label shape */}
        <select value={labelShape} onChange={e => setLabelShape(e.target.value)}
          style={{ ...s.inp, width:'auto', marginBottom:0, fontSize:11, padding:'3px 6px' }}>
          {SHAPES.map(sh => <option key={sh} value={sh}>{SHAPE_LABELS[sh] || sh}</option>)}
        </select>

        <div style={{ flex:1 }} />

        {/* Undo / Redo */}
        <button onClick={undo} disabled={!history.length} style={{ ...s.iconBtn, opacity: history.length ? 1 : 0.35 }} title="Undo (Ctrl+Z)">↩</button>
        <button onClick={redo} disabled={!future.length} style={{ ...s.iconBtn, opacity: future.length ? 1 : 0.35 }} title="Redo">↪</button>

        {/* Snap */}
        <button onClick={() => setSnap(s => !s)} style={{ ...s.iconBtn, color: snap ? '#C8A060' : '#6A5840', outline: snap ? '1px solid #C8A060' : 'none' }} title="Snap to grid">⊞</button>

        <div style={{ width:1, height:20, background:'#2E2820', margin:'0 4px' }} />

        <button onClick={togglePreview} style={s.sec}>{mode === 'stitch' ? '🎨 Design' : '🧵 Preview'}</button>
        <select value={exportFormat} onChange={e => setExportFormat(e.target.value)}
          style={{ ...s.inp, width:'auto', marginBottom:0, padding:'6px 8px', fontSize:12 }}
          title="Export format">
          <option value="jef">JEF — Janome</option>
          <option value="pes">PES — Brother</option>
          <option value="dst">DST — Tajima</option>
          <option value="vp3">VP3 — Pfaff</option>
          <option value="exp">EXP — Bernina</option>
        </select>
        <button onClick={doPreview} style={{ ...s.sec }}>🖼 Preview</button>
        <button onClick={doExport} disabled={exporting} style={{ ...s.pri, opacity: exporting ? 0.6 : 1 }}>
          {exporting ? '⏳ Exporting…' : '⬇ Export'}
        </button>
        <button onClick={doColorChart} style={{ ...s.sec, fontSize:11 }}>🎨 Color Chart</button>
      </div>

      <div style={s.body}>

        {/* ─── Left Sidebar ─── */}
        <div style={s.leftSide}>
          {/* Tab headers */}
          <div style={{ display:'flex', borderBottom:'1px solid #2E2820', flexShrink:0 }}>
            {[['templates','Templates'],['fonts','Fonts']].map(([id, label]) => (
              <button key={id} onClick={() => setLeftTab(id)} style={s.tabBtn(leftTab === id)}>{label}</button>
            ))}
          </div>

          <div style={{ overflowY:'auto', flex:1, padding:'12px 13px', scrollbarWidth:'thin' }}>

            {/* ── Templates tab ── */}
            {leftTab === 'templates' && <>
              {TEMPLATES.map(tpl => (
                <div key={tpl.id} onClick={() => applyTemplate(tpl)}
                  style={{ display:'flex', alignItems:'flex-start', gap:8, padding:'9px 10px', borderRadius:6, cursor:'pointer', marginBottom:4,
                    background: activeTemplate === tpl.id ? '#241E14' : 'transparent',
                    border: '1px solid #2E2820', outline: activeTemplate === tpl.id ? '1px solid #5A3A18' : 'none' }}>
                  <span style={{ fontSize:18, lineHeight:1, flexShrink:0 }}>{tpl.icon}</span>
                  <div>
                    <div style={{ fontSize:12, fontWeight:600, color:'#D4B080', marginBottom:2 }}>{tpl.label}</div>
                    <div style={{ fontSize:10, color:'#5A4830', lineHeight:1.4 }}>{tpl.description}</div>
                  </div>
                </div>
              ))}
            </>}


            {/* ── Fonts tab ── */}
            {leftTab === 'fonts' && <>
              <div style={{ fontSize:10, color:'#5A4830', marginBottom:10 }}>
                {selEl ? 'Click a font to apply it to the selected element.' : 'Select a text element on canvas first.'}
              </div>
              {FONT_CATEGORIES.map(cat => (
                <div key={cat.id}>
                  <span style={{ fontSize:9, fontWeight:700, color:'#4A3820', letterSpacing:2, textTransform:'uppercase', display:'block', marginBottom:6, marginTop:10 }}>
                    {cat.label} · min {cat.minHeight_mm}mm
                  </span>
                  {cat.fonts.map(f => {
                    const svg = fontSamples[f.value];
                    const isSelected = selEl?.font === f.value;
                    return (
                      <div key={f.value} onClick={() => selEl && upd(selEl.id, { font: f.value })}
                        style={{ padding:'6px 10px', marginBottom:4, borderRadius:5,
                          cursor: selEl ? 'pointer' : 'default',
                          background: isSelected ? '#241E14' : 'transparent',
                          outline: isSelected ? '1px solid #5A3A18' : 'none',
                          opacity: selEl ? 1 : 0.5 }}>
                        {svg
                          ? <div style={{ height:48, display:'flex', alignItems:'center', justifyContent:'center', overflow:'hidden' }}
                              dangerouslySetInnerHTML={{ __html: svg }} />
                          : <div style={{ fontFamily: f.previewFont, fontStyle: f.previewStyle||'normal', fontSize:18, color:'#D4B080', height:32, display:'flex', alignItems:'center' }}>Abc</div>
                        }
                        <div style={{ fontSize:10, color: isSelected ? '#C8A060' : '#5A4830', marginTop:2 }}>{f.label}</div>
                      </div>
                    );
                  })}
                </div>
              ))}
              {Object.keys(fontSamples).length === 0 &&
                <div style={{ fontSize:9, color:'#3A3020', textAlign:'center', marginTop:16 }}>Loading stitch previews…</div>
              }
            </>}
          </div>
        </div>

        {/* ─── Canvas ─── */}
        <div style={s.main}>
          <div style={{ position:'relative' }}>
            {/* Rulers */}
            <RulerH width={cw} hoopW={dims.hoopW} style={{ display:'block', height:16, width:`min(${maxCanvasW}, ${cw / canvasAspect * (canvasAspect < 1 ? 1 : canvasAspect)}px)`, marginLeft:16 }} />
            <div style={{ display:'flex' }}>
              <RulerV height={ch} hoopH={dims.hoopH} style={{ width:16, height:`min(${maxCanvasH}, ${ch}px)` }} />
              <canvas ref={cvs} width={cw} height={ch}
                onMouseDown={onDown} onMouseMove={onMove} onMouseUp={onUp} onMouseLeave={onUp}
                tabIndex={0}
                style={{ display:'block',
                  width: `min(${maxCanvasW}, ${cw}px)`,
                  height: `min(${maxCanvasH}, ${ch}px)`,
                  cursor: drag ? 'grabbing' : 'grab',
                  outline:'none',
                  boxShadow:'0 8px 40px rgba(0,0,0,.6)' }} />
            </div>
          </div>
        </div>

        {/* ─── Right Sidebar ─── */}
        <div style={s.rightSide}>

          {/* Properties Panel */}
          {selEl && <>
            <span style={s.lbl}>Selected Element</span>
            <div style={s.card}>
              {selEl.type !== 'decorative' && <>
                <label style={{ fontSize:10, color:'#6A5840', display:'block', marginBottom:3 }}>Text</label>
                <input value={selEl.content} onChange={e => upd(selEl.id, { content: e.target.value })} style={s.inp} />
                <label style={{ fontSize:10, color:'#6A5840', display:'block', marginBottom:3 }}>Font</label>
                <select value={selEl.font} onChange={e => upd(selEl.id, { font: e.target.value })} style={s.inp}>
                  {FONT_CATEGORIES.map(cat => (
                    <optgroup key={cat.id} label={cat.label}>
                      {cat.fonts.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
                    </optgroup>
                  ))}
                </select>
              </>}

              {/* ── Size slider with in / cm toggle ── */}
              <div style={{ display:'flex', gap:6, alignItems:'center', marginBottom:3 }}>
                <span style={{ fontSize:10, color:'#6A5840', flexShrink:0, minWidth:16 }}>Size</span>
                {/* numeric readout */}
                <span style={{ fontSize:11, color:'#C8A060', minWidth:38, flexShrink:0, fontVariantNumeric:'tabular-nums' }}>
                  {fmtUnit(pxToUnit(selEl.fontSize, unit), unit)}
                </span>
                {/* unit toggle */}
                <div style={{ display:'flex', border:'1px solid #3A3020', borderRadius:4, overflow:'hidden', flexShrink:0, marginLeft:'auto' }}>
                  {['in','cm'].map(u => (
                    <button key={u} onClick={() => setUnit(u)}
                      style={{ padding:'2px 7px', fontSize:9, fontFamily:'inherit', cursor:'pointer', border:'none',
                        background: unit === u ? '#3A2E1E' : 'transparent',
                        color: unit === u ? '#C8A060' : '#5A4830' }}>
                      {u}
                    </button>
                  ))}
                </div>
              </div>
              <input type="range"
                min={UNIT_SLIDER[unit].min}
                max={UNIT_SLIDER[unit].max}
                step={UNIT_SLIDER[unit].step}
                value={parseFloat(pxToUnit(selEl.fontSize, unit).toFixed(unit === 'in' ? 2 : 1))}
                onChange={e => upd(selEl.id, { fontSize: unitToPx(+e.target.value, unit) })}
                style={{ width:'100%', accentColor:'#C8A060', marginBottom:6 }} />
              {selEl.type === 'text' && (() => {
                const sizeMm = selEl.fontSize / PX_PER_MM;
                const minMm  = getMinHeight(selEl.font);
                if (sizeMm < minMm) return (
                  <div style={{ fontSize:9, color:'#C05020', background:'rgba(192,80,32,0.12)', borderRadius:4, padding:'4px 7px', marginBottom:6 }}>
                    ⚠ {fmtUnit(mmToUnit(sizeMm, unit), unit)} is below the {fmtUnit(mmToUnit(minMm, unit), unit)} minimum for this font — stitching may be illegible.
                  </div>
                );
                return null;
              })()}

              {selEl.type === 'text' ? (<>
                {/* Text uses the Hershey satin engine — show density slider */}
                {(() => {
                  const PX_PER_MM = 4;
                  const autoDensity = Math.round(Math.max(18, Math.min(38, 10 + (selEl.fontSize / PX_PER_MM) * 1.0)));
                  const isAuto = selEl.density_mm == null;
                  const sliderVal = isAuto ? autoDensity : Math.round(selEl.density_mm * 100);
                  return (<>
                    <div style={{ display:'flex', gap:8, alignItems:'center', marginBottom:3 }}>
                      <span style={{ fontSize:10, color:'#6A5840', flexShrink:0, minWidth:58 }}>
                        Density {isAuto ? <span style={{ color:'#C8A060' }}>Auto</span> : `${selEl.density_mm.toFixed(2)}mm`}
                      </span>
                      <input type="range" min={15} max={45} step={1}
                        value={sliderVal}
                        onChange={e => upd(selEl.id, { density_mm: +e.target.value / 100 })}
                        style={{ flex:1, accentColor:'#C8A060' }} />
                    </div>
                    <div style={{ display:'flex', justifyContent:'space-between', marginBottom:6 }}>
                      <span style={{ fontSize:9, color:'#6A5840' }}>Dense 0.15</span>
                      {!isAuto && <button onClick={() => upd(selEl.id, { density_mm: null })}
                        style={{ fontSize:9, color:'#C8A060', background:'none', border:'none', cursor:'pointer', padding:0 }}>
                        ↺ Auto
                      </button>}
                      <span style={{ fontSize:9, color:'#6A5840' }}>Light 0.45</span>
                    </div>
                  </>);
                })()}
              </>) : (<>
                {/* Decorative element stitch type */}
                <label style={{ fontSize:10, color:'#6A5840', display:'block', marginBottom:3 }}>Stitch Type</label>
                <select value={selEl.stitchType} onChange={e => upd(selEl.id, { stitchType: e.target.value })} style={s.inp}>
                  <option value="tatami">Tatami Fill (45°)</option>
                  <option value="fill">Fill (horizontal)</option>
                  <option value="satin">Satin Stitch</option>
                </select>
                {(selEl.stitchType === 'tatami') && <>
                  <div style={{ display:'flex', gap:8, alignItems:'center', marginBottom:6 }}>
                    <span style={{ fontSize:10, color:'#6A5840', flexShrink:0, minWidth:40 }}>Angle {selEl.stitchAngle || stitchAngle}°</span>
                    <input type="range" min={0} max={90} value={selEl.stitchAngle || stitchAngle}
                      onChange={e => upd(selEl.id, { stitchAngle: +e.target.value })}
                      style={{ flex:1, accentColor:'#C8A060' }} />
                  </div>
                </>}
              </>)}

              {selEl.type === 'decorative' && <>
                <div style={{ display:'flex', gap:8, alignItems:'center', marginBottom:6 }}>
                  <span style={{ fontSize:10, color:'#6A5840', flexShrink:0, minWidth:40 }}>Scale {Math.round((selEl.scale||1)*100)}%</span>
                  <input type="range" min={80} max={120} value={Math.round((selEl.scale||1)*100)}
                    onChange={e => upd(selEl.id, { scale: +e.target.value / 100 })}
                    style={{ flex:1, accentColor:'#C8A060' }} />
                </div>
              </>}

              <button onClick={() => del(selEl.id)}
                style={{ width:'100%', padding:'6px', background:'#2E1010', border:'1px solid #4A2020', borderRadius:5, color:'#D08080', cursor:'pointer', fontSize:11, fontFamily:'inherit', marginTop:4 }}>
                🗑 Remove
              </button>
            </div>
          </>}

          {/* Add Free Text */}
          <span style={s.lbl}>Custom Text</span>
          <div style={{ display:'flex', gap:4, marginBottom:14 }}>
            <input value={newText} onChange={e => setNewText(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && newText.trim() && (addText(newText), setNewText(''))}
              placeholder="Quilted by Carol…" style={{ ...s.inp, marginBottom:0, flex:1 }} />
            <button onClick={() => { if (newText.trim()) { addText(newText); setNewText(''); } }}
              style={{ ...s.iconBtn, padding:'5px 10px', fontSize:13 }}>+</button>
          </div>

          {/* Thread Color */}
          <span style={s.lbl}>Thread Color</span>
          <div style={s.card}>
            <div style={{ display:'flex', gap:6, marginBottom:5, alignItems:'center' }}>
              <select value={palette} onChange={e => { setPalette(e.target.value); setColorFilter(''); }}
                style={{ ...s.inp, width:'auto', flex:1, marginBottom:0, fontSize:11 }}>
                {Object.entries(PALETTES).map(([k,v]) => <option key={k} value={k}>{v.label}</option>)}
              </select>
              <input value={colorFilter} onChange={e => setColorFilter(e.target.value)}
                placeholder="Search…" style={{ ...s.inp, width:64, marginBottom:0, fontSize:11 }} />
            </div>
            <div style={{ fontSize:9, color:'#4A3820', marginBottom:6 }}>
              {filteredColors.length === paletteColors.length
                ? `${paletteColors.length} colors · hover for name`
                : `${filteredColors.length} of ${paletteColors.length} · hover for name`}
            </div>
            <div style={{ display:'flex', flexWrap:'wrap', gap:4, maxHeight:130, overflowY:'auto', scrollbarWidth:'thin' }}>
              {filteredColors.map(col => (
                <div key={col.h + col.code} title={`${col.n}  ${col.code}`}
                  onClick={() => {
                    setNewColor(col.h);
                    if (selEl) upd(selEl.id, { color: col.h, colorName: col.n, brandCode: col.code });
                  }}
                  style={{ width:20, height:20, borderRadius:'50%', background:col.h, cursor:'pointer', flexShrink:0,
                    outline: col.h === '#FFFFFF' || col.h === '#FFF8E8' ? '1px solid #3A3020' : 'none',
                    boxShadow: newColor === col.h ? '0 0 0 2px #D4A060' : 'none' }} />
              ))}
            </div>
          </div>

          {/* Border */}
          <span style={s.lbl}>Border</span>
          <div style={s.card}>
            <select value={border.type} onChange={e => setBorder(b => ({ ...b, type: e.target.value }))} style={s.inp}>
              {BORDER_TYPES.map(b => <option key={b.id} value={b.id}>{b.label}</option>)}
            </select>
            {border.type !== 'none' && (
              <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                <span style={{ fontSize:10, color:'#6A5840' }}>Color</span>
                <div style={{ display:'flex', flexWrap:'wrap', gap:3 }}>
                  {['#000000','#111111','#6B3520','#A61C00','#0C1F6E','#1E5C2A'].map(h => (
                    <div key={h} onClick={() => setBorder(b => ({ ...b, color: h }))}
                      style={{ width:18, height:18, borderRadius:'50%', background:h, cursor:'pointer',
                        boxShadow: border.color === h ? '0 0 0 2px #D4A060' : 'none' }} />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Layers */}
          {els.length > 0 && <>
            <span style={s.lbl}>Layers ({els.length})</span>
            {[...els].reverse().map(el => (
              <div key={el.id} onClick={() => setSel(el.id)}
                style={{ display:'flex', alignItems:'center', gap:7, padding:'6px 8px', borderRadius:5, cursor:'pointer', marginBottom:3,
                  background: el.id === sel ? '#241E14' : 'transparent', outline: el.id === sel ? '1px solid #3A2E18' : 'none' }}>
                <div style={{ width:10, height:10, borderRadius:'50%', background:el.color, flexShrink:0, border:'1px solid rgba(255,255,255,.1)' }} />
                <span style={{ flex:1, fontSize:11, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{el.content}</span>
                <span style={{ fontSize:9, color:'#4A3820', flexShrink:0 }}>{el.stitchType}</span>
              </div>
            ))}
          </>}
        </div>
      </div>

      {/* ─── Bottom Status Bar ─── */}
      <div style={s.bottomBar}>
        <span style={{ fontSize:10, color:'#5A4830' }}>
          {hoop.label} · {dims.hoopW}×{dims.hoopH}mm
        </span>
        <span style={{ fontSize:10, color:'#3A3020' }}>|</span>
        <span style={{ fontSize:10, color:'#5A4830' }}>
          Design area: {dims.hoopW - 50}×{dims.hoopH - 50}mm
        </span>
        {mode === 'stitch' && <>
          <span style={{ fontSize:10, color:'#3A3020' }}>|</span>
          <span style={{ fontSize:10, color:'#C8A060' }}>{totalSt.toLocaleString()} stitches</span>
          <span style={{ fontSize:10, color:'#3A3020' }}>|</span>
          <span style={{ fontSize:10, color:'#5A4830' }}>{sGroups.length} color{sGroups.length !== 1 ? 's' : ''}</span>
          <span style={{ fontSize:10, color:'#3A3020' }}>|</span>
          <span style={{ fontSize:10, color:'#5A4830' }}>~{estMin} min</span>
        </>}
        <div style={{ flex:1 }} />
        <span style={{ fontSize:10, color:'#3A3020' }}>
          {snap ? '⊞ Snap on' : ''} · drag to position · Del to remove · Ctrl+Z undo
        </span>
      </div>
    </div>
  );
}

// ─── Element thumbnail ──────────────────────────────────────────────────────
function ElemThumb({ item }) {
  const canvasRef = useRef(null);
  useEffect(() => {
    const c = canvasRef.current;
    if (!c) return;
    const ctx = c.getContext('2d');
    ctx.clearRect(0, 0, 44, 38);
    const scaleX = 40 / item.baseW, scaleY = 34 / item.baseH;
    const scale = Math.min(scaleX, scaleY) * 0.9;
    const ox = (44 - item.baseW * scale) / 2;
    const oy = (38 - item.baseH * scale) / 2;
    ctx.save();
    ctx.translate(ox, oy);
    ctx.scale(scale, scale);
    ctx.fillStyle = '#C8A060'; ctx.strokeStyle = '#C8A060';
    for (const p of item.paths) {
      const p2d = new Path2D(p.d);
      if (p.fill !== false) ctx.fill(p2d);
      if (p.stroke) { ctx.lineWidth = (p.strokeWidth || 1.5) / scale * 1.5; ctx.stroke(p2d); }
    }
    ctx.restore();
  }, [item]);
  return <canvas ref={canvasRef} width={44} height={38} />;
}

// ─── Minimal ruler components ────────────────────────────────────────────────
function RulerH({ width, hoopW, style }) {
  const ref = useRef(null);
  useEffect(() => {
    const c = ref.current; if (!c) return;
    const ctx = c.getContext('2d');
    const W = c.width, H = c.height;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = '#1A1610'; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#3A3020'; ctx.fillRect(0, H - 1, W, 1);
    ctx.fillStyle = '#5A4830'; ctx.font = '8px Arial'; ctx.textAlign = 'center';
    const pxPerMm = W / hoopW;
    for (let mm = 0; mm <= hoopW; mm += 5) {
      const x = mm * pxPerMm;
      ctx.fillRect(x, H - (mm % 10 === 0 ? 7 : 4), 1, mm % 10 === 0 ? 7 : 4);
      if (mm % 10 === 0 && mm > 0 && mm < hoopW) ctx.fillText(mm, x, H - 8);
    }
  }, [width, hoopW]);
  return <canvas ref={ref} width={width} height={16} style={{ ...style, display:'block', imageRendering:'pixelated' }} />;
}

function RulerV({ height, hoopH, style }) {
  const ref = useRef(null);
  useEffect(() => {
    const c = ref.current; if (!c) return;
    const ctx = c.getContext('2d');
    const W = c.width, H = c.height;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = '#1A1610'; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#3A3020'; ctx.fillRect(W - 1, 0, 1, H);
    ctx.fillStyle = '#5A4830'; ctx.font = '8px Arial'; ctx.textAlign = 'right';
    const pxPerMm = H / hoopH;
    for (let mm = 0; mm <= hoopH; mm += 5) {
      const y = mm * pxPerMm;
      ctx.fillRect(W - (mm % 10 === 0 ? 7 : 4), y, mm % 10 === 0 ? 7 : 4, 1);
      if (mm % 10 === 0 && mm > 0 && mm < hoopH) {
        ctx.save(); ctx.translate(W - 9, y); ctx.rotate(-Math.PI / 2);
        ctx.fillText(mm, 0, 0); ctx.restore();
      }
    }
  }, [height, hoopH]);
  return <canvas ref={ref} width={16} height={height} style={{ ...style, display:'block', imageRendering:'pixelated' }} />;
}
