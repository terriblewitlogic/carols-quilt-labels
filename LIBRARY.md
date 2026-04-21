# Embroidery Design Library — Builder Guide

The library is a collection of 50 pre-generated embroidery designs across six categories.
Each design is stored as static files in `public/library/{id}/` and indexed in
`public/library/manifest.json`.  Once committed to git the designs appear in the
**Design Library** section of the app.

---

## How it works

```
Catalog item (prompt + settings)
        │
        ▼
  /api/generate        ← Gemini image generation
        │
        ▼
  /api/image_to_jef    ← raster → embroidery stitches
        │
        ▼
  Review in browser    ← you approve or retry
        │
        ▼
  /api/save_to_library ← writes files to public/library/{id}/
        │
        ▼
  git commit           ← publishes to all users
```

---

## Prerequisites

**Node.js** (v18+) and **Python 3.11** must be installed.

Install Python dependencies once:

```bash
pip install pyembroidery Pillow numpy scikit-image scikit-learn shapely
```

Install Node dependencies once:

```bash
npm install
```

You need a **Gemini API key** with the `gemini-3.1-flash-image-preview` model enabled.
Add it to a `.env` file at the project root:

```
GEMINI_API_KEY=your-key-here
```

---

## Starting the dev servers

The app needs two processes running simultaneously — open two terminal tabs.

**Tab 1 — Python function server** (port 9999):

```bash
python3 scripts/dev-functions.py
```

Expected output:
```
[functions] Loaded .env from .../jeflabelmaker/.env
Local functions server running on http://localhost:9999
Available: /export  /preview  /font_samples  /generate  /image_to_jef  /save_to_library
```

**Tab 2 — Vite dev server** (port 5199):

```bash
npm run dev
```

Vite proxies all `/api/*` requests to the Python server automatically.

---

## Using the Library Builder

Open in your browser:

```
http://localhost:5199/library-builder.html
```

### Page overview

The builder shows all 50 catalog designs as cards, grouped by category.
Each card displays:

- The design name, description, and category icon
- Hoop size, colour count, fill density, and outline style
- **Left preview** — the AI-generated source image
- **Right preview** — the converted stitch preview
- Status badge: `Not generated` → `Ready to save` → `Saved ✓`

### Generating a single design

1. Find the design you want and click **▶ Generate & Convert**
2. The card runs two steps automatically — *Generating image…* then *Converting stitches…*
3. Both previews appear when done
4. **Review the stitch preview.** If it looks good, click **✓ Save**
5. If the result isn't right, click **↺ Retry** — Gemini generates a different image each time

### Batch auto-generation

Click **⚡ Auto-Generate All** to process every unsaved design in sequence with no manual
approval step.  A progress bar tracks completion.  Click **■ Stop** to pause the queue at
any point — already-saved designs are not re-run.

> **Tip:** Auto-mode is useful for a first pass.  After it finishes, open individual cards
> to review and regenerate any that look wrong before committing.

### Refreshing status

If you've saved designs in another session or browser tab, click **↺ Refresh** to re-read
`manifest.json` and sync the badge status.

---

## What gets saved

For each design, four files are written to `public/library/{id}/`:

| File | Contents |
|---|---|
| `preview.svg` | Stitch-preview SVG shown in the Library page |
| `image.png` | Original AI-generated source image |
| `embroidery.jef` | Ready-to-stitch machine embroidery file |
| `meta.json` | Name, category, stitch count, thread palette, timestamp |

`public/library/manifest.json` is updated with an entry for every saved design.
The Library page in the app reads this file to know what to display.

---

## Committing to git

After saving one or more designs:

```bash
git add public/library/
git status          # review the new files
git commit -m "Add library designs: sunflower, red-rose, daisy"
```

Push to your deployment branch to publish.

---

## Adding a new catalog entry

The full catalog is defined in two places that must stay in sync:

- **`src/image-embroidery/library-catalog.js`** — used by the React app (Library page + Save modal)
- **`public/library-builder.html`** — the `CATALOG` constant near the top of the `<script>` block

Add the same entry to both files using this shape:

```js
{
  id: 'my-design',           // unique slug, becomes the folder name
  name: 'My Design',
  category: 'florals',       // florals | birds-insects | animals | botanicals | folk-art | geometric
  description: 'One line shown on the library card',
  prompt: 'a detailed image description for Gemini',
  settings: {
    hoopKey: '4x4',          // 4x4 | 5x7 | 6x10
    numColors: 4,            // 2–6
    densityMm: 0.4,          // fill row spacing in mm
    outline: 'running',      // none | running | satin
    minFeatureMm: 1.5,       // smallest region to keep
  },
}
```

Then open the builder, find the new card, and run the pipeline for it.

---

## File layout

```
public/
  library/
    manifest.json            ← index of all saved designs
    sunflower/
      preview.svg
      image.png
      embroidery.jef
      meta.json
    red-rose/
      ...

src/image-embroidery/
  library-catalog.js         ← source of truth for the 50-item catalog
  LibraryPage.jsx            ← browse page shown in the app

netlify/functions/
  generate/                  ← Gemini image proxy
  image_to_jef/              ← raster → stitch conversion
  save_to_library/           ← writes files to public/library/

scripts/
  dev-functions.py           ← local dev server (port 9999)
```

---

## Troubleshooting

**`GEMINI_API_KEY` missing / 401 errors**
Make sure `.env` exists at the project root and the dev server was started *after*
the file was created.  The server reads `.env` only at startup — restart it after
any changes.

**Port 9999 already in use**
```bash
lsof -ti tcp:9999 | xargs kill -9
python3 scripts/dev-functions.py
```

**`save_to_library` 500 error — path not found**
The endpoint resolves `public/library/` relative to its own file path.
Make sure you are running the dev server from the project root:
```bash
cd /path/to/jeflabelmaker
python3 scripts/dev-functions.py
```

**Stitch preview looks wrong / too many stitches**
Retry the design — the generated image varies each time and some are better suited
to the conversion pipeline than others.  You can also adjust the settings in
`library-catalog.js` (`densityMm`, `numColors`, `minFeatureMm`) before retrying.

**Gemini 429 quota error**
The `gemini-3.1-flash-image-preview` model requires billing enabled on the
Google Cloud project.  Image generation is not available on the free tier.
