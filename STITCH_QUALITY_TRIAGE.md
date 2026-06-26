# Stitch Quality Triage

Last updated: 2026-06-26

## Current Read

The engine is no longer failing mainly because of simple geometry primitives. Current generated-icon work is now measured through `generated_acceptance.py`, `underpaint_benchmark.py`, and the generated-run HTML comparison harness.

Recent shipped backend changes:

- `compare_generated_runs.py` compares two existing acceptance/benchmark output dirs and produces an HTML visual + metric report.
- The frontend source gate now accepts simple connected generated icons with soft shading instead of rejecting them as too detailed.
- `gradient_elephant_simple` is a backend fixture and regression case.
- Mild generated gradient tone bands now collapse into stitchable thread fields while preserving meaningful material contrast.
- Large radial repeated motifs can use angular routing; this reduced `flower_sunflower_simple` trims `9 -> 7` without changing the daisy.
- Graph-aware route candidate diagnostics compare nearest, angular, MST preorder, and 2-opt tours for disconnected same-color fill islands.
- Upload-style source/detail policy diagnostics now surface tiny-detail accounting, compact-detail promotion, simplification, and detail-budget status in acceptance summaries.
- Upload-style tone-material preservation now has a deterministic `same_hue_acorn` guard: dark-brown cap, tan body, and light tan highlight must survive as separate thread colors.

The remaining quality problems are mostly in generated icon art:

- repeated-island designs still have too many jumps/trims, especially `flower_daisy_simple`
- source-generation detail overload: too many small regions, low-contrast tones, or embroidery-like source imagery
- meaningful small accent colors must be preserved without preserving noisy fragments
- some residual preview clutter from jumps that are not actually stitched
- broad-underpaint/lane routing should only be revisited when reports show actual stitched-span risk

## Current Tooling: Generated Run Comparison

Use `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/compare_generated_runs.py` for every ambiguous stitch-quality change.

Example:

```bash
cd /Users/partido/jeflabelmaker/website/embroidery-stitch-backend
python3 scripts/compare_generated_runs.py BEFORE_DIR AFTER_DIR \
  --out tmp/generated_compare_report.html \
  --fail-on-regression
```

The report shows source art, preview SVGs, stitch/path/travel diagnostics, surface diagnostics, colors, fill strategies, top risks, metric deltas, added/removed cases, and strict regression failures.

Current useful reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_gradient_elephant.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_underpaint_final_to_tonal_merge.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_radial_route_20260626.html`

## Research Coverage Map

Reviewed against `Embroidery Stitching Algorithm Research.pdf` and the follow-up bibliography screenshot on 2026-06-26.

Already implemented in the current engine:

- role-specific stitch caps for fill, underlay, outline, and travel
- multi-pass layer planning with foundation/detail/outline roles
- underlay caps and underlay-before-cover stitch chains
- medial-axis/satin handling for narrow shapes
- overlap/seam ownership between fills and outlines
- heuristic source/detail classification and tiny-detail pruning/promotion
- gated angular routing for large repeated radial motifs
- generated-run HTML comparison harness for visual keep/revert decisions
- source/detail policy guardrails for uploaded-art fixtures
- tone/material color guardrails for same-hue uploaded art

Implemented now:

- graph-aware component routing for disconnected same-color fill islands, inspired by embroidery/sewing path-ordering work, geometric TSP/MST heuristics, and 2-opt. The production adaptation compares nearest, angular, MST preorder, and 2-opt component tours, then keeps a new route only when predicted trims/jumps improve without increasing long-span or visible-carry risk.
- source/detail decision diagnostics for upload-style fixtures: `surface-plan.json` records tiny-component decision counts and `uploaded_art_acceptance.py --strict-source-policy` fails on unresolved tiny decisions, bad detail budgets, lost accent colors, or detail-fill risk regressions.
- same-hue material preservation fixture: `same_hue_acorn` verifies the posterizer/thread snap keeps `#783c14`, `#c3915a`, and `#d2aa6e` instead of collapsing a dark cap, tan body, and light highlight into one family.

