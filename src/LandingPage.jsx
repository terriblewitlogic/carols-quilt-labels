import { useState } from 'react';

const s = {
  page: {
    display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
    height: '100vh', background: '#1A1410', color: '#E8E0D4',
    fontFamily: '"Iowan Old Style", Georgia, serif',
  },
  logo: {
    fontSize: 13, letterSpacing: '0.18em', textTransform: 'uppercase',
    color: '#9A8A78', marginBottom: 12,
  },
  title: {
    fontSize: 32, fontWeight: 700, color: '#E8E0D4', marginBottom: 6, textAlign: 'center',
  },
  subtitle: {
    fontSize: 14, color: '#6B5D50', marginBottom: 52, textAlign: 'center',
  },
  grid: {
    display: 'flex', gap: 24,
  },
  card: {
    width: 220, padding: '32px 24px 28px', background: '#110E0B',
    border: '1px solid #2E2820', borderRadius: 10, cursor: 'pointer',
    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14,
    transition: 'border-color 0.15s, background 0.15s',
    textAlign: 'center',
  },
  cardHovered: {
    borderColor: '#7A6A5A', background: '#1C1712',
  },
  icon: { fontSize: 40, lineHeight: 1 },
  cardTitle: { fontSize: 16, fontWeight: 600, color: '#E8E0D4', letterSpacing: '0.03em' },
  cardDesc: { fontSize: 12, color: '#6B5D50', lineHeight: 1.55 },
  badge: {
    fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase',
    background: '#2E2820', color: '#9A8A78', borderRadius: 4,
    padding: '2px 8px', marginTop: 4,
  },
};

function Card({ icon, title, desc, badge, onClick }) {
  const [hovered, setHovered] = useState(false);
  return (
    <div
      style={{ ...s.card, ...(hovered ? s.cardHovered : {}) }}
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div style={s.icon}>{icon}</div>
      <div>
        <div style={s.cardTitle}>{title}</div>
        {badge && <div style={s.badge}>{badge}</div>}
      </div>
      <div style={s.cardDesc}>{desc}</div>
    </div>
  );
}

export default function LandingPage({ onSelect }) {
  return (
    <div style={s.page}>
      <div style={s.logo}>Embroidery Studio</div>
      <div style={s.title}>What are you making today?</div>
      <div style={s.subtitle}>Choose a tool to get started</div>
      <div style={s.grid}>
        <Card
          icon="🪡"
          title="Quilt Label"
          desc="Design text labels with custom fonts, borders, and decorative elements. Export to .JEF, .PES, and more."
          onClick={() => onSelect('label')}
        />
        <Card
          icon="🖼️"
          title="Image Embroidery"
          desc="Generate an image from a prompt, then convert it to filled embroidery stitches. Export to .JEF."
          badge="New"
          onClick={() => onSelect('image')}
        />
        <Card
          icon="📚"
          title="Design Library"
          desc="Browse pre-generated embroidery designs across 6 categories. Download ready-to-stitch files."
          onClick={() => onSelect('library')}
        />
      </div>
    </div>
  );
}
