# Design specification for a web-based quilt label maker with embroidery file export

**A dedicated quilt label maker that generates machine embroidery files does not exist as a web application today — this represents a significant market gap.** Quilters currently cobble together expensive desktop software ($139–$1,299), pre-made templates, or printable fabric sheets to create labels. A browser-based tool combining label-specific templates, text customization, real-time stitch preview, and DST/PES export would serve an underserved community where **94% of quilters believe labeling is important yet only 57% do it consistently** (2016 Handi Quilter survey, 24,185 respondents). This specification defines the functional, technical, and UX requirements for building that tool.

---

## 1. Functional requirements

### 1.1 Core label creation workflow

The application must support a complete label creation pipeline: select template or start blank → choose label size and shape → add and format text → add decorative elements → preview stitch rendering → export embroidery file (DST/PES).

**Label sizes to support (based on standard hoop sizes):**

| Label Size | Metric Equivalent | Target Hoop | Use Case |
|---|---|---|---|
| 3.5" × 3.5" | 89 × 89 mm | 4×4" hoop | Minimal labels, small quilts |
| 4.5" × 6.5" | 114 × 165 mm | 5×7" hoop | **Primary size — most popular for quilt labels** |
| 5.5" × 9.5" | 140 × 241 mm | 6×10" hoop | Detailed labels with extensive text/decoration |
| 7" × 7" | 178 × 178 mm | 8×8" hoop | Square decorative labels |

Each label size must account for a **1–1.5" margin** between the design boundary and the hoop edge for needle clearance. The actual embroiderable area is always smaller than the hoop's labeled dimensions.

