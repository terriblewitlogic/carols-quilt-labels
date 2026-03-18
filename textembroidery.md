# Building a Python text-to-embroidery digitizing engine

**No mature end-to-end Python library exists for converting text into machine embroidery stitch data**, but a working pipeline can be assembled from proven open-source components: `fonttools` or `freetype-py` for glyph extraction, `shapely` for computational geometry, a Voronoi-based medial axis for satin rail computation, `stitch_generator` for stitch effects, and `pyembroidery` for JEF output. The hardest unsolved problem is automatic satin column generation—splitting glyph polygons into paired rails—which Ink/Stitch sidesteps entirely by using pre-digitized fonts. Three viable implementation strategies exist, ranging from a weekend proof-of-concept (pre-digitized character assembly) to a months-long full digitizing engine.

---

## Extracting glyph outlines from TTF/OTF fonts

Two Python libraries dominate font outline extraction. **fonttools** (github.com/fonttools/fonttools) provides the Pen protocol—a visitor-pattern API that walks glyph contours and emits `moveTo`, `lineTo`, `curveTo` (cubic Bézier for CFF/OTF), and `qCurveTo` (quadratic Bézier for TrueType) operations. The core pattern is:

```python
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

font = TTFont("MyFont.ttf")
glyphset = font.getGlyphSet()
pen = DecomposingRecordingPen(glyphset)  # resolves composite glyphs
glyphset["A"].draw(pen)
# pen.value → [('moveTo', ((x,y),)), ('curveTo', (cp1, cp2, pt)), ('closePath', ())]
```

**freetype-py** (github.com/rougier/freetype-py) wraps FreeType2 and provides `outline.decompose()` with callbacks for `move_to`, `line_to`, `conic_to` (quadratic), and `cubic_to`. FreeType automatically resolves TrueType's implicit on-curve points between consecutive off-curve control points, producing cleaner quadratic segments than raw fonttools output. Coordinates arrive in **26.6 fixed-point** format (divide by 64.0 for pixel units).

Bézier curves must be **flattened to polylines** for downstream geometry operations. Three approaches exist: fontPens' `FlattenPen` with `approximateSegmentLength=5` font units, adaptive De Casteljau subdivision with a flatness tolerance test, or parametric sampling via `fontTools.misc.bezierTools.splitCubicAtT()`. For embroidery at typical 0.1mm machine resolution with 1000 UPM fonts rendered at 10mm height, **1–5 font units tolerance** (≈0.01–0.05mm) is appropriate. The `bezier` library (github.com/dhermes/bezier) offers `curve.evaluate_multi(np.linspace(0, 1, N))` for uniform sampling.

**Kerning and multi-character layout** require reading advance widths from the `hmtx` table (`hmtx.metrics[glyph_name]` returns `(advanceWidth, lsb)`) and kerning values from either the legacy `kern` table (simple dict lookup of `(left, right)` glyph pairs) or the modern GPOS table (class-based PairPos lookups under the `kern` feature tag). Character-to-glyph mapping uses `font.getBestCmap()` which returns `{unicode_int: glyph_name}`. A layout function walks the string, accumulating `x_cursor += advance + kern_adjustment` per character.

For **inner versus outer contour classification** (critical for letters like O, B, A with holes), compute the signed area via the shoelace formula—TrueType outer contours wind clockwise (negative area), CFF outer contours wind counter-clockwise (positive area). The practical approach builds Shapely `Polygon` objects from each contour and uses containment tests (`poly_j.contains(poly_i)`) to classify holes, then constructs `Polygon(exterior, [hole1, hole2])`. Shapely's `orient(polygon, sign=1.0)` normalizes winding to CCW exterior, CW holes.

---

## The satin column algorithm: skeleton extraction and dual-rail stitching

Satin columns are the primary stitch type for lettering. Two parallel "rails" define the column edges, and stitches zigzag perpendicularly between them at **0.3–0.4mm spacing** (density measured between needle penetrations on each rail). The fundamental challenge is: given a filled glyph polygon, compute the medial axis to derive the two rails automatically.

The **medial axis** of a polygon is the locus of centers of maximal inscribed circles touching the boundary at two or more points. For simple polygons it forms a tree; for polygons with holes (like "A" or "B") it forms a planar graph. The medial axis consists of line segments (bisectors between edges) and parabolic arcs (bisectors between vertices and edges). US Patents 5506784, 5510994, and 5541847 specifically describe using medial axes for embroidery pattern generation.