Research later:

- direction-field/divergence or vector-field streamlines for artistic flow fills
- offset-curve and auto-split fill partitioning for complex regions
- improved raster-to-vector contour simplification before surface planning
- stitch-style classification beyond current heuristic labels
- texture synthesis for preview/style inspiration, not direct machine stitches
- genetic/evolutionary multi-objective optimization after deterministic fixtures are stronger

Out of scope for now:

- exact b-matching/planar graph formulation from the embroidery-path papers; the current engine routes generated stitch segments, not a pure required-edge graph
- cross-stitch DFS/parity algorithms unless cross-stitch becomes a product mode
- applique placement/cutting/tackdown workflows until the core generated-icon pipeline is stable

## Current Patch: Graph-Aware Component Routing

Disconnected same-color fill islands now enter a guarded route-candidate selector. The selector compares nearest, angular, MST preorder, 2-opt from nearest, and 2-opt from MST. Non-radial groups benchmark against nearest; radial rings benchmark against the already-accepted angular behavior so the selector cannot quietly undo the sunflower fix.

Current outcome:

- `flower_daisy_simple`: graph candidates rejected; nearest stays selected at `26 jumps / 14 trims`, with no same-surface long spans or risk surfaces.
- `flower_sunflower_simple`: radial baseline preserved; angular stays selected at `20 jumps / 7 trims`, with no same-surface long spans or risk surfaces.
- `gradient_elephant_simple`: stable at `8 jumps / 4 trims`, no same-surface long spans, no `scan_lanes` on the body.
- synthetic cutout and circle-hole benchmarks stayed inside their existing guardrails.

Validation:

- targeted flower generated acceptance
- targeted underpaint focus set for daisy, sunflower, gradient elephant, cutout trap, and circle-hole
- full generated acceptance
- full generated comparison with `--fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- full `npm run benchmark:underpaint`

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_graph_route_flowers_20260626.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_graph_route_full_20260626.html`

## Recent Patch: Radial Repeated Motif Routing

Large radial repeated color islands now route angularly when the geometry clearly forms a ring. The gate is deliberately narrow: at least 10 similarly sized components, enough radial spread, and no large angular gap. Loose clusters stay on nearest routing.

What improved:

- `flower_sunflower_simple`: trims `9 -> 7`
- `flower_sunflower_simple`: stitches `1832 -> 1823`
- no strict generated-comparison regressions
- `flower_daisy_simple` is unchanged at `26 jumps / 14 trims`

Validation:

- targeted flower generated acceptance
- targeted sunflower underpaint benchmark
- full generated acceptance
- `compare_generated_runs.py ... --fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- full `npm run benchmark:underpaint`

## Recent Patch: Gradient Elephant Source Acceptance + Tonal Cleanup

The product had rejected a simple soft-shaded generated elephant as “too detailed.” That case should work: it has one clear subject, white background, few semantic parts, and mild gradients.

What changed:

- Frontend source-quality gate allows `simpleConnectedSubject` with soft shading when no structural problems are present.
- Backend fixture `gradient_elephant_simple` was added from the user screenshot.
- Tonal cleanup now collapses broad mild gradient bands unless they are strongly luminance/perceptually separated.

Result:

- `gradient_elephant_simple`: same-surface long spans `3 -> 0`
- trims `8 -> 4`
- jumps `14 -> 8`
- stitches `6269 -> 5062`
- `scan_lanes` removed from the gradient body

## Historical Patch: Narrowed Small Patch Stable Scan

The latest guarded patch scores patch-like foundation surfaces before they reach satin fallback. If the scan-row candidate has no long spans and no trim count, it forces scan fill and records debug fields in `surface-plan.json`.

This helped the generated sunflower leaves:

- `flower_sunflower_simple`: `fillCoherenceRiskSurfaces 4 -> 2`
- `flower_sunflower_simple`: `detailFillRiskSurfaces 3 -> 1`
- visible result: green leaf patches read as orderly filled patches instead of webby satin

The first version also caught a tiny bee fragment and made `bee_simple` worse. The rule is now narrowed to medium-small foundation patches (`area_mm2 >= 32.0`) so it skips those tiny decorative fragments.

Caveat: the generated acceptance score for sunflower still drops from `100` to `84`, even though visual-risk counts improve. Treat that as a scoring-model limitation to revisit, not as a clean rejection by itself.

## Baseline Artifacts

- Generated baseline before this patch: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_lane_order_guarded_full/review.md`
- Narrowed small-patch generated full: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_small_patch_scan_narrowed_full/review.md`
- Narrowed small-patch before/after comparison:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_lane_to_small_patch_narrowed/comparison.html`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_lane_to_small_patch_narrowed/comparison-contact-sheet.png`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_lane_to_small_patch_narrowed/comparison.md`
- Product quality gate: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/quality_gate_lane_vs_small_patch_narrowed/quality-gate.md`
- Focused sunflower artifact: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_small_patch_scan_focus3/flower_sunflower_simple/preview.svg`
- Primitive/export regression prefix: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_small_patch_scan_narrowed_`

## Fixture Status

| Fixture | Current State | Notes |
| --- | --- | --- |
| badge_circle_star | Stable | Primitive-like; no risk surfaces. |
| bee_simple | Stable | Still diagnosed as source complexity, but no long-span/risk regression. |
| cartoon_elephant | Stable but not solved | Still has one same-surface trimmed long span and a visual-lobe route conflict diagnostic. |
| gradient_elephant_simple | Improved | Accepted as valid generated source; tonal cleanup removed same-surface long spans and lane-routed gradient body. |
| flower_daisy_simple | Stable but trim-heavy | Eight-petal case stays better on nearest routing; current result is `26 jumps / 14 trims`. |
| flower_sunflower_simple | Improved | Angular repeated-ring routing reduced trims `9 -> 7` with no long-span regression. |
| leaf_single_smooth | Stable | Guarded detail scan correctly rejects the bad dark-detail candidate. |
| leaf_two_tone | Improved | Guarded detail stable scan remains useful here. |
| sparrow_flat_app_icon | Stable but not solved | Remaining issues are source complexity and broad underpaint/detail handling. |

## Next Best Work

1. Expand color/tone preservation fixtures.
   The first same-hue material guard is live (`same_hue_acorn`, quality `100`, no broad/detail risk, cap/body/highlight preserved). The next broad quality pass should add real generated/uploaded examples where meaningful same-hue materials still collapse or stitch as fragmented surfaces.

2. Add targeted repeated-island route fixtures before broadening optimization.
   Daisy and sunflower now prove the selector can reject unsafe tours and preserve radial angular routing. The next route-specific step should add non-flower disconnected-island fixtures before changing acceptance rules.

3. Fix color preservation on upload-style art.
   The upload-style badge and thick-outline flower both show dropped source colors. This is the same class of problem the bird beak/feet exposed: visible accent colors should not vanish just because they are small or near another thread color.

4. Keep tiny detail decisions explicit.
   `tiny_detail_icon` now accounts for all 9 tiny source components: 9 compact-detail promotions, 6 simplified excess details, 3 intentional tiny stitch surfaces, and 0 unresolved tiny decisions. Future detail changes should keep `uploaded_art_acceptance.py --strict-source-policy` green before moving into broader generated fixtures.

5. Use generated comparison reports for every keep/revert decision.
   The current comparison script puts source, preview, stitch-only preview, path preview, travel debug, segmentation, surface diagnostics, colors, strategies, and metric deltas side by side. It should be part of every ambiguous keep/revert decision.

6. Continue broad-underpaint diagnostics only when actual stitched spans return.
   The latest triage reports show most current "web" risk is source complexity, detail fragmentation, or preview-only clutter rather than long stitched connector spans. Do not spend another sprint on lane routing unless the report points to `stitch_planner_routing`.

## Source-Art Triage Reports

Added `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/source_art_triage_report.py` to read acceptance artifacts without rerunning conversion and classify each case as:

- `source_art_complexity`
- `color_preservation`
- `detail_fragmentation`
- `stitch_planner_routing`
- `preview_only_clutter`
- `conversion_failure`
- `mostly_ok`

Current reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_impactful_next/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_impactful_next/source-triage.md`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_large_lane_crosscheck/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_large_lane_crosscheck/source-triage.md`

Headline from the cross-check:

- source complexity: 4 cases
- detail fragmentation: 3-4 cases depending on upload suite
- color preservation: 2-3 cases depending on upload suite
- preview-only clutter: 1 case
- mostly OK: 3 cases
- stitch-planner routing: 0 top-root cases in these reports

Interpretation: the next impactful fix should be source compiler/detail/color preservation, not another generic scan-angle or lane-routing tweak.

## Candidate Review Workflow

Use `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/compare_generated_runs.py` whenever a patch has a plausible visual win but ambiguous numeric movement. The report should compare the previous generated acceptance or underpaint run against the candidate run and include:

- status/stitch/jump/trim/quality deltas
- long-span and risk-surface deltas
- side-by-side source, preview, stitch-only preview, path preview, travel debug, segmentation, and surface diagnostics
- color and fill-strategy changes
- explicit regression failures when `--fail-on-regression` is used

Keep `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/compare_acceptance_runs.py` as a historical/product-rubric comparison tool, but prefer `compare_generated_runs.py` for the current generated-icon stitch work because it reads both generated acceptance and underpaint benchmark outputs.

## Do Not Repeat

- Do not use species-specific prompt or stitch rules.
- Do not force detail stable scan globally; `leaf_single_smooth` already proved that can explode trims and long spans.
- Do not use broad tone merging as a blanket fix.
- Do not evaluate product quality on primitives alone.
- Do not accept embroidery-rendered source images as valid source fixtures.

## Latest Candidate: Accent Preservation

Implemented an additive small-accent preservation path in `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py`.

What improved:

- Small vivid/muted semantic colors can survive extraction even when below the normal component threshold.
- `low_contrast_bird` keeps its orange accent thread (`#ff8c14`).
- Surface plans now explain why a color/component was preserved or classified.

