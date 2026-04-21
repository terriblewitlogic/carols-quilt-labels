import { useState, useCallback } from 'react';
import { IMAGE_HOOPS, DEFAULT_IMAGE_HOOP } from './hoops.js';
import { generateImage, convertToStitches, downloadBase64, saveToLibrary } from './api-client.js';
import { CATEGORIES, CATALOG } from './library-catalog.js';

// ─── Styles ──────────────────────────────────────────────────────────────────
const s = {
  wrap: {
    display: 'flex', flexDirection: 'column', height: '100vh',
    fontFamily: '"Iowan Old Style", Georgia, serif',
    background: '#1A1410', color: '#E8E0D4', overflow: 'hidden',
  },
  topBar: {
    display: 'flex', alignItems: 'center', padding: '0 16px', height: 46,
    background: '#110E0B', borderBottom: '1px solid #2E2820', gap: 10, flexShrink: 0,
  },
  body: { display: 'flex', flex: 1, overflow: 'hidden', minHeight: 0 },

  // Left sidebar — controls
  sidebar: {
    width: 256, background: '#110E0B', borderRight: '1px solid #2E2820',
    display: 'flex', flexDirection: 'column', flexShrink: 0, overflowY: 'auto',
    scrollbarWidth: 'thin',
  },
  sectionHead: {
    fontSize: 10, letterSpacing: '0.14em', textTransform: 'uppercase',
    color: '#6B5D50', padding: '12px 14px 6px', borderBottom: '1px solid #1E1A16',
  },
  section: { padding: '10px 14px', borderBottom: '1px solid #1E1A16' },

  label: { fontSize: 11, color: '#9A8A78', display: 'block', marginBottom: 4 },
  inp: {
    width: '100%', background: '#1C1712', border: '1px solid #2E2820',
    color: '#E8E0D4', borderRadius: 4, padding: '6px 8px', fontSize: 12,
    outline: 'none', boxSizing: 'border-box',
  },
  textarea: {
    width: '100%', background: '#1C1712', border: '1px solid #2E2820',
    color: '#E8E0D4', borderRadius: 4, padding: '6px 8px', fontSize: 12,
    outline: 'none', boxSizing: 'border-box', resize: 'vertical', minHeight: 72,
    fontFamily: 'inherit',
  },
  row: { display: 'flex', gap: 8, alignItems: 'center', marginBottom: 6 },
  rowLabel: { fontSize: 11, color: '#9A8A78', flex: 1 },
  smallInp: {
    width: 64, background: '#1C1712', border: '1px solid #2E2820',
    color: '#E8E0D4', borderRadius: 4, padding: '4px 6px', fontSize: 12,
    outline: 'none', textAlign: 'right',
  },
  slider: { flex: 1, accentColor: '#D4A060' },
  select: {
    width: '100%', background: '#1C1712', border: '1px solid #2E2820',
    color: '#E8E0D4', borderRadius: 4, padding: '5px 8px', fontSize: 12,
    outline: 'none',
  },

  // Buttons
  btn: {
    width: '100%', padding: '8px 0', borderRadius: 5, fontSize: 13, fontWeight: 600,
    cursor: 'pointer', border: 'none', letterSpacing: '0.02em',
  },
  btnPrimary: { background: '#D4A060', color: '#110E0B' },
  btnSecondary: { background: '#2E2820', color: '#E8E0D4' },
  btnDisabled: { background: '#1C1712', color: '#3A3028', cursor: 'not-allowed' },

  // Main canvas area
  canvas: {
    flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center',
    justifyContent: 'center', overflow: 'auto', padding: 24, gap: 20,
  },
  imageBox: {
    background: '#110E0B', border: '1px solid #2E2820', borderRadius: 8,
    overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center',
    maxWidth: 480, maxHeight: 480,
  },
  previewBox: {
    background: '#110E0B', border: '1px solid #2E2820', borderRadius: 8,
    overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center',
    maxWidth: 480, maxHeight: 480,
  },
  placeholder: {
    width: 320, height: 320, display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center', gap: 12,
    color: '#3A3028', fontSize: 13,
  },
  statusBar: {
    padding: '6px 16px', background: '#110E0B', borderTop: '1px solid #2E2820',
    fontSize: 11, color: '#6B5D50', flexShrink: 0, display: 'flex', gap: 16,
  },
  error: {
    margin: '8px 0 0', padding: '6px 8px', background: '#2A1212', border: '1px solid #5A2020',
    borderRadius: 4, fontSize: 11, color: '#C07070',
  },
};

