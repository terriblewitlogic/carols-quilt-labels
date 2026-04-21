import { useState, useEffect } from 'react';
import { CATEGORIES, CATALOG } from './library-catalog.js';

// ─── Styles ───────────────────────────────────────────────────────────────────
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
  backBtn: {
    background: 'none', border: 'none', color: '#6B5D50', cursor: 'pointer',
    fontSize: 13, padding: '0 6px 0 0', display: 'flex', alignItems: 'center', gap: 4,
  },
  topTitle: { fontSize: 15, fontWeight: 700, color: '#D4A060', letterSpacing: 0.3 },

  // Category tabs
  tabs: {
    display: 'flex', gap: 2, padding: '10px 20px 0',
    background: '#110E0B', borderBottom: '1px solid #2E2820', flexShrink: 0, flexWrap: 'wrap',
  },
  tab: {
    padding: '7px 14px', fontSize: 12, cursor: 'pointer', border: 'none',
    borderRadius: '4px 4px 0 0', fontFamily: 'inherit', letterSpacing: '0.02em',
    transition: 'background 0.12s, color 0.12s',
  },
  tabActive: { background: '#1A1410', color: '#D4A060', fontWeight: 600 },
  tabInactive: { background: 'transparent', color: '#6B5D50' },

  // Content
  content: { flex: 1, overflowY: 'auto', padding: '24px 24px', scrollbarWidth: 'thin' },
  sectionLabel: {
    fontSize: 10, letterSpacing: '0.16em', textTransform: 'uppercase',
    color: '#4A3E34', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 10,
  },
  sectionLine: { flex: 1, height: 1, background: '#2E2820' },

  // Grid
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: 16,
  },

  // Cards
  card: {
    background: '#110E0B', border: '1px solid #2E2820', borderRadius: 8,
    overflow: 'hidden', display: 'flex', flexDirection: 'column',
    transition: 'border-color 0.15s',
  },
  cardHover: { borderColor: '#4A3E34' },
  previewBox: {
    width: '100%', aspectRatio: '1', background: '#0C0A08',
    display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden',
    position: 'relative',
  },
  cardBody: { padding: '10px 12px 12px', display: 'flex', flexDirection: 'column', gap: 6, flex: 1 },
  cardName: { fontSize: 13, fontWeight: 600, color: '#D4C4B0', lineHeight: 1.3 },
  cardDesc: { fontSize: 11, color: '#6B5D50', lineHeight: 1.45, flex: 1 },
  cardMeta: { display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' },
  badge: {
    fontSize: 9, letterSpacing: '0.1em', textTransform: 'uppercase',
    padding: '2px 6px', borderRadius: 3, fontWeight: 600,
  },
  badgeGenerated: { background: '#1A2E1A', color: '#6A9A6A' },
  badgePending: { background: '#1E1A16', color: '#4A3E34' },
  stitchCount: { fontSize: 10, color: '#4A3E34', marginLeft: 'auto' },

  downloadBtn: {
    width: '100%', padding: '7px 0', borderRadius: 4, fontSize: 11, fontWeight: 600,
    cursor: 'pointer', border: '1px solid #3A2E22', background: '#1E1810',
    color: '#D4A060', letterSpacing: '0.06em', textTransform: 'uppercase',
    marginTop: 6, transition: 'background 0.12s',
  },

  // Placeholder preview
  placeholderPreview: {
    width: '100%', height: '100%', display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center', gap: 8,
  },
  placeholderIcon: { fontSize: 32, opacity: 0.25 },
  placeholderText: { fontSize: 10, color: '#3A3028', textAlign: 'center', padding: '0 12px' },

  // Empty state
  empty: {
    display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
    padding: '60px 20px', color: '#4A3E34', gap: 12, textAlign: 'center',
  },
  emptyIcon: { fontSize: 40 },
  emptyTitle: { fontSize: 16, color: '#6B5D50', fontWeight: 600 },
  emptyDesc: { fontSize: 12, lineHeight: 1.6, maxWidth: 360 },

  // Loading
  loading: {
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    flex: 1, color: '#4A3E34', fontSize: 13, gap: 8,
  },
};

// Category icon map for placeholders
const CATEGORY_ICONS = {
  'florals':       '🌸',
  'birds-insects': '🦋',
  'animals':       '🦊',
  'botanicals':    '🍃',
  'folk-art':      '🎨',
  'geometric':     '✦',
};

function fmtStitches(n) {
  return n >= 1000 ? `${(n / 1000).toFixed(1)}k stitches` : `${n} stitches`;
}