What did not improve:

- This does not fix broad artistic fill quality.
- This does not make tiny complex source art clean; `tiny_detail_icon` remains caution/C- territory.
- This does not resolve the current sunflower score disagreement.

Validation artifacts:

- Generated acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_accent_preserve_refined_full`
- Uploaded acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_accent_preserve_refined_full`
- Format regressions:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_preserve_refined_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_preserve_refined_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_preserve_refined_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_preserve_refined_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_preserve_refined_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_preserve_refined_xxx`

Keep/revert recommendation:

- Keep this patch if the next visual review confirms the rescued accent colors read correctly.
- Do not treat this as an answer to the remaining webby/artistic fill problems.

## Latest Candidate: Fragile Detail Absorption Diagnostics

Implemented a planner-level fragile-detail absorption hook in `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py`.

What improved:

- `surface-plan.json` now exposes when small tonal/detail components are absorbed, dropped, or rejected by the planner.
- Each planned surface can report its absorption decision and absorbed child components.
- The all-format primitive regression remains clean.

What did not improve:

- The rule barely fires on the saved generated/uploaded acceptance fixtures.
- It did not materially improve the remaining webby broad-fill cases.
- The real alpha `posed_sparrow.png` case points to a larger issue: many separate same-hue surfaces and tiny dark accent regions, not just absorbable tonal chips.

Validation artifacts:

- Generated acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_detail_absorb_full`
- Uploaded acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_detail_absorb_full`
- Format regressions:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_absorb_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_absorb_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_absorb_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_absorb_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_absorb_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_absorb_xxx`

Keep/revert recommendation:

- Keep if we value the added diagnostics and want a safe hook for future simplification.
- Do not claim this as a quality fix.
- Next work should shift to source/detail simplification and same-hue surface policy instead of more local absorption-threshold tuning.

## Latest Candidate: Controlled Tonal Family Collapse

Implemented a gated source-compiler rule in `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py` to collapse adjacent same-hue tonal slivers only when the posterized source already looks oversegmented.

What improved:

- `sparrow_flat_app_icon` simplified from 5 colors to 4, 9 regions to 7, 55 jumps to 45, and 14 trims to 13.
- The extra tan sliver `#c3915a` was absorbed into the retained tan field.
- Two-tone leaf stayed intact.
- Uploaded `low_contrast_bird` kept orange accent color.
- Uploaded `no_outline_teddy` kept four colors after tightening the gate.

What did not improve:

- This does not solve `tiny_detail_icon`; that case remains C-/caution with too many fragile details.
- This does not solve broad artistic fill feel.
- The sparrow comparison now flags more preview-jump clutter even though actual stitched long-span risk did not increase. Treat this as a visual-review item, not an automatic win.

Validation artifacts:

- Generated acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_tonal_family_full`
- Uploaded acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_tonal_family_full`
- Comparison reports:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_tonal_family_generated`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_tonal_family_uploaded`
- Format regressions:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_tonal_family_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_tonal_family_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_tonal_family_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_tonal_family_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_tonal_family_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_tonal_family_xxx`

Keep/revert recommendation:

- Keep as a candidate patch after visual review.
- Do not make tonal merging global. The first attempt flattened `no_outline_teddy`, which is the exact failure mode to avoid.
- Next focus should be either small-detail simplification or better preview/stitch-travel separation, not more broad tone-threshold tuning.

## Latest Candidate: Repeated Compact Detail Promotion

Implemented a narrow planner rule in `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py` for repeated small colored details.

What improved:

- `tiny_detail_icon` colored dots render more solidly instead of hollow/sparse.
- `tiny_detail_icon` jumps improved `93 -> 81`.
- `tiny_detail_icon` trims improved `12 -> 6`.
- Generated acceptance stayed stable with no flagged regressions.
- All format regressions passed for `JEF`, `PES`, `DST`, `EXP`, `VP3`, and `XXX`.

What did not improve:

- The current rubric marks `tiny_detail_icon` worse because intentional compact detail fills are still counted as `detailFillRiskSurfaces`.
- This does not address broad fill artistry, bird/elephant underpaint, or source-generation detail overload.
- It is not evidence that every tiny detail should be preserved; it only helps repeated compact colored details that are visually intentional.

Validation artifacts:

- Uploaded acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_compact_detail_full`
- Generated acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_compact_detail_full`
- Comparison reports:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_compact_detail_uploaded_full/output.json`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_compact_detail_generated_full/output.json`
- Format regressions:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_detail_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_detail_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_detail_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_detail_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_detail_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_detail_xxx`

Keep/revert recommendation:

- Keep as a candidate if visual review agrees the tiny detail icon looks better.
- Before deployment, update quality scoring so intentional repeated compact details are not treated the same as accidental noisy fragmentation.

## Latest Tooling: Compact Detail Scoring Calibration

Updated the quality tools so intentional repeated compact details are not scored as accidental detail fragmentation.

What changed:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/grade_stitch_quality.py` now reads `surface-plan.json` and emits `intentional_compact_details` as a zero-penalty visual-review finding.
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/compare_acceptance_runs.py` now subtracts those intentional compact details from adjusted fill-risk flags.
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/source_art_triage_report.py` applies the same discount in root-cause triage.

Validation artifacts:

- Uploaded comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_compact_detail_uploaded_scoring_calibrated`
- Generated comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_compact_detail_generated_scoring_calibrated`
- Uploaded quality gate: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/grade_compact_detail_scoring_calibrated/quality-gate.md`
- Generated quality gate: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/grade_generated_compact_detail_scoring_calibrated/quality-gate.md`
- Source triage: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_compact_detail_scoring_calibrated/source-triage.html`