The most practical Python computation uses a **Voronoi-based approach**: densely sample the polygon boundary, compute `scipy.spatial.Voronoi` on those sample points, then clip resulting Voronoi edges to the polygon interior using Shapely's `contains()`. The **trimesh** library (github.com/mikedh/trimesh) provides `trimesh.path.polygons.medial_axis(polygon)` which accepts a Shapely Polygon directly and returns edges and vertices via internal Voronoi computation. Alternatively, `skimage.morphology.medial_axis()` operates on rasterized binary arrays but requires polygon→raster→skeleton→vector round-tripping.

```python
from scipy.spatial import Voronoi
from shapely.geometry import LineString
from shapely.ops import unary_union

def voronoi_medial_axis(shape, sample_density=1):
    boundary = shape.exterior
    num_samples = max(500, int(boundary.length * sample_density))
    coords = np.array([boundary.interpolate(d).coords[0]
                       for d in np.linspace(0, boundary.length, num_samples)])
    vor = Voronoi(coords)
    edges = []
    for s, e in vor.ridge_vertices:
        if s == -1 or e == -1: continue
        seg = LineString([vor.vertices[s], vor.vertices[e]])
        if shape.contains(seg):
            edges.append(seg)
    return unary_union(edges)
```

Once the skeleton is computed, the polygon boundary splits into two rail chains at the skeleton endpoints. The stitch generation algorithm walks both rails simultaneously using parametric interpolation, placing needle penetration points at regular intervals:

```
for i in 0..numStitches:
    t = i / numStitches
    p_left  = rail_left.interpolate(t, normalized=True)
    p_right = rail_right.interpolate(t, normalized=True)
    if i % 2 == 0: emit_stitch(p_left)
    else:          emit_stitch(p_right)
```

**Pull compensation** widens each stitch by 0.15–0.40mm (varying by column width and fabric type) to counteract thread tension that contracts the satin column. The algorithm extends each stitch endpoint outward along the stitch direction vector by the compensation amount. **Corner handling** is the other major challenge: sharp corners cause stitch crowding on the inner rail and spreading on the outer rail, requiring either splitting the satin into separate sections at corners or dynamically reducing inner-rail stitch count.

---

## Fill stitches, underlay, and scanline algorithms

Fill stitches (tatami fill) use a **scanline algorithm** adapted from computer graphics. The polygon is rotated by the negative fill angle to align scanlines horizontally, then parallel horizontal lines sweep from yMin to yMax at **0.4–0.5mm row spacing**. At each scanline, intersections with polygon edges are computed and paired (using an Active Edge List sorted by x-coordinate), producing interior segments. Stitches are placed along each segment at **3–7mm intervals**, with adjacent rows **staggered by 1/N of the stitch length** (typically N=4) to avoid visible vertical valleys—creating the characteristic brick-pattern texture.

Ink/Stitch's implementation in `lib/stitches/fill.py` uses `intersect_region_with_grating()`, which creates parallel Shapely `LineString` objects and intersects them with the fill polygon using Shapely's `intersection()`. The resulting segments become nodes in a **NetworkX graph**, and `build_travel_graph()` constructs edges for travel stitches between disconnected segments. **Dijkstra's algorithm** (`networkx.bidirectional_dijkstra`) finds the optimal stitching order that minimizes travel distance—a key innovation over older "legacy fill" approaches that simply jumped between sections.

**Three underlay types** provide fabric stabilization beneath top stitching:

- **Center-walk**: Running stitch along the medial axis of a satin column and back. Computed by sampling midpoints between corresponding rail points at ~4mm stitch intervals. Best for thin columns and small text.
- **Edge-walk**: Running stitch up one rail and down the other, inset slightly from the true edge. Provides crisp edge definition for wider columns (**2.5mm+**).
- **Zigzag underlay**: Lower-density satin stitch (2× the top layer spacing) for wide satin areas and challenging fabrics.

For fill areas, underlay uses the same scanline algorithm but at **3× the top-layer row spacing** and rotated **90°** from the top fill angle, counteracting directional pull.

---

## How Ink/Stitch implements everything under the hood

The Ink/Stitch repository (github.com/inkstitch/inkstitch, GPL-3.0, ~1.2k stars) organizes its core algorithms in two key directories. **`lib/elements/`** contains SVG-aware element classes that read Inkscape parameters, and **`lib/stitches/`** contains pure geometry algorithms operating on Shapely objects—these are the most extractable components.

