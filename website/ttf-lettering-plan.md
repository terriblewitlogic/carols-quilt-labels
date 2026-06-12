# TTF Lettering — Feature Plan

**Status:** Planned (supersedes ROADMAP.md § 2A "Label Maker wiring")
**Date:** 2026-06-11
**Depends on:** `hatch-quality-2026-06` branch merged + deployed (stitch engine with text support)

---

## 1. Why now (the pivot re-opened)

The original label-maker pivot died because the old method supported only a handful of
pre-digitized fonts. That constraint no longer exists. The June 2026 stitch-quality
campaign ended with the engine satin-stitching **arbitrary TTF letterforms**:

- Any dark stroke 0.6–4.5mm wide becomes professional satin columns (medial-axis bars,
  underlay, spur-pruned skeletons, corridor-routed carries).
- Letterforms wider than satin range get satin border + serpentine interior fill
  (`stroke_blob_region`) — the classic appliqué-lettering look.
- Verified results (renders in `embroidery-stitch-backend/tmp/text_experiment/`):
  - **Block** (Arial Rounded Bold) "Sophie", 15mm cap: q100, 2,078 stitches, 62% satin.
  - **Script** (Bradley Hand) "Sophie", 15mm cap: q100, all letters legible.
  - Both fonts readable at 6mm cap height.
- The full acceptance suite held (average 96.3 Hatch-likeness) with the text fixes in —
  they were general engine improvements, not text hacks.

**The product unlock:** we render the text ourselves, so we control everything AI text
cannot guarantee — spelling, kerning, stroke-width consistency, and **anti-aliasing**
(binary rendering eliminates the quantization halo problem at the source). Any font
file on disk is a "stitch font." Thousands of free fonts become inventory.

**The margin unlock:** lettering jobs skip Gemini entirely — no per-generation AI cost.
A lettering credit is nearly pure margin versus an AI-generation credit.

---

## 2. Product surfaces

| Surface | What it is | Phase |
|---|---|---|
| **Label Maker page** (exists, stubbed) | Name/quilt labels: text + optional frame, sized to hoop | L1 |
| Lettering in Generator | "Add text" layer over generated artwork | L2 |
| Monogram tool | 1–3 letters + decorative frame presets | L2 |
| Seller batch names | One design, many names (CSV → zip of files) — Seller-tier feature | L3 |

---

## 3. Architecture

### Recommended: client-side canvas rendering

```
TextSpec { text, fontId, capHeightMm, layout }
   → <canvas> render (font loaded via FontFace API, NO anti-aliasing tricks needed:
      render large at 4–8× and hard-threshold to pure black/white)
   → PNG base64 (2-tone, binary)
   → POST /convert (existing endpoint, zero backend changes)
      { num_colors: 2, outline: 'auto', fill_pattern: 'organic',
        preview_style: 'thread', hoop_w/h_mm sized from text metrics }
   → previewSvg (thread-realistic) + stitch file
```

**Why client-side:** zero new backend surface; fonts ship as static WOFF2 assets (or
Google Fonts); user-uploaded fonts become possible later without server file handling;
the existing `convertImageBase64ToStitches()` in `src/api/generator.js` already does the
API call shape we need.

**Critical sizing rule:** the hoop dimensions sent to the API control physical size.
Map UI size to **cap height in mm**, then compute hoop box from rendered text metrics:
`hoop_h_mm = capHeightMm × (canvas_h / cap_px)`. Never let text size be an accident of
canvas proportions. (The text experiment validated this math.)

### Engine settings profile for lettering

```js
{
  num_colors: 2,            // binary source; engine no longer raises this (fixed)
  density_mm: 0.6,
  min_feature_mm: 0.8,
  outline: 'auto',
  fill_pattern: 'organic',
  outline_policy: 'selective',
  preview_style: 'thread',
  thread_brand: userChoice,  // single thread color picker
}
```

### Known physical constraints (from the experiment — enforce in UI)

| Constraint | Value | UI behavior |
|---|---|---|
| Minimum cap height | ~5mm | Hard floor on the size slider; show "too small to stitch" below 6mm |
| Satin stroke range | 0.95–4.5mm | Font qualification handles this (below) |
| Strokes < 0.95mm | degrade to runlines | Qualification flags; warn "outline-style result" |
| Strokes > ~4.5mm | border + fill treatment | Fine — looks like appliqué lettering |
| Hoop fit | text box ≤ hoop | Live check against selected hoop |

---

## 4. Font strategy

### Qualification harness (build first — it gates everything)

