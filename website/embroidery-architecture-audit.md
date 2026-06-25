# Embroidery Architecture Audit

> Audit of the current `embroidery-mom` + `embroidery-stitch-backend` codebase against the architecture/recommendation doc covering Python pipeline libraries, Cloudflare ops layer, and frontend workflow.
>
> Companion docs in this repo: [PLAN.md](PLAN.md), [ROADMAP.md](ROADMAP.md), [embroidery_mom_site_architecture_1-19.md](embroidery_mom_site_architecture_1-19.md).

---

## Verdict

**The pipeline is significantly further along than the reference doc anticipates.** The core image-to-embroidery engine is built, well-engineered, and follows the recommended bitmap → regions → stitch-plan philosophy rather than bitmap → SVG. Library choices diverge from the reference (no OpenCV, no Potrace) but the substitutions are defensible — scikit-image + scipy.ndimage cover the same ground, and the algorithmic approach (region labeling + Shapely + pyembroidery) doesn't need Potrace's edge-tracing.

The two genuinely missing layers are (1) the Cloudflare ops layer — no R2, no Queues, no real auth, files round-trip as base64 in JSON — and (2) the semi-assisted UI — the backend exposes per-region fill/outline knobs that the frontend hardcodes to defaults. Everything else either exists or has clean prototype scaffolding.

---

## Philosophy / approach

**✅ Matches the bitmap → regions → stitch-plan model.**

The codebase explicitly follows the recommended data flow. Bitmap input goes through KMeans color reduction, per-color masking, morphology cleanup, contour-to-polygon conversion via Shapely, then stitch-plan generation in pyembroidery 0.1 mm units. SVG is generated only as a *preview*, not as an intermediate stage. The data model docstring at [raster_to_stitches.py:1-21](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py) lays this out unambiguously:

```python
# groups = [
#     {'color': '#rrggbb',
#      'segments': [[{'x': float, 'y': float}, ...], ...]},
#     ...
# ]
# All coordinates in pyembroidery units (0.1 mm), origin at image centre.
```

Working resolution is fixed at `PX_PER_MM = 10` and `EMB_PER_MM = 10` at [raster_to_stitches.py:50-52](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py). The pipeline never serializes to SVG and re-parses it back — region polygons go directly to stitch plans.

---

## Python pipeline coverage