The **satin column** lives in `lib/elements/satin_column.py` (~1884 lines). The `SatinColumn` class expects an SVG `<path>` containing exactly two subpaths (rails) plus optional short crossing segments (rungs). Its pipeline: `validate_satin_column()` → `flattened_sections()` (Bézier → polyline) → `plot_points_on_rails()` (parametric stitch placement) → `compensated_shape()` (Shapely `buffer()` for pull compensation) → `do_satin()` (zigzag stitch generation). Notably, **Ink/Stitch never computes a medial axis automatically**—it requires users to provide two explicitly drawn rails, or uses pre-digitized fonts where rails are already defined.

The **auto-fill** algorithm spans `lib/stitches/auto_fill.py` and `lib/stitches/fill.py`. The scanline intersection uses Shapely; the travel routing uses NetworkX graph algorithms. Additional fill types include contour fill, circular fill (`lib/stitches/circular_fill.py`), guided fill, and meander fill using space-filling curves.

Key dependencies beyond Shapely and NetworkX include **NumPy** (coordinate math), **SciPy** (path smoothing, being reduced), **lxml** (SVG parsing), and **pyembroidery** (Ink/Stitch maintains its own fork at github.com/inkstitch/pyembroidery, renamed "pystitch"). **The `lib/stitches/` modules can be extracted** for use without Inkscape—they operate on Shapely geometries and produce coordinate lists—though `lib/elements/` has deep inkex dependencies.

Ink/Stitch's **lettering system does NOT digitize TTF fonts on the fly**. Each font is a directory of SVG files where every glyph is a manually digitized Inkscape layer containing satin columns, fills, and running stitches with embroidery parameters embedded as SVG attributes. The open-source font collection lives at github.com/inkstitch/embroidery-fonts. Creating a new font requires manual digitizing of every glyph—there is no automatic TTF→embroidery pipeline even in Ink/Stitch.

---

## Pre-digitized font formats and what's available

The embroidery industry uses several proprietary font formats, none with open specifications:

- **BX (Embrilliance)**: Installation packages containing pre-digitized stitch data per character, assigned to keystrokes. The free Embrilliance Express can use them. Thousands of BX fonts exist from commercial designers. **No public parser exists**—fully proprietary binary format.
- **ESA (Wilcom/Hatch)**: Object-based, fully scalable embroidery fonts that re-digitize when resized. Considered the gold standard. **Completely proprietary**, locked to Wilcom's ecosystem.
- **Native format collections**: Sets of individual .PES/.DST/.JEF files (one per character per size). **This is the most accessible format for programmatic use**—pyembroidery reads all these formats natively.
- **Ink/Stitch fonts**: Open SVG-based format with JSON metadata, the **only fully open and documented** embroidery font format. ~80+ fonts available. Each glyph is an Inkscape layer with embedded stitch parameters.

For programmatic use, the realistic options are: (1) native format character files read with pyembroidery, (2) Ink/Stitch SVG fonts parsed with lxml, or (3) the Ink/Stitch CLI for batch lettering.

---

## SVG path to stitch data pipeline

**svgpathtools** (github.com/mathandy/svgpathtools) is the standard library for parsing SVG `d=""` attributes. It represents coordinates as complex numbers (`real=x, imag=y`) and provides `Line`, `QuadraticBezier`, `CubicBezier`, and `Arc` segment types. Each segment supports `segment.point(t)` for parametric evaluation and `segment.length()` for arc length. The `svg2paths('file.svg')` function reads all paths from an SVG file.

The full pipeline from SVG to embroidery-ready Shapely polygons:

```python
from svgpathtools import svg2paths
from shapely.geometry import Polygon

paths, attrs = svg2paths('text.svg')
for path in paths:
    subpaths = path.continuous_subpaths()
    contours = []
    for sp in subpaths:
        pts = []
        for seg in sp:
            n = max(2, int(seg.length() / 0.5))  # 0.5mm tolerance
            for i in range(n):
                p = seg.point(i / n)
                pts.append((p.real, p.imag))
        pts.append((sp[-1].point(1.0).real, sp[-1].point(1.0).imag))
        contours.append(pts)
    # Classify outer/inner by containment → build Polygon with holes
```

Alternative libraries include **svgelements** (github.com/meerk40t/svgelements) for full SVG transform/CSS support, and **svg.path** for lightweight parsing. For converting text rendered in a font to SVG paths, use FontForge's Python scripting or Inkscape's "Object to Path" conversion, then parse the resulting SVG.