Result:

- `tiny_detail_icon` is no longer falsely reported as a compact-detail regression.
- Comparison changed from `fill risk up` / `rubric down` to `fill risk down` / `preview jumps down`.
- Rubric moved from `C- 57` to `C- 70`, still manual review.
- Triage now points more clearly at remaining real issues: dropped color and many tiny components.

Next focus:

- Preserve meaningful small colors more reliably.
- Add a deliberate tiny-component decision layer: keep as compact fill, merge into parent, or drop with an explicit reason.

## Latest Candidate: Vivid Accent Preservation

Implemented a narrow color-preservation fix so tiny but meaningful vivid accents are not overwritten or demoted before surface planning.

What improved:

- `tiny_detail_icon` now keeps its yellow detail color instead of losing it during accent preservation.
- `no_outline_teddy` improved in calibrated grading from `C+ 80` to `B 95`.
- Generated acceptance stayed stable; the only generated comparison flag was positive (`flower_daisy_simple` fill risk down).
- All format regressions passed for `JEF`, `PES`, `DST`, `EXP`, `VP3`, and `XXX`.

What did not improve:

- `tiny_detail_icon` still grades `C-`.
- Its score moved from `70` to `66` because restored yellow details add real small islands and preview jumps.
- This does not solve repeated-detail routing or preview clutter.
- This does not address broad fill artistry.

Validation artifacts:

- Uploaded acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_accent_slot_fix_full`
- Generated acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_accent_slot_fix_full`
- Uploaded comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_accent_slot_uploaded`
- Generated comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_accent_slot_generated`
- Uploaded grading: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/grade_uploaded_accent_slot_fix`
- Generated grading: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/grade_generated_accent_slot_fix`
- Format regressions:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_slot_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_slot_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_slot_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_slot_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_slot_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_slot_xxx`

Keep/revert recommendation:

- Keep. Losing meaningful colors is worse than a small local preview-jump regression.
- Treat `tiny_detail_icon` as the next focused fixture for compact-detail routing, not as a reason to revert color preservation.

## Latest Candidate: Compact Detail Serpentine Fill

Implemented a narrow compact-detail execution fix: repeated intentional tiny details now try a continuous serpentine fill before falling back to the older compact scan fill.

What improved:

- `tiny_detail_icon` no longer reports compact detail fill risk after the restored yellow detail islands are stitched.
- `cartoon_elephant` generated comparison also dropped from `2` detail-risk surfaces to `0`.
- Quality grading now reports intentional compact details with the correct promoted count, so the report does not imply `0` promoted details when compact surfaces are present.
- Uploaded, generated, and all-format regressions stayed clean.

What did not improve:

- Jumps and trims did not meaningfully change.
- `tiny_detail_icon` still needs visual review because it has many tiny components and jump pressure.
- This does not solve broad fill artistry, source-generation over-detailing, or preview clutter from legitimate cross-region jumps.

Validation artifacts:

- Uploaded acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_compact_serpentine_full`
- Generated acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_compact_serpentine_full`
- Uploaded comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_compact_serpentine_uploaded`
- Generated comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_compact_serpentine_generated`
- Uploaded grading: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/grade_uploaded_compact_serpentine`
- Generated grading: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/grade_generated_compact_serpentine`
- Format regressions:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_serpentine_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_serpentine_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_serpentine_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_serpentine_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_serpentine_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_serpentine_xxx`

Keep/revert recommendation:

- Keep. It reduces false compact-detail risk without hiding the remaining real issues.
- Next focus should be a deliberate tiny-component decision layer and preview/routing cleanup, not more broad threshold changes.

## Latest Tooling: Tiny Component Policy Accounting

Added explicit tiny-component policy accounting so the reports distinguish between tiny regions that are intentionally handled and tiny regions still likely to fail.