| Step | Status | Evidence |
|---|---|---|
| Input bitmap | ✅ Done | `POST /stitch` multipart at [app.py:34-65](embroidery-stitch-backend/python_src/app.py); `imageBase64` payload contract at [converter.py:6-23](embroidery-stitch-backend/python_src/stitch_engine/converter.py). |
| Resize / denoise | ⚠️ Partial | Working-resolution rescale at `PX_PER_MM = 10` ([raster_to_stitches.py:50](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py)). **No explicit denoise pass** (no Gaussian/bilateral). Relies on KMeans + morphology opening to clean. Adequate for AI-generated flat-art input; weaker for photographic uploads. |
| Color reduction → thread palette | ✅ Done | `KMeans` / `MiniBatchKMeans` at [raster_to_stitches.py:36, 118-120](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py); thread snap at [raster_to_stitches.py:2413-2419](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py) via `nearest_thread(rgb, brand=brand)` in dedicated [thread_palette.py](embroidery-stitch-backend/python_src/stitch_engine/thread_palette.py). Brand pluggable through `thread_brand` payload field ([generator.js:138](embroidery-mom/src/api/generator.js)). |
| One mask per thread color | ✅ Done | Per-color connected-component labeling at [raster_to_stitches.py:258, 393, 584, 988](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py) via `measure.label(mask, connectivity=2)`. Each blob is treated independently — fill angle / direction is per-component, not per-color. |
| Morphology cleanup | ✅ Done | `binary_opening`, `binary_closing`, `remove_small_objects`, `remove_small_holes` at [raster_to_stitches.py:254-255, 983-984, 2703-2722](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py). One-pixel crumb removal handled distinctly from larger noise — see comment at [raster_to_stitches.py:1921](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py). |
| Contour extraction | ✅ Done | Marching-contour polygonization (comment at [raster_to_stitches.py:1006](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py)) converts labeled masks into Shapely polygons. |
| Polygon simplification | ✅ Done | `poly.simplify(1.5, preserve_topology=True)` at [raster_to_stitches.py:1391](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py). Accent-line / detail pruning at [raster_to_stitches.py:1152, 1936](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py). |
| Remove tiny regions | ✅ Done | Configurable `min_feature_mm` (default 0.8 mm) drives `min_area_px2 = (min_feature_mm * PX_PER_MM) ** 2` at [raster_to_stitches.py:226, 375, 570, 751](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py). Preflight pass emits a `tiny_regions` flag at [raster_to_stitches.py:314](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py) so the UI can warn before committing. |
| Stitch planning (fill / satin / running) | ✅ Done — more sophisticated than the reference | All three present, with smart routing decisions: `COMPACTNESS_THRESH = 0.60` (contour vs directional), `MEDIAL_EIGEN_THRESH = 3.0` (medial-axis fills for thin shapes — petals, leaves), `SATIN_WIDTH_MM = 6.0`, `MAX_SATIN_BAR_MM = 8.0`, tatami row-offset to break visible seams (`TATAMI_CYCLE = 3`), per-role stitch length caps (`MAX_STITCH_FILL_MM = 2.8`, `MAX_STITCH_OUTLINE_MM = 1.2`). All calibrated from professional Hatch examples ([raster_to_stitches.py:54-79](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py)). |
| Travel optimization | ⚠️ Partial | Nearest-endpoint routing via `_to_emb(raw_components, route_mode='nearest')` at [raster_to_stitches.py:770, 1789-1802](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py). Functional, **not full TSP**. The comment at [raster_to_stitches.py:1766](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py) acknowledges the tradeoff ("For many separate islands, prefer clean scan fills"). `MAX_STITCH_TRAVEL_MM = 12.0` caps how long a single travel run can grow before forcing a jump. |
| Export DST/PES/JEF/EXP/VP3 + SVG preview | ✅ Done | `SUPPORTED_FORMATS = {'jef', 'pes', 'dst', 'vp3', 'exp', 'xxx'}` at [converter.py:46](embroidery-stitch-backend/python_src/stitch_engine/converter.py). XXX is a bonus. `READ_ONLY_FORMATS = {'hus', 'vip'}` accepted as input. Preview SVG ships in the JSON response (`previewSvg`); PDF instruction sheet via `reportlab` ([instruction_sheet.py:24](embroidery-stitch-backend/python_src/stitch_engine/instruction_sheet.py)) is a bonus the reference doesn't ask for. |

### Library substitutions vs the reference doc

The reference doc recommends OpenCV, scikit-image, Pillow, Potrace/pypotrace, Shapely, svgwrite/svgpathtools, pyembroidery. The codebase ships only a subset, and the substitutions are deliberate.

- ❌ **OpenCV** — not used. Replaced by `scikit-image` (`morphology`, `measure`, `skeletonize`) + `scipy.ndimage`. Equivalent operations for the morphology/label/distance-transform paths this pipeline actually needs. OpenCV's photographic-preprocessing strengths (denoising, bilateral filtering) aren't relevant when the input is AI-generated flat sticker art. **Fine.**
- ❌ **Potrace / pypotrace** — not used. The pipeline polygonizes via `measure.label` + marching-contour conversion, not edge tracing. Potrace shines for vectorizing high-contrast bitmaps where the *boundary* is the primary signal; here the regions are the primary signal and Potrace would be redundant. **Fine — by design.**
- ❌ **svgwrite / svgpathtools** — SVG is built as an inline string for preview only. No round-tripping through SVG means no library needed. **Fine.**
- ✅ **scikit-image, Pillow, Shapely, pyembroidery** — all present in [requirements.txt](embroidery-stitch-backend/python_src/requirements.txt).
- Plus extras: **scikit-learn** (KMeans for palette reduction), **scipy.ndimage** (distance-transform for nearest-label assignment), **trimesh** (likely for 3D preview — worth confirming), **reportlab** (PDF instruction sheet).

---

## Cloudflare architecture coverage

The reference doc's recommended topology: Worker (uploads, auth, jobs, queues, signed URLs) → R2 → Queue → Python service (Cloud Run / Fly / Render / Railway / Lambda) → R2 → Worker returns download URL.