function DesignCard({ entry, manifestEntry }) {
  const [hovered, setHovered] = useState(false);
  const [svgLoaded, setSvgLoaded] = useState(false);
  const generated = !!manifestEntry;

  const handleDownload = (e) => {
    e.stopPropagation();
    const fmt = manifestEntry?.format || 'jef';
    const link = document.createElement('a');
    link.href = `/library/${entry.id}/embroidery.${fmt}`;
    link.download = `${entry.id}.${fmt}`;
    link.click();
  };

  return (
    <div
      style={{ ...s.card, ...(hovered ? s.cardHover : {}) }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Preview */}
      <div style={s.previewBox}>
        {generated ? (
          <>
            <img
              src={`/library/${entry.id}/preview.svg`}
              alt={entry.name}
              style={{
                width: '100%', height: '100%', objectFit: 'cover',
                opacity: svgLoaded ? 1 : 0, transition: 'opacity 0.2s',
              }}
              onLoad={() => setSvgLoaded(true)}
            />
            {!svgLoaded && (
              <div style={{ ...s.placeholderPreview, position: 'absolute', inset: 0 }}>
                <div style={s.placeholderIcon}>{CATEGORY_ICONS[entry.category] || '🪡'}</div>
              </div>
            )}
          </>
        ) : (
          <div style={s.placeholderPreview}>
            <div style={s.placeholderIcon}>{CATEGORY_ICONS[entry.category] || '🪡'}</div>
            <div style={s.placeholderText}>{entry.description}</div>
          </div>
        )}
      </div>

      {/* Body */}
      <div style={s.cardBody}>
        <div style={s.cardName}>{entry.name}</div>
        {generated && manifestEntry.description && (
          <div style={s.cardDesc}>{manifestEntry.description || entry.description}</div>
        )}
        <div style={s.cardMeta}>
          <span style={{ ...s.badge, ...(generated ? s.badgeGenerated : s.badgePending) }}>
            {generated ? 'Ready' : 'Not yet generated'}
          </span>
          {generated && manifestEntry.stitchCount && (
            <span style={s.stitchCount}>{fmtStitches(manifestEntry.stitchCount)}</span>
          )}
        </div>
        {generated && (
          <button style={s.downloadBtn} onClick={handleDownload}>
            ↓ Download
          </button>
        )}
      </div>
    </div>
  );
}

export default function LibraryPage({ onBack }) {
  const [manifest, setManifest] = useState(null); // null = loading
  const [activeCategory, setActiveCategory] = useState('all');
  const [loadError, setLoadError] = useState(null);

  useEffect(() => {
    fetch('/library/manifest.json')
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(data => setManifest(Array.isArray(data) ? data : []))
      .catch(e => {
        console.warn('manifest load failed:', e);
        setManifest([]);
        setLoadError(e.message);
      });
  }, []);

  // Build fast-lookup from manifest
  const manifestById = Object.fromEntries((manifest || []).map(m => [m.id, m]));
  const generatedCount = manifest ? manifest.length : 0;

  // Filter catalog by active category
  const filteredCatalog = activeCategory === 'all'
    ? CATALOG
    : CATALOG.filter(e => e.category === activeCategory);

  // Separate into generated vs placeholder
  const generated = filteredCatalog.filter(e => manifestById[e.id]);
  const pending   = filteredCatalog.filter(e => !manifestById[e.id]);

  const tabs = [{ id: 'all', label: 'All', icon: '✦' }, ...CATEGORIES];

  return (
    <div style={s.wrap}>
      {/* ─── Top Bar ─── */}
      <div style={s.topBar}>
        {onBack && (
          <button onClick={onBack} style={s.backBtn}>← Back</button>
        )}
        <span style={s.topTitle}>📚 Design Library</span>
        {manifest !== null && (
          <span style={{ fontSize: 11, color: '#4A3E34', marginLeft: 8 }}>
            {generatedCount} of {CATALOG.length} generated
          </span>
        )}
      </div>

      {/* ─── Category Tabs ─── */}
      <div style={s.tabs}>
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveCategory(t.id)}
            style={{
              ...s.tab,
              ...(activeCategory === t.id ? s.tabActive : s.tabInactive),
            }}
          >
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* ─── Content ─── */}
      {manifest === null ? (
        <div style={s.loading}>⟳ Loading library…</div>
      ) : (
        <div style={s.content}>
          {/* Generated section */}
          {generated.length > 0 && (
            <>
              {pending.length > 0 && (
                <div style={s.sectionLabel}>
                  <span>Ready to download</span>
                  <div style={s.sectionLine} />
                </div>
              )}
              <div style={{ ...s.grid, marginBottom: pending.length > 0 ? 32 : 0 }}>
                {generated.map(entry => (
                  <DesignCard key={entry.id} entry={entry} manifestEntry={manifestById[entry.id]} />
                ))}
              </div>
            </>
          )}

          {/* Pending section */}
          {pending.length > 0 && (
            <>
              {generated.length > 0 && (
                <div style={s.sectionLabel}>
                  <span>Coming soon</span>
                  <div style={s.sectionLine} />
                </div>
              )}
              {generated.length === 0 && (
                <div style={{ ...s.empty, paddingTop: 32, paddingBottom: 24 }}>
                  <div style={s.emptyIcon}>🧵</div>
                  <div style={s.emptyTitle}>Library coming soon</div>
                  <div style={s.emptyDesc}>
                    These designs will be generated with the Image Embroidery tool
                    and added to the library. Below are the designs planned for each category.
                  </div>
                </div>
              )}
              <div style={s.grid}>
                {pending.map(entry => (
                  <DesignCard key={entry.id} entry={entry} manifestEntry={null} />
                ))}
              </div>
            </>
          )}

          {/* Fully empty */}
          {generated.length === 0 && pending.length === 0 && (
            <div style={s.empty}>
              <div style={s.emptyIcon}>🔍</div>
              <div style={s.emptyTitle}>No designs in this category</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