A script in `embroidery-stitch-backend/scripts/` that takes a font file and:
1. Renders a pangram + "Sophie"-style test word at 6 / 10 / 15 / 25mm cap heights (binary).
2. Converts each through the production engine.
3. Scores: engine quality (must be ≥ 96), legibility proxy (letter component count vs
   expected), satin fraction, stitch count, and renders a contact sheet.
4. Emits a per-font verdict: **qualified sizes** + recommended default size.

Fonts ship only with their qualified size ranges. This is the same
measurement-first discipline that won the stitch campaign — no font goes live on vibes.

### Launch set (curate ~12–16 from free/open licenses)

| Class | Expectation | Examples to test |
|---|---|---|
| Rounded block (best) | satin columns, crisp at 6mm+ | Arial Rounded class: Varela Round, Baloo, Fredoka |
| Bold sans | satin columns | Montserrat Bold, Nunito ExtraBold |
| Slab/retro | mixed satin + region | Alfa Slab One, Chewy |
| Script/hand | satin, needs 10mm+ | Pacifico, Caveat Bold, Dancing Script Bold (brand font!) |
| Serif display | qualification will decide | Playfair Display Bold (brand font) |

Thin-stroke fonts (light weights, delicate serifs) will fail qualification — don't fight
it; bold weights exist for a reason and pros use them for the same physics.

---

## 5. UI spec (Label Maker page, L1)

- **Text input** — single line L1; live character count; warn at hoop-width limit.
- **Font picker** — cards showing each font rendered in *thread-preview style* (pre-render
  a static sample image per font at build time; do not run conversions for browsing).
- **Size** — slider in mm cap height (6–40mm), with hoop-fit indicator.
- **Thread color** — single color from the brand palette (maps to `thread_brand` + color).
- **Frame (optional)** — 3–5 simple border presets (rounded rect, scallop, heart) rendered
  into the same canvas as strokes the engine satins. Frames are just more line art.
- **Preview** — thread-realistic SVG from the API (the engine's `preview_style='thread'`).
- **Download** — existing DownloadGate (ad / credit / subscription) unchanged.
- **Credits** — lettering download = 1 credit (vs 2–3 for AI generation; no Gemini cost).

Flow: type → pick font/size → [Generate preview] (1 API call) → gate → download.

---

## 6. Phasing

### L1 — Label Maker MVP
- Qualification harness + ~12 qualified fonts (static WOFF2 assets).
- Canvas render module (`src/lib/textRender.js`): FontFace load, 4× supersample,
  hard threshold, metrics → hoop math.
- Replace `src/api/label.js` stubs: `generatePreview` / `exportLabel` →
  `convertImageBase64ToStitches` with the lettering profile.
- Wire `LabelMakerPage.jsx`: input, font cards, size slider, thread color, preview, gate.
- Acceptance: 2 text fixtures added to the backend suite (block + script reference words)
  so engine changes can never silently break lettering again.

### L2 — Composition
- Multi-line text + alignment; letter spacing control.
- Arc/curved baseline (canvas transform before threshold — engine doesn't care).
- Monogram presets (letter + frame combos).
- "Add text" layer in the Generator flow (composite text canvas over generated art
  before conversion).

### L3 — Seller features
- User font upload (runs the qualification harness server-side or in a worker; show the
  verdict before accepting).
- Batch names: one design × CSV of names → zip (Seller tier; queue + email when ready).
- Solid-satin upgrade for wide block letters if fabric sew-outs say border+fill reads
  less premium (engine task, parked pending sew-out evidence).

---

## 7. Open questions

1. **Font licensing** — stick to OFL (Open Font License) fonts for embedded WOFF2; verify
   each license permits rendering-to-product. (OFL does; avoid "desktop-only" licenses.)
2. **AI-text comparison arm** — still worth one session (GEMINI_API_KEY available) to
   document where AI lettering fits (decorative text *inside* artwork) vs the TTF path.
   Not a launch blocker.
3. **Frame art source** — hand-drawn SVG strokes vs generated; start with 3 hand-drawn.
4. **Default size per font** — qualification harness output decides; don't hand-pick.

---

## 8. Success criteria

- A user types a name, picks a font, and downloads a stitchable file in under 60 seconds.
- Every shipped font/size combination scores engine quality ≥ 96 in the harness.
- Lettering conversion p95 latency < 10s (no Gemini in the loop).
- Text fixtures live in the backend acceptance battery (regression-proof).
- First fabric sew-out of a label reads as a product someone would pay for.