The actual topology: Worker → Cloudflare Container (Durable Object) running FastAPI → response back through the Worker. Files travel as **base64 in JSON, both directions.**

| Component | Status | Evidence |
|---|---|---|
| Worker entrypoint | ✅ Done | Two workers in play. Frontend worker at [embroidery-mom/src/worker.js:80-98](embroidery-mom/src/worker.js) routes `/api/stitch`, `/api/generate`, `/api/health` and serves the SPA assets. Backend worker at [embroidery-stitch-backend/src/index.ts:1-24](embroidery-stitch-backend/src/index.ts) forwards to the Container. |
| Auth | ❌ Not done | [account.js:1-30](embroidery-mom/src/api/account.js) is **stub-only**: `signup` / `login` / `logout` are `delay()` mocks. Top-of-file comment: `// Phase 2: replace with real Supabase/Clerk auth + Stripe billing`. The GeneratorPage explicitly labels these prototype placeholders ([GeneratorPage.jsx:266-283](embroidery-mom/src/pages/GeneratorPage.jsx)). |
| Jobs / Queues | ❌ Not done | No Cloudflare Queue bindings in either `wrangler.toml` ([embroidery-mom](embroidery-mom/wrangler.toml)) or `wrangler.jsonc` ([embroidery-stitch-backend](embroidery-stitch-backend/wrangler.jsonc)). The backend uses **Durable Objects + Containers** directly (`MyContainer extends Container` at [src/index.ts:3-6](embroidery-stitch-backend/src/index.ts)) — synchronous fetch-to-container per request. No queue/poll pattern. Note: the "Queued for ${outFormat} stitch conversion" string at [worker.js:547](embroidery-mom/src/worker.js) is a placeholder text inside a fallback error SVG, not real queueing infrastructure. |
| Signed URLs | ❌ Not done | Grep returns zero hits for `R2`, `signedUrl`, `presigned`. |
| R2 storage | ❌ Not done | No R2 bucket bindings anywhere. Files travel as **base64 in JSON**: `imageBase64` going in at [generator.js:131-138](embroidery-mom/src/api/generator.js), `fileBase64` coming back at [app.py:50](embroidery-stitch-backend/python_src/app.py). Works at current scale (small designs, low concurrency); will break on large multi-color DST exports or under load. |
| Python processing service | ✅ Done — but runs **in a Cloudflare Container**, not Cloud Run / Fly / Render / Railway / Lambda. See [wrangler.jsonc:14-32](embroidery-stitch-backend/wrangler.jsonc): `containers[0].image: "./Dockerfile"`, `instance_type: "basic"`, `max_instances: 10`. FastAPI app at [app.py:1-65](embroidery-stitch-backend/python_src/app.py). This is the newer CF pattern — same outcome, no separate hosting provider needed. Worth flagging: `sleepAfter = "2m"` at [src/index.ts:5](embroidery-stitch-backend/src/index.ts) means cold-starts after 2 min of idleness. |
| Worker returns download URL | ⚠️ Partial | Frontend gets `fileBase64` in the response payload and triggers a client-side blob download via `downloadBase64File` at [generator.js:147-167](embroidery-mom/src/api/generator.js). **Not a presigned URL.** The file is delivered in the response body. Acceptable for kilobyte-scale JEF/PES; not great for large multi-color DST or PDF instruction sheets. |

### Pattern divergence note

The reference doc's Worker + R2 + Queue + external Python service topology is the *classic* Cloudflare data-processing topology, assembled before CF Containers existed. The Container-as-Durable-Object pattern in use here (released 2025) collapses several of those layers — the Container *is* the Python service, addressable directly from a Worker. It's a valid simplification, but it inherits Durable Object request limits (currently 30s soft cap, extended via `wrangler.jsonc` config — note the 420s timeout at [worker.js:7](embroidery-mom/src/worker.js) is enforced client-side, the Container still has CF-level ceilings).

The synchronous pattern works while a single stitch run fits comfortably under those ceilings (current pipeline runs ~10–30s for typical designs per the FastAPI `metrics.requestMs` instrumentation). It will break under any of: bigger designs, longer hoops, more colors, multi-color DST. **The queue + R2 + presigned URL pattern is the migration when those break, not a same-day rewrite.**

