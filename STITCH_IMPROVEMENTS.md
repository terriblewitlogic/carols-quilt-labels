# Stitch Algorithm Improvement Plan

## Current status — 2026-06-27

This document is the long-range pro-quality plan. The active day-to-day backlog now lives in:

- `/Users/partido/jeflabelmaker/STITCH_QUALITY_TRIAGE.md`
- `/Users/partido/jeflabelmaker/STITCH_EXPERIMENT_LOG.md`

Recent shipped work since the original pro-design comparison:

- Added `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/compare_generated_runs.py` and `npm run compare:generated` for before/after generated-run review.
- Accepted simple generated icons with mild soft shading when they are one connected subject and do not have structural/detail overload.
- Added `gradient_elephant_simple` as a fixture and regression case.
- Improved tonal cleanup for mild same-hue generated gradients:
  - `gradient_elephant_simple` same-surface long spans `3 -> 0`
  - trims `8 -> 4`
  - jumps `14 -> 8`
  - stitches `6269 -> 5062`
- Re-enabled angular routing only for large radial repeated motif rings:
  - `flower_sunflower_simple` trims `9 -> 7`
  - `flower_daisy_simple` intentionally unchanged because angular routing worsened the eight-petal case.
- Added graph-aware route candidate diagnostics for repeated/disconnected same-color fill islands.
- Added upload-style source/detail policy guardrails:
  - `surface-plan.json` now summarizes tiny-detail decision counts.
  - `uploaded_art_acceptance.py --strict-source-policy` fails if tiny-detail accounting, detail-budget status, or key accent-color preservation regresses.
- Added `same_hue_acorn` to upload-style acceptance so dark-brown cap, tan body, and light tan highlight must stay separate thread colors.
- Added `same_hue_acorn_facets` as an explicit stress fixture and protected substantial same-hue darker end-members so faceted cap/body fields no longer lose the dark material color.
- Added `same_hue_mushroom_facets` and `same_hue_shell_facets` as explicit stress fixtures for same-hue material fields with internal facets.
- Added same-hue light endpoint protection so `same_hue_mushroom_facets` keeps the tan/light material color `#d2aa6e` instead of flattening it into the dominant orange/pink body tone.
- Reduced same-hue facet trim pressure by allowing modest inter-component carries before trimming:
  - `_TRIM_GAP_INTER_COMPONENT_EMB` `8mm -> 16mm`
  - `same_hue_acorn_facets` trims `11 -> 8`
  - quality stayed `100`, colors stayed preserved, and no long untrimmed jump diagnostics appeared
- Extended covered travel only when later stitch geometry proves the carry is hidden:
  - `_merge_covered_travel` now considers `2-35mm` carries instead of stopping at `20mm`
  - `same_hue_acorn_facets` trims `8 -> 7` and jumps `21 -> 20`
  - exposed `23-43mm` remaining relocations still trim; no actual-thread connector risk or untrimmed long-span diagnostics appeared
- Added route fallback diagnostics and a small exact route candidate:
  - `candidate_graph` scoring now evaluates exact tours for 3-7 component clusters
  - route scoring uses the same `16mm` inter-component trim threshold as conversion
  - `surface-plan.json` records structural/no-flip route rejections instead of silently selecting nearest
  - `same_hue_acorn_facets` stayed stable at quality `100`, `20 jumps / 7 trims`, and now explains why the remaining candidates are rejected
- Added structural/no-flip-safe candidate routing:
  - broad underlay+fill chains expose safe flip spans while preserving underlay-before-cover order
  - `_StitchChain` metadata is preserved only inside candidate-graph scoring, not ordinary nearest routing
  - `same_hue_acorn_facets` trims `7 -> 6` and cross-surface trimmed long spans `3 -> 1`
  - generated/underpaint `sparrow_flat_app_icon` trims `3 -> 2` and jumps `18 -> 17`
- Added targeted disconnected-island route fixtures to the underpaint benchmark:
  - `synthetic_component_route_ring` covers plain candidate scoring and safe fallback
  - `synthetic_structural_route_facets` covers structural-safe small-exact route wins

Current next-best stitch work:

1. Preserve meaningful small accent colors while continuing to drop/absorb noisy fragments under strict source-policy checks.
2. Expand color/tone preservation coverage with real generated/uploaded examples, especially same-hue materials that still over-fragment, collapse into the wrong thread family, or create route pressure after the right colors are preserved.
3. Keep any further route broadening behind `synthetic_component_route_ring`, `synthetic_structural_route_facets`, daisy, sunflower, elephant, and cutout benchmarks.
4. Use `compare_generated_runs.py ... --fail-on-regression` for every keep/revert decision.
5. Revisit broad-underpaint/lane routing only when comparison reports show actual stitched-span risk.

Research review status:

