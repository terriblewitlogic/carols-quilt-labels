// ─── Printable Color Chart (opens in new window) ────────────────────────────

const FORMAT_LABELS = {
  jef: 'Janome JEF',
  pes: 'Brother PES',
  dst: 'Tajima DST',
  vp3: 'Pfaff VP3',
  exp: 'Bernina EXP',
  xxx: 'Singer XXX',
  hus: 'Viking HUS',
};

export function openColorChart(groups, canvasDataUrl, hoopLabel, paletteName, format = 'jef') {
  const formatLabel   = FORMAT_LABELS[format] || format.toUpperCase();
  const totalStitches = groups.reduce((s, g) => s + g.stitches.length, 0);
  const estMinutes    = Math.ceil(totalStitches / 800);
  const hasText       = groups.some(g => g.isText);

  const rows = groups.map((g, i) => {
    const count     = g.stitches.length;
    const countStr  = g.isText
      ? `~${count.toLocaleString()} <span title="Estimated — exact count available after export" style="color:#999;font-size:11px">est.</span>`
      : count.toLocaleString();
    return `
    <tr style="background:${i % 2 === 0 ? '#fff' : '#faf8f5'}">
      <td style="text-align:center;font-weight:bold">${i + 1}</td>
      <td><div style="width:28px;height:28px;border-radius:50%;background:${g.color};border:1px solid #ccc;margin:auto"></div></td>
      <td>${g.colorName || g.color}${g.isText ? ' <em style="color:#aaa;font-size:11px">(text)</em>' : ''}</td>
      <td style="text-align:center;font-family:monospace">${g.brandCode || '—'}</td>
      <td style="text-align:right">${countStr}</td>
    </tr>
  `;
  }).join('');

  const html = `<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<title>Thread Color Chart — Carol's Quilt Labels</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: Georgia, serif; max-width: 720px; margin: 40px auto; padding: 0 20px; color: #333; }
  h1 { font-size: 22px; border-bottom: 2px solid #8B4513; padding-bottom: 10px; color: #8B4513; margin-bottom: 6px; }
  h2 { font-size: 13px; color: #999; font-weight: normal; margin: 0 0 20px; }
  .preview { text-align: center; margin: 20px 0; }
  .preview img { max-width: 320px; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.1); }
  .info { display: flex; gap: 20px; flex-wrap: wrap; margin: 16px 0 24px;
          background: #faf8f5; border: 1px solid #e8d8c0; border-radius: 8px; padding: 14px 18px; }
  .info div { font-size: 13px; }
  .info strong { color: #8B4513; display: block; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px; }
  table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }
  thead tr { background: #F5EDE0; }
  th { color: #6B3520; padding: 9px 12px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid #e0c8a8; }
  td { padding: 9px 12px; border-bottom: 1px solid #eee; vertical-align: middle; }
  .note { font-size: 12px; color: #888; margin: 4px 0 20px; font-style: italic; }
  .tips { background: #FFF8F0; border: 1px solid #E8D8C0; border-radius: 8px; padding: 16px 20px; margin: 24px 0; }
  .tips h3 { color: #8B4513; margin: 0 0 10px; font-size: 14px; }
  .tips ul { margin: 0; padding-left: 20px; font-size: 13px; line-height: 1.8; }
  .printbtn { display: block; margin: 24px auto 0; padding: 11px 36px; font-size: 15px;
              background: #8B4513; color: #fff; border: none; border-radius: 6px; cursor: pointer;
              font-family: Georgia, serif; letter-spacing: .5px; }
  @media print {
    .printbtn { display: none; }
    body { margin: 20px; }
  }
</style>
</head><body>

<h1>Carol's Quilt Labels — Thread Color Chart</h1>
<h2>Generated ${new Date().toLocaleDateString('en-US', { year:'numeric', month:'long', day:'numeric' })}</h2>

<div class="preview">
  ${canvasDataUrl ? `<img src="${canvasDataUrl}" alt="Design Preview">` : ''}
</div>

<div class="info">
  <div><strong>Hoop</strong>${hoopLabel}</div>
  <div><strong>Thread Brand</strong>${paletteName}</div>
  <div><strong>Format</strong>${formatLabel}</div>
  <div><strong>Colors</strong>${groups.length}</div>
  <div><strong>Total Stitches</strong>${totalStitches.toLocaleString()}${hasText ? '*' : ''}</div>
  <div><strong>Est. Sew Time</strong>~${estMinutes} min @ 800 spm</div>
</div>

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Color</th>
      <th>Name</th>
      <th>${paletteName} Code</th>
      <th style="text-align:right">Stitches</th>
    </tr>
  </thead>
  <tbody>${rows}</tbody>
</table>

${hasText ? '<p class="note">* Text stitch counts are estimated. Exact counts are available in the exported file.</p>' : ''}

<div class="tips">
  <h3>Stitch-Out Tips</h3>
  <ul>
    <li>Use medium-weight <strong>tear-away stabilizer</strong> for quilting cotton</li>
    <li>Use <strong>40wt polyester thread</strong> for most text; 60wt for text under 6mm</li>
    <li>Always do a <strong>test stitch-out</strong> on scrap fabric first</li>
    <li>Stitch on muslin or quilting cotton, fold edges under, hand-stitch to quilt back</li>
    <li>Press from the back with a pressing cloth to avoid flattening stitches</li>
    <li>If thread breaks: reduce speed, increase needle size, or loosen upper tension slightly</li>
  </ul>
</div>

<button class="printbtn" onclick="window.print()">🖨 Print Color Chart</button>

</body></html>`;

  const w = window.open('', '_blank');
  if (w) { w.document.write(html); w.document.close(); }
}
