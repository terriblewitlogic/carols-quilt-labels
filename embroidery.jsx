import { useState, useRef, useEffect, useCallback } from "react";

// ─── Scale / Units ──────────────────────────────────────────────────────────
const HOOP_PX   = 500;                        // canvas pixels
const HOOP_MM   = 100;                        // 100mm hoop
const MM2PX     = HOOP_PX / HOOP_MM;          // 5 px/mm
const PX2JEF    = 10 / MM2PX;                 // JEF units per px (0.1mm = 2.0)
const ROW_PX    = Math.round(2.4 * MM2PX);    // fill row spacing ~12px
const STITCH_PX = Math.round(3.5 * MM2PX);    // stitch length ~17px

// ─── Data ───────────────────────────────────────────────────────────────────
const THREAD_COLORS = [
  {n:'Crimson',    h:'#A61C00'}, {n:'Red',       h:'#CC0000'},
  {n:'Tomato',     h:'#E8412A'}, {n:'Coral',     h:'#FF6347'},
  {n:'Tangerine',  h:'#FF7518'}, {n:'Marigold',  h:'#F4A828'},
  {n:'Gold',       h:'#D4A017'}, {n:'Butter',    h:'#F5D060'},
  {n:'Fern',       h:'#5A8A3C'}, {n:'Forest',    h:'#1E5C2A'},
  {n:'Teal',       h:'#006B6B'}, {n:'Aqua',      h:'#00AEAE'},
  {n:'Sky',        h:'#6BAED6'}, {n:'Royal',     h:'#2650A0'},
  {n:'Navy',       h:'#0C1F6E'}, {n:'Indigo',    h:'#3D1F8C'},
  {n:'Plum',       h:'#7B2FBE'}, {n:'Orchid',    h:'#C060B0'},
  {n:'Rose',       h:'#D44070'}, {n:'Blush',     h:'#F48080'},
  {n:'Chocolate',  h:'#6B3520'}, {n:'Caramel',   h:'#A0522D'},
  {n:'Black',      h:'#111111'}, {n:'Charcoal',  h:'#555555'},
  {n:'Silver',     h:'#C0C0C0'}, {n:'White',     h:'#F5F5F5'},
];

const FONTS = [
  {label:'Georgia (Classic)',    value:'Georgia'},
  {label:'Times New Roman',      value:'Times New Roman'},
  {label:'Palatino (Elegant)',   value:'Palatino'},
  {label:'Garamond',             value:'Garamond'},
  {label:'Arial (Clean)',        value:'Arial'},
  {label:'Verdana',              value:'Verdana'},
  {label:'Trebuchet MS',         value:'Trebuchet MS'},
  {label:'Courier New (Mono)',   value:'Courier New'},
];

const EMOJI_GROUPS = {
  'Nature':  ['🌸','🌺','🌻','🌹','🍀','🌿','🌲','🌊','🌙','☀️','⭐','🌈'],
  'Animals': ['🦋','🐝','🐾','🦄','🐶','🦊','🐣','🦚','🦜','🐠','🦋','🌸'],
  'Objects': ['❤️','✨','🎀','💎','🏆','🎵','🎸','🎯','🎨','🧵','✂️','🪡'],
};

// ─── Canvas Helpers ─────────────────────────────────────────────────────────

function makeCanvas(el, mode = 'fill') {
  const pad = 28;
  const tmp = document.createElement('canvas');
  tmp.width = 4; tmp.height = 4;
  const tc = tmp.getContext('2d');
  tc.font = `bold ${el.fontSize}px "${el.font}"`;
  const m = tc.measureText(el.content);
  const w = Math.max(4, Math.ceil(m.width) + pad * 2);
  const h = Math.max(4, Math.ceil(el.fontSize * 1.6) + pad * 2);

  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  const ctx = c.getContext('2d');
  ctx.font = `bold ${el.fontSize}px "${el.font}"`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  if (mode === 'outline') {
    ctx.strokeStyle = '#000';
    ctx.lineWidth = Math.max(3, el.fontSize / 10);
    ctx.strokeText(el.content, w / 2, h / 2);
  } else {
    ctx.fillStyle = '#000';
    ctx.fillText(el.content, w / 2, h / 2);
  }
  return { canvas: c, ox: el.x - w / 2, oy: el.y - h / 2 };
}