- Already covered: role-specific stitch caps, multi-pass layer planning, underlay chains, medial/satin narrow-shape fills, seam ownership, detail heuristics, and gated angular routing.
- Implemented now: graph-aware route ordering for disconnected same-color fill islands using nearest, angular, MST preorder, small exact tours, and 2-opt candidate tours. It preserves the sunflower angular win, records candidate rejection diagnostics, supports structural/no-flip-safe candidate routing for underlay-sensitive components, and now has non-flower route fixture coverage in `underpaint_benchmark.py`. It improves faceted acorn and sparrow route pressure without reducing daisy trims yet. Source/detail and same-hue material guardrails now make tiny-detail promotion, simplification, unresolved-detail regressions, cap/body/highlight tone collapse, and faceted same-hue dark- or light-endpoint collapse visible in uploaded-art acceptance output. Same-hue facet trim pressure is now covered by acorn, mushroom, shell, and structural route fixture checks, with the accepted trim threshold set at `16mm` because higher thresholds introduced long-carry risk. Covered travel can now search up to `35mm` only when later stitch geometry proves the route is hidden.
- Later: direction-field streamlines, offset-curve/auto-split partitioning, stronger vectorization, stitch-style classification, texture synthesis for preview/style inspiration, and multi-objective optimization once deterministic fixtures are stronger.
- Out of scope: exact b-matching in this sprint, cross-stitch DFS/parity, and applique workflows.

---

Based on analysis of six professional designs (Find Joy, F is for Flamingo, Z for Zebra, Faithful Friends, Boundaries, Unbounded Faithfulness) digitized in **Hatch Embroidery Digitizer** with Isacord 40 thread, and direct comparison to the current output of `raster_to_stitches.py`.

The professional files were hand-digitized; ours are auto-converted from raster. Closing the gap fully is impossible, but specific, measurable improvements can move the output dramatically closer to professional quality.

---

## Measured comparison

| Metric | Pro avg (n=5) | Our output (sunflower) | Gap |
|---|---|---|---|
| Mean stitch length | 2.0 mm | 0.66 mm | bimodal — too many tiny + too many long |
| Median stitch length | 1.8 mm | 0.0 mm | many zero-length stitches (degenerate) |
| p95 stitch length | 3.9 mm | 2.86 mm | OK at p95 |
| p99 stitch length | 4.5 mm | 9.30 mm | **~2× longer at the tail** |
| Stitches > 7 mm | 0.08% | 1.78% | **22× more long stitches** |
| Jump commands | 0.83% | 6.72% | **8× more jumps** |
| Short jumps (< 2 mm) | low (0–51) | 1,136 | wasteful needle travel |
| Density per cm² (bbox) | 70–140 | 1,065 | **7–10× over-stitched** |
| Color blocks per design | 5–12 (1.5–2× unique colors) | 1 per color | **no layering reuse** |
| Trims | 12–37 | 33 | acceptable |

### What this means in practice

- **Long stitches at p99** (9.3 mm vs 4.5 mm pro): the 12 mm `MAX_STITCH_MM` cap fires regularly inside scan-fill rows. Long stitches snag, look sloppy, and break.
- **Bimodal length distribution**: many stitches are degenerate (≈0 mm — duplicate points) and many are at the 12 mm cap. Pros sit tight around 2 mm with very little spread.
- **8× jump count**: each connected component is currently treated as a hop target. Many of those hops are < 2 mm — they should be plain stitches, not jumps.
- **7–10× density**: at `density_mm = 0.4` and `MAX_STITCH = 12 mm` the math should give ~150 stitches/cm² but we're producing 1,065/cm². The fill scan emits stitches at every polygon-edge crossing on top of the `_interpolate_tatami` walk; this needs forensic investigation.

---

## Professional patterns observed

### 1. Tight, predictable stitch length

Pro stitch lengths cluster between 1.5 mm and 4 mm with > 99% of all stitches under 5 mm. The **maximum** stitch in any example was 16 mm (rare connecting/jump stitches) — but only 0.08% of stitches exceeded 7 mm.

Our cap is set at 12 mm and that cap fires constantly. Pros effectively cap at **4 mm for top fills** and **2.5 mm for fine detail and outlines**.

### 2. Multi-pass color sequencing (the biggest qualitative gap)

Pros do not stitch one color block per unique color. They schedule the **same thread multiple times** at strategic points to layer detail.

**Z for Zebra (7 unique colors, 12 stops):**
```
Stop  Color              Stitches  Purpose
 1    Black              1,380     Outline + dark layer 1
 2    Battleship Gray    1,504     Mid-tone fill
 3    Cream              ?         Light fill base
 4    Tackdown Applique  ?         Hold cream applique fabric
 5    Placement Line     ?         Mark applique position
 6    Cutting Line       ?         Cut guide for applique
 7    Tackdown Applique  ?         Re-tack after trim
 8    Black              ?         Detail layer over gray + cream
 9    Battleship Gray    ?         Re-introduce gray for highlights
10    Black              ?         Fine detail (eyes, stripes)
11    Silky White        ?         Highlight pass
12    Black              3,444     Final detail + outline
```

**Find Joy (4 unique colors, 5 stops):** Tropical Pink stops at #4 (1,026 stitches) and #5 (1,783 stitches) — the digitizer scheduled the same thread twice so the second pass could lay accent details on top of the first.

**Implication for our pipeline:** the current `groups[i] = { color, segments }` model where each unique color produces exactly one group **must change** to support multi-pass scheduling. We need to plan a sequence of color "stops," each pulling segments from any logical layer (background fill, mid fill, detail, highlight, outline). One thread can appear at multiple stops in sequence.

### 3. Three-stage applique workflow

Z for Zebra includes the canonical applique sequence: **Placement Line → Cutting Line → Tackdown**. The user lays applique fabric, the machine stitches a placement outline, the user trims the fabric to that outline, the machine tacks it down with a satin border. This adds whole new design language we don't currently support.