---

## Frontend coverage

| Feature | Status | Evidence |
|---|---|---|
| Thread color display | ✅ Done | `result.colors?.length` shown at [GeneratorPage.jsx:521, 712](embroidery-mom/src/pages/GeneratorPage.jsx). |
| Stitch density control | ✅ Done | `density_mm` param at [generator.js:135](embroidery-mom/src/api/generator.js). Three preset bundles (`balanced` / `clean` / `simple`) at [GeneratorPage.jsx:28-32](embroidery-mom/src/pages/GeneratorPage.jsx) that vary `minFeatureMm`, `edgeWalkPasses`, `densityMm` together. |
| Travel paths preview | ⚠️ Partial | `result.pathPreviewSvg` referenced on the client at [GeneratorPage.jsx:257](embroidery-mom/src/pages/GeneratorPage.jsx) and a toggle exists for it. Verify the backend actually emits `pathPreviewSvg` as a separate SVG variant from `previewSvg`; if it doesn't, the toggle silently falls back. |
| Estimated stitch count | ✅ Done | `result.stitchCount` shown at [GeneratorPage.jsx:521, 711, 731, 781](embroidery-mom/src/pages/GeneratorPage.jsx). |
| Thread usage estimate | ❌ Not done | Stitch count is exposed; total thread metrage per color is not. Cheap to compute from existing `groups` — sum per-color segment lengths × pyembroidery scale, surface as "≈ N meters madeira-1234". |
| Hoop sizes / format picker | ✅ Done | `HOOP_SIZES` (4×4 / 5×7 / 6×10) and `FORMATS` (JEF/PES/DST/EXP/VP3/XXX) at [GeneratorPage.jsx:22-27](embroidery-mom/src/pages/GeneratorPage.jsx). |
| Credits / billing UI | ⚠️ Partial | `CreditMeter`, `useCredits` hook, "+ Add credits" link exist ([GeneratorPage.jsx:299-304](embroidery-mom/src/pages/GeneratorPage.jsx)) but the page itself labels them prototype placeholders ([GeneratorPage.jsx:266-283](embroidery-mom/src/pages/GeneratorPage.jsx)). Wired to the same mock auth as account.js. |
| **Bonus: client-side source-art quality scoring** | ✅ Done — not in the reference doc, but valuable | [generator.js:213-360](embroidery-mom/src/api/generator.js) scores generated images for stitchability before submitting to the Python backend: component count, color bins, foreground ratio, border-background ratio, soft-shading detection, local-detail-cluster detection. Drives flags like `low-contrast-source`, `tiny-fragments`, `soft-shading`, `floating-small-detail`, `local-detail-cluster`. A `score < 58` or specific flag-set triggers a retry pass with a stricter prompt suffix (`STRICT_RETRY_SUFFIX` at [worker.js:140-153](embroidery-mom/src/worker.js)). |

---

## Semi-assisted workflow gap

The reference doc's strongest recommendation — *"semi-assisted (auto + manual overrides), not fully automatic"* — is the largest single product-level gap.

**The backend already exposes the right knobs.** From [raster_to_stitches.py:705-721](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py):

```python
def raster_to_stitch_groups(
    ...
    min_feature_mm: float = 0.8,
    ...
    outline_policy: str = 'selective',          # 'selective'|'all'|'dark'|'none'
    solid_fill_mode: str = 'auto',              # 'auto'|'scan'|'medial'
    center_fill_mode: str = 'contour',          # 'contour'|'scan'|'seed'
    ...
):
```

Plus `num_colors`, `density_mm`, `outline`, `outline_width_mm`, `edge_walk_passes`, `pull_comp_mm`, `fill_underlap_mm`, `thread_brand` — all live params accepted on the `/api/stitch` endpoint.

**The frontend wires them as auto-only.** [GeneratorPage.jsx:33-38](embroidery-mom/src/pages/GeneratorPage.jsx):

```js
const AUTOMATIC_STITCH_SETTINGS = {
  pullCompMm: 0.18,
  fillUnderlapMm: 0.24,
  solidFillMode: 'scan',
  centerFillMode: 'scan',
};
```