What improved:

- `surface-plan.json` now reports `tinyComponentPolicy`.
- Grading and source triage no longer double-penalize tiny details that the planner explicitly kept, absorbed, or dropped.
- `tiny_detail_icon` now reports `9 kept`, `0 absorbed`, `0 dropped`, `0 unresolved` tiny components.
- `tiny_detail_icon` grade moved to `C+ 80`, while still retaining real warnings for jump pressure and preview clutter.
- Cases with unresolved tiny fragments still get flagged.

What did not improve:

- No stitch paths changed.
- Jump counts, trim counts, and visual preview quality are unchanged.
- This is not a broad-fill, source-generation, or routing fix.

Validation artifacts:

- Focused tiny detail run: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_tiny_policy_tiny`
- Uploaded acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_tiny_policy_full`
- Generated acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_tiny_policy_full`
- Uploaded grading: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/grade_uploaded_tiny_policy`
- Generated grading: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/grade_generated_tiny_policy`
- Uploaded comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_tiny_policy_uploaded`
- Generated comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_tiny_policy_generated`
- Source triage: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_tiny_policy/source-triage.html`

Keep/revert recommendation:

- Keep. This makes the acceptance reports more honest.
- Next actual stitch-quality work should focus only on unresolved tiny components and cross-surface preview/routing artifacts.

## Latest Source Guard: Flat Art Prompt Tightening

Tightened the generation prompts after confirming that one problematic leaf fixture was source-art failure, not only stitch-engine failure: the image was rendered as an embroidered object on fabric instead of flat conversion art.

What improved:

- The live generator prompt, Cloudflare Worker prompt, and generated-fixture prompt now explicitly reject embroidered patch renderings, thread mockups, satin/raised borders, rope-like borders, textured canvas, woven backgrounds, and tiny decorative pieces.
- The strict retry prompt now also removes simulated embroidery, thread, fabric, stitch texture, satin borders, and raised borders.
- Existing source scoring already rejects the bad rendered leaf strongly enough: local candidate scoring picked the flat leaf (`97`) over the rendered/thread-like leaf (`0`, with `tiny-fragments` and `local-detail-cluster`).

What did not improve:

- No stitch geometry changed.
- No live generation batch was run because the shell did not have an image API key available.
- This helps AI-generated source art, but user uploads will still need source normalization and stitch planning improvements.

Validation artifacts:

- Local candidate guard: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_prompt_guard_local_candidates/summary.md`

Keep/revert recommendation:

- Keep. This narrows the source images toward the class the stitch engine can actually convert.
- Next live check should generate a leaf, sparrow, teddy/bear, and flower with the updated prompt, then convert the selected candidates.

## Latest Source Guard: Local Cleanup Before Conversion

Added a no-extra-generation local normalization pass for prompt-generated source art.

Why:

- Automatic paid retries are not a good default because image generation is the expensive step.
- Generated source art can be close but still contain gradients, tiny shards, near-duplicate tones, and texture-like pixels.
- The stitch engine should receive a cleaner source when possible, without paying for another image.

What changed:

- Prompt generation still requests one image by default.
- The frontend scores the selected source image, locally flattens/cleans it in canvas, scores the cleaned image, and only uses the cleaned version if it improves or preserves the source score.
- The cleaner keeps broad colors, dark separators, and meaningful vivid accents while replacing tiny label islands with neighboring regions.
- If cleanup still leaves the source below the quality gate, the UI now says it failed even after local cleanup.
- The diagnostics panel now reports whether source cleanup was used and roughly how much of the source changed.
- Worker and legacy Python generation now default `allowRetry` to false so paid retries are opt-in.

What this should improve:

- Over-detailed or softly shaded generated source art should become more stitchable before conversion.
- Max-color reprocessing should be less misleading when the source itself was the problem.
- Users do not burn another image-generation call by default.

What this does not solve:

- True stitch-routing spiderwebs.
- Bad source composition from the image model.
- User-uploaded art quality unless we later apply a similar normalization policy to upload mode.

Validation:

- Website build passed.
- Python generator compile passed.
- Diff whitespace check passed.
- Local source-normalization review passed with conservative opt-in behavior:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_normalization_review_costsafe_v2/summary.md`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_normalization_review_costsafe_v2/contact-sheet.png`

Review result:

- Cleanup is used for the clearly bad embroidery-rendered leaf source only.
- Cleanup is skipped for already-good leaf/teddy/bird/elephant sources.
- Cleanup is skipped when it improves the numeric score slightly but still leaves the source below the gate.

Next review:

- Generate or upload the same bird-like case and compare original source thumb against the converted preview.
- If the cleaner flattens useful details too much, make the normalizer stricter about when it opts in.

## Latest Source Guard: Downstream Stitch Check

Ran source cleanup through actual stitch conversion on three representative cases.

Artifacts:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_normalization_stitch_leaf_single/summary.md`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_normalization_stitch_sparrow_bad/summary.md`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_normalization_stitch_elephant_guard/summary.md`