---

## Three practical implementation strategies

### Strategy A: Pre-digitized character assembly (days to build)

The simplest approach assembles pre-digitized character files without any digitizing:

```python
import pyembroidery
combined = pyembroidery.EmbPattern()
x_offset = 0
for char in "HELLO":
    char_pattern = pyembroidery.read(f"fonts/{char}.pes")
    for s in char_pattern.stitches:
        combined.add_stitch_absolute(s[2], s[0] + x_offset, s[1])
    combined.add_command(pyembroidery.SEQUENCE_BREAK)
    x_offset += char_width[char] + spacing
pyembroidery.write_jef(combined, "output.jef")
```

This requires a collection of pre-digitized character files (many free sets exist online in PES/DST format). **~100 lines of Python**. No fill or satin algorithms needed.

### Strategy B: Ink/Stitch CLI wrapper (hours to build)

Ink/Stitch supports batch lettering from the command line with **80+ professional pre-digitized fonts**:

```bash
./inkstitch --extension=batch_lettering \
  --text="Hello World" --font="Abecedaire" \
  --file-formats="jef" input.svg > output.zip
```

A Python wrapper calls this via `subprocess`. The downside is requiring Inkscape + Ink/Stitch installed as a heavyweight dependency. **~50 lines of Python** for the wrapper.

### Strategy C: Full from-scratch digitizing engine (weeks to months)

The complete pipeline combines all the libraries discussed:

1. **fonttools/freetype-py** → glyph Bézier outlines
2. **Adaptive subdivision** → flattened polygon contours  
3. **Shapely** → `Polygon` objects with classified holes
4. **scipy.spatial.Voronoi** or **trimesh** → medial axis skeleton
5. **Custom rail extraction** → split boundary into left/right rails at skeleton endpoints
6. **stitch_generator** (github.com/bastanja/stitch_generator) → satin stitch coordinates from paths
7. **Scanline fill** (Shapely intersection with parallel LineStrings) → fill stitches for wide areas
8. **pyembroidery** → JEF file output

The **stitch_generator** library is particularly valuable here. It accepts a `Path` object (with position, direction, width, and stitch angle functions) and returns a numpy array of stitch coordinates in millimeters:

```python
from stitch_generator.stitch_effects.path_effects.satin import satin
from stitch_generator.subdivision.subdivide_by_length import regular
effect = satin(spacing_function=regular(2), line_subdivision=regular(4))
stitches = effect(path)  # → ndarray of (x,y) in mm
pattern.add_block((stitches * 10).tolist(), "red")  # ×10 for pyembroidery's 1/10mm units
```

### The hardest algorithmic problems

The three most difficult challenges in Strategy C, in descending order of difficulty:

**Automatic dual-rail extraction** is the hardest problem. Computing the medial axis is tractable, but splitting the glyph boundary into two properly-paired rail chains—handling junctions where strokes meet (like the center of "H" or "K"), branching skeletons, and varying-width sections—requires sophisticated graph traversal of the skeleton tree. This is why Ink/Stitch requires manually-drawn rails and why every professional tool uses pre-digitized fonts rather than automatic digitizing for production lettering.

**Corner and junction handling** in satin columns requires splitting columns at sharp angles, managing stitch crowding on inner curves, and connecting separate column sections with travel stitches. Serif fonts are particularly challenging—pointed serifs, ball terminals, and bracket curves each need different treatment.

**Thin-versus-thick classification** must determine whether each region of a glyph should use satin stitches (2–12mm width), fill stitches (>12mm), or running stitches (<2mm). This requires computing the local width along the medial axis—the distance transform gives this, but thresholding and transitioning between stitch types at boundaries is non-trivial.

## A pragmatic path forward

For a working tool with professional-quality output, **Strategy B** (Ink/Stitch CLI) delivers immediately with 80+ fonts. For a self-contained Python tool, **Strategy A** (pre-digitized assembly) is achievable in a weekend. For Strategy C, the recommended v1 simplification is: use a **monoline stroke font** (single-line fonts like Hershey fonts, available as SVG), trace each stroke with satin stitches using stitch_generator, skip fill stitches and underlay entirely, use fixed character spacing, and output via pyembroidery. This avoids the medial axis problem completely—monoline fonts are already single-stroke paths that can be directly widened into satin columns by treating the stroke as the spine and generating rails at a fixed offset using Shapely's `buffer()`. Iterate from there toward filled fonts, underlay, and pull compensation as the algorithms mature.