— hardcoded. The user never sees them. The only user-tunable knobs surfaced are hoop, format, color count, and a 3-way detail-level preset (`balanced` / `clean` / `simple`) that bundles `minFeatureMm` + `edgeWalkPasses` + `densityMm` into preset triplets.

**What's missing for "semi-assisted":**

1. **Expose the backend knobs as UI controls.** Even an "Advanced settings" disclosure with sliders for `density_mm`, `min_feature_mm`, `pull_comp_mm`, `fill_underlap_mm` and toggles for `outline_policy` / `solid_fill_mode` / `center_fill_mode` would close most of the gap. The plumbing is already there in `generator.js`.
2. **Per-region overrides.** The bigger product feature: click a region in the preview, change *that region's* fill type (`scan` → `medial`), color (re-map to a different thread), or skip it entirely. This is the real "semi-assisted" loop. Requires the backend to emit per-region IDs in the preview SVG, accept a region-override payload on re-stitch, and the frontend to wire click handlers on SVG regions.
3. **Re-stitch loop.** The current re-process control at [GeneratorPage.jsx:525](embroidery-mom/src/pages/GeneratorPage.jsx) only re-runs with a different color count. Extend it to accept any subset of overrides and re-run incrementally.

The Hatch-calibrated stitch heuristics ([raster_to_stitches.py:54-79](embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py)) make the *auto* path competitive with hand-digitized work for simple flat-art subjects. The remaining design space — complex subjects, photographic uploads, branding-specific palettes — needs the manual override layer to land.

---

## Ranked punch list — biggest gaps

1. **Real auth + billing.** Mocks at [account.js:1-30](embroidery-mom/src/api/account.js). Blocks shipping. The Supabase/Clerk + Stripe path is already telegraphed in the file's own header comment.
2. **Semi-assisted manual-override UI.** Backend has the knobs; frontend doesn't expose them. Biggest product-value gap. No region-click → re-stitch flow exists.
3. **R2 + presigned URLs.** Base64-in-JSON round-trip works at current scale; doesn't scale. Worker CPU/memory and request-body limits will bite first on large multi-color DST exports.
4. **Job queue.** Synchronous fetch-to-Container at [src/index.ts:18-22](embroidery-stitch-backend/src/index.ts) ties up the Worker for up to 420s (client timeout at [worker.js:7](embroidery-mom/src/worker.js)). One slow stitch blocks one request. Cloudflare Queues + a poll endpoint would decouple submission from completion and enable status UI.
5. **Thread usage estimate.** Stitch count is shown; per-color thread metrage is not. ~20 lines on the Python side, one new payload field, one new HUD row. Cheap value-add.
6. **Travel-path preview SVG.** `pathPreviewSvg` is referenced on the client; verify the backend emits it as a distinct SVG (separate from `previewSvg`). If missing, either implement or remove the dead toggle.
7. **Explicit denoise step.** The pipeline relies on KMeans + morphology opening to clean noise. An upfront bilateral or Gaussian filter would help photographic uploads. Less critical for the AI-generated flat-art workflow the project is currently optimized for.

---

## Non-issues / intentional deviations

- **No OpenCV.** Replaced by scikit-image + scipy.ndimage. The morphology / label / distance-transform operations this pipeline needs are covered. OpenCV's photographic-preprocessing strengths aren't relevant for the AI-generated flat-art use case.
- **No Potrace / pypotrace.** The pipeline polygonizes via `measure.label` + marching contours. Region-first algorithm, not boundary-first — Potrace would be redundant.
- **No svgwrite / svgpathtools.** SVG is generated inline as a string, preview-only. No SVG round-tripping in the data flow means no library needed.
- **No separate Python hosting provider (Cloud Run / Fly / Render / Railway / Lambda).** Cloudflare Containers (released 2025) collapses the Worker → external-service hop into Worker → Durable-Object-Container. Same outcome, less ops. Re-evaluate when single-request runtime starts pushing CF's Container ceilings.
- **No SVG intermediate.** The codebase deliberately follows bitmap → regions → stitch plan, not bitmap → SVG → stitch plan. This is the reference doc's *recommendation*, not a gap.