function fillStitches(el) {
  const { canvas, ox, oy } = makeCanvas(el, 'fill');
  const { width: w, height: h } = canvas;
  const data = canvas.getContext('2d').getImageData(0, 0, w, h).data;
  const pts = [];
  let dir = 1;

  for (let row = 0; row < h; row += ROW_PX) {
    const rp = [];
    let start = -1;
    for (let col = 0; col <= w; col++) {
      const filled = col < w && data[(row * w + col) * 4 + 3] > 80;
      if (filled && start < 0) start = col;
      if (!filled && start >= 0) {
        for (let x = start; x <= col - 1; x += STITCH_PX)
          rp.push({ x: ox + x, y: oy + row });
        rp.push({ x: ox + col - 1, y: oy + row });
        start = -1;
      }
    }
    if (rp.length) { if (dir < 0) rp.reverse(); pts.push(...rp); dir *= -1; }
  }
  return pts;
}

function outlineStitches(el) {
  const { canvas, ox, oy } = makeCanvas(el, 'outline');
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

// ─── JEF Color Palette (Janome thread codes 1–78) ───────────────────────────
const JEF_PALETTE = [
  [1,0,0,0],[2,0,0,0],[3,255,255,255],[4,255,255,23],[5,250,160,96],
  [6,92,118,73],[7,64,192,48],[8,101,194,200],[9,172,128,190],[10,245,188,203],
  [11,255,0,0],[12,192,128,0],[13,0,0,240],[14,228,195,93],[15,165,42,42],
  [16,213,176,212],[17,252,242,148],[18,240,208,192],[19,255,192,0],[20,201,164,128],
  [21,155,61,75],[22,160,184,204],[23,127,194,28],[24,229,197,202],[25,77,65,107],
  [26,0,0,0],[27,238,146,148],[28,167,79,47],[29,255,249,227],[30,0,73,134],
  [31,172,98,166],[32,173,183,151],[33,0,0,0],[34,65,130,153],[35,0,0,0],
  [36,14,8,100],[37,0,0,0],[38,140,198,211],[39,225,196,132],[40,255,123,178],
  [41,0,0,0],[42,255,0,0],[43,209,92,0],[44,0,128,0],[45,113,81,56],
  [46,240,220,80],[47,255,127,80],[48,255,255,23],[49,0,128,192],[50,0,0,128],
  [51,204,0,255],[52,255,128,200],[53,0,128,0],[54,255,165,65],[55,128,48,48],
  [56,0,35,85],[57,192,255,255],[58,138,174,128],[59,250,210,170],[60,127,127,127],
  [61,64,0,96],[62,255,64,64],[63,0,180,0],[64,255,200,0],[65,240,128,32],
  [66,176,24,112],[67,120,140,160],[68,96,96,48],[69,32,32,32],[70,228,196,148],
  [71,255,80,128],[72,0,200,200],[73,220,90,230],[74,128,128,0],[75,48,48,48],
  [76,240,230,210],[77,200,180,150],[78,64,104,64],
];

function hexToJefColor(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  let best = 1, bestD = Infinity;
  for (const [code, pr, pg, pb] of JEF_PALETTE) {
    const d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2;
    if (d < bestD) { bestD = d; best = code; }
  }
  return best;
}

// ─── JEF Binary Encoder ─────────────────────────────────────────────────────
// Janome JEF format: header(116) + thread-colors + thread-types + stitch-data
//   Normal stitch:   [dx_signed, dy_signed]  (range ±127, units = 0.1mm)
//   Jump/move:       [0x80, 0x02, dx, dy]
//   Color change:    [0x80, 0x01]
//   End of file:     [0x80, 0x10]

function encodeJEF(groups) {
  const threadCount = groups.length;
  const headerSize = 116;
  const colorListSize = threadCount * 4;
  const typeListSize = threadCount * 4;
  const stitchOffset = headerSize + colorListSize + typeListSize;

  // ── Build stitch data and track extents ──
  const sd = [];
  let cx = 0, cy = 0, stitchCount = 0;
  let minX = 0, minY = 0, maxX = 0, maxY = 0;

  const emit = (dx, dy, jump) => {
    while (Math.abs(dx) > 0 || Math.abs(dy) > 0) {
      const sx = Math.sign(dx) * Math.min(Math.abs(dx), 127);
      const sy = Math.sign(dy) * Math.min(Math.abs(dy), 127);
      if (!sx && !sy) break;
      if (jump) { sd.push(0x80, 0x02); }
      sd.push(sx < 0 ? sx + 256 : sx, sy < 0 ? sy + 256 : sy);
      dx -= sx; dy -= sy;
      stitchCount++;
    }
  };

  for (let g = 0; g < groups.length; g++) {
    if (g > 0) sd.push(0x80, 0x01); // color change
    for (let i = 0; i < groups[g].stitches.length; i++) {
      const { x, y } = groups[g].stitches[i];
      const ex = Math.round((x - HOOP_PX / 2) * PX2JEF);
      const ey = -Math.round((y - HOOP_PX / 2) * PX2JEF);
      if (ex < minX) minX = ex; if (ex > maxX) maxX = ex;
      if (ey < minY) minY = ey; if (ey > maxY) maxY = ey;
      const dx = ex - cx, dy = ey - cy;
      emit(dx, dy, i === 0 || Math.hypot(dx, dy) > 40);
      cx = ex; cy = ey;
    }
  }
  sd.push(0x80, 0x10); // end

  // ── Assemble file ──
  const totalSize = stitchOffset + sd.length;
  const buf = new ArrayBuffer(totalSize);
  const view = new DataView(buf);
  const bytes = new Uint8Array(buf);

  // Header
  view.setUint32(0, stitchOffset, true);  // stitch data offset
  view.setUint32(4, 0x14, true);          // flags

  const now = new Date();
  const ds = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}`;
  const ts = `${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}00`;
  for (let i = 0; i < 8; i++) bytes[8 + i] = ds.charCodeAt(i);
  for (let i = 0; i < 8; i++) bytes[16 + i] = ts.charCodeAt(i);

  view.setUint32(24, threadCount, true);
  view.setUint32(28, stitchCount, true);
  view.setUint32(32, 0, true);            // hoop code 0 = Standard A (126×110mm)

  // Extents for hoop 0
  view.setInt32(36, minX, true);
  view.setInt32(40, minY, true);
  view.setInt32(44, maxX, true);
  view.setInt32(48, maxY, true);
  // Hoops 1–4 unused
  for (let h = 1; h < 5; h++) {
    const off = 36 + h * 16;
    view.setInt32(off, -1, true); view.setInt32(off + 4, -1, true);
    view.setInt32(off + 8, -1, true); view.setInt32(off + 12, -1, true);
  }

  // Thread color list
  for (let i = 0; i < threadCount; i++)
    view.setInt32(headerSize + i * 4, hexToJefColor(groups[i].color), true);

  // Thread type list (13 = normal thread)
  for (let i = 0; i < threadCount; i++)
    view.setInt32(headerSize + colorListSize + i * 4, 13, true);

  // Stitch data
  bytes.set(sd, stitchOffset);

  return bytes;
}

// ─── Component ───────────────────────────────────────────────────────────────
let uid = 10;

export default function QuiltLabelMaker() {
  const [els, setEls] = useState([
    { id: 1, type: 'text', content: 'Made with Love', x: 250, y: 200, fontSize: 48, font: 'Georgia', color: '#A61C00', stitchType: 'fill' },
    { id: 2, type: 'text', content: 'by Mom · 2026', x: 250, y: 280, fontSize: 34, font: 'Palatino', color: '#6B3520', stitchType: 'fill' },
    { id: 3, type: 'emoji', content: '❤️', x: 250, y: 360, fontSize: 42, font: 'serif', color: '#D44070', stitchType: 'fill' },
  ]);
  const [sel, setSel]     = useState(1);
  const [textIn, setTI]   = useState('');
  const [nFont, setNF]    = useState('Georgia');
  const [nSize, setNS]    = useState(70);
  const [nColor, setNC]   = useState('#A61C00');
  const [mode, setMode]   = useState('design'); // 'design' | 'stitch'
  const [sGroups, setSG]  = useState([]);
  const [drag, setDrag]   = useState(null);
  const [emojiTab, setET] = useState('Nature');
  const cvs = useRef(null);

  const selEl = els.find(e => e.id === sel);
  const totalSt = sGroups.reduce((s, g) => s + g.stitches.length, 0);

  // ── Draw ──
  useEffect(() => {
    const canvas = cvs.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = HOOP_PX, H = HOOP_PX;
    ctx.clearRect(0, 0, W, H);

    // Fabric
    const bg = ctx.createRadialGradient(W / 2, H / 2, 0, W / 2, H / 2, W / 2);
    bg.addColorStop(0, '#FBF7F0'); bg.addColorStop(0.6, '#F5EDE0'); bg.addColorStop(1, '#EDE3D0');
    ctx.fillStyle = bg;
    ctx.beginPath(); ctx.arc(W / 2, H / 2, W / 2 - 14, 0, Math.PI * 2); ctx.fill();

    // Linen weave dots
    ctx.fillStyle = 'rgba(140,115,80,.08)';
    for (let x = 12; x < W; x += 12) for (let y = 12; y < H; y += 12) {
      const dx = x - W / 2, dy = y - H / 2;
      if (dx * dx + dy * dy < (W / 2 - 20) ** 2) {
        ctx.beginPath(); ctx.arc(x, y, 0.7, 0, Math.PI * 2); ctx.fill();
      }
    }

    // Hoop ring (woodgrain)
    for (let i = 0; i < 3; i++) {
      const rg = ctx.createLinearGradient(40, 40, W - 40, H - 40);
      rg.addColorStop(0, i === 0 ? '#D4962A' : i === 1 ? '#C07818' : '#E0AA3A');
      rg.addColorStop(0.3, '#9A6010'); rg.addColorStop(0.7, '#B87820'); rg.addColorStop(1, '#D4962A');
      ctx.strokeStyle = rg;
      ctx.lineWidth = 6;
      ctx.beginPath(); ctx.arc(W / 2, H / 2, W / 2 - 7 - i * 3, 0, Math.PI * 2); ctx.stroke();
    }
    // Inner shadow
    ctx.strokeStyle = 'rgba(0,0,0,.12)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(W / 2, H / 2, W / 2 - 22, 0, Math.PI * 2); ctx.stroke();

    // Clip to hoop interior
    ctx.save();
    ctx.beginPath(); ctx.arc(W / 2, H / 2, W / 2 - 24, 0, Math.PI * 2); ctx.clip();

    if (mode === 'stitch' && sGroups.length) {
      for (const grp of sGroups) {
        const st = grp.stitches;
        ctx.strokeStyle = grp.color; ctx.lineWidth = 1.3;
        ctx.beginPath();
        for (let i = 0; i < st.length; i++) {
          if (i === 0) { ctx.moveTo(st[i].x, st[i].y); continue; }
          Math.hypot(st[i].x - st[i - 1].x, st[i].y - st[i - 1].y) > 22
            ? (ctx.stroke(), ctx.beginPath(), ctx.moveTo(st[i].x, st[i].y))
            : ctx.lineTo(st[i].x, st[i].y);
        }
        ctx.stroke();
        ctx.fillStyle = grp.color;
        for (const s of st) { ctx.beginPath(); ctx.arc(s.x, s.y, 1.4, 0, Math.PI * 2); ctx.fill(); }
      }
    } else {
      for (const el of els) {
        ctx.save();
        ctx.font = `bold ${el.fontSize}px "${el.font}"`;
        ctx.fillStyle = el.color;
        ctx.textAlign = 'center'; ctx.textBaseline = 'middle';

        // Thread shadow
        ctx.shadowColor = 'rgba(0,0,0,.22)';
        ctx.shadowBlur = 3; ctx.shadowOffsetX = 1; ctx.shadowOffsetY = 2;
        ctx.fillText(el.content, el.x, el.y);
        ctx.shadowBlur = 0; ctx.shadowOffsetX = 0; ctx.shadowOffsetY = 0;

        if (el.id === sel) {
          const mw = ctx.measureText(el.content).width;
          const bw = mw + 20, bh = el.fontSize + 16;
          ctx.strokeStyle = 'rgba(255,255,255,.7)'; ctx.lineWidth = 2; ctx.setLineDash([5, 4]);
          ctx.strokeRect(el.x - bw / 2, el.y - bh / 2, bw, bh); ctx.setLineDash([]);
          ctx.strokeStyle = 'rgba(60,130,255,.9)'; ctx.lineWidth = 1.5; ctx.setLineDash([5, 4]);
          ctx.strokeRect(el.x - bw / 2 + 1, el.y - bh / 2 + 1, bw - 2, bh - 2); ctx.setLineDash([]);
          ctx.fillStyle = '#4A90FF';
          [[el.x - bw / 2, el.y - bh / 2], [el.x + bw / 2, el.y - bh / 2],
           [el.x - bw / 2, el.y + bh / 2], [el.x + bw / 2, el.y + bh / 2]].forEach(([px, py]) => {
            ctx.beginPath(); ctx.arc(px, py, 4.5, 0, Math.PI * 2); ctx.fill();
          });
        }
        ctx.restore();
      }
    }
    ctx.restore();
  }, [els, sel, mode, sGroups]);

  // ── Stitch Generation ──
  const genStitches = useCallback(() => {
    const g = els.map(el => ({
      color: el.color,
      stitches: (el.stitchType === 'outline' && el.type !== 'emoji') ? outlineStitches(el) : fillStitches(el)
    })).filter(g => g.stitches.length);
    setSG(g); return g;
  }, [els]);

  const togglePreview = () => { if (mode !== 'stitch') { genStitches(); setMode('stitch'); } else setMode('design'); };

  const doExport = () => {
    const g = genStitches();
    const bytes = encodeJEF(g);
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([bytes], { type: 'application/octet-stream' }));
    a.download = 'quilt-label.jef'; a.click(); URL.revokeObjectURL(a.href);
  };

  // ── CRUD ──
  const addText = () => {
    if (!textIn.trim()) return;
    const el = { id: uid++, type: 'text', content: textIn, x: 250, y: 250, fontSize: nSize, font: nFont, color: nColor, stitchType: 'fill' };
    setEls(p => [...p, el]); setSel(el.id); setTI(''); setMode('design');
  };
  const addEmoji = em => {
    const el = { id: uid++, type: 'emoji', content: em, x: 250, y: 250, fontSize: 58, font: 'serif', color: nColor, stitchType: 'fill' };
    setEls(p => [...p, el]); setSel(el.id); setMode('design');
  };
  const upd = (id, props) => { setEls(p => p.map(e => e.id === id ? { ...e, ...props } : e)); setMode('design'); };
  const del = id => { setEls(p => p.filter(e => e.id !== id)); setSel(null); setMode('design'); };

  // ── Mouse ──
  const toHoop = e => {
    const r = cvs.current.getBoundingClientRect();
    return { x: (e.clientX - r.left) * (HOOP_PX / r.width), y: (e.clientY - r.top) * (HOOP_PX / r.height) };
  };
  const hitEl = ({ x, y }) => {
    const ctx = cvs.current.getContext('2d');
    for (let i = els.length - 1; i >= 0; i--) {
      const el = els[i]; ctx.font = `bold ${el.fontSize}px "${el.font}"`;
      const hw = ctx.measureText(el.content).width / 2 + 12, hh = el.fontSize / 2 + 10;
      if (Math.abs(x - el.x) <= hw && Math.abs(y - el.y) <= hh) return el;
    }
    return null;
  };
  const onDown = e => { const p = toHoop(e); const h = hitEl(p); if (h) { setSel(h.id); setDrag({ id: h.id, ox: p.x - h.x, oy: p.y - h.y }); } else setSel(null); };
  const onMove = e => { if (!drag) return; const p = toHoop(e); upd(drag.id, { x: p.x - drag.ox, y: p.y - drag.oy }); };
  const onUp = () => setDrag(null);

  // ── Styles ──
  const c = {
    wrap: { display: 'flex', flexDirection: 'column', height: '100vh', fontFamily: '"Iowan Old Style", Georgia, serif', background: '#1A1410', color: '#E8E0D4', overflow: 'hidden' },
    bar: { display: 'flex', alignItems: 'center', padding: '10px 20px', background: '#110E0B', borderBottom: '1px solid #2E2820', gap: 12, flexShrink: 0 },
    body: { display: 'flex', flex: 1, overflow: 'hidden' },
    side: { width: 270, background: '#110E0B', borderRight: '1px solid #2E2820', overflowY: 'auto', padding: '14px 16px', flexShrink: 0, scrollbarWidth: 'thin' },
    main: { flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0D0B08', padding: 20 },
    inp: { width: '100%', padding: '7px 10px', background: '#1A1410', border: '1px solid #3A3020', borderRadius: 6, color: '#E8E0D4', fontSize: 13, marginBottom: 8, boxSizing: 'border-box', fontFamily: 'inherit', outline: 'none' },
    sec: { padding: '8px 14px', background: '#1E1C18', border: '1px solid #3A3020', borderRadius: 6, color: '#C8A060', cursor: 'pointer', fontSize: 13, fontFamily: 'inherit' },
    pri: { padding: '9px 20px', background: '#7A1A10', border: 'none', borderRadius: 6, color: '#F8E8D8', cursor: 'pointer', fontWeight: 700, fontSize: 13, letterSpacing: '.3px', fontFamily: 'inherit' },
    lbl: { fontSize: 9, fontWeight: 700, color: '#5A4830', letterSpacing: 2, textTransform: 'uppercase', marginBottom: 9, marginTop: 4, display: 'block' },
    card: { background: '#1A1410', border: '1px solid #2E2820', borderRadius: 8, padding: 12, marginBottom: 14 },
    tab: (active) => ({ padding: '4px 10px', borderRadius: 4, border: 'none', background: active ? '#3A2E1E' : 'transparent', color: active ? '#C8A060' : '#6A5840', cursor: 'pointer', fontSize: 12, fontFamily: 'inherit' }),
  };

  return (
    <div style={c.wrap}>
      {/* ── Top bar ── */}
      <div style={c.bar}>
        <span style={{ fontSize: 16, fontWeight: 700, letterSpacing: .3, color: '#D4A060' }}>🧵 Quilt Label Maker</span>
        <span style={{ fontSize: 11, color: '#3A3020', fontStyle: 'italic' }}>Janome JEF</span>
        <span style={{ flex: 1 }} />
        {mode === 'stitch' && <span style={{ fontSize: 11, color: '#5A4830' }}>{totalSt.toLocaleString()} stitches · {sGroups.length} color{sGroups.length !== 1 ? 's' : ''}</span>}
        <button onClick={togglePreview} style={c.sec}>{mode === 'stitch' ? '🎨 Design' : '🧵 Stitch Preview'}</button>
        <button onClick={doExport} style={c.pri}>⬇ Export .JEF</button>
      </div>

      <div style={c.body}>
        {/* ── Sidebar ── */}
        <div style={c.side}>

          {/* Add Text */}
          <span style={c.lbl}>Add Label Text</span>
          <input value={textIn} onChange={e => setTI(e.target.value)} onKeyDown={e => e.key === 'Enter' && addText()}
            placeholder="Made with Love, name, date…" style={c.inp} />
          <select value={nFont} onChange={e => setNF(e.target.value)} style={c.inp}>
            {FONTS.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
          </select>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
            <span style={{ fontSize: 11, color: '#6A5840', flexShrink: 0, minWidth: 54 }}>Size {nSize}</span>
            <input type="range" min="18" max="140" value={nSize} onChange={e => setNS(+e.target.value)} style={{ flex: 1, accentColor: '#C8A060' }} />
          </div>
          <button onClick={addText} style={{ ...c.pri, width: '100%', marginBottom: 18 }}>+ Add Text</button>

          {/* Emojis */}
          <span style={c.lbl}>Embellishments</span>
          <div style={{ display: 'flex', gap: 4, marginBottom: 8 }}>
            {Object.keys(EMOJI_GROUPS).map(t => <button key={t} onClick={() => setET(t)} style={c.tab(emojiTab === t)}>{t}</button>)}
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 18 }}>
            {EMOJI_GROUPS[emojiTab].map(em => (
              <button key={em} onClick={() => addEmoji(em)}
                style={{ fontSize: 22, background: '#1A1410', border: '1px solid #2E2820', borderRadius: 6, cursor: 'pointer', padding: '4px 6px', lineHeight: 1.1, transition: 'border-color .15s' }}
                onMouseEnter={e => e.target.style.borderColor = '#C8A060'}
                onMouseLeave={e => e.target.style.borderColor = '#2E2820'}>
                {em}
              </button>
            ))}
          </div>

          {/* Thread Colors */}
          <span style={c.lbl}>Thread Color</span>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 18 }}>
            {THREAD_COLORS.map(col => (
              <div key={col.h} title={col.n} onClick={() => { setNC(col.h); if (selEl) upd(selEl.id, { color: col.h }); }}
                style={{ width: 21, height: 21, borderRadius: '50%', background: col.h, cursor: 'pointer', boxSizing: 'border-box',
                  border: nColor === col.h ? '2px solid #D4A060' : '2px solid transparent',
                  outline: col.h === '#F5F5F5' ? '1px solid #3A3020' : 'none',
                  boxShadow: nColor === col.h ? '0 0 0 1px #D4A060' : 'none' }} />
            ))}
          </div>

          {/* Selected element */}
          {selEl && <>
            <span style={c.lbl}>Selected — {selEl.content}</span>
            <div style={c.card}>
              <label style={{ fontSize: 11, color: '#6A5840', display: 'block', marginBottom: 4 }}>Content</label>
              <input value={selEl.content} onChange={e => upd(selEl.id, { content: e.target.value })} style={c.inp} />
              <label style={{ fontSize: 11, color: '#6A5840', display: 'block', marginBottom: 4 }}>Font</label>
              <select value={selEl.font} onChange={e => upd(selEl.id, { font: e.target.value })} style={c.inp}>
                {FONTS.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
              </select>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <span style={{ fontSize: 11, color: '#6A5840', flexShrink: 0, minWidth: 54 }}>Size {selEl.fontSize}</span>
                <input type="range" min="18" max="160" value={selEl.fontSize}
                  onChange={e => upd(selEl.id, { fontSize: +e.target.value })} style={{ flex: 1, accentColor: '#C8A060' }} />
              </div>
              <label style={{ fontSize: 11, color: '#6A5840', display: 'block', marginBottom: 4 }}>Stitch Type</label>
              <select value={selEl.stitchType} onChange={e => upd(selEl.id, { stitchType: e.target.value })} style={c.inp}>
                <option value="fill">Fill Stitch (solid area)</option>
                <option value="outline">Running Stitch (outline)</option>
              </select>
              <button onClick={() => del(selEl.id)}
                style={{ width: '100%', padding: '7px', background: '#2E1010', border: '1px solid #4A2020', borderRadius: 6, color: '#D08080', cursor: 'pointer', fontSize: 12, fontFamily: 'inherit' }}>
                🗑 Remove
              </button>
            </div>
          </>}

          {/* Layers */}
          {els.length > 0 && <>
            <span style={c.lbl}>Layers ({els.length})</span>
            {[...els].reverse().map(el => (
              <div key={el.id} onClick={() => setSel(el.id)}
                style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '7px 9px', borderRadius: 6, cursor: 'pointer', marginBottom: 3,
                  background: el.id === sel ? '#241E14' : 'transparent', border: el.id === sel ? '1px solid #3A2E18' : '1px solid transparent' }}>
                <div style={{ width: 11, height: 11, borderRadius: '50%', background: el.color, flexShrink: 0, border: '1px solid rgba(255,255,255,.1)' }} />
                <span style={{ flex: 1, fontSize: 13, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{el.content}</span>
                <span style={{ fontSize: 10, color: '#4A3820' }}>{el.stitchType === 'fill' ? 'Fill' : 'Run'}</span>
              </div>
            ))}
          </>}
        </div>

        {/* ── Canvas ── */}
        <div style={c.main}>
          <div style={{ position: 'relative', display: 'inline-block' }}>
            <canvas ref={cvs} width={HOOP_PX} height={HOOP_PX}
              onMouseDown={onDown} onMouseMove={onMove} onMouseUp={onUp} onMouseLeave={onUp}
              style={{ display: 'block', width: 'min(470px, calc(100vw - 300px))', height: 'min(470px, calc(100vw - 300px))',
                borderRadius: '50%', cursor: drag ? 'grabbing' : 'grab',
                boxShadow: '0 0 80px rgba(200,160,80,.12), 0 24px 60px rgba(0,0,0,.65)' }} />
            <div style={{ textAlign: 'center', marginTop: 12, fontSize: 11, color: '#3A3020', letterSpacing: .5 }}>
              {mode === 'stitch'
                ? `${totalSt.toLocaleString()} stitches · ${sGroups.length} color${sGroups.length !== 1 ? 's' : ''} · 100 × 100 mm`
                : '100 × 100 mm hoop  ·  drag to reposition  ·  click to select'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