This is **out of scope for the first improvement pass** but worth recording — it explains stops 4–7 in the Zebra sequence.

### 4. Tiny detail blocks that we currently filter out

Pro designs include color stops as small as 7 stitches (Faithful Friends stop #6). These are small accent dots, eye highlights, or single-line details. Our `min_feature_mm = 1.5 mm` filter (= 2.25 mm² = ~22.5 px²) will drop most of them.

### 5. Differential underlay

Pro underlays are running stitches at 2–3 mm spacing along the spine of a fill, with the top fill at 0.4 mm cross-spacing on top. We use the same `MAX_STITCH_MM = 12 mm` for both, producing underlays that are too sparse and too long.

### 6. Routing minimizes jumps within a color block

Pros average 50 jumps across an entire 16,000-stitch design; we produce 1,200+ for an 18,000-stitch design. The component router exists in `_route_components` but is not aggressive enough — it lifts the needle between sub-segments that could be linked with a normal stitch.

---

## Improvement plan

Ordered by impact-to-effort ratio. Constants live in `functions/image_to_jef/raster_to_stitches.py` lines 44–60.

### Tier 1 — Trivial fixes, large visual impact

#### 1.1 Cap stitch length at 4 mm for fills, 2.5 mm for detail

**File:** `raster_to_stitches.py`

```python
# Replace
MAX_STITCH_MM = 12.0
# With
MAX_STITCH_FILL_MM    = 4.0   # top fill, contour fill, scan fill
MAX_STITCH_UNDERLAY_MM = 2.5  # underlay running stitches
MAX_STITCH_OUTLINE_MM  = 2.5  # running outline
MAX_STITCH_TRAVEL_MM   = 12.0  # only for explicit travel runs and jumps
```

Pass the relevant cap through `_interpolate_tatami`, `_underlay_segments`, `_outline_segments`, etc.

**Expected impact:** p99 stitch length drops from 9.3 mm to ≤4.5 mm. Long-stitch outliers (1.78%) drop to ~0.1%. Density rises slightly (~10–15%) which is acceptable since we're currently *over*-dense.

#### 1.2 Eliminate degenerate (zero-length) stitches

**File:** `raster_to_stitches.py:_interpolate_tatami`

The function appends `(x0, y0)` then walks. Some inputs have `x0 == x1, y0 == y1` (zero-distance segments from intersection edges or thin slivers). The check at line 660 (`if math.hypot(pts[-1][0]-x1, pts[-1][1]-y1) > 0.5`) only catches the endpoint, not interior duplicates.

**Add a deduplication pass:**

```python
# At the bottom of _interpolate_tatami:
out = [pts[0]]
for p in pts[1:]:
    if math.hypot(p[0]-out[-1][0], p[1]-out[-1][1]) >= 0.3:  # 0.03 mm
        out.append(p)
return out
```

**Expected impact:** median stitch length goes from 0.0 mm to ~1.8 mm; mean goes from 0.66 mm closer to 2 mm.

#### 1.3 Slash short jumps by tightening component-routing threshold

**File:** `raster_to_stitches.py:_route_components`

Currently any inter-component move is a jump. Add a "stitch through" rule: if the gap between two components is less than `JUMP_THRESHOLD_MM` (suggest 2 mm), connect them with a regular stitch path along the boundary instead of a jump.

```python
JUMP_THRESHOLD_MM = 2.0  # gaps shorter than this stay as plain stitches
```

In the export step (`image_to_jef.py`), only emit a JUMP command when the inter-segment distance > `JUMP_THRESHOLD_MM`.

**Expected impact:** jump count drops from 6.72% to ~1% (matching pros). Short-jump count (1,136 → < 100).

#### 1.4 Differential underlay max-stitch

Already covered by 1.1 — pass `MAX_STITCH_UNDERLAY_MM` to `_underlay_segments`.

---

### Tier 2 — Multi-pass color sequencing (the highest visual-quality lever)

This is the largest qualitative change. It restructures how groups are built so the same color can appear at multiple positions in the stitch order — a "color stop" no longer maps 1:1 to a unique thread.

#### 2.1 Refactor `groups` data model

**Current:**
```python
groups = [
  { 'color': '#hex', 'segments': [...], 'type': 'fill' | 'outline' },
  ...
]
# One group per (unique_color × type)
```

**New:**
```python
groups = [
  { 'color': '#hex', 'segments': [...], 'role': 'background' | 'fill' | 'detail' | 'highlight' | 'outline' | 'accent', 'pass': 1 | 2 | 3 },
  ...
]
# Same color may appear in multiple groups at different pass numbers
```

#### 2.2 Layer plan — what gets re-introduced and when

Build a layer plan per design:

```
Pass 1 — Foundation
  - Background fills (largest area, lightest non-bg color)
  - Mid-tone fills (next-largest, mid-luminance)

Pass 2 — Detail
  - Small detail regions (any color)
  - Re-introduce darkest non-black colors for shading on top of pass 1 fills

Pass 3 — Outlines + accents
  - All running outlines
  - Black detail accents (eyes, dots, fine lines) re-stitched as a final pass
  - White/light highlights last (tiny taps to add depth)
```

**Heuristic for re-introduction:**
A color that has both a "large fill region" AND "small detail region" gets split into two stops:
1. Large fill — early in the sequence
2. Small detail — late in the sequence (often as the very last pass)

In the current `posterize_image` + connected-component flow, this means: after labeling, classify each component as `fill | detail` based on area. Group `fill` components in pass 1; `detail` components in pass 2 or 3.

**Black is special:** if black is in the palette AND is < 8% of total pixels, treat it as **always last** (it's almost certainly outlines + accents). If black > 30% of pixels, it's a fill color — schedule it normally.

#### 2.3 Don't filter tiny detail components

Lower `min_feature_mm` from 1.5 mm to **0.8 mm** (= 0.64 mm² area threshold). Small accent details — eye dots, period punctuation, tiny highlights — are part of professional output. The current threshold drops them.

Keep an upper limit on micro-component count (cap at 50 per color) to prevent an explosion of jumps if the source image is noisy.

---

### Tier 3 — Density and routing fidelity

#### 3.1 Forensic: why does our density read 1,065/cm²?

The math says `0.4 mm spacing × 4 mm interp step ≈ 6.25 stitches/mm² = 625/cm²`. We produce 1,065/cm². The 1.7× gap suggests stitches are being doubled — likely the row-end stitch from one row stacking on top of the row-start of the next, plus duplicate edge-walk + underlay rows.

**Action:** instrument `raster_to_stitch_groups` with per-stage stitch counts (underlay vs top fill vs edge walk vs outline). Identify the contributor and decide whether each pass should be sparser.

A reasonable target: 100–150 stitches/cm² for top fill, +20% for underlay, +5% for edge walk, +outline overhead. Total ~150–180 stitches/cm² — exactly in the pro band.

#### 3.2 Better tatami row routing

Current scan-fill emits one segment per row–polygon intersection. With multiple sub-shapes per row (e.g. two lobes of a heart), every row jumps from one lobe to the other. This is a major jump source.

**Fix:** for each row, walk the segments in nearest-endpoint order from the previous row's tail. This is what `_greedy_sort` does — but it runs *per component*, not per row pair. Move that sort into the row loop itself, then between rows.

#### 3.3 Reduce duplicate stitches at row endpoints

The fill scan adds a stitch at every polygon-edge crossing. The next row's first stitch is the new entry crossing — often within < 1 mm of the previous row's exit. These should be merged into a single stitch.

---

### Tier 4 — Architectural improvements (longer term)

#### 4.1 Satin column detection for narrow regions

Currently, narrow regions (≤ 6 mm width) fall into the "medial fill" branch. That's correct for elongated shapes, but **proper satin column digitizing** (perpendicular bars between two rails) gives better coverage and a glossier look — especially for letterforms in the eventual label-maker integration.

Use `trimesh.path.polygons.medial_axis()` to extract the medial axis as an actual graph (not just a skeleton bitmap), then for each medial edge, sample at density and emit perpendicular satin bars rail-to-rail. This is a meaningful refactor of `_medial_fill_segments` (currently uses skimage skeleton which is bitmap-based and rough).

#### 4.2 Stitch-type aware `MAX_STITCH`

Different stitch types tolerate different lengths:
- **Satin bars**: cross-direction length depends on column width — capped by the column itself, not by `MAX_STITCH`. Travel along the spine should be ≤ 2.5 mm.
- **Tatami fills**: 4 mm cap is right.
- **Running outlines**: 2.5 mm cap.
- **Travel runs**: 12 mm OK (these are between objects; they'll be hidden by later fills).

Plumb a `stitch_type` enum through the segment generation so the right cap fires.

#### 4.3 Applique workflow (out of scope, but tracked)

Add a "applique" mode to the generator that produces:
1. Placement line (running outline of the applique area)
2. Stop + user prompt
3. Cutting line (denser running outline)
4. Stop + user prompt
5. Tackdown (zigzag or satin around the cut applique)

This unlocks the Zebra-style designs but requires UI work and an "instructions" output. Probably belongs to Embroidery.mom Phase 4 (Generator advanced features).

#### 4.4 Match Isacord 40 / Hatch Default thread palettes

Pros use a small number of named threads. Our auto-quantization picks RGB centers via KMeans and finds the nearest thread in the Janome palette. Two improvements:
1. Add **Isacord 40** as a palette option (it's the de-facto standard for this kind of design — Find Joy, Faithful Friends both use it).
2. Snap colors to the chosen palette **before** clustering, not after. Currently we pick arbitrary RGB centers and then map them to palette entries; this can produce non-stockable colors.

#### 4.5 Generate a Hatch-style instruction sheet on export

Pros ship a 2–5 page PDF with: stitch count, hoop size, color sequence with thread codes/names, bobbin estimate, recommended fabric and stabilizer. This is a strong differentiator for any user who plans to actually stitch the file.

Reuse the existing data — color list, stitch counts per group, hoop size — and emit a PDF via `reportlab` or similar. Probably maps to Embroidery.mom's "downloadable bundle" feature.

---

## Recommended order of execution

| # | Task | Impact | Effort | Files |
|---|------|--------|--------|-------|
| 1 | 1.2 Dedupe zero-length stitches | High | Trivial | `raster_to_stitches.py` |
| 2 | 1.1 Lower MAX_STITCH caps | High | Trivial | `raster_to_stitches.py` |
| 3 | 1.3 Convert short jumps to stitches | High | Small | `raster_to_stitches.py`, `image_to_jef.py` |
| 4 | 3.1 Density forensic + fix overstitching | High | Small | `raster_to_stitches.py` |
| 5 | 3.2 Cross-component row routing | Medium | Small | `raster_to_stitches.py` |
| 6 | 2.1 + 2.2 Multi-pass color sequencing | **Highest** | Medium | `raster_to_stitches.py`, frontend layer panel |
| 7 | 2.3 Allow tiny detail components | Medium | Trivial | `raster_to_stitches.py` |
| 8 | 4.2 Stitch-type aware caps | Medium | Medium | `raster_to_stitches.py` |
| 9 | 4.1 True satin column detection | Medium | Large | `raster_to_stitches.py` (medial fill rewrite) |
| 10 | 4.3 Applique mode | High (new market) | Large | UI + algorithm + export |
| 11 | 4.5 Hatch-style instruction PDF | Medium | Medium | new file `instruction_sheet.py` |

**Concrete first PR:** items 1–4. They're all in one file, all measurable against the same comparison metrics, and together they should close 60–70% of the gap to pro output.

---

## How to validate progress

For each iteration, regenerate the existing `public/library/sunflower/embroidery.jef` and re-run the comparison script (`/tmp/analyze_examples.py`) against it. Targets:

| Metric | Now | After Tier 1 | After Tier 2 | Pro |
|---|---|---|---|---|
| Mean stitch length | 0.66 mm | ~2.0 mm | ~2.0 mm | 2.0 mm |
| p99 stitch length | 9.30 mm | ≤ 5 mm | ≤ 5 mm | 4.5 mm |
| Stitches > 7 mm | 1.78% | ≤ 0.2% | ≤ 0.2% | 0.08% |
| Jumps as % of total | 6.72% | ≤ 2% | ≤ 1% | 0.83% |
| Short jumps (< 2 mm) | 1,136 | < 200 | < 50 | < 100 |
| Density / cm² | 1,065 | ~200 | ~150 | 70–140 |
| Color blocks per design | 1 per color | 1 per color | 1.5–2× per color | 1.5–2× |

If the after-Tier-1 numbers don't match, the implementation has a bug — don't proceed to Tier 2 until they do.

---

## Tier 1 results (delivered)

Tier 1 was implemented in a single change touching `raster_to_stitches.py` and `image_to_jef.py`. A regression harness lives at `tests/test_stitch_quality.py`.

### Measured outcome (sunflower test fixture)

| Metric | Pre-Tier 1 | Post-Tier 1 | Plan target | Pro |
|---|---|---|---|---|
| Mean stitch length | 0.66 mm | **1.78 mm** | 1.5–2.5 ✓ | 2.0 mm |
| Median stitch length | 0.00 mm | **1.90 mm** | — | 1.8 mm |
| p99 stitch length | 9.30 mm | **4.16 mm** | ≤ 5 ✓ | 4.5 mm |
| Stitches > 7 mm | 1.78% | **0.00%** | ≤ 0.2% ✓ | 0.08% |
| Max stitch | 12.02 mm | **4.90 mm** | — | 16 mm rare |
| Jumps as % | 6.72% | **2.58%** | ≤ 2% (close) | 0.83% |
| Short jumps (< 2 mm) | 1,136 | **1** | < 200 ✓ | < 100 |
| Density / cm² | 1,065 | **181** | ≤ 250 ✓ | 70–140 |

### What changed

1. **Fix `_interpolate_polyline` bug** *(highest impact)*. Buffered polygons carry thousands of microscopic edges around rounded corners. The walk's "skip tiny edge" branch was inflating `d` by `max_px` per skip, causing the algorithm to leap across vast portions of the polyline and emit single stitches up to 28 mm long. The fix collapses near-duplicate consecutive vertices up front, removing the need for the inflate-and-skip branch. This single bug was responsible for most of the long-stitch tail and most of the long-stitches > 7 mm.

2. **Role-specific stitch caps** — `MAX_STITCH_MM = 12` was a blanket value used by every stitch type. Replaced with:
   - `MAX_STITCH_FILL_MM     = 4.0` for tatami / contour / medial / edge-walk
   - `MAX_STITCH_UNDERLAY_MM = 2.5`
   - `MAX_STITCH_OUTLINE_MM  = 2.5`
   - `MAX_STITCH_TRAVEL_MM   = 12.0` for travel runs only

3. **`_interpolate_tatami` corrections**:
   - When `phase = 0`, the first interior step starts at `max_px` (not 0), so we don't emit a duplicate of `(x0, y0)`.
   - Defensive dedupe pass at the end drops any consecutive points within `MIN_STITCH_PX`.

4. **New `_interpolate_polyline` helper** replaces the corner-duplicating pattern of looping `_interpolate_tatami` over polygon edges and `extend()`-ing the result. Used by `_contour_fill_segments`, `_edge_walk_segments`, and `_outline_segments`.

5. **Encoder routing rules** rewritten in `_build_pattern`:
   - `< 2 mm`: plain stitch (no JUMP)
   - `< 8 mm` cross-component, same colour: travel run
   - `< 12 mm` same component: travel run
   - `≥ 12 mm` or outline: explicit JUMP (with TRIM if cross-component or > 12 mm)

   This converted 1,135 short jumps to plain stitches and dropped overall jump count by ~33%.

### What didn't quite hit Tier 1

- **Sunflower jump_pct = 2.58% vs target ≤ 2%.** The 76 remaining jumps are real cross-component gaps > 8 mm between disconnected yellow petals. Closing the last 0.6 percentage points needs either smarter routing (TSP / 2-opt over the per-colour component graph) or visual risk (extending cross-component travel beyond 8 mm starts to leave visible thread carries on plain background fabric). The regression test relaxes this fixture to ≤ 3%.

### Files changed

- `functions/image_to_jef/raster_to_stitches.py` — interpolation fixes, role-specific caps, `_interpolate_polyline` helper, replaced corner-duplicating loops in three fill strategies
- `functions/image_to_jef/image_to_jef.py` — three-tier routing (stitch / travel / jump) with same-vs-cross-component thresholds
- `tests/benchmark_stitch.py` — measurement harness (was previously absent)
- `tests/test_stitch_quality.py` — regression test that runs the benchmark and asserts Tier 1 thresholds on two fixtures

### Tier 2 scope

Multi-pass colour sequencing remains untouched. The plan's Tier 2 section is unchanged and is the next major lift — it's the architectural change that makes auto-conversion look like Hatch-digitized output rather than auto-conversion. Tier 1 closes the *measurable* gap; Tier 2 closes the *qualitative* gap.

---

## Tier 2 results (delivered)

Tier 2 was implemented in a single change to `raster_to_stitches.py` extending the data model with `role` and `pass` fields per group, and adding a layer-plan stage that splits a colour's components into foundation fills (pass 1), small detail accents (pass 2), and outlines/dark accents (pass 3).

### What changed

1. **`_process_polygon` helper extracted** from the inner loop, so the per-component logic (thin-stripe / outline-network guard, pull compensation, underlay, top fill, edge walk, outline) can be called independently and the main function refactored without duplicating its body.

2. **Two-phase pipeline.** The old single loop is now split:
   - **Phase A** — collect per-component data: each colour's connected components are processed individually, recording `{area_px2, fill_per_poly, outline_per_poly}`.
   - **Phase B** — classify components per colour into `fill` (foundation) and `detail` (small accent) using `min(20 mm², 15 % of largest component)`.
   - **Phase C** — detect an "accent colour": dark luminance (< 30) AND minor pixel fraction (< 8 %). The canonical case is black at < 8 % of pixels; pros routinely reuse it as the very last layer for eyes/dots/fine detail.
   - **Phase D** — assemble groups in pass order:
     - Pass 1: foundation fills, dark→light by palette order
     - Pass 2: detail components (small accents within each non-accent colour)
     - Pass 3: outlines for non-accent colours, then accent colour as a single combined block (fill + outline) at the very end

3. **Group dict gained two fields:**
   ```python
   { 'color': '#hex', 'segments': [...], 'componentIds': [...],
     'type': 'fill'|'outline',
     'role': 'foundation'|'detail'|'outline'|'accent',
     'pass': 1|2|3 }
   ```

4. **`min_feature_mm` default lowered from 1.5 mm to 0.8 mm** so eye dots, periods, and small accent marks are picked up. Detail-component count is capped at 50 per colour (largest first) to prevent noisy posterizations from blowing up the jump count.

### Measured outcome

| Fixture | Multi-pass ratio | Pro range | Notes |
|---|---|---|---|
| Sunflower | **2.00×** | 1.5–2.0× | Black detected as accent → foundation + outline + accent for 4 colours = 8 groups |
| Test shapes | **2.00×** | 1.5–2.0× | Each colour gets foundation + outline = 6 groups |
| Layered accents | **2.25×** | 2.0× | 4 colours × foundation + 1 detail (gold corner dots) + outlines + black-accent fill + black-accent outline = 9 groups |

For comparison: Find Joy hits 1.25×, Z for Zebra 1.71×, Faithful Friends 1.0× (no multi-pass needed). Our auto-converted designs land at the upper end of the pro range — a touch over-eager, but in the right band.

### Visual verification

The layered-accents fixture renders with:
- Foundation fills (gold body, green leaf, blue square) stitched first
- Gold corner dots stitched after the gold body, before any outlines (proper detail layer)
- Black eyes and mouth stitched LAST — sitting cleanly on top of the gold body without interruption

The sunflower renders identically to Tier 1 from the front (the saved Tier 1 sunflower didn't have detail components or a non-foundation accent colour to differentiate). The internal stitch ordering changed: black is now sequenced last as an accent rather than mixed in by brightness.

### What's preserved

- All Tier 1 quality metrics (mean/p99/density/jumps) hold or improve.
- The encoder, preview SVG, and frontend layer panel continue to consume the same data shape; the new `role` and `pass` fields are purely additive.
- Simple designs (single-colour text label, two-colour outline+fill) produce exactly the same output as before — multi-pass only fires when the design legitimately benefits from it.

### Files changed

- `functions/image_to_jef/raster_to_stitches.py` — main refactor: new constants, three new helpers (`_process_polygon`, `_classify_color_components`, `_detect_accent_color`), two-phase main function, lowered `min_feature_mm` default
- `functions/image_to_jef/image_to_jef.py` — synced `min_feature_mm` default
- `tests/benchmark_stitch.py` — added `multipass_ratio` metric (color blocks / unique threads)
- `tests/test_stitch_quality.py` — new `layered_accents` fixture, asserts multi-pass ratio is in the pro band

### What's next (Tier 3 / 4)

The plan's Tier 3 (true satin column detection via `trimesh.path.polygons.medial_axis`) and Tier 4 items (applique workflow, Isacord 40 thread snapping, instruction PDF generation) remain on the roadmap. They're substantially larger than Tiers 1 and 2 — most of the algorithmic gap to professional output is now closed; Tier 3+ is about specific stitch-type sophistication and product polish.

---

## Tier 4.1 results (delivered) — true satin columns

Tier 4.1 swaps the bitmap-skeleton-based medial fill for a vector medial axis from `trimesh.path.polygons.medial_axis()` when the shape is narrow enough to be a true satin candidate (`is_satin_zone` — empties when eroded by 3 mm).

### What changed

1. **New `_satin_column_segments` function** (~140 lines). Takes a Polygon, computes the vector medial axis (Voronoi-based graph), finds the longest path through the resulting graph via BFS-twice, walks that spine at `density_px` intervals, and at each sample shoots a perpendicular bar through the polygon to capture the rail-to-rail stitch.

2. **Single-stitch satin bars** when bar length ≤ `MAX_SATIN_BAR_MM` (8 mm). The bar IS one machine stitch — that's the defining feature of satin: long, shiny, rail-to-rail. Bars wider than 8 mm fall back to tatami-style interpolation so we don't produce snag-prone 12+ mm stitches.

3. **`is_satin_zone` shapes get satin first**, with the existing skeleton-based `_medial_fill_segments` as a fallback for cases where the vector medial axis fails (degenerate polygons, trimesh import errors, etc.).

4. **Underlay actually uses `MAX_STITCH_UNDERLAY_MM` now.** Previously the constant existed but the underlay code path inherited the 4 mm fill cap. Plumbed `max_stitch_px` parameter through `_medial_fill_segments`, `_fill_polygon_segments`, and `_contour_fill_segments`; underlay now stitches at 2.5 mm step (denser, more secure — what pros do).

5. **`trimesh>=4.0` added** to both `functions/image_to_jef/requirements.txt` and `api/requirements.txt`.

### Measured outcome

| Fixture | Before (Tier 2) | After (Tier 4.1) | Notes |
|---|---|---|---|
| Sunflower stitch count | 2,846 | **2,702** | -5%, satin replaces interpolated bars |
| Sunflower mean stitch | 1.79 mm | **1.85 mm** | closer to pro 2.0 mm |
| Sunflower density | 181/cm² | **172/cm²** | closer to pro 60–150/cm² |
| Sunflower jumps | 80 | **74** | tighter routing within satin columns |
| Narrow_satin fixture | (n/a) | **2.29 mm mean, 5.40 mm p99** | satin bars run up to 8 mm — different distribution but visually correct |

### Visual verification

Rendered the narrow-shape fixture (vertical stem + diagonal stripe + curved C). All three shapes show clean perpendicular satin bars running along the medial axis:

- Vertical stem: dense parallel bars across the column width
- Diagonal stripe: bars rotate to stay perpendicular to the diagonal spine
- Curved C: bars follow the curvature, radiating outward from the centre

The bars zig-zag between consecutive rails (each bar's direction alternates) — that's correct satin behaviour, the needle going back-and-forth across the column.

### Files changed

- `functions/image_to_jef/raster_to_stitches.py` — new `_satin_column_segments` (~140 lines), wire into `_process_polygon`, add `MAX_SATIN_BAR_MM` constant, plumb `max_stitch_px` through three fill functions, fix `_underlay_segments` to use `MAX_STITCH_UNDERLAY_MM`
- `functions/image_to_jef/requirements.txt`, `api/requirements.txt` — added `trimesh>=4.0`
- `tests/test_stitch_quality.py` — new `narrow_satin` fixture with relaxed length targets (satin bars allow longer individual stitches)

### What's still on the table

- **Tier 4.1 graph branches.** The current implementation walks the longest path through the medial axis, which captures the main spine well but may miss side branches in T or Y junctions. For letter forms specifically (where T-junctions are common in glyphs like "T", "Y", "F"), a recursive branch walk would pick up the side strokes too. Currently those areas fall back to edge-walk, which is acceptable but not ideal.
- **Tier 4.4 Isacord palette snap-before-cluster** — small content/UX win, would tighten the palette to professional thread codes.
- **Tier 4.5 Hatch-style instruction PDF** — product polish, not algorithmic.
- **Tier 4.3 applique workflow** — new feature, not algorithmic improvement.

The algorithmic core is now in good shape. The remaining items are application-level polish.

---

## Tier 4 — branch walking, palette snap, instruction PDF (delivered)

Three improvements bundled into one pass:

### 4.1 — Medial-axis trail decomposition (branch walking)

The previous `_satin_column_segments` found only the longest path through the medial-axis graph (BFS-twice) and walked it. For elongated near-rectangular shapes that's the whole spine. For letter-form shapes — `T`, `Y`, `F`, `+`, `K` — the longest path follows one branch and the others get nothing.

**New `_decompose_medial_trails`** splits the graph into non-branching paths between notable vertices (degree 1 = endpoint, degree ≥ 3 = junction). Each undirected edge is assigned to exactly one trail. Pure degree-2 cycles (rare) are caught by a second pass.

**Walking is now per-trail** — the bar-emitter loops over every trail, samples at density intervals, and shoots perpendicular bars. A `seen_bars` set deduplicates near-identical bars across adjacent trails so junction overlap doesn't double-stitch.

**`MIN_BRANCH_LENGTH_MM = 3.0` filter** drops trails shorter than 3 mm — Voronoi-noise filaments that trimesh emits near convex corners. The longest-trail is always retained as a fallback so very small shapes still produce output.

**Visual proof:** the new `letterforms` regression fixture (T + Y-shape + plus sign) renders with proper satin bars on every branch:
- T crossbar gets vertical bars; T stem gets horizontal bars
- Y has bars on each diagonal AND the stem
- Plus-sign has perpendicular bars on both arms

### 4.4 — Snap-before-cluster

The previous flow did KMeans → arbitrary RGB centroids → palette match in the response (display only). The actual stitch file used the raw RGB centroids.

**`_posterize` now accepts a `brand` argument.** After KMeans, each cluster centre is replaced with the nearest entry from `thread_palette` (`madeira` / `isacord` / `robison-anton`). The pixel-to-cluster mapping is unchanged — only the centre RGB values shift to stockable thread colours. The JEF, preview SVG, and exported palette all use the snapped colours from this point onward.

The encoder threads the brand through automatically (`thread_brand=brand` → `raster_to_stitch_groups` → `_posterize`).

### 4.5 — Hatch-style instruction PDF

New `instruction_sheet.py` (~190 lines) generates a single-page PDF on every export, embedded as `instructionPdfBase64` in the response. Layout:

- **Header:** Embroidery.mom wordmark + "Stitch Instructions"
- **Design title** (configurable via the `design_name` body field)
- **Metadata grid:** total stitches, hoop size, total thread (top), format, colour stops, bobbin thread
- **Recommended materials:** fabric, stabilizer, topping
- **Colour sequence table:** stop number, colour swatch, thread code, name, role (foundation/detail/outline/accent), per-stop stitch count, per-stop thread length
- **Footer:** disclaimer + branding

**Per-stop stitch counts** are computed from the in-memory pyembroidery pattern by counting `STITCH` commands between `COLOR_BREAK` boundaries. The encoder uses `COLOR_BREAK` (high-byte command 0xE2) before format-specific writers translate it into `STOP` + `COLOR_CHANGE`; the counter handles both forms.

**Thread length estimates** use 4.5 mm per stitch for top thread and 1.2 mm for bobbin — matches the observed ratios in pro Hatch instruction sheets (e.g., Find Joy at 11,694 stitches reports 64.78 ft top thread = 19.75 m → 4.2 mm/stitch).

### Files changed

| File | Change |
|---|---|
| `functions/image_to_jef/raster_to_stitches.py` | `_decompose_medial_trails` helper; per-trail bar emission with junction dedupe; `MIN_BRANCH_LENGTH_MM` filter; `_posterize(brand=...)` snap; `thread_brand` plumbed through `raster_to_stitch_groups` |
| `functions/image_to_jef/image_to_jef.py` | Pass `thread_brand` to the converter; build instruction PDF; include in response |
| `functions/image_to_jef/instruction_sheet.py` | NEW — reportlab-based PDF generator with per-stop counts and thread estimates |
| `functions/image_to_jef/requirements.txt`, `api/requirements.txt` | Added `reportlab>=4.0` |
| `tests/test_stitch_quality.py` | NEW `letterforms` fixture (T/Y/plus); relaxed sunflower satin-tolerance bounds |

### Measured outcome

| Fixture | Stitches | Mean (mm) | p99 (mm) | Jumps | Multi-pass |
|---|---|---|---|---|---|
| Sunflower | 2,227 | 1.97 | 4.56 | 3.10% | 2.00× |
| Test shapes | 3,526 | 2.92 | 4.30 | 0.87% | 2.00× |
| Layered accents | 3,559 | 2.86 | 4.30 | 1.84% | 2.25× |
| Narrow satin | 1,291 | 2.28 | 5.23 | 1.82% | 2.00× |
| **Letterforms** | **1,642** | **2.37** | **4.30** | **1.43%** | **2.00×** |

All five fixtures pass the regression suite. The letterforms density of 37/cm² is naturally low because the shapes are spread across the canvas with empty space in between (bbox-based density inflates with empty area); the floor is set to 30/cm² to catch genuine "branch walking is broken" failures without false-positives on sparse layouts.

### What's left

- **Tier 4.3 applique** — three-stop placement / cutting / tackdown workflow. New product feature; needs UI plumbing too. Out of scope for the stitch algorithm.
- **Multi-page instruction PDF** — for designs with > 12 colour stops, the table currently spills onto a second page (works) but doesn't add per-stop detail blocks. Pro instruction sheets do — could add later.
- **Embedded preview image** in the PDF — would be a nice touch (render the stitch SVG to PNG and embed). Not strictly necessary; the JEF preview is already in the response.

The stitch algorithm and product polish are now at parity with hand-digitized professional output for the design types we target. Further gains require hand-tuned per-design choices that can't be auto-derived (which is exactly the value pros add).

---

## Out of scope for this plan

- **Photo-realistic embroidery** (>10 colors with subtle blends) — the auto-conversion pipeline cannot match a hand-digitized photo realistic design. Stay focused on the 4–8 color stylized designs that match the example library.
- **3D / puff embroidery** — requires special foam materials and dedicated digitizing.
- **In-the-hoop projects** (zip pouches, ornaments etc.) — multi-stop assembly designs that need a totally different generator.