Findings:

- Rendered/thread-like leaf is the good cleanup case: normalized source clears the gate and improves stitch quality.
- Bad sparrow remains bad even after cleanup: metrics improve, but the source still has too many tones and local detail clusters, so it should block instead of silently converting.
- Elephant proves why cleanup must be conservative: normalizing it worsens the source and stitch quality, so the original should be preserved.

Keep/revert recommendation:

- Keep. The local cleanup is useful as a cost-safe source guard, but only with the current conservative opt-in rule.
- Next stitch-quality work should stay focused on planner/routing problems, not broadening this cleanup into a destructive filter.

## Stabilization Checkpoint: 2026-06-24

Goal: verify the current stitch-engine/product-backend worktree enough to decide whether it is a reasonable checkpoint before more quality work.

Validation passed:

- Root app build: `npm run build`
- Embroidery.mom app build: `npm run build` in `website/embroidery-mom`
- Backend TypeScript: `npm run typecheck` in `website/embroidery-stitch-backend`
- Backend Python compile: `PYTHONPYCACHEPREFIX=/private/tmp/jeflabelmaker-pycache python3 -m compileall -q python_src scripts`
- Root image-stitching unit tests: `python3 tests/test_image_stitching.py`
- Root stitch quality suite: `python3 tests/test_stitch_quality.py`
- Backend JEF regression smoke: `python3 scripts/regression_stitch_samples.py --out tmp/stabilize_regression_jef_fixed --format jef`
- Generated acceptance: `python3 scripts/generated_acceptance.py --out tmp/stabilize_generated_acceptance --format jef`
- Product quality gate: `python3 scripts/grade_stitch_quality.py --input tmp/stabilize_generated_acceptance --out tmp/stabilize_quality_gate`

Fix made during stabilization:

- Added a backend source-label cleanup rule that absorbs broad pale generator backdrops into the existing fabric background before preflight/stitching.
- This fixed `leaf_tinted_background`, where a large pale blue rectangle (`#d2e6f8`) was previously stitched as a thread color instead of treated as background residue.
- The rule is connectivity/shape gated: it only absorbs large, light, low-chroma labels adjacent to a recognized background component, preserving small highlights and enclosed white-thread regions.

Quality gate result:

- Generated fixtures: 7 `A`, 1 `B`.
- All generated fixtures remained `candidate` downloads.
- `leaf_single_smooth` is the only `B`, with a minor source-normalization-pressure finding.

Checkpoint recommendation:

- The current engine/backend state is stable enough to checkpoint after repo hygiene.
- Do not stage the whole worktree blindly: `website/embroidery-stitch-backend/`, `website/embroidery-mom/`, tests, example files, tmp artifacts, and a Cloudflare security CSV are all currently untracked.
- Next best action is to split a clean commit set: stitch engine/backend code and docs first; generated tmp artifacts and sensitive/account CSVs should stay out of version control.