const FABRIC_PRESETS = [
  { label: 'Natural linen', color: '#f5f0eb' },
  { label: 'White',         color: '#ffffff' },
  { label: 'Cream',         color: '#fdf8ee' },
  { label: 'Black',         color: '#111111' },
  { label: 'Navy',          color: '#1a2540' },
  { label: 'Red',           color: '#7a1818' },
  { label: 'Sage',          color: '#8a9e82' },
];

/** Swap the SVG background colour without re-fetching from the server. */
function injectFabricColor(svg, color) {
  return svg.replace(/background:[^"']+/, `background:${color}`);
}

const EMBROIDERY_PROMPT_SUFFIX =
  ', bold vector sticker art style, flat colors, thick black outlines, no gradients, white background, 4 to 6 distinct colors, clean simple shapes';

const STITCH_SPEED_SPM = 400; // stitches per minute (typical home machine)

export default function ImageEmbroidery({ onBack }) {
  // ── Generation state
  const [prompt, setPrompt] = useState('');
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState(null);
  const [generatedImage, setGeneratedImage] = useState(null); // base64 PNG

  // ── Conversion settings
  const [hoopKey, setHoopKey] = useState(DEFAULT_IMAGE_HOOP);
  const [numColors, setNumColors] = useState(4);
  const [densityMm, setDensityMm] = useState(0.4);
  const [fillAngle, setFillAngle] = useState(null); // null = auto PCA per region
  const [minFeatureMm, setMinFeatureMm] = useState(1.5);
  const [outline, setOutline] = useState('running');
  const [outlineWidthMm, setOutlineWidthMm] = useState(1.0);
  const [format, setFormat] = useState('jef');
  const [threadBrand, setThreadBrand] = useState('madeira');

  // ── Preview settings
  const [fabricColor, setFabricColor] = useState('#f5f0eb');

  // ── Conversion state
  const [converting, setConverting] = useState(false);
  const [convError, setConvError] = useState(null);
  const [result, setResult] = useState(null); // { jefBase64, previewSvg, stitchCount, colors, threads }

  // ── Save to Library state
  const [saveOpen, setSaveOpen]   = useState(false);
  const [saveId, setSaveId]       = useState('');
  const [saveName, setSaveName]   = useState('');
  const [saveCat, setSaveCat]     = useState('florals');
  const [saveDesc, setSaveDesc]   = useState('');
  const [saveCatalogKey, setSaveCatalogKey] = useState(''); // '' = custom
  const [saving, setSaving]       = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const hoop = IMAGE_HOOPS[hoopKey];

  // ── Handlers
  const handleGenerate = useCallback(async () => {
    if (!prompt.trim()) return;
    setGenerating(true);
    setGenError(null);
    setResult(null);
    try {
      const fullPrompt = prompt.trim() + EMBROIDERY_PROMPT_SUFFIX;
      const data = await generateImage(fullPrompt);
      setGeneratedImage(data.imageBase64);
    } catch (e) {
      setGenError(e.message);
    } finally {
      setGenerating(false);
    }
  }, [prompt]);

  const handleConvert = useCallback(async () => {
    if (!generatedImage) return;
    setConverting(true);
    setConvError(null);
    try {
      const data = await convertToStitches(generatedImage, {
        hoop_w_mm: hoop.w,
        hoop_h_mm: hoop.h,
        num_colors: numColors,
        density_mm: densityMm,
        fill_angle_deg: fillAngle,  // null → server uses auto PCA
        min_feature_mm: minFeatureMm,
        outline,
        outline_width_mm: outlineWidthMm,
        format,
        thread_brand: threadBrand,
      });
      setResult(data);
    } catch (e) {
      setConvError(e.message);
    } finally {
      setConverting(false);
    }
  }, [generatedImage, hoop, numColors, densityMm, fillAngle, minFeatureMm, outline, outlineWidthMm, format]);

  const handleDownload = useCallback(() => {
    if (!result?.jefBase64) return;
    downloadBase64(result.jefBase64, `embroidery.${format}`);
  }, [result, format]);

  const estimatedMin = result
    ? Math.ceil((result.stitchCount / STITCH_SPEED_SPM) * 10) / 10
    : null;

  const stitchWarning = result?.stitchCount > 30000;

  // ── Save to Library helpers
  const slugify = (text) =>
    text.toLowerCase().replace(/[^a-z0-9-]/g, '-').replace(/-{2,}/g, '-').replace(/^-|-$/g, '') || 'design';

  const openSaveModal = useCallback(() => {
    setSaveError(null);
    setSaveSuccess(false);
    // Try to pre-match a catalog entry by prompt keywords
    const firstWord = prompt.trim().split(/\s+/)[0].toLowerCase();
    const match = CATALOG.find(e =>
      e.id.includes(firstWord) || e.name.toLowerCase().includes(firstWord)
    );
    if (match) {
      setSaveCatalogKey(match.id);
      setSaveId(match.id);
      setSaveName(match.name);
      setSaveCat(match.category);
      setSaveDesc(match.description);
    } else {
      setSaveCatalogKey('');
      const autoName = prompt.trim().slice(0, 40) || 'Untitled';
      setSaveName(autoName);
      setSaveId(slugify(autoName));
      setSaveCat('florals');
      setSaveDesc('');
    }
    setSaveOpen(true);
  }, [prompt]);

  const handleCatalogSelect = useCallback((catalogId) => {
    setSaveCatalogKey(catalogId);
    if (catalogId === '') {
      // Custom – keep whatever the user typed
      return;
    }
    const entry = CATALOG.find(e => e.id === catalogId);
    if (entry) {
      setSaveId(entry.id);
      setSaveName(entry.name);
      setSaveCat(entry.category);
      setSaveDesc(entry.description);
    }
  }, []);

  const handleSave = useCallback(async () => {
    if (!result || saving) return;
    setSaving(true);
    setSaveError(null);
    try {
      await saveToLibrary({
        id:           saveId,
        name:         saveName,
        category:     saveCat,
        description:  saveDesc,
        imageBase64:  generatedImage,
        previewSvg:   result.previewSvg,
        jefBase64:    result.jefBase64,
        format,
        stitchCount:  result.stitchCount,
        colors:       result.colors,
        threads:      result.threads,
      });
      setSaveSuccess(true);
    } catch (e) {
      setSaveError(e.message);
    } finally {
      setSaving(false);
    }
  }, [result, saving, saveId, saveName, saveCat, saveDesc, generatedImage, format]);

  // ── Render helpers
  const btnStyle = (disabled, primary = true) => ({
    ...s.btn,
    ...(disabled ? s.btnDisabled : primary ? s.btnPrimary : s.btnSecondary),
  });

  return (
    <div style={s.wrap}>
      {/* ─── Top Bar ─── */}
      <div style={s.topBar}>
        {onBack && (
          <button onClick={onBack} style={{ background: 'none', border: 'none', color: '#6B5D50', cursor: 'pointer', fontSize: 13, padding: '0 6px 0 0', display: 'flex', alignItems: 'center', gap: 4 }}>
            ← Back
          </button>
        )}
        <span style={{ fontSize: 15, fontWeight: 700, color: '#D4A060', letterSpacing: 0.3 }}>
          🖼️ Image Embroidery
        </span>
      </div>

      {/* ─── Body ─── */}
      <div style={s.body}>
        {/* ── Left Sidebar ── */}
        <div style={s.sidebar}>

          {/* Prompt */}
          <div style={s.sectionHead}>Image Prompt</div>
          <div style={s.section}>
            <label style={s.label}>Describe your image</label>
            <textarea
              style={s.textarea}
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              placeholder="e.g. a sunflower in a garden, a sleeping cat, a geometric pattern..."
              onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleGenerate(); }}
            />
            <div style={{ fontSize: 10, color: '#4A3E34', marginBottom: 8, lineHeight: 1.4 }}>
              Embroidery-optimized suffix is added automatically.
            </div>
            <button
              style={btnStyle(generating || !prompt.trim())}
              disabled={generating || !prompt.trim()}
              onClick={handleGenerate}
            >
              {generating ? 'Generating…' : generatedImage ? 'Regenerate Image' : 'Generate Image'}
            </button>
            {genError && <div style={s.error}>{genError}</div>}
          </div>

          {/* Hoop */}
          <div style={s.sectionHead}>Hoop Size</div>
          <div style={s.section}>
            <select style={s.select} value={hoopKey} onChange={e => setHoopKey(e.target.value)}>
              {Object.entries(IMAGE_HOOPS).map(([k, v]) => (
                <option key={k} value={k}>{v.label}</option>
              ))}
            </select>
          </div>

          {/* Color & Fill */}
          <div style={s.sectionHead}>Fill Settings</div>
          <div style={s.section}>
            <div style={s.row}>
              <span style={s.rowLabel}>Colors</span>
              <input type="range" min={2} max={6} step={1} value={numColors}
                onChange={e => setNumColors(+e.target.value)} style={s.slider} />
              <span style={{ fontSize: 12, color: '#E8E0D4', width: 20, textAlign: 'right' }}>{numColors}</span>
            </div>

            <div style={s.row}>
              <span style={s.rowLabel}>Density (mm)</span>
              <input type="range" min={0.3} max={0.8} step={0.05} value={densityMm}
                onChange={e => setDensityMm(+e.target.value)} style={s.slider} />
              <span style={{ fontSize: 12, color: '#E8E0D4', width: 32, textAlign: 'right' }}>{densityMm.toFixed(2)}</span>
            </div>

            <div style={s.row}>
              <span style={s.rowLabel}>Fill angle</span>
              <button onClick={() => setFillAngle(null)} style={{
                padding: '3px 8px', borderRadius: 4, fontSize: 11, cursor: 'pointer',
                border: `1px solid ${fillAngle === null ? '#D4A060' : '#2E2820'}`,
                background: fillAngle === null ? '#2A200E' : '#1C1712',
                color: fillAngle === null ? '#D4A060' : '#9A8A78',
                fontWeight: fillAngle === null ? 600 : 400, flexShrink: 0,
              }}>Auto</button>
              <input type="range" min={0} max={165} step={15}
                value={fillAngle ?? 45}
                onChange={e => setFillAngle(+e.target.value)} style={s.slider} />
              <span style={{ fontSize: 12, color: fillAngle === null ? '#4A3E34' : '#E8E0D4', width: 32, textAlign: 'right' }}>
                {fillAngle === null ? '—' : `${fillAngle}°`}
              </span>
            </div>

            <div style={s.row}>
              <span style={s.rowLabel}>Min feature (mm)</span>
              <input type="range" min={1.0} max={4.0} step={0.5} value={minFeatureMm}
                onChange={e => setMinFeatureMm(+e.target.value)} style={s.slider} />
              <span style={{ fontSize: 12, color: '#E8E0D4', width: 32, textAlign: 'right' }}>{minFeatureMm}</span>
            </div>
          </div>

          {/* Outlines */}
          <div style={s.sectionHead}>Outlines</div>
          <div style={s.section}>
            <div style={{ display: 'flex', gap: 6, marginBottom: 8 }}>
              {['none', 'running', 'satin'].map(opt => (
                <button key={opt} onClick={() => setOutline(opt)} style={{
                  flex: 1, padding: '5px 0', borderRadius: 4, fontSize: 11, cursor: 'pointer',
                  border: `1px solid ${outline === opt ? '#D4A060' : '#2E2820'}`,
                  background: outline === opt ? '#2A200E' : '#1C1712',
                  color: outline === opt ? '#D4A060' : '#9A8A78', fontWeight: outline === opt ? 600 : 400,
                }}>{opt}</button>
              ))}
            </div>
            {outline === 'satin' && (
              <div style={s.row}>
                <span style={s.rowLabel}>Width (mm)</span>
                <input type="range" min={0.5} max={3.0} step={0.5} value={outlineWidthMm}
                  onChange={e => setOutlineWidthMm(+e.target.value)} style={s.slider} />
                <span style={{ fontSize: 12, color: '#E8E0D4', width: 32, textAlign: 'right' }}>{outlineWidthMm}</span>
              </div>
            )}
          </div>

          {/* Fabric colour */}
          <div style={s.sectionHead}>Fabric Preview</div>
          <div style={s.section}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 8 }}>
              {FABRIC_PRESETS.map(p => (
                <button key={p.color} title={p.label} onClick={() => setFabricColor(p.color)} style={{
                  width: 22, height: 22, borderRadius: 4, cursor: 'pointer', flexShrink: 0,
                  background: p.color,
                  border: `2px solid ${fabricColor === p.color ? '#D4A060' : '#3A3028'}`,
                  padding: 0,
                }} />
              ))}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <label style={{ ...s.label, marginBottom: 0, flexShrink: 0 }}>Custom</label>
              <input type="color" value={fabricColor} onChange={e => setFabricColor(e.target.value)}
                style={{ width: 36, height: 24, padding: 0, border: '1px solid #2E2820',
                         background: 'none', cursor: 'pointer', borderRadius: 3 }} />
              <span style={{ fontSize: 11, color: '#6B5D50', fontFamily: 'monospace' }}>{fabricColor}</span>
            </div>
          </div>

          {/* Export format */}
          <div style={s.sectionHead}>Export</div>
          <div style={s.section}>
            <label style={s.label}>Thread brand</label>
            <select style={{ ...s.select, marginBottom: 10 }} value={threadBrand} onChange={e => setThreadBrand(e.target.value)}>
              <option value="madeira">Madeira Polyneon</option>
              <option value="isacord">Isacord</option>
              <option value="robison-anton">Robison-Anton</option>
            </select>

            <label style={s.label}>Format</label>
            <select style={{ ...s.select, marginBottom: 10 }} value={format} onChange={e => setFormat(e.target.value)}>
              {['jef', 'pes', 'dst', 'vp3'].map(f => (
                <option key={f} value={f}>.{f.toUpperCase()}</option>
              ))}
            </select>

            <button
              style={{ ...btnStyle(!generatedImage || converting), marginBottom: 8 }}
              disabled={!generatedImage || converting}
              onClick={handleConvert}
            >
              {converting ? 'Converting…' : 'Convert to Stitches'}
            </button>

            <button
              style={btnStyle(!result?.jefBase64, false)}
              disabled={!result?.jefBase64}
              onClick={handleDownload}
            >
              Download .{format.toUpperCase()}
            </button>
            {convError && <div style={s.error}>{convError}</div>}
          </div>

          {/* Save to Library */}
          {result?.jefBase64 && (
            <>
              <div style={s.sectionHead}>Library</div>
              <div style={s.section}>
                {saveSuccess ? (
                  <div style={{ fontSize: 11, color: '#6A9A6A', padding: '4px 0', lineHeight: 1.5 }}>
                    ✓ Saved! Commit <code style={{ fontSize: 10, background: '#1A2E1A', padding: '0 4px', borderRadius: 3 }}>public/library/</code> to git to publish.
                  </div>
                ) : (
                  <button
                    style={{ ...btnStyle(saving, false) }}
                    disabled={saving}
                    onClick={openSaveModal}
                  >
                    {saving ? 'Saving…' : '📚 Save to Library'}
                  </button>
                )}
              </div>
            </>
          )}
        </div>

        {/* ── Main Canvas ── */}
        <div style={s.canvas}>
          {!generatedImage && !generating && (
            <div style={s.placeholder}>
              <div style={{ fontSize: 48 }}>🖼️</div>
              <div>Enter a prompt and click Generate Image</div>
            </div>
          )}

          {generating && (
            <div style={s.placeholder}>
              <div style={{ fontSize: 32 }}>⏳</div>
              <div>Generating image…</div>
            </div>
          )}

          {/* Side-by-side: generated image + stitch preview */}
          {generatedImage && !generating && (
            <div style={{ display: 'flex', gap: 24, alignItems: 'flex-start', flexWrap: 'wrap', justifyContent: 'center' }}>

              {/* Generated image */}
              <div>
                <div style={{ fontSize: 11, color: '#6B5D50', marginBottom: 6, textAlign: 'center' }}>
                  Generated image
                </div>
                <div style={s.imageBox}>
                  <img
                    src={`data:image/png;base64,${generatedImage}`}
                    alt="Generated"
                    style={{ maxWidth: 380, maxHeight: 420, display: 'block' }}
                  />
                </div>
              </div>

              {/* Stitch preview or converting spinner */}
              <div>
                <div style={{ fontSize: 11, color: '#6B5D50', marginBottom: 6, textAlign: 'center' }}>
                  {converting ? 'Converting…' : result?.previewSvg ? (
                    <>
                      Stitch preview
                      {stitchWarning && (
                        <span style={{ color: '#C07A30', marginLeft: 8 }}>
                          ⚠ {result.stitchCount.toLocaleString()} stitches
                        </span>
                      )}
                    </>
                  ) : 'Stitch preview'}
                </div>
                <div style={{ ...s.previewBox, minWidth: 200, minHeight: 200 }}>
                  {converting && (
                    <div style={{ padding: 40, color: '#6B5D50', fontSize: 13, textAlign: 'center' }}>
                      <div style={{ fontSize: 28, marginBottom: 8 }}>🧵</div>
                      <div>10–30 seconds…</div>
                    </div>
                  )}
                  {result?.previewSvg && !converting && (
                    <div
                      dangerouslySetInnerHTML={{ __html: injectFabricColor(result.previewSvg, fabricColor) }}
                      style={{ maxWidth: 380, maxHeight: 420 }}
                    />
                  )}
                  {!result?.previewSvg && !converting && (
                    <div style={{ padding: 40, color: '#3A3028', fontSize: 12, textAlign: 'center' }}>
                      Click Convert to Stitches
                    </div>
                  )}
                </div>
              </div>

            </div>
          )}
        </div>
      </div>

      {/* ─── Status Bar ─── */}
      <div style={s.statusBar}>
        <span>Hoop: {hoop.w}×{hoop.h} mm</span>
        {result && (
          <>
            <span>Stitches: {result.stitchCount.toLocaleString()}</span>
            <span>~{estimatedMin} min @ 400 spm</span>
          </>
        )}
      </div>

      {/* ─── Suggestions Panel ─── */}
      {result?.suggestions?.length > 0 && (
        <div style={{ background: '#1A1208', borderTop: '1px solid #3A2810', padding: '8px 16px', flexShrink: 0 }}>
          <div style={{ fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#C07A30', marginBottom: 6 }}>
            ⚠ High Stitch Count — Tips to Reduce
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {result.suggestions.map((s, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'baseline', gap: 8, fontSize: 11 }}>
                {s.param ? (
                  <>
                    <span style={{ color: '#C07A30', flexShrink: 0 }}>→</span>
                    <span style={{ color: '#D4B090' }}>{s.text}</span>
                    <button onClick={() => {
                      if (s.param === 'density_mm') setDensityMm(s.suggested);
                      if (s.param === 'min_feature_mm') setMinFeatureMm(s.suggested);
                      if (s.param === 'num_colors') setNumColors(s.suggested);
                    }} style={{
                      fontSize: 10, padding: '2px 8px', borderRadius: 3, cursor: 'pointer',
                      background: '#2A1A08', border: '1px solid #C07A30', color: '#C07A30',
                      flexShrink: 0, whiteSpace: 'nowrap',
                    }}>Apply</button>
                  </>
                ) : (
                  <span style={{ color: '#6B5D50' }}>{s.text}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── Thread Panel ─── */}
      {result?.threads && (
        <div style={{ background: '#110E0B', borderTop: '1px solid #2E2820', padding: '8px 16px', flexShrink: 0 }}>
          <div style={{ fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#6B5D50', marginBottom: 6 }}>
            {result.threads[0]?.brand ?? 'Thread'} — Stitch Order
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 16px' }}>
            {result.threads.map((t, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11 }}>
                <span style={{ fontSize: 12, color: '#6B5D50', fontVariantNumeric: 'tabular-nums' }}>{i + 1}.</span>
                <span style={{ width: 14, height: 14, borderRadius: 3, background: t.thread_hex, border: '1px solid #3A3028', flexShrink: 0 }} />
                <span style={{ color: '#E8E0D4' }}>{t.name}</span>
                <span style={{ color: '#4A3E34' }}>#{t.code}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── Save to Library Modal ─── */}
      {saveOpen && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100,
        }} onClick={e => { if (e.target === e.currentTarget) setSaveOpen(false); }}>
          <div style={{
            background: '#110E0B', border: '1px solid #3A3028', borderRadius: 10,
            padding: '28px 28px 24px', width: 400, maxWidth: '90vw',
            display: 'flex', flexDirection: 'column', gap: 14,
            fontFamily: '"Iowan Old Style", Georgia, serif',
          }}>
            <div style={{ fontSize: 16, fontWeight: 700, color: '#D4A060' }}>📚 Save to Library</div>
            <div style={{ fontSize: 11, color: '#6B5D50', lineHeight: 1.5, marginTop: -6 }}>
              Files will be written to <code style={{ background: '#1C1712', padding: '1px 4px', borderRadius: 3 }}>public/library/{saveId || '…'}/</code>.
              Commit that folder to git to publish.
            </div>

            {/* Catalog entry picker */}
            <div>
              <label style={{ fontSize: 11, color: '#9A8A78', display: 'block', marginBottom: 4 }}>
                Match to catalog entry
              </label>
              <select
                style={s.select}
                value={saveCatalogKey}
                onChange={e => handleCatalogSelect(e.target.value)}
              >
                <option value="">— Custom —</option>
                {CATEGORIES.map(cat => (
                  <optgroup key={cat.id} label={`${cat.icon} ${cat.label}`}>
                    {CATALOG.filter(e => e.category === cat.id).map(e => (
                      <option key={e.id} value={e.id}>{e.name}</option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>

            {/* ID */}
            <div>
              <label style={{ fontSize: 11, color: '#9A8A78', display: 'block', marginBottom: 4 }}>
                ID <span style={{ color: '#4A3E34' }}>(filename-safe slug)</span>
              </label>
              <input
                style={s.inp}
                value={saveId}
                onChange={e => { setSaveId(slugify(e.target.value)); setSaveCatalogKey(''); }}
                placeholder="e.g. sunflower"
              />
            </div>

            {/* Name */}
            <div>
              <label style={{ fontSize: 11, color: '#9A8A78', display: 'block', marginBottom: 4 }}>Name</label>
              <input
                style={s.inp}
                value={saveName}
                onChange={e => setSaveName(e.target.value)}
                placeholder="e.g. Sunflower"
              />
            </div>

            {/* Category */}
            <div>
              <label style={{ fontSize: 11, color: '#9A8A78', display: 'block', marginBottom: 4 }}>Category</label>
              <select style={s.select} value={saveCat} onChange={e => setSaveCat(e.target.value)}>
                {CATEGORIES.map(c => (
                  <option key={c.id} value={c.id}>{c.icon} {c.label}</option>
                ))}
                <option value="custom">Custom</option>
              </select>
            </div>

            {/* Description */}
            <div>
              <label style={{ fontSize: 11, color: '#9A8A78', display: 'block', marginBottom: 4 }}>
                Description <span style={{ color: '#4A3E34' }}>(optional)</span>
              </label>
              <textarea
                style={{ ...s.textarea, minHeight: 52 }}
                value={saveDesc}
                onChange={e => setSaveDesc(e.target.value)}
                placeholder="Short description for the library card"
              />
            </div>

            {saveError && (
              <div style={{ ...s.error, margin: 0 }}>{saveError}</div>
            )}

            {/* Buttons */}
            <div style={{ display: 'flex', gap: 10, marginTop: 4 }}>
              <button
                style={{ ...s.btn, ...s.btnSecondary, flex: 1 }}
                onClick={() => setSaveOpen(false)}
                disabled={saving}
              >
                Cancel
              </button>
              <button
                style={{ ...s.btn, ...(saving || !saveId || !saveName ? s.btnDisabled : s.btnPrimary), flex: 2 }}
                disabled={saving || !saveId || !saveName}
                onClick={handleSave}
              >
                {saving ? 'Saving…' : 'Save to Library'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