**Label shapes:** Rectangle (default, most common), square, oval, heart, and corner triangle (the folded-corner method popularized by Bonnie Hunter, made from a 6–6.5" square folded diagonally). Rectangle with rounded corners should be the default — it's the easiest to finish and attach.

### 1.2 Text fields and content templates

The app must provide structured text input fields pre-populated based on label purpose. Research shows the following information hierarchy:

**Essential fields (always shown):**
- Quilter/maker's full name (first and last — avoid initials per Quilt Alliance guidance)
- Date completed (month and year minimum)
- City, state/province, country

**Standard fields (shown by default, togglable):**
- Quilt name / pattern name
- Pattern designer credit
- Recipient's name
- Occasion (birthday, wedding, baby, memorial, holiday, graduation, retirement)
- "Quilted by" credit (if different from piecer)

**Optional fields (expandable section):**
- Personal message, quote, or scripture (free text, multi-line)
- Care/washing instructions (pre-written templates: "Machine wash cold, tumble dry low")
- Fabric collection name
- Guild or group name
- Copyright notice
- Quilt number (for inventory tracking)

**Occasion-specific templates** should pre-configure relevant fields. A baby quilt template should include child's name, birth date, weight, length, and parents' names. A Quilts of Valor template must state "Quilt of Valor" and exclude religious/political messages per QOVF requirements.

### 1.3 Decorative element library

The app needs a curated library of pre-digitized decorative elements organized by category:

- **Floral motifs:** Roses, rose buds, daisies, sunflowers, wildflower sprays, vine trails, leaf sprays, laurel wreaths, floral wreaths, forget-me-nots
- **Geometric/symbolic:** Hearts (scrolling, feathered, simple), stars (5-point, 8-point), butterflies, birds/love birds, teddy bears (baby quilts), patchwork block miniatures
- **Frames and borders:** Rectangular frames with rounded corners, scalloped edges, scrollwork borders, double-line frames, oval frames, heart-shaped frames, simple single-line running stitch frames, satin stitch frames
- **Corner ornaments:** Floral corner sprays, vine/leaf corners, scroll corners, butterfly corners, daisy arrangements
- **Holiday/occasion:** Holly and snowflakes (Christmas), baby rattles and storks (baby), rings and doves (wedding), pumpkins (fall), patriotic stars and flags

All decorative elements must be stored as **pre-digitized stitch data** with object-level metadata (not just raw stitches) to allow scaling within safe bounds (±10–20% from original digitized size without re-digitizing, per industry standard).

### 1.4 Border system

Borders require special architectural consideration because they must scale to different label sizes:

- Borders are composed of **repeating motif units** along straight edges plus **dedicated corner files** that connect seamlessly to straight runs
- The system must calculate how many repeats fit each edge and adjust spacing to avoid partial motifs
- **Corner handling:** Each border style needs a paired corner motif (a larger flower, diagonal flourish, or mirrored element) — corners cannot simply be a rotated version of the straight segment
- Border types to include: running stitch outline, satin stitch outline (**1.5–8mm width**), bean/triple stitch outline, decorative scrollwork, vine and leaf, scalloped edge, crosshatch band

---

## 2. Technical requirements

### 2.1 Embroidery file format specifications

The application must generate valid **DST (Tajima)** and **PES (Brother)** files. These two formats cover the vast majority of home embroidery machines.

**DST format constraints:**

| Parameter | Specification |
|---|---|
| Header size | Always **512 bytes** (125 bytes data + 387 bytes padding with 0x20) |
| Command size | Always **3 bytes** per stitch command |
| Coordinate unit | **0.1 mm** (1 unit = 0.1 mm) |
| Max stitch/jump per command | **121 units (12.1 mm)** in X or Y |
| Color information | **None** — colors must be assigned on machine |
| Trim encoding | 3+ consecutive small jump commands (+2,+2 → -4,-4 → +2,+2 pattern) |
| Color change | c0=1, c1=1 in byte 3's control bits |
| End command | STOP command |
| Header fields | LA (label, 16 chars), ST (stitch count, 7 digits), CO (color changes, 3 digits), +X/-X/+Y/-Y (extents), AX/AY (delta from start to end) |

**PES format constraints:**

| Parameter | Specification |
|---|---|
| Version target | **PES v1** (broadest compatibility) with optional PES v6 for object preservation |
| Magic number | 8-byte ASCII string `#PES0001` |
| Coordinate unit | **0.1 mm** (same as DST) |
| Color storage | Index values into **PEC color palette (~65 predefined colors)** |
| Max thread colors | **127** per design |
| Max stitch count | **~300,000** stitches |
| Structure | PES section (design objects) + PEC section (stitch execution commands, backward-compatible) |
| Byte order | Little-endian throughout |

**Both formats:** Long stitches exceeding the per-command maximum must be broken into multiple commands automatically. For DST, any movement greater than 12.1mm in either axis requires chained commands.

### 2.2 Stitch generation parameters

**Text stitch parameters:**

| Letter Height | Stitch Type | Density (row spacing) | Thread Weight |
|---|---|---|---|
| < 3 mm | Not supported | — | — |
| 3–5 mm | Satin stitch | 0.30–0.35 mm | 50wt or 60wt recommended |
| 5–25 mm | Satin stitch (default) | 0.35–0.40 mm | 40wt standard |
| > 25 mm | Fill stitch or split satin | 0.40 mm | 40wt standard |

**Satin stitch column limits:** Minimum width **1.27 mm (0.05")**, maximum width **12.7 mm (0.5")**. Columns exceeding ~10 mm should automatically split to prevent loose/snagging stitches.

**Stitch count estimates** for capacity planning (per running inch of satin column):
- 1 mm width: ~100 stitches/inch (115 with underlay)
- 2–3 mm width: ~125 stitches/inch (150 with underlay)
- 4–6 mm width: ~150 stitches/inch (180 with underlay)
- Fill stitch: ~1,000 stitches per square inch at 0.4 mm density

**Underlay rules:** Text under 5 mm height requires no underlay. Text 6–10 mm gets center-run underlay. Larger text gets edge-run underlay. All fill areas require at least zigzag underlay on quilting cotton.

### 2.3 Fill stitch patterns for backgrounds and decorative areas

The system should support these fill types, listed by priority for quilt labels:

**Stipple/meander fill** is the highest-priority fill pattern — it mimics free-motion quilting texture and is the most contextually appropriate for quilt labels. It produces a continuous, non-crossing curved meandering line. Key parameters include stippling spacing (distance between meander rows, ~0.4 mm default) and run pitch (stitch length within the meander).

**Tatami fill** (standard brick-pattern fill) creates a smooth, flat, woven-look surface and is best for solid backgrounds behind text. Standard density is **0.4 mm row spacing** with **4–6 mm stitch length**. Stitch angle should default to 45° diagonal to prevent thread sinking into fabric weave.

**Crosshatch fill** creates a lattice/grid pattern with adjustable angle and spacing (~10 mm typical). **Contour/echo fill** follows shape edges inward, creating a dimensional sculpted effect. **Motif fill** uses small repeated patterns (geometric, floral, sashiko-inspired) for decorative open-textured backgrounds.

### 2.4 Thread color system

The application must support multiple thread brand palettes for color selection:

| Brand | Palette Size | Primary Market |
|---|---|---|
| Brother | 63 colors | Consumer/home machines |
| Isacord (AMANN) | ~400 solid + 27 variegated | Professional standard |
| Madeira Polyneon | 400+ | Global commercial standard |
| Sulky | Several hundred | Popular rayon thread |
| Janome | 80 colors | Consumer/home machines |

**Color encoding differs by format:** DST files contain no color data — the app must generate an accompanying **color sequence chart** (printable PDF or on-screen) showing thread order and recommended colors. PES files store colors as PEC palette indices; the app maps selected brand colors to the nearest PEC palette entry.

For a quilt label maker, a **simplified palette of 20–30 curated colors** (plus user-selectable brand mapping) is sufficient. Most quilt labels use 1–4 thread colors. The default should be single-color (black or dark navy on light fabric), with the option to add color changes for decorative elements.

### 2.5 File generation architecture

**Recommended approach: pyembroidery via Pyodide (Python-in-WebAssembly)**

No mature JavaScript library exists for embroidery file generation. The most viable options, ranked:

1. **pyembroidery via Pyodide** — pyembroidery is the most mature open-source embroidery library (reads 46 formats, writes 20 including DST and PES). It's pure Python with no C extensions, making it compatible with Pyodide (Python compiled to WebAssembly for browser execution). This keeps all processing client-side — no server needed for file generation.

2. **Native JavaScript DST/PES writer** — DST's format is straightforward enough (512-byte header + 3-byte encoded commands) to implement directly in TypeScript. PES v1 minimal files are also feasible. This eliminates the Pyodide dependency (~10+ MB download) but requires building and maintaining format-specific code.

3. **libembroidery compiled to WebAssembly** — The Embroidermodder project's C library (`embroidery.h`, single-header, zlib license) handles 45+ formats and could be compiled via Emscripten. No production WASM build currently exists, so this requires development effort.

4. **Server-side pyembroidery** — Python backend generates files on request. Simplest to implement but adds server infrastructure and latency.

**Recommendation:** Start with option 2 (native JS for DST/PES v1) for speed and minimal bundle size, with option 1 as a fallback for additional format support. DST's 3-byte ternary encoding and PES v1's minimal structure are well-documented enough for direct implementation.

**Key pyembroidery API pattern** (reference for any implementation):
```
Internal coordinate unit: 0.1 mm
Commands: STITCH, JUMP, TRIM, COLOR_CHANGE, STOP, END
Pattern: create pattern → add threads → add stitch commands (absolute coordinates) → write to format
PES writer supports versions 1, 6, and 6t
DST writer supports standard and extended headers
```

---

## 3. UI/UX requirements

### 3.1 Design canvas architecture

**Fabric.js is the recommended canvas library** for the design workspace. It provides built-in object transformation (drag, resize, rotate), SVG import/export, in-place text editing, and canvas-to-JSON serialization — all critical for an embroidery design editor. It has **25,700+ GitHub stars** and is proven in production design tools.

The workspace must be **hoop-centric**: the canvas displays a hoop outline at the selected size (4×4", 5×7", 6×10", or 8×8"), with the embroiderable area clearly bounded. A ruler/grid system with **0.25" / 5mm snap increments** helps users position elements precisely. The design must show a clear boundary warning when any element extends beyond the hoop's safe embroidery area.

**Canvas features required:**
- Drag-and-drop placement of text blocks and decorative elements
- Resize handles with aspect-ratio lock for decorative elements
- Multi-select and alignment tools (center horizontally, center vertically, distribute evenly)
- Undo/redo (minimum 20 steps)
- Zoom and pan (scroll-to-zoom, pinch-to-zoom on touch devices)
- JSON serialization for save/load of in-progress designs

### 3.2 Dual preview modes

The app needs two rendering modes, togglable with a single click:

**Design mode (default):** Clean vector rendering using Fabric.js — text appears as formatted screen text, decorative elements as SVG/raster graphics. Fast and responsive for editing. This is where users compose their label.

**Stitch preview mode:** Renders the actual stitch paths that will appear in the exported file. Each stitch is drawn as a line segment between stitch coordinates on an HTML5 Canvas 2D context. Color changes are shown as stroke color changes. This mode gives users confidence that their design will stitch correctly. An optional **Three.js-based 3D preview** (using textured geometry to simulate thread appearance, as demonstrated by the dst-format library) can be offered as an advanced feature.

The stitch preview must show **stitch direction indicators** on satin columns, **jump stitch paths** as dashed lines, and **color change points** as markers. A stitch count and estimated time display helps users gauge design complexity.

### 3.3 Font system

**The app must use pre-digitized embroidery fonts, not real-time TrueType conversion.** Auto-converting TTF fonts to embroidery produces poor results because software cannot reliably determine stitch pathing, column segmentation, or pull compensation. As embroidery expert Andy Shuman notes: "It's very difficult, even with good software and a great machine, to make a name done with a serif font look good at a quarter of an inch tall."

**Curated font library (minimum 12–15 fonts):**

| Category | Examples | Min Height | Best For |
|---|---|---|---|
| Sans-serif block | Arial, Helvetica, Century Gothic, Futura | 6.35 mm (0.25") | Names, dates, all small text |
| Serif | Times New Roman, Georgia, Baskerville, Palatino | 8.89 mm (0.35") | Formal labels, titles |
| Script/cursive (thick stroke) | Lobster, Pacifico equivalents | 7.6 mm (0.30") | Decorative names, "Made with love" |
| Monogram/decorative | 2–3 display fonts | 15+ mm | Single initials, monograms |

Each font must be digitized as embroidery stitch data at multiple reference sizes (small, medium, large) with proper satin stitch columns, underlay, pull compensation, and optimized stitch sequencing. The font picker should show a **stitch-simulated preview** (not screen-font rendering) so users see how each font will actually appear when embroidered.

**Minimum size enforcement:** The UI must prevent users from setting text below the font's minimum height. Sans-serif fonts lock at **6.35 mm minimum**; serif fonts at **8.89 mm**; script fonts at **7.6 mm**. If a user's text doesn't fit within the label at the minimum size, the app should warn and suggest reducing text content or increasing label size.

### 3.4 User interface layout

**Layout structure:**
- **Left sidebar:** Template gallery, decorative element library (categorized with thumbnail previews), font selector
- **Center:** Hoop-centric design canvas with rulers
- **Right sidebar:** Properties panel (selected object's settings: font size, color, stitch type, spacing) and label info fields (structured text inputs)
- **Top toolbar:** Hoop size selector, undo/redo, zoom controls, preview mode toggle, export button
- **Bottom bar:** Stitch count, color count, estimated stitch time, design dimensions

**Beginner mode vs. advanced mode:** Default to a simplified interface where stitch parameters are auto-calculated. Advanced users can toggle to expose stitch density, underlay type, stitch angle, and pull compensation controls.

### 3.5 Export workflow

The export flow should be: click Export → select format (DST or PES, with clear explanation: "DST works with most machines; PES is for Brother/Babylock/Bernina") → select thread brand for color chart → download ZIP containing the embroidery file + a printable PDF color chart showing thread sequence, brand-specific color numbers, and a design preview.

The PDF color chart is essential for DST files (which carry no color data) and useful for PES files. It should include: design preview image, dimensions, stitch count, thread color sequence with brand-specific numbers, and a placement guide.

---

## 4. Typography specification

### 4.1 Stitch type selection logic

The system must automatically select the correct stitch type based on letter size:

| Letter Height | Primary Stitch | Underlay | Notes |
|---|---|---|---|
| 3–5 mm | Satin, no serifs | None | 50–60wt thread recommended; sans-serif only |
| 5–10 mm | Satin stitch columns | Center-run | Standard label text size |
| 10–25 mm | Satin stitch columns | Edge-run | Title/header text |
| 25+ mm | Split satin or fill | Zigzag + edge-run | Monogram initials, large display text |

**Satin stitch** produces a smooth, glossy appearance with parallel stitches perpendicular to the letter stroke. It's the default and best choice for **95% of quilt label text** (which falls in the 5–15 mm range).

**Running stitch** (single line, ~12 stitches/inch) and **bean stitch** (triple-run, ~37 stitches/inch) are used for outline-only text effects — a "redwork" aesthetic popular on quilt labels. The app should offer an "Outline Only" text style toggle that switches from satin fill to bean stitch outlines.

**Fill stitch** (tatami) is automatically applied when letter stroke width exceeds the satin maximum (~12.7 mm). The system must detect this and switch seamlessly.

### 4.2 Critical typography constraints

Several hard constraints must be enforced in the application:

- **Minimum stitch length: 1 mm.** Shorter stitches risk cutting holes in fabric.
- **Minimum counter opening: 1 mm.** The interior space of letters like "e", "a", "o" must stay open or stitches will merge and create holes. This constrains minimum font size.
- **Minimum stroke width: 1.27 mm (0.05").** Any letter feature thinner than this will not render as visible stitching.
- **Letter spacing must be generous.** Tight kerning causes letters to merge into an unreadable mass. Default letter spacing should be **120–150% of screen-font default** for embroidery.
- **Pull compensation: add ~0.2–0.4 mm** to each side of satin columns to compensate for thread tension pulling fabric inward. Without this, letters appear narrower than designed.

### 4.3 Text layout features

- **Multi-line text** with adjustable line spacing (default: 150% of letter height)
- **Text alignment:** Left, center, right
- **Curved/arc text** for placement along circular borders or wreath elements
- **All-caps toggle** (recommended for smallest sizes, since lowercase letters are ~70% the height of uppercase, requiring the overall font size to increase by ~35% for mixed case)
- **Character spacing adjustment** (wider for embroidery than screen defaults)

---

## 5. Constraints, risks, and known challenges

### 5.1 No JavaScript embroidery generation library exists

This is the single largest technical risk. The options — pyembroidery via Pyodide, native JS implementation, or libembroidery via WASM — all require significant development. **Pyodide adds ~10+ MB to initial page load.** A native TypeScript DST/PES writer targeting only v1 formats is the leanest path but must be thoroughly tested against real machines. The ternary encoding for DST byte packing is non-trivial and the PES format has limited public documentation beyond reverse-engineered specifications.

### 5.2 Font digitizing is labor-intensive

Each embroidery font must be professionally digitized at multiple sizes with proper stitch pathing, pull compensation, and underlay. **This is not automatable at production quality.** Budget for 12–15 fonts × 3 size variants × full character set (uppercase, lowercase, numerals, punctuation) = significant upfront digitizing cost. Consider licensing existing BX-format fonts from established digitizers (Designs by JuJu, LindeeG Embroidery) or adapting Ink/Stitch's open-source pre-digitized font library (GNU GPL v3).

### 5.3 Stitch preview accuracy versus performance

Rendering thousands of individual stitch line segments on canvas is computationally expensive. A typical quilt label with text and a decorative border might contain **5,000–15,000 stitches**. Canvas 2D can handle this, but real-time updates during editing will require **debounced regeneration** (regenerate stitch preview 300–500ms after the user stops editing, not on every keystroke). The 3D Three.js preview is even more expensive and should be on-demand only.

### 5.4 Machine compatibility testing

Embroidery files must be tested on **actual machines**, not just validated against format specifications. Common failure modes include: incorrect trim sequences causing thread nests, color change commands not recognized, stitch density causing fabric puckering, and hoop size mismatches. A beta testing program with quilters using Brother, Janome, Husqvarna Viking, and Bernina machines is essential before launch.

### 5.5 Design-to-stitch conversion fidelity

The gap between what users see on screen (clean vector graphics) and what machines stitch (thread on fabric) is a persistent UX challenge in embroidery software. **Pull compensation, fabric stretch, stabilizer choice, thread weight, and machine tension all affect the final result.** The app should include a "Stitch Tips" panel with the exported file, advising: use medium-weight tear-away stabilizer for quilting cotton, use 40wt polyester thread (default) or 60wt for text under 6mm, and always do a test stitch-out on scrap fabric.

### 5.6 Competitive landscape

Two browser-based embroidery tools have recently launched: **Embrowser** ($4.99/month hobby plan, supports TTF upload and 3D preview) and **Ember** (free tier, growing community). Neither is quilt-label-specific. The differentiation opportunity is **template-driven simplicity** — quilters want to select a label template, type their information, and download a file in under 5 minutes. General-purpose digitizing tools require users to understand stitch types, densities, and pathing. A quilt label maker should abstract all of that away for beginners while exposing controls for experienced users.

---

## 6. Recommended MVP scope

The minimum viable product should target the **5×7" hoop size** (the most popular for quilt labels), support **DST and PES v1 export**, include **6–8 pre-digitized sans-serif and script fonts**, offer **10–15 label templates** with pre-designed borders and decorative elements, and provide a **2D stitch preview**. This scope addresses the core gap: no tool today lets a quilter design a custom embroidered label in a browser and download a machine-ready file.

**Phase 2 additions:** Additional hoop sizes (4×4", 6×10", 8×8"), 3D stitch preview, expanded font and motif libraries, thread brand color matching, curved text, stipple fill backgrounds, mobile-responsive design, and save/load functionality via browser storage or accounts.

The combination of template-driven simplicity for beginners, embroidery-correct stitch generation under the hood, and browser-based accessibility at a lower price point than desktop software ($0–5/month vs. $139–$1,299) positions this tool to capture meaningful adoption in a community where the majority of quilters want to label their work but lack accessible tools to do so.