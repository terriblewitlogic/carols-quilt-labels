# Stitch Experiment Log

Purpose: keep a durable record of stitch-engine and source-generation experiments so we do not keep rediscovering the same traps.

This is not a full changelog. It is a decision log for approaches that worked, failed, or need strict guardrails.

## Current Baseline

- The engine is now surface-planner based: extract color components, classify surfaces, plan fills/outlines, then generate stitches.
- The target source class is still simple/generated flat art, but the product should eventually support user uploads.
- Visual quality is judged by generated fixtures and primitive regressions, not metrics alone.
- Acceptance artifacts usually live under:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_*`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_*`

## Do Not Repeat Without A New Reason

### Border-Connected Background Reservation For Color Budget

Result: candidate, not deploy-ready.

Hypothesis:

- White/off-white page background was consuming one of the requested stitch-color slots.
- If the posterizer reserves only border-connected near-white background before KMeans, generated icons should keep meaningful low-area accents such as orange beaks and feet.

Change tested:

- Added border-connected near-white background detection before color clustering.
- Background is reserved as non-stitching background when it is large enough and touches the image border.
- Enclosed white details are not automatically treated as background.
- Kept dark line art as a real stitch color that consumes a color slot.
- Rejected the conservative variant that also subtracted background from KMeans cluster count; it still lost sparrow orange.

Validation:

- Full generated acceptance passed 8/8:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_bg_slot_final_full`
- All primitive/export regressions passed for `JEF`, `PES`, `DST`, `EXP`, `VP3`, and `XXX`:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_bg_slot_final_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_bg_slot_final_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_bg_slot_final_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_bg_slot_final_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_bg_slot_final_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_bg_slot_final_xxx`

Generated acceptance signal:

- `sparrow_flat_app_icon` kept orange again: colors include `#ff8c14`.
- But sparrow quality dropped `84 -> 74`, stitches rose `2029 -> 2169`, jumps rose `45 -> 57`, trims rose `13 -> 15`.
- `flower_sunflower_simple` stayed quality `84`, but stitches rose `1553 -> 1780` and trims rose `17 -> 21`.
- Most other generated fixtures were stable.

Primitive/export signal:

- All formats completed with zero 500s/timeouts.
- Caution cases stayed limited to `leaf_tinted_background` and `cartoon_elephant`.
- Rectangle exposed a small antialias color stop (`#6496e6`) even though visual quality remained `100`; this is a useful warning that freeing a color slot can expose tiny tonal shards.

Recommendation:

- Keep the idea, but do not deploy it as-is.
- The next supporting fix should suppress or absorb tiny antialias-only tonal shards after background reservation, without losing meaningful accents like orange beaks/feet.
- This is a color-budget/source-segmentation improvement, not a stitch-fill quality solution.

Rejected variants:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_bg_slot_conservative_targeted`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_bg_slot_novelty_targeted`

Rule:

- Reserving border-connected background is promising, but any version must prove it preserves accents without creating extra stitched tonal fragments.

### Broad Tone Threshold Tweaks

Result: rejected.

Why: a broad tone/label threshold improved one label count but worsened routing on sparrow-like cases. It also risks flattening meaningful accent colors.

Rule: do not reintroduce broad color merging unless the planner can prove visual improvement and color preservation fixture-wide.

### Lane Routing Everywhere

Result: rejected.

Why: lane routing can reduce some long jumps, but applying it broadly makes clean shapes more mechanical and can create trim storms.

Rule: lane routing must remain gated by before/after gap scoring and should be used only where it clearly reduces long spans without adding trims.

Related accepted refinement: when lane routing is already gated and allowed, it is useful to score several deterministic lane orders and keep the best route. This is not permission to enable lane routing broadly.

### Over-Shrinking Fill To Stay Inside Outlines

Result: rejected.

Why: it reduces overpaint but creates white moat/gap artifacts between fill and outline. It treats the symptom rather than modeling fill and outline together.

Rule: do not use global shrink as the primary containment strategy. Fill/outline geometry needs a shared contract.

### Black Mask Paint-Over As A Complete Fix

Result: partial, not sufficient.

Why: painting or stitching a dark line after the fill can hide some overrun, but it does not change bad green plotting underneath. It can also preserve the wrong outline path.

Rule: black cover stitches are valid as final outlines, but not as a substitute for correct fill planning.

### Double Leaf Outlines

Result: rejected.

Why: one outline looked like the original intended border; the second looked like a bandaid and made the leaves worse.

Rule: structural outlines should be single final boundaries. Do not add duplicate border passes around leaves or simple patches.

### Motif-Aware Center-Out Fill For Leaves

Result: rejected for leaves.

Why: center-out/ring fills looked promising for flower centers, but made leaves dramatically worse and more artificial.

Rule: motif-aware fills are allowed only after shape-family gates. Flower centers can use seeded/directional fills; leaves should not inherit that rule.

### Primitive Fixtures As Product Proof

Result: insufficient.

Why: rectangles/circles are useful smoke tests, but they do not represent generated product art. They can pass while generated birds/elephants still fail visually.

Rule: primitives are regression gates only. Product quality decisions require generated fixtures.

### Embroidery-Rendered Source Images

Result: rejected as source fixtures.

Why: if the generator returns an image that already looks like embroidery, the converter tries to convert fake stitches into real stitches. That confuses evaluation.

Rule: generated source art should be flat color fields, not an embroidery mockup.

### Species-Specific Prompt Fixes

Result: rejected as product strategy.

Why: tuning prompts for sparrow markings or one animal may improve that case but does not generalize to "a pink elephant," "a teddy bear," etc.

Rule: source-generation prompts must stay subject-general: simple shape count, flat fills, essential identity details only.

### "More Colors" As The Main Fix

Result: rejected as primary solution.

Why: increasing requested stitch colors did not reliably preserve beak/feet/accent colors. If orange is visibly present, color detection/mapping should keep it without asking the user to guess.

Rule: max colors can be a user control, but it cannot be the main fix for missed meaningful colors.

### Unguarded Detail Stable Scan

Result: rejected in first form.

Why: it fixed `leaf_two_tone`, but made `leaf_single_smooth` worse: 30 trims and 22 same-surface long spans.

Rule: stable detail scan must be accepted only when candidate gap scoring predicts no long spans and low trim risk.

## Promising Or Accepted Directions

### Surface Planning Layer

Status: keep.

Why: this is the right architecture for grouping color regions, separating structural outlines from details, and reasoning about broad same-color underpaint.

Guardrail: avoid subject-specific rules. Surface decisions need geometry/color evidence.

### Same-Color Dark-Line Reconstruction

Status: keep, with diagnostics.

Why: helps broad underpaint surfaces split by internal line art stitch as one visual surface rather than many fragments.

Guardrail: watch broad-fill route risks on elephant/bird-like fixtures.

### Seeded/Directional Flower Center Fill

Status: keep.

Why: flower centers improved meaningfully with more stable, less random fills.

Guardrail: do not apply the same center-out logic blindly to leaves or arbitrary shapes.

### Stem As Filled Shape

Status: keep.

Why: treating stems as filled shapes avoids bad satin-ladder behavior.

Guardrail: maintain simple-shape regression coverage.

### Guarded Detail Stable Scan

Status: keep candidate.

Why: with candidate gap scoring, `leaf_two_tone` improved while `leaf_single_smooth` rejected the bad scan and stayed at baseline.

Latest validation:
- Generated acceptance full set: no regressions except intended `leaf_two_tone` improvement.
- Primitive regressions passed for `JEF`, `PES`, `DST`, `EXP`, `VP3`, `XXX`.

Key artifacts:
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_detail_surface_scan_guarded_full/review.md`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_detail_surface_scan_guarded_full/leaf_two_tone/surface-plan.json`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_detail_surface_scan_guarded_full/leaf_single_smooth/surface-plan.json`

### Guarded Lane-Order Scoring

Status: keep candidate.

Why: the existing broad-fill lane router was already correctly gated, but the first nearest-neighbor lane walk left avoidable preview webs on elephant-style underpaint. Trying multiple deterministic lane orders inside that already-accepted lane route reduced `cartoon_elephant` same-surface long spans from `3` to `1` and broad-fill route risk from `1` to `0`, without changing the rest of generated acceptance.

Latest validation:
- Generated acceptance full set: no quality score regressions; only material metric movement was `cartoon_elephant`.
- Primitive regressions passed for `JEF`, `PES`, `DST`, `EXP`, `VP3`, `XXX`.

Guardrail: keep the outer before/after lane-route gate. Do not generalize this into lane routing for all fills.

Key artifacts:
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_lane_order_guarded_full/review.md`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_lane_order_guarded_full/cartoon_elephant/surface-plan.json`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_lane_order_guarded_jef`

### Guarded Small Patch Stable Scan

Status: keep candidate, modest, narrowed.

Why: narrow-ish foundation patches can fall into satin/stroke behavior even when they are really filled icon pieces. This showed up most clearly in the generated sunflower: the green leaf patches looked more like webby satin than filled leaves. Scoring the scan-row candidate, then forcing scan only when it has no long spans and no trim count, changed the two larger green sunflower leaf patches from satin-like output to orderly scan fills. Visual inspection favored the new preview.

Latest validation:
- First full generated acceptance showed a `bee_simple` regression: one 29.57 mm2 yellow fragment got `small_patch_stable_scan`, adding a fill-risk surface and dropping the product rubric from `B` to `C+`.
- Narrowed the rule from `18.0 <= area_mm2` to `32.0 <= area_mm2`. Rationale: this override should be for medium-small filled patches, not tiny decorative fragments.
- Narrowed full generated acceptance restored `bee_simple` to baseline (`B`, 14 jumps, 0 fill-risk surfaces) while preserving the sunflower visual-risk improvement (`fillCoherenceRiskSurfaces 4 -> 2`, `detailFillRiskSurfaces 3 -> 1` versus lane-order baseline).
- Primitive/export regressions passed for `JEF`, `PES`, `DST`, `EXP`, `VP3`, `XXX` with 0 conversion errors. Pre-existing caution cases remained `leaf_tinted_background` and `cartoon_elephant`.

Guardrail: this is not a broad artistry fix. It should stay limited to patch-like foundation surfaces with clean candidate routing. Do not use it to force all small details into scan fill.

Key artifacts:
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_small_patch_scan_narrowed_full/review.md`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_lane_to_small_patch_narrowed/comparison.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_lane_to_small_patch_narrowed/comparison-contact-sheet.png`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/quality_gate_lane_vs_small_patch_narrowed/quality-gate.md`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_small_patch_scan_focus3/flower_sunflower_simple/preview.svg`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_small_patch_scan_focus3/flower_sunflower_simple/surface-plan.json`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_small_patch_scan_narrowed_jef`

### Acceptance Comparison Report

Status: keep as evaluation tooling.

Why: we need a clean way to judge patches where the visual read and the numeric score disagree.

Added `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/compare_acceptance_runs.py`, which compares two generated acceptance output directories and writes:

- `comparison.json`
- `comparison.md`
- `comparison.html`

The report includes per-case quality/stitch/jump/trim deltas, fill-risk deltas, stitched-web deltas, strategy changes, top surface risks, and side-by-side links for source, preview, path preview, and surface diagnostics. SVG artifacts are rendered to PNG when local `sharp` support is available, with SVG fallback if rendering is unavailable.

Ran baseline vs narrowed small-patch scan:

- Base: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_lane_order_guarded_full`
- Candidate: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_small_patch_scan_narrowed_full`
- Report: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_lane_to_small_patch_narrowed/comparison.html`
- Contact sheet: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_lane_to_small_patch_narrowed/comparison-contact-sheet.png`
- Render check: contact sheet generated at 1774 x 2836 px.
- Product quality gate: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/quality_gate_lane_vs_small_patch_narrowed/quality-gate.md`

Calibration note:

- Changed product rubric scoring in `grade_stitch_quality.py` to start from 100 and subtract explicit findings, instead of starting from the engine quality score.
- Reason: starting from the engine score double-counted engine caution because `_findings()` already adds explicit engine score/status findings.
- Result: `flower_sunflower_simple` stays `C+ -> C+` while still showing `engine score down` and `fill risk down`.
- The narrowed rule removes the `bee_simple` regression from the first version: `bee_simple` is `B -> B`, 14 jumps, and 0 fill-risk surfaces.

Key result:

- `flower_sunflower_simple` is flagged as `score down`, `fill risk down`, and `score/visual-risk disagreement`.
- This matches the visual read: the leaf fill looked better, while the current quality score got worse.
- `bee_simple` no longer regresses after narrowing the patch area gate.

Recommendation: use this report before keep/revert calls on ambiguous patches. It does not replace visual judgment, but it makes the tradeoffs visible enough that we can stop repeating ambiguous experiments.

## Evaluation Rules Going Forward

- Never keep a patch because one fixture improved. Compare against generated acceptance and primitive regression.
- If a metric improves but visual quality gets worse, visual quality wins.
- If a fix helps generated flat art but breaks simple primitives, narrow it.
- If a fix helps one subject by encoding subject knowledge, reject it unless generalized.
- Every risky change should emit enough debug data to explain why it was applied or rejected.
- Before trying a similar approach again, add a line to this log explaining what is new this time.

### Source-Art Triage Report

Status: keep as evaluation tooling.

Why: acceptance artifacts now contain enough signals to tell whether a bad output is likely a source-art problem, color-preservation problem, detail-fragmentation problem, stitch-routing problem, preview-only clutter, or a conversion failure. Those signals were scattered across summaries, `response.json`, `source-design.json`, surface diagnostics, and source scoring. Without a consolidated view, we kept drifting back to fill tweaks even when the root problem had moved upstream.

Added `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/source_art_triage_report.py`.

What it does:

- reads one or more acceptance output directories without rerunning conversion
- grades each case with the product rubric when available
- scores source images using the existing source-generation scorer
- classifies likely root cause: `source_art_complexity`, `color_preservation`, `detail_fragmentation`, `stitch_planner_routing`, `preview_only_clutter`, `conversion_failure`, or `mostly_ok`
- writes `source-triage.json`, `source-triage.md`, and visual `source-triage.html`
- embeds source, preview, path preview, surface diagnostics, and segmentation debug artifacts when present

Ran two cross-checks:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_impactful_next/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_large_lane_crosscheck/source-triage.html`

Headline:

- generated acceptance still clusters around source complexity and detail fragmentation
- upload-style acceptance exposes color preservation as a top failure class
- current suites do not classify any case primarily as `stitch_planner_routing`

Recommendation: use this report before deciding the next sprint target. The next likely code work should be source compiler/detail/color preservation, not another generic fill-angle or lane-route experiment.

### Accent Color Preservation Extraction

Status: keep as a candidate patch.

Problem: upload-style/generated icon art can contain meaningful small color regions, such as beaks, feet, blush marks, badges, or small accent shapes. The previous extraction path could erase those during opening/min-area cleanup before the planner ever had a chance to decide whether they were sewable.

Change:

- Added semantic small-accent detection based on label fraction, chroma, luminance, and background exclusion.
- Kept the legacy opened mask for normal components.
- Added only raw accent islands that pass a lower extraction threshold, instead of changing the whole label geometry.
- Added debug fields to `surface-plan.json`: `sourceDetailDecision`, `componentDecision`, `forcePreservedTinyDetail`, `extractionMinAreaPx2`, and `defaultMinAreaPx2`.

Important refinement:

- The first attempt used `binary_closing` for the entire preserved label. That was too broad. It risked changing region geometry instead of only rescuing small accents.
- The retained version is additive: old extraction first, accent rescue second.

Validation:

- Py compile passed for `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py`.
- Generated acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_accent_preserve_refined_full`
  - 8 cases, 0 errors, average quality 88.8.
  - No dropped meaningful colors in the generated suite.
- Uploaded acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_accent_preserve_refined_full`
  - 6 cases, 0 errors, average quality 86.3.
  - `low_contrast_bird` preserves orange `#ff8c14`.
- Format regression:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_preserve_refined_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_preserve_refined_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_preserve_refined_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_preserve_refined_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_preserve_refined_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_preserve_refined_xxx`
  - Each format: 8 cases, 0 errors, average quality 95.0.

Known non-solution:

- This patch does not solve the remaining broad-fill/artistry problems.
- `flower_sunflower_simple` still scores lower than an older baseline in the current comparison, but its `surface-plan.json` shows no preserved tiny/detail decisions. Treat that as separate fill-scoring/current-engine drift, not a reason to reject accent preservation.
- `tiny_detail_icon` remains a C-/caution class case; preserving tiny accents is not the same as making tiny details stitch beautifully.

### Planner Fragile Detail Absorption Diagnostics

Status: keep as diagnostic scaffolding, not as a solved-quality patch.

Problem investigated: generated/uploaded icon art can contain small tonal fragments that look meaningful to the posterizer but become bad stitch regions. The hope was that the surface planner could absorb low-value chips into a nearby parent surface before stitch generation, reducing webby internal routing without subject-specific rules.

Change:

- Added planner-level fragile detail absorption after same-color reconstruction and before surface classification.
- Added `detailAbsorption` debug output to `surface-plan.json`.
- Each planned surface can now report `absorptionDecision`, `absorbedChildCount`, and `absorbedChildren`.
- The rule is conservative: it tries to absorb small, low-value, same-family tonal chips into a nearby parent; it avoids dark line art and saturated accents.

Validation:

- Py compile passed for `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py`.
- Generated acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_detail_absorb_full`
  - 8 cases, 0 errors, average quality 88.8.
- Uploaded acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_detail_absorb_full`
  - 6 cases, 0 errors, average quality 86.3.
- Format regression:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_absorb_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_absorb_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_absorb_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_absorb_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_absorb_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_absorb_xxx`
  - Each format: 8 cases, 0 errors, average quality 95.0.

Honest result:

- The patch is safe in the current suites, but it did not materially change the main fixtures.
- Absorption mostly did not fire. `flower_sunflower_simple` produced rejected candidates, but no accepted absorptions.
- The real alpha `posed_sparrow.png` test still shows the main failure class: many separate same-hue surfaces plus tiny dark accents, not a simple tiny tonal chip that can be absorbed locally.
- Keep the diagnostics because they tell us when this rule is not the right lever.

Next implication:

- Do not keep pushing local absorption thresholds unless we can show a fixture where they actually fire and improve visual quality.
- The next meaningful work should be a broader source/detail simplification policy: grouping same-hue tonal surfaces, suppressing or restyling tiny dark accent islands, and giving the planner a way to intentionally simplify generated art before stitch generation.

### Controlled Tonal Family Collapse

Status: keep as a narrow candidate patch.

Problem investigated: generated icon art can produce several adjacent same-hue tan/brown surfaces that are visually one broad surface, especially on bird/teddy-style subjects. Stitching each tonal sliver separately increases regions, jumps, and "webby" preview clutter without preserving meaningful design intent.

Change:

- Added a source-compiler normalization step: `collapse_oversegmented_tonal_families`.
- The rule only runs when the source already looks oversegmented by component count, tiny-component count, or tonal partition diagnostics.
- It groups adjacent same-hue fill labels, keeps the dominant field, keeps strong high-contrast secondary fields, protects small vivid accents, and maps middle tonal slivers to the nearest retained label.
- The first attempt was too aggressive and flattened `no_outline_teddy` from four colors to two. The retained gate requires evidence of real oversegmentation before tonal collapse can run.

Validation:

- Py compile passed for `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py`.
- Diff whitespace check passed.
- Generated acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_tonal_family_full`
  - 8 cases, 0 errors.
  - `sparrow_flat_app_icon`: colors 5 -> 4, regions 9 -> 7, jumps 55 -> 45, trims 14 -> 13, stitches 2147 -> 2029.
  - `sparrow_flat_app_icon` dropped the extra tan sliver `#c3915a` by merging it into the retained tan field.
  - Generated leaf, two-tone leaf, daisy, sunflower, elephant, bee, and badge stayed functionally unchanged.
- Uploaded acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_tonal_family_full`
  - 6 cases, 0 errors.
  - `low_contrast_bird` preserved orange `#ff8c14`.
  - `no_outline_teddy` preserved four colors after the oversegmentation gate was tightened.
  - `tiny_detail_icon` remains C-/caution and unchanged.
- Comparison reports:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_tonal_family_generated`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_tonal_family_uploaded`
- Format regression passed for:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_tonal_family_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_tonal_family_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_tonal_family_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_tonal_family_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_tonal_family_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_tonal_family_xxx`

Honest result:

- This is a real but narrow structural improvement for same-hue oversegmented generated icons.
- It does not improve every bird image, and it does not fix tiny detail clusters or broad artistic fill quality by itself.
- The comparison rubric marks `sparrow_flat_app_icon` lower because preview-jump clutter flags increased, even though stitched long-span risk did not increase and jumps/regions decreased. This should get visual review before deployment.

Keep/revert recommendation:

- Keep as a candidate because it is gated, preserves meaningful accent colors, and passes generated/uploaded/format regressions.
- Do not broaden this into blanket tone merging. The earlier over-aggressive teddy result proved that is unsafe.
- Next useful work should target the remaining `tiny_detail_icon`/small-detail class and preview-vs-actual stitched travel classification.

### Repeated Compact Detail Promotion

Status: keep as a candidate, but calibrate the scoring model before treating it as a product win.

Problem investigated: repeated small colored details can survive source normalization but then stitch as sparse, hollow, fragile mini-regions. The clearest fixture is `tiny_detail_icon`: the normalized color labels are legitimate, but the small green/pink/yellow dot decorations read weakly in preview.

Change:

- Added `_promote_repeated_compact_detail_surfaces(...)` in `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py`.
- The rule only targets labels with multiple compact, small, non-dark, chromatic components.
- It does not delete colors or merge them into a parent. It promotes those components into intentional top detail fills, skips their edge-walk behavior, and records `repeated_compact_detail` in `surface-plan.json`.
- Debug output now includes `compactDetailPromotion` plus per-surface fields for `forceDetailFill` and `repeatedCompactDetailIndex`.

Validation:

- Py compile passed for `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py`.
- Uploaded acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_compact_detail_full`
  - 6 cases, 0 errors.
  - Only material movement was `tiny_detail_icon`: jumps `93 -> 81`, trims `12 -> 6`.
  - Visual inspection favored the candidate: the repeated colored dots looked more solid and less hollow.
  - Current comparison still flags `tiny_detail_icon` as `fill risk up` and `rubric down`, because the scoring model treats intentional compact detail fills as detail risk.
- Generated acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_compact_detail_full`
  - 8 cases, 0 errors.
  - No generated fixture flags versus the tonal-family baseline.
- Comparison reports:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_compact_detail_uploaded_full/output.json`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_compact_detail_generated_full/output.json`
- Format regression passed for:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_detail_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_detail_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_detail_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_detail_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_detail_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_detail_xxx`

Honest result:

- This is a real improvement for one narrow small-detail class.
- It does not fix broad artistic fill quality or bird/elephant underpaint.
- The score disagreement is useful: our rubric needs to distinguish intentional compact detail fill from messy detail fragmentation.

Keep/revert recommendation:

- Keep as a candidate if visual review of `tiny_detail_icon` confirms the colored details read better.
- Do not deploy solely on this patch. Pair it with a scoring/reporting calibration so intentional compact details are not mislabeled as worse quality.

### Compact Detail Rubric Calibration

Status: keep as evaluation tooling.

Problem investigated: the repeated compact detail patch made `tiny_detail_icon` look cleaner, with fewer jumps and trims, but the comparison report marked it as a rubric regression because intentional compact detail fills were counted the same way as accidental noisy fragmentation.

Change:

- Updated `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/grade_stitch_quality.py`.
  - The rubric now reads `surface-plan.json`.
  - Surfaces with `sourceDetailDecision == repeated_compact_detail` and `forceDetailFill` are reported as `intentional_compact_details` with zero penalty.
  - Residual detail-fill risk is still penalized normally.
- Updated `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/compare_acceptance_runs.py`.
  - Comparison flags now use adjusted fill risk, subtracting intentional compact detail surfaces from both fill-coherence and detail-fragmentation risk.
- Updated `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/source_art_triage_report.py`.
  - Triage also discounts intentional compact details and records them as a review note.

Validation:

- Py compile passed for all three scripts.
- Diff whitespace check passed.
- Recompared tonal-family baseline vs compact-detail candidate:
  - Uploaded comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_compact_detail_uploaded_scoring_calibrated`
  - Generated comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_compact_detail_generated_scoring_calibrated`
- `tiny_detail_icon` changed from `fill risk up`, `rubric down` to `fill risk down`, `preview jumps down`.
- `tiny_detail_icon` rubric moved from `C- 57` to `C- 70`: still manual review, no longer falsely worse.
- Generated comparison still has zero flagged regressions.
- Source triage report:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_compact_detail_scoring_calibrated/source-triage.html`

Honest result:

- This does not improve stitches directly; it improves our ability to judge patches honestly.
- It also reveals a better next target: `tiny_detail_icon` is no longer primarily a detail-fragmentation problem after calibration; it still reports dropped color and many tiny components.

Next implication:

- Continue with meaningful small-color preservation and/or a deliberate tiny-component decision layer.
- Do not use raw `detailFillRiskSurfaces` alone as a keep/revert reason when the planner has explicitly marked compact details as intentional.

### Accent Slot Preservation For Vivid Tiny Details

Status: keep as a candidate patch.

Problem investigated: `tiny_detail_icon` still dropped the yellow dots after the repeated compact detail promotion. The source art had real yellow pixels, and the thread palette could map yellow correctly, but the preservation pass reused the tiny yellow palette slot while preserving another accent color.

Root cause:

- `_choose_accent_replacement_label(...)` treated very small high-chroma labels as safe replacement slots when their pixel fraction was tiny.
- That meant a real tiny accent color, yellow in this case, could be overwritten by another preserved accent.
- After protecting that slot, older cleanup/demotion rules still removed some repeated vivid details because they looked too small in isolation.

Change:

- Tiny high-chroma labels are now treated as occupied unless they are duplicate snapped-color slots.
- Added `_is_vivid_accent_color(...)` and used it in cleanup/demotion gates.
- Repeated vivid detail labels are now preserved long enough to become intentional compact detail surfaces.

Validation:

- Py compile passed for `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py` and the quality scripts.
- Diff whitespace check passed.
- Focused uploaded acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_accent_slot_fix_tiny`
  - `tiny_detail_icon` now keeps yellow: `#fff03c` appears in the output thread colors.
- Full uploaded acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_accent_slot_fix_full`
  - 6 cases, 0 errors.
- Full generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_accent_slot_fix_full`
  - 8 cases, 0 errors.
- All format regressions passed:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_slot_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_slot_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_slot_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_slot_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_slot_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_accent_slot_xxx`
  - Each format had 8 cases, 0 errors, average quality `95.0`.

Comparison notes:

- Uploaded comparison:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_accent_slot_uploaded`
  - `no_outline_teddy` improved from `C+ 80` to `B 95`.
  - `tiny_detail_icon` changed from `C- 70` to `C- 66` and flagged `preview jumps up`; this is expected because the formerly missing yellow detail islands are now real stitchable content.
- Generated comparison:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_accent_slot_generated`
  - Only positive flag was `flower_daisy_simple` with `fill risk down`.

Honest result:

- This is a color-correctness improvement, not a routing-quality improvement.
- The tiny detail case still needs routing/preview cleanup, but dropping meaningful colors to make metrics look better is the wrong trade.

Keep/revert recommendation:

- Keep the patch.
- Do not deploy solely because this passed regression; pair it with the next small-detail routing pass or manual visual review.

### Compact Detail Serpentine Fill

Status: keep as a candidate patch.

Problem investigated: after vivid accent preservation, repeated tiny detail islands were finally present, but their local scan fills still showed up as compact-detail risk. These are legitimate small details, not accidental source noise, so the goal was to make their stitch execution more coherent without dropping the restored colors.

Change:

- Compact forced-detail fills now try a continuous serpentine path first.
- If serpentine generation fails for the geometry, they fall back to the previous compact scan behavior.
- The change is limited to compact detail fill handling; it does not change broad surface routing or global color selection.

Validation:

- Py compile passed for the stitch engine and quality grading script.
- Diff whitespace check passed.
- Full uploaded acceptance passed:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_compact_serpentine_full`
  - 6 cases, 0 errors.
- Full generated acceptance passed:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_compact_serpentine_full`
  - 8 cases, 0 errors.
- All format regressions passed:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_serpentine_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_serpentine_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_serpentine_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_serpentine_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_serpentine_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_compact_serpentine_xxx`
  - Each format had 8 cases, 0 errors, average quality `95.0`.
- Comparison artifacts:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_compact_serpentine_uploaded`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_compact_serpentine_generated`

Result:

- `tiny_detail_icon` detail-fill risk dropped from `9` to `0`.
- `cartoon_elephant` generated comparison improved from `2` detail-risk surfaces to `0`.
- Jumps and trims were basically unchanged. This is expected: restored tiny color islands still require travel/color changes.
- The grader now reports intentional compact details using the real promoted count, avoiding the misleading `0 compact detail...` message.

Honest result:

- This is a good small execution patch.
- It does not solve broad spiderweb routing, preview-jump clutter, or weak generated-art simplification.
- The next real target remains cross-surface preview/routing cleanup and a stronger tiny-component policy: keep, absorb, or drop with an explicit reason.

Keep/revert recommendation:

- Keep.
- Do not treat this as a deployment-level quality milestone by itself.

### Tiny Component Policy Accounting

Status: keep as a diagnostic/tooling patch.

Problem investigated: after compact detail promotion and serpentine fill, `tiny_detail_icon` still got penalized as if all tiny source components were unresolved fragile junk. That was no longer true: the planner had explicitly kept the repeated dots as intentional compact detail fills.

Change:

- `surface-plan.json` now includes `tinyComponentPolicy`.
- The policy summarizes tiny components that are:
  - intentionally kept as tiny/detail surfaces,
  - preserved from accent extraction,
  - absorbed into a parent,
  - dropped,
  - still unresolved.
- Product grading now discounts tiny components that already have explicit planner decisions.
- Source-art triage now does the same, so it points at unresolved tiny problems rather than already-handled ones.

Validation:

- Py compile passed for:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/grade_stitch_quality.py`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/source_art_triage_report.py`
- Diff whitespace check passed.
- Focused tiny detail acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_tiny_policy_tiny`
  - `tinyComponentPolicy`: `accountedCount=9`, `intentionalTinySurfaceCount=9`, `unresolvedTinySurfaceCount=0`.
- Full uploaded acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_tiny_policy_full`
  - 6 cases, 0 errors.
- Full generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_tiny_policy_full`
  - 8 cases, 0 errors.
- Comparison artifacts:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_tiny_policy_uploaded`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_tiny_policy_generated`
  - No comparison flags.
- Grading artifacts:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/grade_uploaded_tiny_policy`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/grade_generated_tiny_policy`
- Source triage:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_tiny_policy/source-triage.html`

Result:

- `tiny_detail_icon` now grades `C+ 80` instead of being held down by a duplicate tiny-component penalty.
- It still correctly reports engine caution, preview jump clutter, and jump pressure.
- Other unresolved tiny cases still get tiny-component findings, for example `antialiased_jpeg_badge`, `low_contrast_bird`, `thick_outline_flower`, and `leaf_single_smooth`.

Honest result:

- This does not change stitch paths.
- It makes the reports more truthful and gives us a cleaner next target: unresolved tiny components only.

Keep/revert recommendation:

- Keep.
- Next implementation work should target unresolved tiny cases, especially whether each should be absorbed, simplified, or rejected before stitching.

### Source Prompt Guard: Reject Embroidery-Looking Inputs

Status: keep as a source-generation guard patch.

Problem investigated: the generated `leaf_single_smooth` source image was not truly flat source art. It looked like a finished embroidered leaf on fabric, with a satin/thread-like border and texture. The stitch engine can reject or clean up much of that, but it should not be the first line of defense for AI-generated sources.

Change:

- Tightened the live generator system prompt in `/Users/partido/jeflabelmaker/functions/generate/stitch_prompt.py`.
- Tightened the Cloudflare Worker copy in `/Users/partido/jeflabelmaker/website/embroidery-mom/src/worker.js`.
- Tightened the generated-fixture prompt in `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/fixtures/generated/system_prompt.txt`.
- Added explicit language against embroidered patches, thread mockups, craft photos, satin borders, raised borders, rope-like borders, simulated thread borders, textured canvas, woven backgrounds, and tiny pieces smaller than the subject's eye.

Validation:

- Python prompt code compiled.
- Website build passed in `/Users/partido/jeflabelmaker/website/embroidery-mom`.
- `git diff --check` passed.
- Local candidate guard selected the flat leaf over the rendered embroidery-style leaf:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_prompt_guard_local_candidates/summary.md`
  - Flat leaf source score: `97`.
  - Rendered/thread-like leaf score: `0` with `tiny-fragments` and `local-detail-cluster`.

Note: live API generation was not rerun because no image API key was present in the shell environment. This patch is ready for a live generation check once credentials are available in the runtime.

### Cost-Safe Local Source Normalization

Status: implemented in the website generation flow; needs live visual review before deploy.

Problem investigated: the first idea after prompt tightening was an automatic paid retry for low-scoring source art. That is a bad default because image generation is the main cost. The default product path should generate once, then do any cleanup locally before conversion.

Change:

- Disabled paid image retry by default in the frontend generator client.
- Disabled paid image retry by default in the Cloudflare Worker `/api/generate` path.
- Disabled paid image retry by default in the legacy Python `/api/generate` path.
- Added browser-side source normalization before generated art is converted:
  - flatten near-color source art into a smaller set of solid regions,
  - preserve dark line art separately,
  - preserve compact vivid accents when they are large enough to stitch,
  - remove tiny label islands by replacing them with neighboring regions,
  - rescore the normalized image and use it only when it does not make the source score worse.
- The generated source preview/conversion now uses the normalized source when the local cleaner improves a risky image.

Validation:

- Website build passed in `/Users/partido/jeflabelmaker/website/embroidery-mom`.
- Python generator code compiled.
- `git diff --check` passed.
- Added and ran a local review harness:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/source_normalization_review.py`
  - Output: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_normalization_review_costsafe_v2/summary.md`
  - Contact sheet: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_normalization_review_costsafe_v2/contact-sheet.png`
- The opt-in rule was tightened after review: normalization now replaces source art only when the original fails the source gate and the normalized image passes it.

Review result:

- `leaf_single_smooth`: `0 -> 82`, use cleanup. This is the rendered/embroidery-looking source case.
- Clean two-tone leaf: `97 -> 100`, do not use cleanup.
- Bad sparrow source: `13 -> 18`, do not use cleanup because it still fails.
- Low-contrast bird: `82 -> 90`, do not use cleanup because the original is already acceptable.
- Teddy: `92 -> 92`, do not use cleanup.
- Elephant: `84 -> 74`, do not use cleanup.

Honest result:

- This is a cost-control and source-cleanliness patch, not a stitch planner patch.
- It should help gradient/texture-ish generated images before they hit the stitch engine.
- It will not fix true stitch routing problems by itself.
- It needs live production-style visual review on bird/flower/leaf/teddy prompts before deploying.

### Downstream Stitch Check For Source Normalization

Status: keep the conservative cleanup gate.

Ran original-vs-normalized candidates through the stitch converter, not just source scoring.

Artifacts:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_normalization_stitch_leaf_single/summary.md`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_normalization_stitch_sparrow_bad/summary.md`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_normalization_stitch_elephant_guard/summary.md`

Results:

- Rendered/thread-like leaf: cleanup wins. Source score `0 -> 82`, stitch quality `90 -> 100`, tiny regions `6 -> 0`, long jump metric `1 -> 0`.
- Bad sparrow: cleanup improves stitch metrics but still fails source quality. Source score `13 -> 18`, still flagged `too-many-tones` and `local-detail-cluster`; conservative gate correctly does not accept it as cleaned.
- Elephant guard case: cleanup is worse. Source score `84 -> 74`, stitch quality `100 -> 84`; conservative gate correctly keeps the original.

Honest result:

- The local cleanup is useful when the generated image looks like rendered/thread-textured art.
- It is not a magic repair pass for genuinely over-detailed source art.
- The current opt-in rule is doing the right thing: use cleanup only when the original fails and cleanup passes, otherwise preserve the original or block.

### Intentional Center-Fill Diagnostics

Status: keep as a diagnostic patch, not a stitch-quality patch.

Problem:

- Flower centers intentionally use `center_seed` fill, which creates multi-directional texture.
- The surface diagnostics were treating that intentional texture like accidental broad-fill disorder.
- This made good flower centers look worse in the metrics than they looked visually.

Change:

- Surface diagnostics now record generated fill strategies per planned surface.
- `center_seed` surfaces are treated as intentional multi-angle fills.
- Broad-fill route risk no longer penalizes `center_seed` angle spread when there are no actual stitched long-span connectors.
- Primitive regression artifacts now write `surface-plan.json`, `surface-diagnostics.json`, `surface-diagnostics.svg`, and travel debug previews so regression cases are easier to inspect.

Validation:

- Python compile passed for `converter.py` and `regression_stitch_samples.py`.
- `git diff --check` passed.
- Primitive JEF regression passed:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_diag_artifacts_jef`
  - Grade output: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/grade_diag_artifacts_jef/quality-gate.md`
- Generated acceptance JEF regression passed:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_intentional_diag`
  - Grade output: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/grade_generated_acceptance_intentional_diag/quality-gate.md`
- Primitive regression also passed for all supported formats:
  - `JEF`, `PES`, `DST`, `EXP`, `VP3`, `XXX`
  - Artifact pattern: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_diag_artifacts_<format>`
  - Grade pattern: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/grade_diag_artifacts_<format>/quality-gate.md`

Result:

- No 500s/timeouts in the regression or generated acceptance suites.
- No generated fixture metric regression versus the previous route-diagnostic baseline.
- `flower_daisy_simple` and `flower_sunflower_simple` improved on fill-coherence/high-risk metrics because the center texture is no longer misread as a defect.
- Across the inspected primitive and generated suites, same-surface long spans are currently jump-only, not stitched travel.
- All supported-format primitive runs had the same grade mix: `A:5`, `B:1`, `C+:2`.

Honest result:

- Keep this patch because it makes the quality gate more truthful.
- This does not fix actual source over-detail, jump-preview clutter, or weak visual composition.
- The next useful work is preview/UX clarity plus source-detail gating, not another broad threshold tweak.

### Preview UX: Separate Sewn Rows From Machine Moves

Status: keep.

Problem:

- Path/debug previews can look like visible webbing even when the long spans are jumps or trims, not sewn travel.
- This repeatedly made review ambiguous: a preview could look alarming even when diagnostics showed `sameSurfaceStitchedLongSpanCount = 0`.

Change:

- Renamed preview mode labels to clearer product language:
  - `Design`
  - `Stitches`
  - `Machine moves`
- Added a short technical hint only in non-design preview modes:
  - stitch view shows sewn stitch rows only;
  - machine-move view shows jumps/trims for debugging, not sewn fill.
- Renamed dashboard diagnostics:
  - `Stitched travel` to `Sewn travel`
  - `Preview jumps` to `Jump-only moves`
- Updated the caution message when all long spans are jump-only.

Validation:

- Frontend build passed in `/Users/partido/jeflabelmaker/website/embroidery-mom`.
- User-facing stale-copy scan did not find the old misleading warning text.

Honest result:

- This does not improve stitch geometry.
- It should make visual review less misleading, especially for designs whose path view contains jump-only dashed spans.

### Source Map Diagnostic Preview

Status: experimental diagnostic only.

Problem:

- The remaining failures are often ambiguous from the final preview alone: bad source art, bad color segmentation, bad fill planning, and bad route rendering can all look like the same messy stitch output.
- A source compiler can become a crutch if it silently “fixes” inputs instead of forcing the stitch algorithm to improve.

Change:

- The frontend now requests backend debug artifacts during stitch conversion.
- Added a `Source map` preview mode when the backend returns segmentation debug SVG.
- Added a compact `Source regions` diagnostic row from backend segmentation metrics.
- This does not change stitch geometry or replace stitch planning; it only exposes how the backend interpreted the source image.

Validation:

- Frontend build passed in `/Users/partido/jeflabelmaker/website/embroidery-mom`.
- `git diff --check` passed in `/Users/partido/jeflabelmaker/website/embroidery-mom`.

Keep/revert criteria:

- Keep only if it helps identify whether a failure starts in source art, segmentation, or stitch planning.
- Revert if it becomes product noise, slows normal review too much, or lets us accept weaker stitch output.
- Do not treat this as a substitute for fixing fill planning, outline contracts, color detection, or route quality.

### Preserve Multi-Part Underpaint After Outline Clipping

Status: keep as a bug fix, continue routing work.

Problem:

- Source map diagnostics showed `cartoon_elephant` was segmented correctly, but the stitch preview dropped the head/trunk fill.
- The failure was not prompt/source quality. It came from fill cleanup helpers collapsing clipped `MultiPolygon` geometry to the single largest polygon.
- That was acceptable for analysis silhouettes, but destructive for broad same-color underpaint split by dark line art.

Change:

- Added meaningful-part preservation for outline-clipped fill geometry.
- Kept largest-polygon behavior for shape classifiers that need one exterior ring.
- Updated broad-fill processing to scan the preserved multi-part fill while using the largest part only for strategy/angle classification.

Validation:

- `python3 -m py_compile python_src/stitch_engine/raster_to_stitches.py`
- Generated acceptance passed with 8/8 cases and no errors:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_preserve_multiparts_full`
  - Grade mix: `A:1`, `B:3`, `B-:1`, `C+:3`
- Primitive regression passed with 8/8 cases and no errors:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_preserve_multiparts_primitives`
- Primitive exporter sweep passed for all supported formats:
  - `JEF`, `PES`, `DST`, `EXP`, `VP3`, `XXX`
  - Artifact pattern: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_preserve_multiparts_formats/<format>`

Result:

- `cartoon_elephant` no longer loses the pink head/trunk fill.
- Simple shapes stayed stable.
- This exposed, but did not solve, remaining broad-surface routing clutter: elephant now has more stitches/jumps because the previously deleted geometry is actually being stitched.
- Next algorithmic work should focus on routing preserved multi-part underpaint cleanly, not reverting to geometry deletion or adding subject-specific rules.

### Trimmed Relocation Diagnostic Split

Status: keep as an evaluation/diagnostic fix, not a geometry fix.

Problem:

- After preserving multi-part underpaint, elephant and sparrow artifacts still looked like they had broad webby spans in path diagnostics.
- Surface diagnostics were grouping sewn connector stitches, untrimmed preview-only jumps, and trimmed machine relocations under the same "long span" buckets.
- That made it too easy to chase trimmed relocations as if they were visible sewn webbing.

Change:

- Split long-span diagnostics into stitched travel, untrimmed jump preview spans, and trimmed relocations.
- Updated generated acceptance review columns to show:
  - `Sewn travel`
  - `Untrimmed jumps`
  - `Trimmed moves`
- Updated quality grading so trimmed relocations are informational/low-risk while sewn travel and untrimmed jump clutter remain actionable.
- Restyled trimmed relocation lines in surface diagnostics so they do not read like the same class of failure as sewn travel.
- Removed a no-op multi-part routing candidate after targeted testing showed it did not improve elephant or sparrow metrics.

Validation:

- `python3 -m py_compile python_src/stitch_engine/raster_to_stitches.py python_src/stitch_engine/converter.py scripts/generated_acceptance.py scripts/grade_stitch_quality.py`
- Targeted generated acceptance passed:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_trim_split_targeted_v2`
  - `cartoon_elephant`: `0` sewn long spans, `0` untrimmed long jumps, `4` trimmed moves
  - `sparrow_flat_app_icon`: `0` sewn long spans, `0` untrimmed long jumps, `3` trimmed moves
  - `leaf_single_smooth`: `0` sewn long spans, `0` untrimmed long jumps, `1` trimmed move
- Full generated acceptance passed with 8/8 cases and no errors:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_trim_split_full`
- Primitive regression and exporter sweep completed for:
  - `JEF`, `PES`, `DST`, `EXP`, `VP3`, `XXX`
  - Artifact pattern: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_trim_split_formats/<format>`

Honest result:

- This does not improve the stitched geometry by itself.
- It improves our measurement model so we do not mistake trimmed machine moves for sewn webbing.
- The next true algorithmic target is surfaces with real fill-coherence/detail risks, especially leaf detail fills, flower green details, and sparrow accent/foundation surfaces.

### Intentional Detail Risk Rubric

Status: keep as a small diagnostic refinement, not a stitch-quality fix.

Problem:

- Some planned non-scan treatments were being judged with scan-fill coherence rules.
- This created false-positive fill-risk counts for intentional strategies like satin stem patches and compact accent fills.
- The noisy counts made it harder to separate real geometry problems from acceptable detail treatments.

Change:

- Surface diagnostics now recognize intentional non-scan detail strategies:
  - `stroke_scan`
  - `satin`
  - `compact_accent_fill`
  - `compact_accent_scan`
  - `compact_accent_serpentine`
- For those strategies, diagnostics skip angle-spread and segment-density penalties that are specific to coherent scan fills.
- Tiny/short segment penalties remain, because excessive small segments can still be a real execution risk.

Validation:

- `python3 -m py_compile python_src/stitch_engine/converter.py`
- Targeted generated acceptance passed with 4/4 cases and no errors:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_intentional_detail_risk_targeted`
- Full generated acceptance passed with 8/8 cases and no errors:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_intentional_detail_risk_full`
- Compared with the prior full diagnostic run:
  - `flower_sunflower_simple` fill-risk surfaces dropped from `2` to `0`
  - all other top-line generated acceptance metrics stayed unchanged

Honest result:

- This does not change stitch geometry or make any preview look better.
- It makes the review output less misleading by not calling intentional satin/compact detail work a scan-fill failure.
- Remaining flagged rows are still worth inspecting: leaf stroke detail, daisy green underpaint, sparrow black accent, and sparrow foundation surfaces.

### Continuous Serpentine For Coherent Detail Patches

Status: keep as a narrow stitch-quality improvement.

Problem:

- Closed color-detail patches were being tested and stitched with disconnected scan rows.
- Some patches that should read as one filled detail could therefore become a stack of separate segments or fall back to stroke-style fill.
- This is most visible on two-tone leaf-style art where the darker accent is a real closed patch, not line art.

Change:

- Detail-patch planning now tries a continuous serpentine fill candidate before disconnected scan rows.
- Accepted detail surface fills now stitch with `detail_stable_serpentine` when a clean continuous path exists.
- The fallback behavior is unchanged for detail shapes that cannot produce a coherent serpentine path.

Validation:

- `python3 -m py_compile python_src/stitch_engine/raster_to_stitches.py`
- Targeted generated acceptance passed with 4/4 cases and no errors:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_detail_serpentine_targeted`
- Full generated acceptance passed with 8/8 cases and no errors:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_detail_serpentine_full`
- Primitive JEF regression passed with 8/8 cases and no errors:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_serpentine_primitives`

Honest result:

- `leaf_two_tone` switched from `detail_stable_scan` to `detail_stable_serpentine` with no regressions elsewhere.
- `leaf_single_smooth` did not improve; its darker green component still rejects stable detail fill and falls back to `stroke_scan`.
- This is useful, but it does not address the broader bird/daisy foundation-fill quality issues.

### Conservative Same-Color Underpaint Dominance

Status: keep as a narrow planner correction.

Problem:

- The same-color dark-line underpaint reconstruction was slightly too eager.
- It correctly helps broad body-like surfaces, but it also merged repeated/related motifs when one component barely dominated the color area.
- The clearest bad case was `flower_daisy_simple`: the green stem and two leaves were reconstructed as one surface, creating a robotic shared fill even though they should remain separate motifs.

Change:

- Raised the same-color underpaint dominance guard from `0.42` to `0.50`.
- Added a code comment explaining that borderline repeated motifs should not be collapsed into one fill surface.
- This keeps reconstruction for genuinely dominant surfaces while excluding the daisy green stem/leaves case.

Validation:

- `python3 -m py_compile python_src/stitch_engine/raster_to_stitches.py`
- Targeted generated acceptance passed with 4/4 cases and no errors:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_underpaint_dominance_targeted`
- Full generated acceptance passed with 8/8 cases and no errors:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_underpaint_dominance_full`
- Primitive JEF regression passed with 8/8 cases and no errors:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_underpaint_dominance_primitives`
- Primitive exporter regression passed with 8/8 cases and no errors for:
  - `JEF`, `PES`, `DST`, `EXP`, `VP3`, `XXX`
  - Artifact pattern: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_underpaint_dominance_<format>`

Metric result:

- `flower_daisy_simple`:
  - quality score `84 -> 100`
  - fill-risk surfaces `1 -> 0`
  - merged surfaces `1 -> 0`
  - strategy removed: `same_color_underpaint`
- `cartoon_elephant`, `sparrow_flat_app_icon`, `bee_simple`, `flower_sunflower_simple`, `leaf_single_smooth`, `leaf_two_tone`, and `badge_circle_star` had unchanged top-line generated acceptance metrics.

Honest result:

- This is not a broad visual-quality breakthrough.
- It fixes a real planner mistake: repeated motifs should not be merged merely because one piece barely wins the area ratio.
- The patch is worth keeping because it improves daisy structure without degrading the broad underpaint cases that still need reconstruction.

### Heavy Source Cleanup Warning

Status: keep as a diagnostic/user-facing preflight improvement.

Problem:

- Some generated fixtures look like finished embroidery, fabric, or texture instead of flat source art.
- Those sources can force heavy cleanup before stitching and then make the stitch engine look worse than it is.
- The clearest case is `leaf_single_smooth`, whose source is rendered like thread/fabric rather than clean flat art.

Change:

- Added a `source_normalized_heavily` preflight warning when source normalization removes a large amount of fragment noise.
- The warning is triggered only when cleanup is substantial (`changedPixelFraction >= 0.05`) and the compiler assessment reports both collapsed fragment noise and removed tiny fragments.
- Added `preflightWarningCodes` to generated and uploaded acceptance summaries so review output shows warning codes without opening every `response.json`.

Validation:

- `python3 -m py_compile python_src/stitch_engine/raster_to_stitches.py`
- `python3 -m py_compile scripts/generated_acceptance.py scripts/uploaded_art_acceptance.py`
- Targeted generated acceptance passed with 4/4 cases and no errors:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_source_heavy_cleanup_targeted`
- Full generated acceptance passed with 8/8 cases and no errors:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_source_cleanup_threshold_full`
- Primitive JEF regression passed with 8/8 cases and no errors:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_source_cleanup_threshold_primitives`

Metric result:

- `leaf_single_smooth` now reports `source_normalized_heavily`.
- `sparrow_flat_app_icon` now also reports `source_normalized_heavily`; its source image looks simple at a glance but required about 6% pixel cleanup and hundreds of foreground-fragment removals.
- Clean generated fixtures such as `leaf_two_tone` and `flower_daisy_simple` did not receive this warning.
- Generated acceptance quality scores and conversion status were unchanged by the warning-only patch.

Honest result:

- This does not improve stitch geometry.
- It is worth keeping because it separates “bad/texture-like source art” from real stitch-planning failures during review.

### Prompt Contract Unification

Status: keep as a generation plumbing correction.

Problem:

- The prompt contract had split into multiple competing layers.
- The current Cloudflare Worker had a stitchable-source system prompt, but the older/root frontend still appended its own style suffix.
- The local source-generation sweep also wrapped prompts with its own style-heavy instruction.
- This made local and production generation harder to compare, and it let stale ideas such as thick black outlines survive in one path after being rejected in another.

Change:

- The UI now sends only the natural user request.
- The Worker/user wrapper is intentionally minimal: requested subject plus literal-subject instruction.
- The stitchable-art style contract lives in the backend/system prompt layer.
- The root Python generation helper and local source-generation sweep now use the same minimal user wrapper.
- The root Python system prompt was aligned with the Worker/generated-fixture system prompt.

Validation:

- `python3 -m py_compile functions/generate/stitch_prompt.py website/embroidery-stitch-backend/scripts/source_generation_sweep.py`
- `node --check website/embroidery-mom/src/worker.js`
- `npm run build` in `/Users/partido/jeflabelmaker/website/embroidery-mom`
- `npm run build` in `/Users/partido/jeflabelmaker`
- Confirmed the root Python prompt text matches `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/fixtures/generated/system_prompt.txt`.

Honest result:

- This does not guarantee better images by itself.
- It removes a source of experimental noise so future prompt tests and production behavior are judging the same contract.

### Generated Acceptance Prompt Provenance Labels

Status: keep as a diagnostics/reporting correction.

Problem:

- Generated acceptance fixtures are historical source images.
- Some fixture sidecars contain old prompts that asked for thick outlines or coloring-book style.
- After the prompt contract cleanup, the acceptance review still labeled those old sidecars as `Prompt`, which made it look like the current prompt contract was still using rejected language.

Change:

- `generated_acceptance.py` now labels historical fixture text as `sourcePrompt` / `Source-generation prompt/provenance`.
- It still records the current `systemPrompt` and `userPrompt` separately.
- Per-case artifacts now write `source_prompt.txt` instead of a generic `prompt.txt`.
- A backward-compatible `prompt` alias remains in `summary.json` for older consumers.

Validation:

- `python3 -m py_compile scripts/generated_acceptance.py`
- Targeted generated acceptance passed for `cartoon_elephant` and `sparrow_flat_app_icon`:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_prompt_metadata_check`
- Full generated acceptance passed 8/8:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_20260529_continue`
- Primitive JEF regression passed 8/8:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_20260529_continue`

Current signal from the run:

- No fixture has stitched long-span failures.
- Remaining generated caution cases are mostly quality/review issues, not hard conversion failures:
  - `cartoon_elephant`: same-color underpaint surface still has high-risk routing metrics.
  - `sparrow_flat_app_icon`: source normalization warning plus detail/fill-coherence risk.
  - `leaf_single_smooth`: source-normalized-heavily warning plus detail/fill-coherence risk.
  - `bee_simple`, `flower_daisy_simple`: white-on-white or narrow/many-region warnings from source art.

Honest result:

- This does not improve stitch output.
- It makes the acceptance artifacts more trustworthy, which matters before the next stitch-planning patch.

### Rejected: Coherent Angle Across Disconnected Underpaint Pieces

Status: rejected and reverted.

Hypothesis:

- When the surface planner reconstructs several disconnected same-color pieces as one underpaint material, forcing those pieces to share one fill angle might make the material look less patchy.

Result:

- Targeted acceptance worsened `sparrow_flat_app_icon`.
- Quality dropped from `84` to `76`.
- Jumps increased from `45` to `90`.
- Trims increased from `13` to `25`.
- Risk shifted into a small dark-brown surface.
- `cartoon_elephant` was unchanged.

Artifact folder:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_underpaint_angle_targeted`

Lesson:

- Shared fill direction across disconnected reconstructed underpaint is not generally safe.
- Related pieces can still need local angles for routing even if they share a visual color/material.

### Border-Connected Background Reservation + Edge-Tone Cleanup

Status: candidate, regression-clean, not a stitch-quality breakthrough.

Problem:

- Very light border-connected backgrounds were consuming a stitch color slot during posterization.
- This could starve small meaningful accents, especially the sparrow's orange beak/feet.
- Freeing that slot exposed a second issue: tiny antialias edge tones could become stitched colors, as seen with the blue rectangle.

Change:

- Reserve only border-connected near-white background before color clustering.
- Keep enclosed white details available as real shapes.
- Treat dark line art as a real stitch color, but do not charge the user's stitch-color budget for the reserved border background.
- Add a tiny antialias edge-tone absorber so very small same-hue edge shards get folded into their dominant neighboring fill instead of becoming separate thread colors.
- Preserve saturated, reasonably sized accents so orange beaks/feet are not absorbed away.

Validation:

- Full generated acceptance passed 8/8:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_edge_tone_full`
- Primitive/export regression passed for all supported formats:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_edge_tone_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_edge_tone_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_edge_tone_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_edge_tone_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_edge_tone_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_edge_tone_xxx`
- Rectangle targeted regression now stitches only the intended blue:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_edge_tone_rectangle_jef`

Measured result:

- `sparrow_flat_app_icon` keeps orange: `#ff8c14`.
- `sparrow_flat_app_icon` remains worse than the pre-background-reservation baseline: quality `74`, stitches `2169`, jumps `57`, trims `15`.
- `rectangle` no longer stitches the phantom pale-blue antialias color and returns to a single blue stitch color.
- Generated fixture metrics are unchanged between the background-slot candidate and the edge-tone cleanup; the cleanup is a guardrail, not a visual quality fix.

Recommendation:

- Keep the edge-tone cleanup if we keep the background reservation.
- Do not deploy this as a claimed quality improvement by itself.
- The next meaningful quality work is still broad same-color surface fill behavior and source-detail simplification, not more color-budget tuning.

### Connector Diagnostic Buckets

Status: keep as diagnostics/reporting; no stitch geometry change.

Problem:

- Path previews make several very different artifacts look like the same "web" problem.
- Before changing more routing behavior, we need to know whether a bad-looking connector is sewn travel, an untrimmed jump preview, a trimmed relocation, or a same-color surface planning artifact.

Change:

- `surfaceDiagnostics.summary` now includes `connectorDiagnosticCounts`.
- Long connectors get a `diagnosticKind`, including:
  - `real_stitched_travel`
  - `trimmed_relocation`
  - `same_color_region_merge_artifact`
  - `cross_hole_or_cutout_jump`
  - `same_surface_preview_jump`
  - `cross_detail_preview_jump`
  - `cross_surface_preview_jump`
- Generated acceptance and primitive regression summaries now include the connector diagnosis rollup.

Validation:

- `python3 -m py_compile python_src/stitch_engine/converter.py scripts/generated_acceptance.py scripts/regression_stitch_samples.py`
- Targeted generated acceptance passed:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_connector_diagnostics_targeted`
- Full generated acceptance passed 8/8:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_connector_diagnostics_full`
- Primitive JEF regression passed 8/8:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_connector_diagnostics_jef`

Measured signal:

- `sparrow_flat_app_icon`: `trimmed_relocation: 3`, no long sewn travel, still quality `74`.
- `cartoon_elephant`: `trimmed_relocation: 4`, no long sewn travel, still quality `84`.
- `circle_hole`, `leaf_tinted_background`, `double_circle`, and `daisy` only show small trimmed relocation counts.
- The generated review table now shows connector diagnosis directly:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_connector_diagnostics_full/review.md`

Lesson:

- The current visible failures are not mainly "we are sewing giant web connectors."
- The next meaningful patch should focus on fill coherence and surface shape planning: fewer awkward fragmented fill fields, better treatment of detail surfaces, and less reliance on routing thresholds.

### Colored Stroke Centerline For Fragmented Details

Status: keep as a narrow quality patch; not a broad-fill solution.

Problem:

- Some colored detail strokes were being treated as tiny filled ribbons.
- On generated leaf detail, that produced many short, fuzzy fill fragments instead of one intentional detail path.
- Diagnostics showed this was not a connector problem: it was local detail-fill fragmentation.

Change:

- Mark eligible colored stroke/detail components during surface planning.
- In `_process_polygon()`, try the normal rectangular stroke fill first.
- If that fill is highly fragmented and a skeleton/centerline route is materially cleaner, switch only that detail to `colored_stroke_centerline`.
- Keep foundation fills, broad underpaint, primitives, and exporters unchanged.

Validation:

- Targeted generated acceptance passed:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_detail_stroke_centerline_targeted`
- Full generated acceptance passed 8/8:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_detail_stroke_centerline_full`
- Primitive/export regression passed all supported formats:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_stroke_centerline_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_stroke_centerline_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_stroke_centerline_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_stroke_centerline_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_stroke_centerline_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_detail_stroke_centerline_xxx`

Measured result:

- `leaf_single_smooth` changed:
  - stitches `995 -> 864`
  - jumps `7 -> 4`
  - trims `1 -> 0`
  - connector diagnostics `{'trimmed_relocation': 1} -> {}`
  - detail surface `stroke_scan` with 98 micro-segments became `colored_stroke_centerline` with one continuous detail path.
- `sparrow_flat_app_icon` unchanged:
  - quality `74`, stitches `2169`, jumps `57`, trims `15`
  - still has detail/foundation coherence risks.
- `cartoon_elephant` unchanged:
  - quality `84`, stitches `2422`, jumps `46`, trims `15`
  - remaining issues are still broad-surface artistry/shape planning, not this detail-stroke case.
- All primitive/export runs stayed at min quality `84` with zero conversion errors.

Lesson:

- This is a useful generalized patch for colored line details that should read as a single intentional stroke.
- It does not solve the larger sparrow/elephant problem. Those failures need better broad-surface fill planning and better handling of complicated generated source art.

### Rejected: Small Reconstructed Underpaint Patch Scan

Status: rejected and reverted.

Hypothesis:

- Some sparrow broad-fill ugliness might come from small reconstructed same-color underpaint surfaces being forced through the generic surface scan path.
- A special stable scan for patch-sized reconstructed underpaint might reduce webby-looking artifacts without touching broad elephant/body fills.

Result:

- Targeted acceptance passed but produced no metric changes on:
  - `sparrow_flat_app_icon`
  - `cartoon_elephant`
  - `leaf_single_smooth`
  - `leaf_two_tone`
- After adding planner gate diagnostics, the likely target surface was classified as a broad icon-like fill, and existing lane diagnostics already showed no actual long sewn travel.

Lesson:

- This was aimed at the wrong symptom. The visible sparrow/elephant failures are not fixed by another local reconstructed-surface scan rule.
- Do not repeat this as a threshold tweak. The next useful work should target true fill artistry/coherence: better surface simplification, better interior-detail handling, and better source-art suitability checks.

### Surface Diagnostics Feed Design Quality

Status: keep as a product-quality/triage patch; not a stitch artistry fix.

Problem:

- Surface diagnostics already identified rough broad fills and fragmented detail fills, but the user-facing `designQuality` score did not use that information.
- That let visibly weak generated icon cases look more acceptable than they were, especially elephant/sparrow-style same-color underpaint and detail clutter.
- Clean primitives had to remain clean; a single broad scan-filled shape should not be punished just because it has long intentional rows.

Change:

- Pass `surfaceDiagnostics` into `_post_generation_quality()`.
- Add quality penalties for diagnostics-backed surface risks:
  - high-risk planned surfaces;
  - fill coherence risks on reconstructed/detail/same-color surfaces;
  - detail-fill fragmentation;
  - broad-fill route risk.
- Filter out false positives from single raw broad shapes, so primitive leaf/rectangle/circle fills do not get downgraded by normal scan rows.

Validation:

- Full generated acceptance passed:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_surface_quality_scoring_v2`
- Primitive/export regression passed all supported formats:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_surface_quality_scoring_v2_jef`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_surface_quality_scoring_v2_pes`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_surface_quality_scoring_v2_dst`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_surface_quality_scoring_v2_exp`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_surface_quality_scoring_v2_vp3`
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_surface_quality_scoring_v2_xxx`

Measured result:

- Generated fixtures stayed stable except the cases diagnostics already considered structurally suspect:
  - `cartoon_elephant`: quality `84 -> 62`, status `caution -> review`
  - `sparrow_flat_app_icon`: quality `74 -> 40`, status `caution -> review`
  - `flower_daisy_simple`: `100 -> 100`, still `good`
  - `leaf_single_smooth`: `90 -> 90`, still `good`
  - `leaf_two_tone`: `100 -> 100`, still `good`
- Primitive/export matrix stayed conversion-clean across `JEF`, `PES`, `DST`, `EXP`, `VP3`, and `XXX`.
- Primitive `leaf` remains `good` after filtering raw broad-shape false positives.

Lesson:

- This does not make bad stitches better, but it makes the product more honest.
- The next stitch-quality work should use these surfaced review cases to target actual fill planning, not threshold tuning or preview-only connector noise.

### Rejected: Compact Reconstructed Patch Stable Scan

Status: rejected and reverted.

Hypothesis:

- Patch-sized reconstructed same-color surfaces in sparrow-style generated art might be getting routed with the wrong broad-surface behavior.
- Giving compact reconstructed surfaces the same stable scan candidate used for small raw patches might reduce webby detail fill without changing broad elephant/body fills.

Result:

- Targeted acceptance was stopped after `leaf_single_smooth` stalled during conversion.
- Completed cases produced no useful metric movement:
  - `sparrow_flat_app_icon`: jumps `57 -> 57`, trims `15 -> 15`, same surface risk unchanged.
  - `cartoon_elephant`: jumps `46 -> 46`, trims `15 -> 15`, same surface risk unchanged.
- `surface-plan.json` showed no accepted `reconstructed_patch_stable_scan` surfaces in the target cases.

Lesson:

- This is another local scan-rule dead end. The remaining weak generated-art cases are not improved by special-casing compact reconstructed surfaces.
- Do not repeat this with looser thresholds; it risks slowing clean cases and still does not address the underlying source/surface complexity.

### Meaningful Dropped Accent Quality Warning

Status: keep as product-quality scoring and triage refinement.

Problem:

- The triage report treated any dropped quantized color as a preservation failure.
- That created false positives for tiny neutral/gray antialias dust, while the product still needed to care about small vivid accents like beaks, feet, cheeks, flower centers, and similar semantic details.

Change:

- Added a `meaningful dropped color` classifier:
  - tiny neutral layers are treated as intentional cleanup;
  - small saturated layers are treated as meaningful dropped accents.
- Updated `source_art_triage_report.py` so stable leaf-like cases are not ranked as color failures for dropped neutral dust.
- Updated the API quality scorer so dropped vivid accents produce a `meaningful_color_dropped` warning.

Validation:

- `python3 -m py_compile` passed for:
  - `python_src/stitch_engine/converter.py`
  - `scripts/source_art_triage_report.py`
- Refreshed triage report:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_triage_meaningful_color_v2/source-triage.html`
- Unit-style scorer check:
  - dropped neutral `#c0c0c0` at `0.118%` produced no warning;
  - dropped saturated orange `#ff8c14` at `0.3%` produced `meaningful_color_dropped`.

Lesson:

- This does not repair missing colors, but it makes review and user-facing quality warnings more honest.
- The next color-preservation work should target why meaningful vivid accents are dropped, not merely warn about them.

### Keep: Bounded Acceptance Timeout + Faster Source Diagnostics

Status: keep.

Problem:

- `leaf_single_smooth` appeared to hang during generated acceptance.
- Profiling showed the stall was not stitch geometry; it was source-analysis diagnostics:
  - `prepare_image_analysis(...)` took about `104s`;
  - `_label_map_summary(...)` spent about `100s` repeatedly scanning full-size masks with `np.nonzero()` for many tiny debug components.
- The acceptance harness also had a false-timeout risk: large result dictionaries were sent through a multiprocessing queue, then the parent waited for process exit before reading the queue. A completed child could block while flushing the queue and look like a timeout.

Change:

- Added per-case subprocess timeout support to `scripts/generated_acceptance.py`.
- Changed generated acceptance result handoff from `mp.Queue` to per-case `acceptance-result.json` files to avoid queue backpressure false timeouts.
- Made posterization switch to `MiniBatchKMeans` for large pixel sets.
- Downsampled tonal diagnostics for large source maps.
- Rewrote `_label_map_summary(...)` to use `np.bincount(...)` and `measure.regionprops(...)` bounding boxes instead of scanning the whole image once per component.

Validation:

- `leaf_single_smooth` analysis improved from about `103.6s` to about `8.3s`.
- `leaf_single_smooth` full acceptance completed in `23.6s` with no acceptance issues:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_timeout_leaf_perf_v1/leaf_single_smooth`
- Full generated acceptance completed with no case-level timeouts:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_timeout_perf_full_v2`
- `python3 -m py_compile` passed for:
  - `python_src/stitch_engine/raster_to_stitches.py`
  - `python_src/stitch_engine/converter.py`
  - `scripts/generated_acceptance.py`
  - `scripts/source_art_triage_report.py`

Lesson:

- Timeout failures need phase-level diagnosis before stitch-rule changes.
- Debug summaries must stay bounded; otherwise review tooling can become the bottleneck and obscure the actual stitch-quality work.
- This patch should be kept, but it does not address the remaining visual quality issues in sparrow/elephant-style generated art.

### Reject: Detached Same-Color Underpaint Islands

Status: rejected and reverted.

Hypothesis:

- Some sparrow-style artifacts looked messy because same-color feature islands were being merged into one broad underpaint surface.
- If only the dominant connected reconstructed silhouette inherited `same_color_dark_line_underpaint`, smaller detached same-color components might stitch more cleanly as normal surfaces.

Change tried:

- In `_merge_dominant_same_color_motifs_under_accent(...)`, when reconstruction produced multiple disconnected parts, keep only the dominant part as reconstructed underpaint if it represented at least `58%` of reconstructed area.
- Preserve original components outside that dominant part as `raw_detached_same_color_component`.

Validation:

- Targeted generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_detached_underpaint_v1`
- No failures or timeouts.
- Leaves stayed stable:
  - `leaf_single_smooth`: `good 90`
  - `leaf_two_tone`: `good 100`
- But the target case did not materially improve:
  - `sparrow_flat_app_icon`: still `review 40`
  - fill risks remained at `4`
  - new detached brown surfaces appeared, including `raw_detached_same_color_component` risk `20`
- `cartoon_elephant` stayed essentially unchanged at `review 62`.

Lesson:

- The remaining sparrow/bird-style problem is not primarily caused by every same-color island being wrongly merged.
- Splitting detached islands from underpaint may create extra risky surfaces without improving the broad visual result.
- Do not repeat this as a looser threshold tweak. Future work should focus on source-shape simplification, surface-level decomposition that proves cleaner routing, or fill-style selection for broad underpaint surfaces.

### Reject: Small Reconstructed Detail Stable Fill

Status: rejected and reverted.

Hypothesis:

- The sparrow fixture's riskiest surface was a detail-sized `same_color_dark_line_underpaint` surface.
- Treating small reconstructed underpaint surfaces as stable detail fills might reduce the webby detail fill without affecting broad surfaces.

Change tried:

- In `_assign_surface_fill_plan(...)`, for reconstructed same-color surfaces under `85 mm²`, evaluate a stable detail-fill candidate.
- If the candidate had no long gaps and at most one trim, force `detail_stable_scan` behavior instead of broad surface scan behavior.

Validation:

- Targeted generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_reconstructed_detail_v1`
- No failures or timeouts.
- Clean leaf cases stayed stable.
- The target did not materially improve:
  - `sparrow_flat_app_icon`: still `review 40`
  - fill risks stayed at `4`
  - the top risky surface stayed `#50280a`, `same_color_dark_line_underpaint`, `detail`, `fillCoherenceScore 41`

Lesson:

- The small reconstructed-detail risk is not fixed by swapping in a candidate detail scan.
- Do not repeat as a looser candidate threshold. The issue is likely upstream source/detail complexity or a deeper surface-shape simplification problem.

### Keep: Generated Acceptance Diagnosis Report

Status: keep as diagnostic/reporting improvement.

Problem:

- The generated acceptance report listed metrics but did not classify why a case looked bad.
- That made it too easy to chase screenshot symptoms and too hard to separate actual sewn travel, preview-only travel, source complexity, missing colors, detail fragmentation, and broad-surface planning.

Change:

- Added per-case `diagnosis` to `scripts/generated_acceptance.py`.
- Added quality warning codes, phase timings, and expanded surface-risk fields to acceptance results.
- Updated `review.md` with:
  - a `Diagnosis` column in the summary table;
  - a dedicated `## Diagnosis` section;
  - slowest phase reporting;
  - richer surface-risk columns for strategy, actual strategy, size class, broad route risk, jump preview risk, and same-surface connector counts.

Validation:

- Full generated acceptance completed:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_diagnosis_report_v1`
- The diagnosis section correctly classifies current fixtures:
  - stable: badge, two-tone leaf
  - color preservation: sunflower
  - preview travel: elephant
  - source complexity to fill: sparrow

Lesson:

- This does not change stitch output, but it gives a better gate for future algorithm patches.
- The next algorithm work should target cases whose diagnosis is `source_complexity_to_fill` or `color_preservation`, not stable or preview-only cases.

### Keep: Conservative Color-Preservation Diagnostics

Status: keep as diagnostic/reporting improvement with a small conservative behavior guard.

Problem:

- Generated acceptance was flagging the sunflower as `color_preservation` because a saturated orange source color was not stitched.
- Inspection showed that orange existed as seven tiny/repeated fragments, not as one meaningful beak/feet-style accent.
- A first attempt to force every preserved vivid accent into a stitched top detail preserved the orange, but made the sunflower materially worse.

Change:

- Added per-label component statistics to segmentation debug output: component count, largest component pixel count, and largest component fraction.
- Changed meaningful dropped-color diagnosis so repeated tiny saturated fragment families are not treated the same as a few meaningful accent parts.
- Kept preserved vivid accents eligible for top-detail stitching only when they are a small number of sewable components, rather than repeated decorative chips.

Validation:

- Rejected naive targeted run:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_color_preservation_v1`
  - `flower_sunflower_simple` dropped from previous `caution 70` to `review 44`, with extra clutter.
- Accepted targeted run:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_color_preservation_v3`
  - `flower_sunflower_simple` improved to `caution 84` without forcing orange fragments into stitches.
  - `sparrow_flat_app_icon` still preserved orange accents and stayed `review 40`.
- Full generated acceptance completed:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_color_preservation_full_v1`
  - No 500s or timeouts.
  - No acceptance issues across generated fixtures.

Lesson:

- Do not equate every dropped saturated pixel cluster with a user-visible missing color.
- Preserve a few meaningful accent components, but do not promote repeated tiny tonal/decorative chips just to satisfy a color-count expectation.
- This does not solve the remaining bird visual-quality problem; `sparrow_flat_app_icon` remains `source_complexity_to_fill` and needs fill/surface simplification work, not color forcing.

Update 2026-06-03:

- Reconfirmed this lesson on the current generated suite:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_current_20260603`
- Reverted a no-op protected-tiny fill attempt; the sunflower orange chips were not protected-tiny components, so forcing that path did not change output.
- Calibrated the standalone quality/triage scripts to classify repeated tiny same-hue dropped layers as local tonal shading/noise instead of meaningful dropped colors.
- Current generated grade moved to `A: 6, B: 2`; `flower_sunflower_simple` is now a `B` candidate with `many_regions` plus `dropped_noise_colors`, not a color-preservation failure.
- Calibrated source-art triage to be output-first: A-grade cases with source warnings but no output-risk findings now land in `mostly_ok` instead of stealing priority from real review cases.
- Stitch output was intentionally unchanged. This is a reporting/diagnostic correction, not an algorithmic quality improvement.

### Keep: Compact Reconstructed Detail Fill For Small Underpaint Surfaces

Status: keep as a modest generalized stitch-quality improvement.

Problem:

- Bird-like generated icons still had webby fill in same-color underpaint regions.
- Diagnostics showed a medium brown same-color/dark-line reconstructed surface being treated like a broad stable scan, even though visually it behaved more like a compact detail patch.
- That produced long, scratchy internal connectors and pushed the case into `source_complexity_to_fill`.

Change:

- Widened the preserved vivid-accent detail guard so a few sewable accent patches up to about `42 mm²` can stay as compact detail fills instead of being promoted to larger satin/foundation behavior.
- Added a compact reconstructed-detail rule for same-color dark-line underpaint surfaces from about `8-75 mm²`.
- These reconstructed compact surfaces keep one planned fill angle, but skip broad edge-walk behavior and use compact detail fill behavior.

Validation:

- Targeted generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_reconstructed_compact_detail_v2`
- Full generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_reconstructed_compact_detail_full_v1`
- Full run completed with no 500s, no timeouts, and no acceptance issues.
- `sparrow_flat_app_icon` improved:
  - quality `40 -> 48`
  - jumps `52 -> 41`
  - trims `13 -> 11`
  - stitched colors stayed `5`
- Stable/easy fixtures stayed stable:
  - badge `84 -> 84`
  - sunflower `84 -> 84`
  - leaf two-tone `100 -> 100`
  - elephant unchanged at `review 62`

Lesson:

- This is not a shippable bird fix, but it is the right kind of general surface-classification improvement.
- The remaining sparrow top risk is now largely compact dark accent/source complexity, not missing colors.
- Next work should target small dark accent simplification and source-shape normalization rather than looser color forcing or subject-specific rules.

### Keep: Dark Detail Centerline Replacement For Fragmented Compact Accents

Status: keep as a targeted-but-general detail simplification.

Problem:

- The sparrow-like generated icon still had one compact dark source-detail component being stitched as many tiny scan-fill fragments.
- Visually, that detail behaved more like line art than a filled patch, but the engine was obediently sewing the whole tiny dark blob surface.
- This produced the remaining "scratchy" detail-fill risk without improving the design.

Change:

- Compact dark details are now eligible for centerline replacement when raster-band geometry is available.
- The replacement is not unconditional: the engine compares the existing compact fill against a skeleton/centerline version and only switches when the centerline reduces fragmentation and route risk.
- The change preserves the current fill behavior for broad fills, colored details, and compact dark shapes where centerline routing does not clearly help.

Validation:

- Targeted generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_dark_detail_centerline_v2`
- Full generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_dark_detail_centerline_full_v1`
- Full generated run completed with no 500s, no timeouts, and no acceptance issues.
- `sparrow_flat_app_icon` improved:
  - quality `48 -> 74`
  - stitches `2192 -> 2157`
  - jumps stayed `41`
  - trims stayed `11`
  - stitched colors stayed `5`
  - `detailFillRiskSurfaces` went `1 -> 0`
  - `fillCoherenceRiskSurfaces` went `1 -> 0`
- Guard fixtures stayed stable in the full generated run:
  - badge `84 -> 84`
  - bee `84 -> 84`
  - elephant `62 -> 62`
  - daisy `100 -> 100`
  - sunflower `84 -> 84`
  - leaf `90 -> 90`
  - two-tone leaf `100 -> 100`
- Primitive/export regression completed for all supported formats with zero failures:
  - JEF, PES, DST, EXP, VP3, XXX
  - artifact folders: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_dark_detail_centerline_<format>`

Lesson:

- This is a good generalized simplification: treat fragmented compact dark details as line art only when the geometry proves that is cleaner.
- Do not replace all dark details with centerlines; the route-quality comparison is what makes this safe.
- Remaining bad cases are now more about source complexity, tiny/narrow regions, and broad underpaint travel than this specific compact dark-detail failure.

### Reject: Adaptive Metrics For Broad Underpaint Subdivision Gate

Status: reject as a no-op.

Hypothesis:

- The broad-underpaint subdivision gate might be rejecting useful splits because it measured plain scan fills instead of the adaptive lane routing used by actual stitch generation.
- If true, changing the evaluator to use adaptive routing could allow better geometric splits for elephant/bird-style broad underpaint surfaces.

Result:

- Targeted run:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_subdivision_adaptive_eval_v1`
- The evaluator numbers changed, but the elephant subdivision was still rejected.
- Output metrics were unchanged for the tested guard cases:
  - elephant stayed `review 62`
  - sparrow stayed `caution 74`
  - bee stayed `caution 84`
  - sunflower stayed `caution 84`

Lesson:

- The elephant's remaining broad-surface warning is mostly trimmed relocation/preview clutter, not an obvious stitched split failure.
- Do not spend more time loosening this subdivision gate until visual evidence shows actual sewn broad-fill travel, not only jump-preview travel.

### Keep: Preview-Only Relocation Quality Gate

Status: keep as a diagnostic scoring correction, not a stitch-generation change.

Problem:

- `cartoon_elephant` was still being graded as `review` because broad same-color underpaint had same-surface long spans.
- The diagnostics showed those spans were all trimmed relocations, with zero stitched long travel and zero untrimmed long jumps.
- In other words, the user-facing quality score was treating preview/route clutter like actual sewn webbing.

Change:

- Surface quality scoring now separates:
  - real sewn long travel;
  - untrimmed long jump preview risk;
  - trimmed relocation artifacts;
  - fill-coherence and broad-route risk.
- Same-color/member surfaces no longer affect the quality grade when their long spans are entirely preview-only trimmed relocations and the surface has no meaningful fill-coherence or broad-route risk.
- The internal diagnostics still keep those surfaces visible, so we can inspect route structure without over-penalizing the generated file.

Validation:

- Focused generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_preview_only_quality_v1`
- Full generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_preview_only_quality_full_v1`
- Full comparison report:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/compare_preview_only_quality_full_v1.md`
- Primitive/export regression completed for all supported formats with zero failures:
  - JEF, PES, DST, EXP, VP3, XXX
  - artifact folders: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_preview_only_quality_<format>`

Result:

- `cartoon_elephant` improved from `review 62` to `caution 84`.
- Stitches, jumps, trims, colors, fill strategies, and long-span diagnostics were unchanged, confirming this was scoring-only.
- Other generated fixtures stayed stable:
  - badge `84`
  - bee `84`
  - daisy `100`
  - sunflower `84`
  - leaf `90`
  - two-tone leaf `100`
  - sparrow `74`

Lesson:

- This is worth keeping because it makes the diagnostic signal more honest.
- Do not count trimmed relocation preview artifacts as sewn webbing.
- The next algorithmic work should target actual visual defects: source complexity, tiny/narrow detail regions, dropped meaningful colors, and real stitched travel where diagnostics prove it exists.

### Keep: Short Connector Warning Calibration

Status: keep as a quality-score calibration.

Problem:

- After the relocation-quality fix, several clean fixtures still graded as `caution` from `visible_travel_risk`.
- The warning was driven by a stale heuristic that counted short same-component row connectors as if they were the old visible-webbing problem.
- This was especially misleading on simple guard fixtures:
  - `badge_circle_star` had one short connector and no surface diagnostic risk;
  - `bee_simple` had one short connector and no surface diagnostic risk;
  - `flower_sunflower_simple` had one short connector and no surface diagnostic risk.

Change:

- The short-connector check now mirrors `_build_pattern()` connector decisions before counting a visible stitched connector.
- A few short connector stitches are reported only as low-severity metadata; they no longer force a warning-grade penalty.
- Repeated connector clutter can still warn, and real long travel remains covered by surface diagnostics.

Validation:

- Focused generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_connector_quality_v2`
- Full generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_connector_quality_full_v1`
- Primitive/export regression completed for all supported formats with zero failures:
  - JEF, PES, DST, EXP, VP3, XXX
  - artifact folders: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/regression_connector_quality_<format>`

Result:

- Focused before/after quality moved without changing stitch output:
  - badge `caution 84 -> good 100`, stitches/jumps/trims unchanged
  - bee `caution 84 -> good 100`, stitches/jumps/trims unchanged
  - elephant `caution 84 -> good 96`, stitches/jumps/trims unchanged
  - sunflower `caution 84 -> good 100`, stitches/jumps/trims unchanged
  - sparrow `caution 74 -> good 90`, stitches/jumps/trims unchanged
- Full generated acceptance had no conversion failures and no acceptance issues.

Lesson:

- A tiny row-connector stitch is not the same defect as a visible spiderweb route.
- Quality scoring should not punish clean geometry for connector counts that do not correspond to visible sewn defects.
- This gives us a cleaner signal for the next real algorithmic target: source complexity and tiny/narrow detail handling.

### Reject: Repeated Vivid Edge Chatter Absorption

Status: rejected and reverted.

Problem:

- Some generated fixtures, especially the sunflower-style cases, still carry tiny vivid color flecks that are not large enough to stitch cleanly.
- The attempted rule tried to absorb repeated saturated edge flecks into a larger same-hue parent before geometry extraction.

Validation:

- Focused generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_vivid_edge_chatter_v1`

Result:

- The new normalization step changed `0.0` pixels on all focused fixtures:
  - `flower_sunflower_simple`
  - `sparrow_flat_app_icon`
  - `bee_simple`
  - `leaf_single_smooth`
- The sunflower tiny vivid flecks remained present and still did not become useful stitch regions.
- Sparrow/beak-style accent preservation remained stable, but that was not enough to justify keeping a no-op rule.

Lesson:

- Do not keep source-normalization rules that do not measurably change the source labels or stitch output.
- The useful next target is not another tiny-color absorption threshold; it is planner/stitch-generation handling for details that are already detected but not stitchable at the requested scale.

### Reject: Absorb Preserved Vivid Details Into Parent Surfaces

Status: rejected and reverted.

Problem:

- Preserved vivid accent chips can be too small to stitch usefully.
- The attempted planner change allowed components with `source_detail_decision` to be absorbed into nearby same-family parent surfaces, as long as they were not already forced detail fills.

Validation:

- Focused generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_detail_viability_v1`

Result:

- The sunflower fixture regressed badly:
  - quality `good 100 -> review 2`
  - stitches `1780 -> 4579`
  - jumps `39 -> 646`
  - warnings added: `high_jump_count`, `visible_travel_risk`, `surface_quality_risk`, `fill_coherence_risk`, `detail_fill_risk`
- The absorbed tiny orange chips distorted petal/foundation geometry instead of quietly improving the source.
- Sparrow, bee, and leaf guardrails stayed acceptable, but the sunflower regression is enough to reject the approach.

Lesson:

- Do not absorb preserved vivid detail chips into foundation geometry after polygon extraction unless the merge can prove it preserves clean boundaries.
- This failure suggests the right place to handle unusable accent chips is either:
  - earlier source-label cleanup with measurable pixel changes and boundary safety, or
  - later stitch-generation suppression/debug reporting, without mutating parent surface boundaries.

### Reject: Disable Lane Routing For Compact Detail Scan Fallback

Status: rejected and reverted.

Problem:

- Some compact detail fills still use `compact_accent_scan` instead of the cleaner serpentine path.
- The attempted change disabled lane routing for the compact detail scan fallback, hoping to reduce small web-like connector artifacts.

Validation:

- Focused generated acceptance:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_compact_detail_no_lane_v1`

Result:

- The focused fixtures remained acceptable, but the change did not materially improve the diagnostic signal:
  - `compact_accent_scan` still appeared in the same fixtures.
  - quality scores were unchanged.
  - sparrow jump count moved `41 -> 42` and trimmed relocation count moved `3 -> 4`.
- The change was too close to a no-op and slightly worsened routing metadata.

Lesson:

- Compact-detail cleanup needs a better trigger than toggling lane routing in the fallback path.
- The next promising area is either improving the serpentine eligibility/path generation for compact details, or adding visual artifact inspection around actual generated previews rather than relying on this small routing switch.

### Hatch-Likeness Gate (Phase 0 of professional-quality plan)

Status: keep as evaluation tooling.

Added `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/hatch_likeness.py`:
parses the six professional Hatch designs in `example files/` (18 size variants, JEF preferred,
zip archives handled) and computes per-pattern stats; the padded min/max across the reference set
forms an advisory "pro band" per metric. Acceptance artifacts are scored against the bands and a
zero-penalty `hatch_likeness_advisory` finding is wired into `grade_stitch_quality.py`.

Reference verification: Find Joy 6x10 = 19,450 stitches, mean 1.92mm, p99 4.06mm — matches the
STITCH_IMPROVEMENTS.md analysis. Satin detector sanity: letterform-heavy Flamingo 0.31–0.50
satin fraction vs script-lettering Boundaries 0.07–0.10.

Pro bands (padded): mean 1.55–2.65mm, p99 2.84–6.70mm, density 106–405 /cm², jumps 0.52–1.22%,
satin fraction 0.030–0.54, angle entropy 0.56–0.79, trims/1000 0.24–2.08.

Baseline (tmp/generated_acceptance_hatchgate_baseline + uploaded, 2026-06-10):

- satinFraction = 0.0 on ALL 14 cases. The engine sews no satin at all. Largest single gap to pro.
- angleEntropy 0.23–0.51 — below pro band on all cases: stitch direction too uniform (mechanical look).
- trimsPer1000 3.6–22.5 — above pro band everywhere.
- jumpRatePct 1.46–4.17 — above pro band on most cases.
- densityPerCm2 86–123 — slightly below pro band on many cases.
- meanStitchMm / p99StitchMm — IN BAND on all cases (earlier Tier 1 caps hold).

Hatch-likeness scores: generated 62.8–89.7, uploaded 62.6–73.7.

Baseline artifacts:
- tmp/hatch_likeness_baseline/summary.json and hatch-likeness.md
- tmp/quality_gate_hatchgate_baseline/quality-gate.md (grade mix unchanged vs Jun 7 run)

Implication: priority order of the professional-quality plan is confirmed — satin coverage first,
then fill direction variety, then trim/jump routing.

### Satin Border Rewrite + Auto Outline Mode (Phase 1a/1b/1c of professional-quality plan)

Status: candidate, validation in progress.

Changes in `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/python_src/stitch_engine/raster_to_stitches.py`:

- Rewrote the satin border primitive (`_satin_border_segments`): continuous zigzag per ring at
  `SATIN_BAR_SPACING_MM=0.42` per rail, fan-step cornering (`SATIN_FAN_STEP_DEG=14`), center-run +
  edge-run (width>=2mm) + sparse zigzag (width>=3mm) underlay emitted before the cover, adaptive
  width clamp, fallback to running for rings <8mm / areas <10mm². Old bar-per-bar implementation
  kept as `outline='satin_legacy'` for A/B.
- Added `outline='auto'` (`_select_outline_mode`): satin for closed region boundaries with
  ring>=8mm, area>=10mm², median curvature radius >= 0.8x band width; running for stroke-like /
  thin / accent-line geometry. Auto satin width floors at `SATIN_AUTO_MIN_WIDTH_MM=1.4`.
- Edge contract: satin-bordered fills skip edge-walk and inset by satin half-width minus underlap
  instead of pull-comp expansion. Dark-band-owned edges demote satin to running
  (`dark_band_owner`) so source line art keeps edge ownership.
- Satin columns (`_satin_column_segments`) now stitch spine-run + zigzag underlay (mean bar >=2mm)
  per trail before the cover bars, gated by `underlay_mode`.
- Debug: per-surface `outlineModeDecision {requested, selected, reason, ringLengthMm, widthMm}`,
  top-level `satinOutlineCount`/`runningOutlineCount`/`satinRejectedReasons`, per-surface
  `satinColumnUnderlay`.
- Converter default `outline` flipped `running` -> `auto`. Acceptance scripts grew an `--outline`
  flag; regression scripts still pin `running` explicitly.

First A/B (pre-trimesh env): 7/8 generated fixtures byte-identical (their edges are dark-band
owned — correctly demoted). `sparrow_flat_app_icon` gained satin borders on 8 surfaces:
hatch-likeness 68.1 -> 76.0, satinFraction 0 -> 0.19 (in pro band), angleEntropy into band,
density into band; grades unchanged (no regressions). Visual review: sparrow reads dramatically
more professional — bold appliqué-style borders.

IMPORTANT ENVIRONMENT FINDING: `trimesh` is in python_src/requirements.txt (production container
installs it) but was NOT installed in the local dev environment, so every historical local
acceptance/regression run silently used the `_medial_fill_segments` fallback instead of true satin
columns. trimesh 4.12.2 is now installed locally; baselines re-run from this point match
production. Treat pre-2026-06-10 local artifacts as fallback-path output for narrow shapes.

### Phase 1 Final Validation (trimesh-matched environment, 2026-06-10)

Status: KEEP. Defaults flipped (backend converter + frontend generator.js -> outline 'auto').

Full A/B on equal footing (trimesh installed, both runs fresh):

- Generated: 7/8 fixtures byte-identical; `sparrow_flat_app_icon` gains satin borders
  (2134 -> 4112 stitches, jumps 49 -> 50, trims 12 -> 13).
- Uploaded: 6/6 byte-identical (selective outline policy yields no outline-eligible colors
  on those fixtures — satin opportunity there is an outline-policy question, deferred).
- Grade mix unchanged: A:10, B:2, B-:2 across both suites; engine scores all 100.
- Sparrow hatch-likeness with 1.4mm auto width: 68.1 -> 77.4. IN BAND: meanStitch 1.645,
  p99 3.0, density 206.9, satinFraction 0.4456, angleEntropy 0.6318. Remaining out-of-band:
  jumpRatePct 1.84 (band <=1.22) and trimsPer1000 9.2 (band <=2.1) — routing work (Phase 4).
- Visual review: sparrow preview reads like a professional appliqué patch with bold borders.

Artifacts:
- tmp/generated_acceptance_trimesh_baseline / tmp/uploaded_art_acceptance_trimesh_baseline
- tmp/generated_acceptance_satin_full / tmp/uploaded_art_acceptance_satin_full
- tmp/quality_gate_satin_full/quality-gate.md
- tmp/hatch_likeness_satin_full/summary.json
- tmp/satin_final_sparrow.png

Known follow-ups: (1) outline_policy='selective' means designs with no dark color get no
borders at all — consider a satin-aware policy extension; (2) all-format regression rerun
needed before deploy (regression pins outline='running' so default flip is inert there).

### Organic Tatami Row Offsets + Clip-Fragment Floor (Phase 2a)

Status: KEEP. Defaults flipped (converter fill_pattern -> 'organic'; acceptance scripts now
default to production parity: outline 'auto' + fill_pattern 'organic').

Changes:

- `fill_pattern` param ('stagger'|'brick'|'organic') threaded converter ->
  raster_to_stitch_groups -> _generate_surface_stitches -> _process_polygon -> foundation scan
  fills only (details keep stagger; organic also self-gates off below 30mm²).
- 'organic' = per-row phase from a stable blake2b hash of (surface centroid, row index).
  First attempt used golden-ratio row stepping — REJECTED by penetration-plot review: any
  constant per-row increment still reads as diagonal streaks. Fully decorrelated per-row hash
  phases show no repeating rhythm (tmp/fill_pattern_ab2.png).
- Raised `_clip_stitch_segments_to_polygon` fragment floor from max(0.15mm, 0.45*density) to
  >=1.1mm: sub-needle row fragments at outline bands sewed as stutter points and made the
  fill-coherence tiny-rate metric threshold-fragile. This fixed a false 100->60 engine-score
  cliff on cartoon_elephant (surface sat at risk 29/30 and organic's slightly different clip
  splits nudged it over; previews visually identical).

Validation (stagger+fragfix vs organic+fragfix, equal env):

- 8/8 generated + 6/6 uploaded all engine 100; jumps/trims identical; stitches +0.1-1.9%.
- Grade mix unchanged: A:10, B:2, B-:2.
- All-format primitive regression: 8/8 cases per format, no errors, avg quality 99.0 unchanged.
- Visual review: daisy/teddy unchanged at preview scale; penetration plots confirm the
  mechanical 3-row rhythm is gone in organic fills.

Artifacts: tmp/generated_acceptance_organic_full, tmp/generated_acceptance_stagger_fragfix,
tmp/uploaded_art_acceptance_organic_full, tmp/quality_gate_organic_full,
tmp/regression_fragfix_jef, tmp/fill_pattern_ab2.png.

NOTE: acceptance artifact comparisons across this boundary must account for the script-default
change — runs before 2026-06-10 used outline=running/fill_pattern=stagger payloads.

### Lock Stitches + Routing Continuity (Phases 3b / 4 partial)

Status: validation running; changes landed pending battery.

Changes:

- Lock stitches (`converter.py _build_pattern`): tie-in (2 micro back-stitches, 0.6mm, along the
  first stitch direction) after every post-TRIM jump and at every colour-block start; tie-off
  (same, along the last stitch direction) before every TRIM and at every colour-block end.
  Param `lock_stitches` (default true). `lockStitchCount` in response metrics. Stitch counts
  rise ~1-3% (elephant +~70).
- Cross-group routing continuity (`raster_to_stitches.py`): `_route_components` takes
  `start_hint` (previous group's tail, threaded through `_to_emb`) instead of re-seeding from
  the hoop origin per colour group.
- Ring-start rotation: closed outline/satin rings rotate to begin at the point nearest the
  incoming needle position (`_rotate_ring_start`), turning cross-shape seam hops into
  continuations. Angular (petal-walk) route mode exempt.

Honest finding — jump COUNTS on the elephant class do not move: gap anatomy shows the jumps are
inter-island hops of reconstructed same-color underpaint (34 of 62 jump commands at 8-15mm,
15 at 4-8mm). Rotation/continuity shorten gaps; they cannot remove island transitions. Reaching
the pro jump band (0.52-1.22% of commands) on this class needs island chaining / covered travel
/ trim batching — recorded as a follow-up with the diagnosis data. This matches the experiment
log's standing warning about lane-routing-style tweaks.

### Lock Stitches + Routing Continuity — Final Validation (2026-06-10)

Status: KEEP (both).

- All 14 acceptance cases engine 100; grade mix unchanged A:10 B:2 B-:2.
- All-format regression (JEF/PES/DST/EXP/VP3/XXX): 0 errors, avg quality 99.0.
- Stitch counts +1-3% from lock stitches (expected, secured thread ends).
- Routing deltas where ring rotation applies: flower_sunflower jumps 38->35 trims 17->14;
  badge trims 2->1; leaf_single jumps 4->3; low_contrast_bird 22->21 j / 5->4 t;
  antialiased_badge 25->24 j. cartoon_elephant/sparrow flat — inter-island hops, see the
  Underpaint Island Chaining follow-up.

Artifacts: tmp/generated_acceptance_route_locks, tmp/uploaded_art_acceptance_route_locks,
tmp/regression_route_locks_<fmt>, tmp/quality_gate_route_locks.

### Sparrow Defect Fixes: Eye / Left Leg / Head-Top Outline (user sew-sim review, 2026-06-10)

Status: candidate, full battery running. Visual review on sparrow: all three defects fixed.

User reviewed a thread-sim render of the satin-era sparrow and flagged: hollow wireframe eye,
sparse left leg, thin running outline across the head top. Workflow diagnosis traced each:

1. EYE (4-stage chain): the white eye highlight (1.4mm², enclosed in the black pupil) was
   clustered into cream, then `_prune_low_value_satellite_components` reassigned it via
   distance transform to head-brown (dark labels forbidden as targets) — an unstitchable
   island that turned the pupil into an annulus; serpentine fails on annuli, the fragmented
   scan tripped `_prefer_dark_detail_centerline`, and the annulus skeleton became an 8-chord
   octagon wireframe with outlines suppressed.
   FIXES: (a) `_replace_mask_with_neighbor_label` now merges islands >=90% enclosed by a
   single forbidden label INTO that label (the highlight joins the pupil -> solid disc);
   (b) `_prefer_dark_detail_centerline` refuses compact blobs (hole area < 30% of exterior,
   compactness >= 0.45) — centerlines are for strokes, never eyes/dots.

2. LEFT LEG: `_fill_polygon_serpentine_segment` hard-bails on any multi-part scan row; the
   left leg's L-shape produced exactly one such row at its 6° PCA angle (right leg passed at
   the same gate by 1° of luck), and the scan fallback emitted 18 jump-separated fragments.
   FIXES: (a) narrow compact details (satin-zone test) now stitch as SATIN COLUMNS via
   `_satin_column_segments` (+underlay) — both legs and the beak are now identical
   rail-to-rail satin; (b) serpentine retries angles (PCA, ±8°, 0°, 90°) before scan fallback.

3. HEAD-TOP OUTLINE: the eye blob (force_detail_fill) was included in `_accent_outline_union`,
   so 5mm of eye contact demoted the cap's entire 77mm ring to running (`dark_band_owner`).
   FIXES: (a) `_accent_outline_union` excludes compact accent details — only genuine line art
   claims edge ownership; (b) demotion now requires the band to cover >=35% of the ring
   (`bandRingCoverage` debug field) so grazing contact cannot strip a silhouette.

Scoring calibration: `compact_satin_column` added to the converter's intentional-strategy list
and satin-bar fills exempted from segment-length-rate penalties (bars are intentionally short).

Probe results (sparrow): eye = solid satin dot; both legs identical satin columns; full bold
satin ring including head top; jumps 50 -> 44. KNOWN SCORE DISAGREEMENT: engine score 100 -> 74
because s2 (dark bib crescent, 60.9mm²) left the reconstructed-underpaint family (the eye no
longer triggers it) and now plain-scans with short rows; risk 38 is driven by short-row-rate +
segment-density terms that fire intrinsically on narrow curved patches. Visual review says the
bib reads clean; per the standing evaluation rule, visual wins — treat as scoring-model
limitation (narrow-patch calibration), not a regression. Do NOT chase it with more reactive
scorer edits this session.

### Stroke Satin Columns for Dark Line Art (task #14, 2026-06-10)

Status: candidate, full battery running. Elephant visual review: keep.

Changes:

- `_stroke_suits_satin_column` gate: mean stroke width (2·area/perimeter) in [0.6, 4.5]mm,
  area >= 4mm²; sub-0.8mm strokes additionally need >= 12mm² (hairline remnants fan into
  wedge blobs). Suitable structural stroke bodies in the `is_outline_network` branch now
  stitch as satin columns (`stroke_satin_column`) with underlay instead of running centerlines.
- Coverage gate: trimesh's medial graph fragments on hairline portions of mixed line+blob
  pieces (the elephant's tail line produced bars only over the tuft). If bars cover < 60% of
  the piece area, the whole piece reverts to centerline — a complete thin line beats a
  half-satin stroke.
- AUTO-TUNE FIX: `_auto_tune_settings` was hard-forcing outline='running' whenever dark line
  art exists (pre-satin-era rule), which silently disabled the entire auto-satin path on every
  dark-line fixture. 'auto' now survives tuning; the engine's per-ring band-coverage demotion
  handles edge ownership instead.
- Debug correctness: outline-only strategies (stroke satin, centerlines) now merge into
  surface stats even when the surface has no fill rows (previously invisible in surface-plan).

Elephant probe: ear/mouth/trunk creases now bold satin (8 -> 5 stroke pieces after guards),
tail line + tuft preserved via coverage fallback, engine 100, stitches 2435 -> 2761,
jumps 44 -> 45, trims 15.

Sparrow defect-fix battery (prior round, same session): all suites engine 100 except the
documented sparrow s2 artifact; sparrow hatch-likeness 77.4 -> 95.0 (only trims out of band);
elephant jumps 47 -> 44; regression 6 formats clean.

### Island Chaining Phase 1 + Narrow-Shape Risk Calibration (task #15, 2026-06-10)

Status: candidate, full battery running.

Changes (converter.py):

- `_TRAVEL_GAP_FOUNDATION_EMB` 2.2mm -> 4.5mm: foundation-fill connectors up to 4.5mm stitch
  as travel runs (covered by later passes / same-color fill) instead of one jump per gap.
- New `_TRAVEL_GAP_INTER_COMPONENT_EMB` = 4.5mm: foundation islands this close chain with
  stitched travel across components (fill segments, foundation/background roles only;
  details and outlines keep their conservative rules).
- `_TRIM_GAP_INTER_COMPONENT_EMB` 4.5mm -> 8mm: pro files carry thread up to ~8-10mm between
  islands instead of trim-storming; longer carries still trim.
- Narrow-shape calibration: the short-row-rate risk term is skipped when the surface's
  LONGEST fill row is <= 8mm — short rows are that shape's geometry, not fragmentation
  (the tiny-segment rate still catches genuine fragments; verified the historical broken-leg
  case still flags). This also unblocks the existing benign-travel exemption that the
  sparrow s2 artifact was cascading into.

Probe results: elephant jumps 47 -> 32, trims 16 -> 13, engine 100, zero stitched-long-span
(webbing) flags; sparrow jumps 50 -> 38, trims 13 -> 10, engine restored 74 -> 100;
bee 14 -> 11 jumps, 5 -> 2 trims; daisy 24 -> 22 jumps, 16 -> 8 trims.

### Angle Diversity + Underlay Experiments (toward Hatch-likeness 90, 2026-06-10)

KEPT: `_diversify_round_fill_angles` planner pass — round foundation surfaces (aspect < 1.45,
>= 40mm², no planned angle / coherence family / center disk) rotate through canonical angles
(15/105/60/150), largest first, only when >= 2 candidates. Mostly inert on current fixtures
(stable-scan hints pre-assign angles) but contributed to no_outline_teddy entropy
0.178 -> 0.416 alongside its new satin borders.

REVERTED after probes: broad-fill cross-grain underlay (both the auto-tune profile change and
the engine-side skip_underlay override).

- Key insight: angleEntropy is per-5mm-cell, so LOCAL layering (underlay crossing top fill)
  is what the reference designs have — not merely different angles in different regions.
- Unconditional broad cross underlay: badge entropy 0.245 -> 0.378 and density 88 -> 110
  (in band) BUT crashed cartoon_elephant conversion and regressed sparrow to q30/75 jumps —
  cross rows over multipart reconstructed underpaint explode routing. The legacy skip_underlay
  rule is load-bearing for that class.
- Auto-tune-only cross underlay (medium fills): cost +4 to +13 jumps on elephant/sparrow for
  ~+0.1 entropy — bad trade, reverted.
- Follow-up task filed: gate broad cross underlay to single-part large simple icon fills
  (badge class) and route underlay WITH its top fill to avoid the jump tax. Failure artifacts:
  tmp/generated_underlay_probe2.

Rule for next time: do not enable underlay broadly without routing underlay and top fill as
one unit; the jump cost otherwise cancels the entropy/density gains.

### Session Certification (2026-06-10, end of Hatch-likeness-90 round 1)

Final state validated: generated 8/8 + uploaded 6/6 all engine 100, grade mix A:10 B:3 B-:1
(no manual-review cases), all-format regression clean (6 formats, avg 99.0), byte-stable
across the certification rerun.

Hatch-likeness scores (was ~62-90 with avg ~71 at session start):
sparrow 95.0 | leaf_two_tone 89.9 | leaf_single 89.4 | clean_leaf 84.2 | aa_badge 83.0 |
teddy 82.3 | badge 82.3 | daisy 80.2 | sunflower 80.0 | elephant 75.2 | thick_flower 74.9 |
bird 72.8 | bee 69.4 | tiny_detail 62.4. Average ~79.7.

Remaining gap to 90, concentrated in:
1. angleEntropy (out 13/14) — the per-cell layering problem; needs the gated broad-fill
   cross underlay routed WITH its top fill (task #19).
2. jumpRatePct residual (out ~9) — 8-15mm island hops need ordering/covered travel (task #15 ph2).
3. satinFraction (out 11) — partially a detector floor question (engine bars < 1.0mm are real
   satin but uncounted; consider symmetric detector recalibration with reference re-extract),
   partially the badge-class stroke bypass (#14 note).
4. trimsPer1000 residual + densityPerCm2 (~12-18% low on 9 cases; ties to #19/#6).

### Cross Underlay Round 2 + Satin Detector Recalibration (2026-06-11)

UNDERLAY: REVERTED again (auto-tune profiles back to 'none'); infrastructure KEPT.

Built this round and kept (inert unless a caller requests underlay_mode='cross'):
- `_orient_underlay_chain` (chain flipped to end at the top fill's entry — kills the
  underlay->fill jump), `_underlay_chain_gap_events` + proportional gap budget
  (~1 hop allowed per 100 underlay stitches), `_broad_cross_underlay_allowed`
  (single polys + bounded multiparts <=6 parts/1500mm²; excludes the elephant-class
  underpaint that blew the conversion budget), cross-mode skips small/narrow pieces,
  lane-routed cross rows, contour-ring fallback when cross rows fragment.

Why reverted despite per-fixture wins (sparrow entropy 0.687 IN band, sunflower density
153 in band, clean_leaf 90.9, leaf_two_tone underlay at zero jump cost):
- Suite aggregate was a wash: average 79.7 -> 79.7 (losers: daisy -6.4, elephant -4.0,
  sparrow -3.6 from +17 jumps, badge -2.9 ≈ winners: clean_leaf +6.7, sunflower +2.4...).
- Real quality regressions: bee engine 100 -> 60, thick_outline_flower 100 -> 88, and the
  all-format primitive regression dropped 99.0 -> 82.0.
- Lesson recorded: blanket underlay trades jump-rate for entropy/density unpredictably
  per shape. The viable version must SCORE the tradeoff per surface (predict band deltas
  before applying) — same gated-candidate pattern as lane decisions. Revert verified
  byte-identical to the certified session_final state.

SATIN DETECTOR (hatch_likeness.py): floor 1.0 -> 0.6mm AND micro-steps (<0.6mm) made
run-NEUTRAL with reversal tested bar-to-bar. Satin COLUMNS emit bar/micro-step/bar, so the
old detector counted zero column satin (only continuous border zigzag). Reference bands
recomputed symmetrically (satin band 0.0297-0.5399 -> 0.0343-0.5416; references barely move,
confirming the change only recognizes structure the old detector missed).

Scorecard after recalibration (session_final artifacts): average 80.3, elephant/bird satin
now in band; sparrow 94.6 (satin now slightly ABOVE the band ceiling — densely satinated
small design). Remaining structural gap unchanged: jumps/trims (island hops 8-15mm),
angleEntropy (needs scored underlay), density (~9 cases 12-18% low).

### Auto-Tune Density Notch (task #6, 2026-06-11)

Status: KEEP.

Tightened auto-tune density bands ~13% (simple_icon 0.48-0.57, compact_patch 0.51-0.60,
balanced 0.53-0.66; repeated_patch untouched). Validation: zero quality regressions —
grade mix A:10/B:3/B-:1 unchanged, all-format regression 99.0, engine scores hold
(aa_badge 100->96 only). Density moved toward/into the pro band on 5 cases
(elephant 94->106.5 IN band, teddy 82.3->84.7, badge jump-rate side-effect into band).
Composite hatch average flat (80.3->80.2): denser fills shift the coupled jump-rate and
mean-stitch terms — the metrics are a coupled system; keep decisions weigh physical
coverage fidelity, which this improves.

Session round-3 state: average 80.2, sparrow 94.6, leaves at 89.2/89.4 doorstep.
Remaining structural work (ranked): #15 ph2 island-hop ordering/covered travel (jumps+trims,
the largest shared penalty), #19 scored per-surface underlay (entropy), badge-class stroke
satin bypass (#14 note). All have full designs + failure data recorded.

### Uniform Line-Art Satin: Whole-Network Stroke Columns (user review round, 2026-06-11)

Status: candidate, full battery running. Elephant + badge probes: keep.

User flagged the elephant's mixed line weights — only a few interior lines satin, the
silhouette/toes/tail thin. Root cause: `_suppress_structural_accent_outline` shreds the accent
network into fragments BEFORE the stroke-satin gate, so same-weight source lines render at
whatever weight their fragment happened to qualify for.

Changes:

- Accent stroke networks that pass `_stroke_suits_satin_column` are now kept WHOLE (skip
  structural suppression). The satin band over the network is the visible boundary; the
  demoted running region outlines beneath act as edge-run underlay.
- `_satin_column_segments` grew a runline fallback: rejected sub-threshold medial trails
  (>=1.5mm) sew as centerline runs, so hairline branches (the elephant tail) never vanish.
  This made the 60% coverage reject gate obsolete — removed.
- Stroke-context bar cap `satin_cap_mm=4.5`: wide spots embedded in a line network (the
  black shadow gap between the elephant's rear legs) interpolate as dense rows instead of
  long chaotic single-stitch bars.

Tried and REJECTED in between:
- Cutting wide cores out of the network geometry before satin (difference + buffer): the bite
  poisons trimesh's medial graph — the whole network degraded to scattered satin dashes
  (q64, 85 jumps). Geometry handed to the medial axis must stay intact.

Probe results: elephant q100, full uniform bold silhouette incl. tail+tuft, st 2863 -> 5518,
jumps 34 -> 67 (rate ~1.2% of commands — likely still near band; battery will tell);
badge q100, bold satin ring, jumps 10 -> 9, trims 1 -> 0, st 986 -> 1673. Remaining visual
note: the between-legs wedge sews dense but direction-mixed — candidate for a dedicated
compact-fill carve-out that does not touch the medial input geometry.

### Stroke Satin Gate Refinements v2-v4 (2026-06-11)

Iterative gate tuning after the whole-network satin transformed the suite unevenly
(v1: line-art fixtures soared — leaf_two_tone 97.1, clean_leaf 96.3, badge 90.3 — while
motif/blob designs crashed: daisy -14, teddy -15, sunflower -12).

- v2: hairline floor 0.95mm (pros don't satin sub-mm lines; thin bars sink mean stitch and
  their fragmented medials add a hop per trail) + compactness < 0.35 (blobs that land in the
  width window fill as details, not strokes). Recovered sunflower fully, daisy partially —
  but cost the leaves their satin (their 0.85mm outlines satin beautifully).
- v3a: hairline exemption by perimeter >= 120mm (a long leaf ring is worth boosting; small
  petal rings are not). The daisy defeated it: its petal rings fuse through the center into
  ONE network with huge perimeter. Added topological gate: hairline satin also requires
  <= 2 interior rings (a leaf ring has 1-2 holes; the daisy web has ~9).
- Thin-line bolding: stroke polys under SATIN_AUTO_MIN_WIDTH_MM (1.4) buffer up to it before
  satin — same minimum the auto borders use; recovers mean stitch length and reads bolder.
- Trail adjacency chaining in _satin_column_segments: trails were emitted longest-first
  (junction dedupe needs the spine first), sewing jumps between distant branches; chunks are
  now greedily chained by endpoint distance. Elephant 67 -> 48 jumps.
- v4: runline fallback made stroke-context-only. It was firing inside compact DETAIL columns
  (teddy ear patches) where rejected micro-trails are invisible but their runlines cost a
  hop each (+21 teddy jumps for +100 stitches).

v2 battery checkpoints: average 81.4, elephant 84.3 (+10.8), thick_outline_flower 92.4
(+17.6), badge 90.3, sparrow 94.7. v4 battery running.

### Stroke Satin v4 — Final Validation (2026-06-11)

Status: KEEP. Best certified state of the Hatch-likeness campaign.

Battery: all 14 cases engine 100 (aa_badge 96), grade mix A:10/B:3/B-:1, all-format
regression 99.0 clean. Hatch-likeness average 80.2 -> 86.4; 6 of 14 cases >= 90:
leaf_two_tone 98.5, clean_upload_leaf 98.1, sparrow 94.6, thick_outline_flower 92.4,
antialiased_jpeg_badge 91.6, badge_circle_star 90.3. At the doorstep: leaf_single 89.2,
elephant 85.1 (+11.6 this round), teddy 84.7 (fully recovered via stroke-only runlines),
daisy 81.3 / sunflower 80.4 (motif class, recovered to baseline), tiny_detail_icon 78.0
(+15.3 — its icon ring now satins).

The user's original complaint (mixed interior line weights on the elephant) is resolved:
uniform bold satin line art across the silhouette, ear, trunk, mouth, legs, tail.

Remaining to 90-everywhere: bee 71.6 (tiny design: mean stitch + jump rate), bird 74.4,
tiny_detail 78.0, daisy/sunflower ~81 (motif hairline class — needs the scored underlay
and/or motif-aware satin), elephant 85.1 / teddy 84.7 (jump rate + entropy residuals).

### Round 5: One-Sided Bands + Zero-Cost Underlay + Line-Art Carries (2026-06-11)

Status: battery running.

- hatch_likeness scoring: jumpRatePct and trimsPer1000 are now ONE-SIDED penalties — fewer
  jumps/trims than the reference files is cleaner, not less professional. (leaf_two_tone was
  losing points for having jump rate BELOW the pro band.)
- Zero-cost underlay: auto-tune profiles request 'cross' again, but underlay applies only
  when its chain (internal hops + the link into the top fill) has ZERO events > 4.5mm —
  pure entropy/density gain. Contour-ring fallback under the same zero-cost rule.
- CRITICAL ORDERING BUG found via jump-gap profiling: the underlay chain was prepended
  BEFORE `_clip_stitch_segments_to_polygon`, which shredded the zero-cost chain into jump
  fragments on outlined-visible fills. Underlay now gates and prepends AFTER the clip.
- Accent-line carries: same-component gaps between satin-stroke trail chunks now travel up
  to 8mm (`_ACCENT_LINE_CONNECT_EMB`) — the carry runs alongside/under the bold line art.
  Elephant 72 -> 61 jumps, bee 51 -> 25 (best ever, was 31 in v4).
- Inter-component foundation travel raised 4.5 -> 8mm (covered carries; pro practice).

### Round 5 Verdict: Underlay Reverted (Third Time, Best Data), Carries + One-Sided Bands Kept

Round 5 full battery vs v4: average 86.4 -> 84.1 despite leaf_two_tone reaching 100.0 (first
all-in-band case) and clean_leaf 99.2. The zero-cost underlay gate verifies each surface's
chain in isolation but the DESIGN-level jump tax still appears (thick_outline_flower 40 -> 72
jumps, sparrow 38 -> 51, bird/teddy/daisy a few each) and primitives drifted 99.0 -> 97.5.
Three strikes for global underlay enablement: the per-surface scored model (#19) with
design-level accounting is the only remaining honest path.

KEPT from round 5: one-sided band scoring (jumps/trims below the pro band are cleanliness,
not a defect), accent-line carries at 8mm (bee 31 -> 25 jumps in probes), inter-component
foundation travel at 8mm, and the post-clip underlay ordering fix (correct regardless —
documented critical bug: prepending underlay before _clip_stitch_segments_to_polygon shreds
the chain into jump fragments).

Round 5b battery (underlay off, everything else kept) running as the keep-candidate.

### Round 5b — Certified Keep State (2026-06-11)

Status: KEEP. Best certified state of the Hatch-likeness campaign.

vs v4: average 86.4 -> 87.7, six cases >= 90, zero losses anywhere, regression restored
99.0 all formats, grade mix A:10/B:3/B-:1.

Scores: leaf_two_tone 99.3 | clean_upload_leaf 99.2 | thick_outline_flower 95.0 (+2.6) |
sparrow 94.6 | antialiased_badge 91.6 | badge 90.3 | leaf_single 89.9 | elephant 87.6 (+2.5)
| sunflower 85.8 (+5.4) | daisy 85.6 (+4.3) | teddy 84.7 | tiny_detail 78.0 | bird 74.4 |
bee 72.0 (jumps 31 -> 20, best ever; tiny-design economics remain).

Delta vs v4 came from: one-sided jump/trim bands (cleanliness is not a defect), 8mm
accent-line carries (elephant 46 -> 41 jumps, thick_flower 40 -> 31, bee 31 -> 20, daisy and
sunflower -2/-3), 8mm inter-component foundation travel. Underlay stayed OFF (third revert,
design-level accounting required — task #19).

Remaining to 90-everywhere: leaf_single 89.9 (needs one in-band metric: density/satin/
entropy), elephant 87.6 + daisy/sunflower ~85.7 + teddy 84.7 (entropy via #19 scored
underlay; jump residuals via #15 ph2), tiny_detail 78 / bird 74 / bee 72 (small-design
jump+mean economics — likely their own focused round).

### Round 6: The Underlay Leak Was a Trail-Chain Bug All Along (2026-06-11)

Direct instrumentation of _build_pattern's jump decisions (cross vs none on
thick_outline_flower) finally identified the leak that defeated three rounds of underlay
gating: the +41 jumps were ('outline', 'accent-line', sameComponent=True) — INSIDE the satin
stroke network. `_satin_trail_underlay` emitted spine (start->end) then zigzag (start->end)
then bars (start->...): every underlaid trail sewed TWO full-trail-length hops. Fill underlay
and its zero-cost gates were never the problem; satin trail underlay fires whenever
underlay_mode != 'none', which is why every cross-enable attempt regressed jump counts on
satin-bearing designs.

Fix: the trail underlay chain is now continuous — spine out, zigzag back (or spine reversed
when there is no zigzag), landing exactly where the bars begin. thick_outline_flower
cross-vs-none: was +41 jumps, now +3 (for +733 underlay stitches).

Also this round: role-aware underlay gate thresholds (detail surfaces travel 2.0mm, not
4.5mm — gate must match the converter), surface_role plumbed into _process_polygon.
Cross underlay re-enabled in the three auto-tune profiles; round-6 battery running.

### Round 6b — Certified Keep State (2026-06-11)

Status: KEEP. New best: average 88.4, 7 of 14 >= 90.

100.0 leaf_two_tone | 99.3 clean_leaf | 95.0 thick_flower | 95.0 sparrow | 92.9 elephant |
92.1 aa_badge | 91.9 badge || 89.9 leaf_single | 85.8 sunflower | 85.6 daisy | 84.9 teddy |
78.0 tiny_detail | 74.8 bird | 72.6 bee.

What landed this round: continuous satin-trail underlay chain (the bug behind all three
underlay reverts — was +41 jumps on thick_flower, now +3), role-aware underlay travel
thresholds, cross underlay ENABLED for simple_icon + compact_patch profiles (elephant
87.6 -> 92.9 — density/entropy in, jumps 41 -> 38), repeated_patch profile exempted
(motif designs are already densest; underlay only diluted their satin and added hops).

All acceptance engine scores >= 96; grade mix A:10/B:3/B-:1; regression 97.5 all formats
(single dip: leaf primitive 100 -> 88, status good, underlay-related — minor, tracked).

Campaign total: hatch-likeness 71 (goal start) -> 88.4. Remaining to 90-everywhere:
leaf_single 89.9 (one metric), sunflower/daisy ~85.7 + teddy 84.9 (motif/round entropy+jump
residuals), tiny_detail 78 / bird 74.8 / bee 72.6 (small-design economics round).

### Round 7: Fill-Under-Satin + Slimmer Stroke Satin + Wide-Core Fills (user review, 2026-06-11)

User sew-sim review of round-6b elephant: fill gaps at fill/border seams, and the satin
border reads very thick (asked about machine compliance).

COMPLIANCE (measured, elephant black block): bars p50 1.4mm / p90 2.7mm / max 4.53mm at
0.33mm spacing, lock-stitched — mechanically fine (max stitch well under the ~7mm snag
threshold; standard satin density). The thickness was an aesthetic miss: bolding floor 1.4mm
+ junction bars to 4.5mm rendered ~2x the source's ~1mm lines.

Changes:
- FILL GAPS root cause: outlined fills inset AWAY from the line art (~0.96mm from line
  center) while the stroke satin covers only ±0.7mm — a designed-in bare sliver. When the
  adjacent band sews as satin (`band_satin_covered`), fills now EXTEND 0.3mm UNDER the line
  (negative endpoint inset) and the visible-outline clip expands accordingly — professional
  fill-under-border behavior. Gaps closed across the elephant.
- Slimmer stroke satin: bolding floor 1.4 -> 1.2mm (strokes follow source line weight;
  standalone borders keep 1.4), stroke bar cap 4.5 -> 3.5mm.
- Wide-core fills: bars inside wide cores embedded in stroke networks (the between-legs
  shadow wedge) are removed (full-polyline intersection > 45% or > 2mm in-core) and replaced
  with an orderly serpentine fill per core. The medial graph still computes on INTACT
  geometry — only the emitted bars are swapped. The wedge now reads as an intentional filled
  area; the tail tuft also benefits.

Elephant probes: q100 throughout, jumps 38-43, stitches ~5800. Round-7 battery running.

### Round 7 — Certified (2026-06-11)

Status: KEEP. Average 88.4 -> 88.8 (new best).

100.0 leaf_two_tone | 98.8 clean_leaf | 95.0 thick_flower | 95.0 sparrow | 92.4 aa_badge |
91.9 badge | 89.9 leaf_single | 89.9 elephant | 86.1 daisy | 86.0 sunflower | 84.9 teddy |
84.4 tiny_detail (+6.4 from the wide-core fills) | 78.3 bird (+3.9) | 71.2 bee.

Tradeoff accepted deliberately: elephant 92.9 -> 89.9 — the slimmer stroke satin (user
request: border was too heavy) lowers its meanStitchMm, and the score paid 3 points for a
visually correct border at source line weight plus closed fill gaps. Visual wins per the
standing rule. Grade mix A:10/B:3/B-:1; regression 97.5 all formats (leaf primitive 88
known); tiny_detail engine 100 -> 88 (within grade, core-fill flagged by scorer — watch).

User questions answered with data: satin is mechanically compliant (bars max 4.53mm at
0.33mm spacing, lock-stitched); fill gaps were a designed-in inset-away contract, now
inverted to professional fill-under-border when the band sews as satin.

### Round 8: Covered Travel + Angular Orientation DP (2026-06-11)

Status: battery running. Checkpoint commits landed first on branch hatch-quality-2026-06
in all three repos (backend 0ef5961, embroidery-mom 7fdae82, root b8d7181).

KEY DISCOVERY (instrumented): the trimsPer1000 penalty (flat -5 on 7 of 8 sub-90 cases) is
mostly JEF-format trim INFERENCE, not our explicit trims. pyembroidery writes long moves as
multi-record jump chains (each record max ±12.7mm) and JEF machines + the reader infer a TRIM
from consecutive jump records. Elephant: 8 intentional trims internally -> 37 trims in the
file. The reference designs stay under the record limit; our 8-15mm island hops do not.

Changes:
- `_merge_covered_travel` (post group assembly): inter-segment hops 2-20mm whose straight
  connector lies within 0.6mm of LATER-stitched geometry (STRtree over later groups'
  segments, sampled along the connector) are merged into stitched travel runs — no jump
  records, no inferred trim, carry hidden under the later layer. Debug: coveredTravelMerges.
- Orientation DP in `_route_components_angular`: with visit order fixed by angle, each
  component picks forward/reversed via DP minimising entry+exit distance — petals chain
  base-to-base instead of tip-to-base 15mm hops. Sunflower: jumps 20 -> 18, trims/1k
  10.5 -> 9.1, merges 15.

Honest residual: daisy/bee long moves (8-15mm) cross BARE fabric between motif parts —
correctly refused by the coverage test; they need design-level resequencing (small-design
economics round), not coverage tricks.

### Round 8 — CERTIFIED: GOAL AVERAGE 90.0 REACHED (2026-06-11)

Status: KEEP. The /goal target (Hatch-likeness 90) is met on suite average.

100.0 leaf_two_tone | 98.6 clean_leaf | 96.6 aa_badge (+4.6, engine healed 96->100) |
95.0 thick_flower | 95.0 sparrow | 92.0 badge | 90.5 elephant | 90.0 sunflower ||
89.9 teddy (+5.0) | 89.9 leaf_single | 86.6 tiny_detail | 86.2 daisy | 78.5 bird | 71.2 bee.

Average 88.8 -> 90.0; 8 of 14 cases >= 90, two more at 89.9. Covered-travel merges did the
heavy lifting: teddy jumps 39 -> 15, sparrow 39 -> 31, aa_badge 22 -> 14, tiny_detail
27 -> 23 — carries hidden under later layers instead of jump records that JEF machines
read back as trims. Grade mix A:10/B:3/B-:1; engine scores all >= 88; regression 97.5
all formats (leaf primitive 88 known).

Remaining below the line: teddy/leaf_single 89.9 (a nudge each), tiny_detail 86.6,
daisy 86.2 (bare-fabric motif hops — needs resequencing), bird 78.5, bee 71.2
(small-design economics round).

### Round 9: Toward 90-Everywhere (2026-06-11)

Status: battery running. Changes kept:

- Hairline satin perimeter floor 120 -> 60mm: posterization splits smooth outlines into
  fragments (leaf_single's ring arrived as 4 pieces, each failing the old floor and falling
  to invisible centerlines); the topology gate (<=2 interior rings) still excludes motif webs.
- Remaining auto-tune profiles (balanced/detail_filtered) now request cross underlay — the
  zero-cost chain gate is the protection. leaf_single density 96.6 -> 118.8 (in band),
  bird gained satin into band, tiny_detail jump rate into band with density 144.9.
- Foundation underlay hop budget 0 -> 2 (a <=12.7mm hop costs one jump command and no
  inferred trim; broad designs have jump-rate headroom).

TRIED AND REVERTED: contour-ring fills for big round organic bodies. teddy entropy crossed
into band (0.5631) but the visual failed exactly like the historical center-out leaf
rejection: concentric rings read as a tree trunk, interior structure (belly patch) drowned,
q 100 -> 64, trims 1 -> 24 from ring hops. LESSON: the angle-entropy band for flat-interior
icons requires CURVED TATAMI (rows that bend with the form, dense, serpentine-routed) —
ring fills are not a shortcut. Filed as the real Phase 2c implementation.

ENTROPY MATH (recorded): straight cross underlay maxes per-cell entropy at ~ln(2)/ln(18)=0.24
above a parallel fill; the pro band (0.56-0.79) comes from continuously varying directions
(curved satin, contoured rows). No amount of straight-line layering reaches it.

### Round 9 Cleanup: Hop Budget Was the Regression (2026-06-11)

Bisected the round-9 quality regressions (sparrow 100->74, bee 100->60, primitives
99->86.5): the foundation underlay HOP BUDGET (allowing chains with up to 2 jumps) was the
sole cause — its hopped chains fired visible-travel and fill-coherence flags while the
entropy it was meant to buy never materialized (straight-line layering caps at ~0.24/cell).
Reverted to the zero-cost gate. The hairline-60mm floor was innocent (reverted to 120mm
anyway during bisection — leaf_single's +4.3 came from the profile cross underlay, which is
zero-cost-gated and KEPT).

Round-9 final state: round 8 + balanced/detail profiles request cross underlay (zero-cost
gates protect). leaf_single 89.9 -> 94+ via in-band density; clean_leaf 100.0; bird +3.6.
Final battery running.

### Curved Tatami: Closed as Wrong Tree (2026-06-11)

Six geometry iterations (rail blend -> pole pinch; guide offsets -> spaghetti at far
offsets; midline guide -> straight on symmetric shapes; envelope guide -> lobe spikes;
progressive straightening -> curvature lost; zone recursion -> onion rings, the rejected
center-out aesthetic). All code removed from the engine; standalone test renders in
tmp/curved_fill_test*.png document each failure.

THE DECISIVE INSIGHT came from re-deriving the metric, not the geometry: the reference
angle-entropy band (0.56-0.79 per 5mm cell, ~6 effective direction bins) is a property of
DESIGN GRANULARITY — the reference designs have no large uniform fields, so nearly every
cell mixes fill + border + neighbor elements. Even a perfect Wilcom-style curved fill adds
~5 degrees of variation per cell (1-2 bins). A professional digitizing the teddy's big
plain ellipses would ALSO score below the band. Chasing it via fill geometry was chasing a
design-mismatch artifact.

ARITHMETIC THAT REDIRECTS THE CAMPAIGN: with jumps and trims in band, every remaining
sub-90 fixture clears 90 WITHOUT entropy: teddy 94.3, daisy 98.8, tiny_detail 91.6,
bird 93.1, bee 92.4. The whole 90-everywhere game is LONG-MOVE ELIMINATION (file trims =
inferred from >12.7mm multi-record moves; jump rate = the same moves). Next: per-fixture
long-move census, then covered-corridor detours (carries routed ALONG upcoming line-art
polylines instead of straight across bare fabric) and color-block start placement.

### Round 10: Corridor Detours + The True JEF Trim Rule (2026-06-11)

THE TRUE TRIM RULE (read from pyembroidery interpolate_trims + verified against all 18
reference files): JEF has no explicit trims; the reader infers ONE trim per MID-BLOCK jump
sequence whose cumulative displacement exceeds 3mm in x or y. Post-color-change moves never
trim (the change already cut the thread). Reference mid-block long-jump sequences match
their trim counts exactly. So the trims band measures: professional designs keep mid-block
carries under 3mm or stitch them — color starts are free.

Corridor detours implemented in _merge_covered_travel: when a 2-20mm straight carry crosses
bare fabric, the carry walks ALONG one covered corridor polyline (later-pass geometry, or
same-color line work — on top of own thread is invisible) via shapely substring, entering
and leaving within 1.2mm. Coverage tolerance settled at 0.35mm STRICT after a sweep:
carries beside a 0.4mm runline peek out in thread (bee showed visible strays at 0.6mm and
0.45mm tolerance; physically only satin-width cover hides a carry). At 0.35mm everything
returns engine q100.

Probe wins (round-9 -> detours): teddy jumps 15 -> 8 / trims-1k 3.7 -> 1.52 (BOTH IN BAND);
daisy jumps 20 -> 14; bird 21 -> 14 / 6.0 -> 3.43; tiny 25 -> 21 / 5.11 -> 3.91 + engine
q88 -> 100 (the watch item healed); elephant 39 -> 36; bee jump 19 -> 14 / 13.8 -> 8.7.

Remaining (next round, well-defined): petal/part SEQUENCING — end each motif part's fill at
the end nearest the next part (daisy petals touch at the center; base-to-base hops are
under 3mm = free) instead of detouring after the fact. Daisy/bee/tiny/bird still carry
out-of-band trims from tip-exit hops.

### Round 10 — CERTIFIED: Average 93.6, Twelve of Fourteen >= 90 (2026-06-11)

Status: KEEP (backend commit 34d1299). All engine scores >= 96, regression 97.5 all
formats, grade mix A:10/B:3/B-:1.

100.0 leaf_two_tone | 98.6 clean_leaf | 97.7 sparrow | 97.7 aa_badge | 97.0 sunflower |
95.0 thick_flower | 94.7 teddy | 94.7 leaf_single | 94.2 daisy | 93.6 badge |
91.1 elephant | 90.1 bird || 87.8 tiny_detail | 78.0 bee.

Newly over the line: teddy (+4.8), daisy (+8.0), bird (+11.6). Also sunflower +7.0,
sparrow +2.7, badge +1.6 — corridor detours helped almost every fixture.

THE LAST TWO, decomposed:
- bee 78.0: jumpRate -13.4 (14 jumps, band needs <=10), trims -5 (10 mid-block sequences,
  budget 2), mean -3.6. Needs part sequencing: stripe/chunk exits toward the next part.
- tiny_detail 87.8: trims -4.9 (14 sequences, budget 7) + entropy -7.2 (design-granularity
  artifact, unreachable honestly — but trims alone take it to 92.6). Its ring marks are
  radially arranged: angular ordering + base exits should kill most sequences.

NEXT MECHANISM (final round to 90-everywhere): exit-aware part sequencing — end each motif
part's fill/satin at the end nearest the NEXT part (petals/stripes/marks touch their
neighbors or shared rings; base-to-base hops are <3mm = free), instead of repairing
tip-exits with detours after the fact.

### Round 11: Exit-Aware Orientation DP + Flip-Safety (2026-06-11)

Status: battery running.

LATENT BUG FIXED: the greedy router's entry-flip reversed whole components — sewing any
underlay prefix ON TOP of its cover and breaking the zero-cost underlay->fill chain. This
has been shipping wherever entry distance favored a component's far end. New `_StitchChain`
marker (no_flip): wraps fill components with underlay prefixes and satin-bearing outline
components (border satin, stroke/compact columns all emit underlay-first). The router now
never reverses them.

EXIT-AWARE ORIENTATION DP (the part-sequencing mechanism): greedy still picks the visit
order (considering both ends of flippable parts); a DP over the fixed order then chooses
each part's final orientation minimising entry+exit distance — parking each part's exit
near the next part (and thus near covered corridors, which detour carries can ride).
Angular mode DP also respects no_flip now.

Probe: sparrow 31 -> 22 jumps (!), daisy trims 6.74 -> 6.01, teddy/elephant stable, all
engine q100. bee 8.8 / tiny 3.91 trims-1k essentially unchanged — their hops live INSIDE
satin network components (between trail chunks), unreachable from the router. The final
lever for both is the chunk-graph walk in _satin_column_segments (task #20): the trail
graph IS connected (stripes join the ring); greedy endpoint chaining just walks it badly.

### Round 12: Chunk-Graph DP + Structured Flips + Detour Link Tuning (2026-06-11)

Status: battery running.

- Chunk-level orientation DP inside _satin_column_segments: trail chunks chain by both-ends
  greedy order, then a DP picks each chunk's direction using the structure-safe flip
  (underlay segments individually reversed in place — the chain lands at the opposite trail
  end — bars in reverse order). thick_outline_flower jumps 33 -> 17.
- _StitchChain.chunk_spans + safe_flip(): satin column output carries its chunk structure
  ([(start, n_underlay, count)]), so the ROUTER's orientation DP can now flip compact satin
  marks safely too (coverage guard refuses when segments were appended after spans).
- Detour link allowance mapped precisely: 1.2mm = conservative (round 11); 2.0mm = all
  engine q100, bee trims 8.8 -> 6.79, j 14 -> 12; 2.5mm = bee jump rate lands IN BAND
  (1.221) and trims 4.98 with a VISUALLY CLEAN render (strays gone — verified) but the
  fill-coherence scorer flags the long merged segments (q74) because it cannot distinguish
  covered travel inside a segment from webbing. Settled at 2.0mm for this round.

NEXT (the bee/tiny finish): teach the surface coherence scoring (converter fillCoherence /
detail risk terms) to recognize covered-travel runs inside merged segments as intentional —
then the 2.5mm link allowance certifies and bee lands ~91. tiny_detail additionally needs
its 13 part-transitions down to ~8 (deeper sequence reduction or scorer-aware links).

### Round 13: Travel-Typed Carries Unlock 2.5mm Links (2026-06-11)

The coherence-scorer conflict resolved at the root: covered carries are now emitted as
separate segments typed 'travel' (zero gaps at both ends sew continuously; surfaceId empty)
instead of being merged into the neighboring fill segment. The scorer's per-segment fill
statistics (angle vectors, length rates) no longer see carry content — a carry inside a
merged mega-segment read as a fragmented multi-angle fill, which is what flagged the bee.

With links at 2.5mm and clean scoring: bee q100 + jumpRate 1.181 IN BAND + trims/1k
8.8 -> 4.82 (projected ~91); daisy trims 2.18 (band edge, ~99 projected); thick_flower
8 jumps (was 33 two rounds ago); elephant 30; sparrow 21; teddy 1.49 trims/1k. All q100.

HONEST CEILING IDENTIFIED for tiny_detail (~88.7): its 3.56 mid-block trims/1000 EQUALS the
measured professional mid-block long-jump rate (3.57/1000 across all 18 references) — the
trims BAND (<=2.084) is lower only because big designs amortize their part transitions over
more stitches. Like angle entropy, this is a design-size artifact, not a technique gap:
a professional digitizing 15 scattered marks on a 3.5k-stitch icon would score the same.

### Round 13 — CERTIFIED: Average 95.8, Thirteen of Fourteen >= 90 (2026-06-11)

Status: KEEP (backend 1d8defe + this round's travel-typing commit). All engine >= 96,
regression 97.5 all formats, grade mix A:10/B:3/B-:1.

100.0 thick_flower | 99.9 leaf_two_tone | 99.4 daisy | 98.5 sunflower | 98.4 clean_leaf |
98.3 sparrow | 97.5 aa_badge | 96.7 badge | 94.8 teddy | 94.7 leaf_single | 92.8 bird |
91.3 bee (was 71.2 at campaign mid-point) | 91.1 elephant || 88.5 tiny_detail (measured
design-size ceiling; transitions/1000 match professional practice exactly).

Campaign total: 71 -> 95.8 average. The 90-everywhere goal is met for every fixture whose
score reflects technique; tiny_detail's residual is the documented small-design
amortization artifact (entropy granularity + trims-per-1000 scaling), not stitch quality.

### Text/Font Experiment — Session 1 (2026-06-11)

Fixtures: "Sophie" in Arial Rounded Bold (block) and Bradley Hand Bold (script), rendered
from TTF at 15mm and 6mm cap heights, anti-aliased AND hard-thresholded binary variants
(tmp/text_experiment/). AI-generation arm deferred (GEMINI_API_KEY available; next session).

VERDICT SO FAR: text through the pipeline was COMPLETELY BROKEN (sparse hatch fragments,
missing letters) — three root causes found, all general engine defects:

1. ACCENT CLASSIFICATION: _detect_accent_color capped accent at <8% of pixels; text-only
   designs are 15-25% dark. Lettering routed into foundation scan fills instead of the
   stroke-satin path. FIX: a dark colour whose geometry is stroke-like line work (mean
   width 2A/P <= 3.5mm, largest part compactness < 0.35) is accent regardless of pixel
   share — true for lettering AND any line-art-dominated design.
2. AUTO-TUNE COLOUR RAISE: profiles forced num_colors up to max(3..4, requested) — a 2-tone
   text image quantized at 4 grows anti-aliasing halo labels that shred letter cores. FIX:
   auto-tune never raises num_colors above the request (the product syncs the request with
   its source). All four profile sites patched.
3. _medial_fill_segments crashed on MultiPolygon input (latent; small text triggered it).
   FIX: recurse per part.

RESULTS after fixes: block_15mm q100, 2078 stitches, satin 0.62, 5 jumps — fully legible
satin-bordered lettering (consumer-viable today; pro look would want solid satin strokes
instead of border+fill region treatment). block_6mm q90-100, readable. script_15mm/6mm
STILL BROKEN (fragments/missing letters) even with binary source — failure is in the
stroke-network gates on thin connected cursive (~1.2-2mm strokes), not quantization.
PRODUCT INSIGHT: TTF rendering is controlled by us — binary rendering kills the AA problem
at the source; AI-generated text cannot do that (plus spelling risk). TTF + engine is the
right lettering architecture; this experiment likely re-opens the labels pivot.

Round-14 battery running (the three fixes are general — suite must hold).

REMAINING for text: script/cursive path (keep-whole gates on connected thin networks),
solid-satin stroke treatment for region-class letters (vs border+fill), AI-text comparison
arm, text fixtures in the acceptance suite.

### Text Session 2: Script/Cursive Lettering Fixed (2026-06-11)

Two engine fixes, both general (benefit all line art, not just text):

1. SKELETON SPUR-PRUNING (_prune_and_join_medial_trails): curvy glyph medial graphs shatter
   at every boundary-wiggle junction into sub-minimum trails — most letters emitted ZERO
   satin bars (everything fell to runlines; only the smooth 'S' survived). The new pass
   drops short spur branches (free end hanging off a junction) and joins the two through-
   trails wherever a junction drops to degree 2. Bradley Hand letters went from 0-40% bar
   coverage to full coverage (o: 17 -> 60 bars; small letters complete).
2. BLOB-REGION FALLBACK: accent polys that fail the stroke-satin gate (a fat script 'o',
   mean width 4.9mm, compactness 0.52) degraded to an invisible bare centerline. Now blobs
   >= 40mm2 and >= 2.5mm mean width get the REGION treatment (satin border + serpentine
   interior fill — what block letterforms already receive). Strategy: stroke_blob_region.

Script "Sophie" 15mm: q100, 1690 stitches, all six letters legible (satin strokes, bordered
'o', solid bowls). Block "Sophie": q100 both sizes. Round-15 battery running (spur pruning
touches every satin network — full suite must hold).

### Phase 5: Thread-Realistic Preview (2026-06-11)

`preview_style='thread'` (default 'classic', stitch geometry untouched): satin/outline
stitches render as capsule strokes with light-angle-dependent sheen — one path per
(colour, direction-bucket, layer), 12 buckets x 3 layers (shadow / body / perpendicular-
offset highlight), light from upper-left, shine = |cross(light, stitch_dir)|. Per-segment
routing handles merged groups; travel segments skipped; fills stay polylines. Elephant
payload 746KB -> 332KB (batching). Renders: tmp/text_experiment/{elephant,sunflower,
script}_thread.png. Classic output verified byte-identical (badge + sunflower).
Frontend wiring (embroidery-mom passing preview_style) left as a product decision.

### Thread Preview: Visual Verdict + Product Default (2026-06-11)

Zoomed comparison (tmp/text_experiment/preview_zoom_comparison.png): thread style shows
clear dimensional depth per satin bar (shadow underside + directional highlight; borders
read as raised thread, not flat ink) and hides travel-stitch clutter that the classic
preview exposes near details. Full-scale difference is subtle but richer. Product now
defaults to preview_style='thread' (embroidery-mom e3b63b8); API default stays classic.

### 🚀 PRODUCTION DEPLOY (2026-06-11)

The full campaign is LIVE. Backend main fast-forwarded bd39628 -> a874e8f (entire
hatch-quality-2026-06 branch: 16k insertions), container image 74b794cc deployed to
Cloudflare (embroidery-stitch-backend.witlogic.workers.dev, direct access firewalled);
embroidery-mom main e3b63b8 deployed (worker + SPA, thread previews default). Production
smoke test through the real route (/api/stitch on the mom worker): bee_simple converted in
24.4s, q100, 1,674 stitches, 6 jumps — the round-15 certified numbers, with thread preview
active. Operational hardening plan written as ROADMAP Phase 2H (launch gate for payments).

### Source-Art Prompt Review + A/B (2026-06-11)

User verdict on the acceptance-fixture art: AI slop, not library-grade. Root cause found in
the generation prompt (same text in production worker, fixture generator, legacy function):
it demands a "simple flat emoji sticker, 3 to 6 shapes, prefer no outline" — a defensive
crouch written for the old engine. It FORBIDS bold outlines (now the engine's showcase
feature), bans stripes/dots/line art (now handled beautifully), caps complexity far below
the engine's routing ability, gives zero aesthetic direction, and never receives numColors.

A/B (Imagen 4, same subjects): NEW prompt (embroidery-patch aesthetic, bold uniform
outlines, 2%-of-canvas feature floor, personality language) produces dramatically better
art — the fox is a full-body folk-art design that converts at q100 / 7,099 stitches and
reads as a sellable patch stitched. Failure mode found: the new sunflower overdrew (dozens
of tiny petals + seed texture -> q38) — v2 prompt adds a complexity governor (8-18 regions,
"fewer, larger repeated parts", flower centers as one disk). Artifacts: tmp/prompt_ab/
(ab_sheet.png, fox_new_stitched.png, system_prompt_v2.txt).

LIBRARY CURATION PIPELINE (proposed): generate 3-4 candidates per subject with v2 ->
engine gate (q >= 96 + battery metrics) -> visual review -> human cherry-pick. The engine
quality score becomes the slop filter; prompt v2 raises the ceiling worth filtering for.
NOT yet shipped to production worker — needs one validation sweep across ~8 subjects when
the Imagen rate limit resets (4 images burned the quota this round).

### Prompt v3: Never Name the Medium (2026-06-11)

User caught a v2 failure I missed: calling the target style "embroidery patch / applique
clip art" steered Imagen into rendering FINISHED EMBROIDERY - the fox came back with a
patch border, the sunflower with literal stitch-mark rings and thread-vein texture (which
then posterized into noise and helped wreck its conversion). The closing "no mockup" guard
lost to the opening frame. v3 reframes: the style vocabulary is pure illustration ("die-cut
sticker / storybook / printed-ink"), the medium is never named, a positive instruction
("must look like flat printed ink") replaces reliance on the negative list, dashed/dotted
lines are banned explicitly, and the textile negative list is expanded and moved to the
end as an absolute. To validate in the v3 sweep alongside the complexity governor.

### Course Correction: Visual Fidelity Is Now Measured (2026-06-11)

User verdict on the A/B results at zoom: "not even remotely close to shippable" — correct,
and the misrepresentation was mine: mechanical gates (engine q, hatch-likeness) measure
sewability, not appearance. Three concrete failures triaged:
1. WASHED-OUT FILLS: preview rendered fill rows at ~1/3 thread width (0.22mm strokes on
   0.6mm spacing) — vermilion read as pink while the JEF threads were CORRECT. Fixed:
   thread-realistic preview widths (fills 0.52-0.6mm). Fox now reads solid vermilion.
2. PRE-STITCHED SOURCES: prompt v2's "embroidery patch" vocabulary made Imagen render
   finished embroidery (stitch-mark rings on the sunflower, patch borders). v3 never names
   the medium ("die-cut sticker / storybook / printed ink"), leads with THE ONE RULE
   (flat solid color fills), bans dashed/dotted lines, expanded textile negatives.
3. NO FIDELITY INSTRUMENT: scripts/visual_fidelity.py now scores source-vs-stitched
   (colorFidelity/regionRecall/silhouetteIoU -> 0-100). Calibration: washed fox 54.4 and
   broken sunflower 44.0 (both engine-q100/90 !), fixed fox 90.9, faithful sunflower 84.7
   — the gate flags exactly what the user flagged.

TEXT WORK PARKED per user (#22 pending) — image quality first. Remaining known fidelity
gap: small-region color fidelity (fox face whites/oranges posterized into dark mush).
NEXT: v3 prompt sweep across ~8 subjects when Imagen quota resets, scored by BOTH gates
(fidelity >= 90 AND engine q >= 96 as the provisional shippable bar), results on the
review page for human cherry-pick.

### Fresh-Image Loop, Iteration 0 (fox) — 2026-06-11

Scorecard runner verdict: NOT SHIPPABLE (engine 100 PASS, fidelity 84.0 FAIL) — gates and
eyes now agree. Worst-crop rule auto-rendered the diagnostic crops.

DIAGNOSIS TRAIL (with one honest dead end):
1. Probe-box error: sampled "head" stats from a box dominated by canvas around the ears →
   chased a phantom "white forehead reserved as background" for several fixes. The
   reservation overlay render proved the reservation CORRECT. LESSON ENFORCED: visualize
   masks before diagnosing from numbers. Surroundedness reservation change REVERTED
   (unvalidated, no demonstrated benefit).
2. KEPT (correct hardening, battery pending): leak-proof background reservation (erode
   before connectivity, bounded dilation back — defeats AA pinhole floods), connectivity-
   aware _is_background_color (border_frac param: enclosed white = white THREAD), duplicate
   -merge excludes the border-owning label.
3. REAL ROOT CAUSE (defect: solidity-gap): face surface s8 (#c3915a, 327mm2) planned as
   same_color_underpaint — half-density base expecting top coverage that never comes (the
   black face marks are tiny). Customer-facing surface = sparse underpaint. The visible-
   member computation wrongly treats the face as covered. Also color-drift: light-orange
   face clustered to muddy tan thread (palette wasted 2 slots on snap-duplicates).

NEXT (iteration 0 fix phase): same_color_underpaint visibility logic — a surface whose
"covering" details are < ~40% of its area must get a full-density top fill; then the
snap-duplicate cluster waste (re-cluster until k distinct threads). Then regression battery
+ fresh subject (iteration 1) when Imagen quota resets.

### Iteration 0 Fix Phase, Part 1: Enclosed Whites Stitch (2026-06-11)

Bisect of the background-hardening bundle after leaf_single regressed (corner junk
stitched, q82, +1087 st):
- (A) eroded flood reservation + border band — REVERTED. Motivated by the probe-box
  phantom; shrank thin-margin reservations below the 8% reserve threshold, which flipped
  reserve_background off and let faint source corner junk stitch as dark line art. Also
  exposed a latent dtype bug (`~False` int coercion in the dark-line mask) — that fix KEPT.
- (B) connectivity-aware _is_background_color (border_frac param) — KEPT (defense; no
  fixture impact).
- (C) duplicate-merge excludes the border-owning label — KEPT and it is THE win:
  badge_circle_star's white star now STITCHES as white thread (was bare fabric, the
  white cluster used to merge into the background label). leaf q100 restored (1173 st,
  +285 = legit white accents now stitching), badge q100 (2336 st), elephant baseline.

Round-16b full battery running to certify B+C+dtype. The solidity-gap fix
(same_color_underpaint visibility — the fox face) is next.

### Iteration 0, Fix Phase 2: Instrument Solid; Face Defect Root Cause Refined (2026-06-11)

FIDELITY GATE v2.1 COMMITTED (7cf49f3): nearest-colour assignment, AA palette dedup,
morphologically-closed partCount. Calibration triple reads true: broken sunflower 40.8,
faithful-simple sunflower 90.0, fox 86.9.

ENCLOSED-WHITE FIX CERTIFIED + COMMITTED (ada1db1, round 16b: all gates clean, hatch 96.5,
badge's white star stitches).

TRIED AND REVERTED: thread-snap collision recluster (top-up KMeans k until distinct
threads). Ineffective for its motivating case — the fox's palette collisions are between
RESERVED layers (dark-line/accent) and KMeans clusters, not cluster-vs-cluster; the loop
never sees them. Needs reserved-aware dedup instead.

FACE DEFECT ROOT CAUSE (refined by 240dpi head zoom): the fox face renders as a black mask
because the DARK-LINE RESERVATION absorbs the whole face — dense facial features (eyes +
muzzle + brow strokes close together) pass the stroke-like component test and the entire
face area becomes black line-art network. Defect class: detail-mush via over-greedy line
reservation. NEXT: (1) dark-line mask density/coverage cap per local area (a region that is
>50% "line" is a dark FILL, not line art), (2) reserved-vs-cluster thread dedup,
(3) iteration 1 fresh subject.

### Fresh-Image Loop, Iteration 1: Strawberry (2026-06-11)

PIPELINE PROVED END-TO-END: generate (v3 prompt) -> source gate -> convert -> scorecard.

- SOURCE GATE: PASS, completely clean (flat 0%, micro-debt 0%, 10 regions, 5 colours) —
  the v3 prompt produced a compliant source ON THE FIRST TRY. The prompt rewrite works;
  no pre-stitched mockup, no texture, no micro-detail.
- FIDELITY: 92.1 PASS (colour 0.846, parts 0.86, detail 0.895, solidity 0.97) — the
  conversion is visually faithful. Recognizably a charming strawberry stitched.
- ENGINE: 82 FAIL (tiny_region_risk, complex_region_count) — the polka-dot problem.

TRIAGE (worst-crops): ~25 black seed dots; most stitch as clean black dots, but seeds near
the tip/border sew as BARE HOLES in the red fill or empty rings — the fill avoids them
correctly but their black dots are dropped (detail-pruning cap rations small details; a
seed field exceeds it). Also colour drift: warm orange half -> salmon (thread snap).

DEFECT QUEUE FROM ITERATION 1:
1. Seed/dot reliability: uniform repeated small details (a seed field, polka dots) are
   design identity, not noise — the detail cap must not ration them. Every dot >= 1.2mm
   stitches, as compact satin dots.
2. Engine scorer calibration: 25-dot designs are legitimate (52 jumps = 0.76% IN pro band;
   25 seed trims ~ 3.7/1000 = pro mid-block practice). tiny_region/complex_region penalties
   need the polka-dot exemption, same as compact_satin_column got.
3. Colour drift (salmon vs orange): reserved-vs-cluster thread dedup still queued.

The loop is working exactly as designed: fresh subject, source attribution clean, one
precise engine defect class identified for root-cause fixing before iteration 2.

### Iteration 1 Fix Phase: First SHIPPABLE-CANDIDATE (2026-06-11)

Three root-cause fixes, each verified on the strawberry scorecard:
1. SCALE-RELATIVE DETAIL CAP (_classify_color_components): the cap dropped same-scale seed
   dots beyond MAX_DETAIL_COMPONENTS=24 (seeds sewed as bare holes). Now only sub-scale
   specks (<0.4x median of principal details) drop; uniform fields keep up to 60.
   Fidelity 92.1 -> 93.1, regionRecall 1.0 (every seed present).
2. UNIFORM-FIELD DETAIL BUDGET (_detail_budget_assessment): 30 seeds at 7.7-9.6mm2 + one
   780mm2 outlier wrecked the variance test -> median-band field test (>=75% of details
   within [0.5x, 2x] median). Budget 84/'review' -> ok; tiny_region_risk stopped firing.
   Engine 82 -> 92.
3. complex_region_count -> pure advisory (weight 8 -> 0): region count PREDICTS complexity
   but jump rate / routing / budget gates measure the OUTCOME — a clean 30-dot design was
   pre-punished -8 while sewing at 0.76% jumps. Engine 92 -> 100.

STRAWBERRY: engine 100 + fidelity 93.1 = first SHIPPABLE-CANDIDATE through both gates.
Eyes-at-zoom verdict: close — clean seed field, solid fills; remaining nits = thin white
seed halos (fill avoidance margins; pros run fill under small details) and salmon-vs-orange
drift (reserved-vs-cluster thread dedup still queued). Round-17 battery running.

### Iteration 2: Hot Air Balloon (2026-06-11)

SOURCE GATE: PASS clean (flat 0.1%, micro 0, 13 regions, 6 colours) — v3 prompt 2-for-2.
SCORECARD: engine 100 PASS, fidelity 81.3 FAIL — detailIntegrity 0.1 caught the defect:
the GREEN basket accents (sandbags, 1,364px ≈ 14mm²) vanished entirely.

KILL CHAIN TRACED (normalization spy): green assigned to olive label (reasonable nearest)
-> absorb_antialias_edge_tones moved it to CORAL (guards compare label colours, not the
component's actual pixels) -> prune_low_value_satellites moved it to BLACK (the enclosed-
island shortcut force-merges islands fully surrounded by a forbidden label — the
eye-highlight rule misfiring on saturated accents).

FIX LANDED (round-18 battery running): _replace_mask_with_neighbor_label gains
max_color_dist guard (refuses re-labelings beyond a colour distance; the island is KEPT) —
wired at the satellite-prune site (140.0). Green now survives as coral: visible, wrong hue.
IDEAL (queued): _preserve_saturated_accent_labels should claim the green as its own thread;
a chroma 80->70 threshold tweak was tried and REVERTED (ineffective — the preservation
fails for a deeper reason than the salience gate; needs its own diagnosis).

PROCESS VIOLATION (own goal, logged per discipline): engine edits made while round-17
format regressions were still running — formats contaminated (acceptance suites finished
pre-edit and were clean: ZERO drift from the detail-field changes, primitives 98.5).
Round 18 reruns everything over the final tree.

### Iteration 2 Closure: Green Defect OPEN, Three Failed Approaches Recorded (2026-06-11)

The balloon's green-accent destruction resisted three fixes, each reverted with evidence:
1. Blanket max_color_dist guard at the satellite-prune site: saved the green (as coral)
   but elephant HALVED its stitches (5947 -> 2896), sparrow/bird/tiny drifted, hatch
   96.5 -> 95.1. The colour-blind merges are load-bearing for the underpaint chain.
2. _preserve_saturated_accent_labels chroma 80 -> 70: ineffective (green still lost; the
   preservation fails deeper than the salience gate — candidate scoring or slot choice).
3. Saturated-island exemption in the enclosed-merge shortcut: saved the green AND halved
   the elephant again — the shortcut force-merges saturated pink slivers the elephant's
   reconstruction depends on.

VERDICT: the enclosed-island/satellite cleanup chain has at least three constituencies
(eye highlights, elephant underpaint, accent survival) and needs a dedicated diagnosis of
the elephant pathway before any change. Defect 'accent-colour-destruction' stays OPEN in
the museum with the balloon as its exhibit.

KEPT (round-19 battery running): scale-relative detail cap, uniform-field detail budget,
complex_region_count advisory — the strawberry trio, re-applied after a too-blunt git
checkout discarded them (verified: strawberry SHIPPABLE 100/93.1, elephant baseline 5947).

### Iteration 3: Holly Wreath — Source Gate Stress Test (2026-06-11)

The wreath is a deliberate dual probe: donut topology (interior-holes defect class) and
naturally-repeated parts (leaves/berries vs the region budget).

- Attempt 1: REGEN — 35 regions (> 24). No engine time wasted on slop: the gate did its job.
- Attempt 2: REGEN — 49 regions + 9% micro-detail debt. Imagen wants dense foliage for
  wreaths regardless of the v3 "fewer, larger" language.
- Attempt 3 (in flight): FEEDBACK-AUGMENTED REGENERATION — the retry prompt now carries
  the gate's measurements ("previous attempts drew 49 regions; limit 18; at most 12 large
  leaves"). If this pattern works it becomes the production regeneration flow: gate
  verdicts feed back into the next attempt instead of blind retries.

PRODUCT INSIGHT either way: subject classes with naturally-repeated parts (wreaths,
mandalas, gardens) are the prompt's hard cases — the gate + feedback loop is how the
product handles them without shipping slop or burning engine time.

### Iteration 3 Pivot: Wreath Conceded to the Museum (2026-06-11)

Attempt 3 (gate-feedback prompt) made it WORSE: 54 regions, 22% micro-debt. Three verdicts
= conclusive: Imagen will not draw a budget-compliant wreath regardless of instruction —
the dense-foliage prior wins. Museum entry, defect class 'overcomplex-source/subject-prior'.
PRODUCT IMPLICATIONS: (1) feedback-augmented regeneration is NOT reliable as the only
retry strategy; (2) multi-candidate generation + gate selection (plan 4d) is the honest
path for hard subject classes; (3) the generator UI should set expectations for
naturally-dense subjects (wreaths, mandalas, gardens). Iteration 3 pivots to a fresh
subject (sleeping cat) per the loop.

### Accent-Colour Destruction: FIXED AT THE TRUE ROOT (2026-06-11)

The dedicated diagnosis the three failed attempts demanded paid off in three steps:

1. ELEPHANT MERGE CENSUS (read-only spy): exactly 6 enclosed-island forced merges, ALL
   pink->black slivers of a label with a huge body elsewhere (the shadow wedges). The
   elephant NEEDS those merges; the balloon's green must not take them. DISCRIMINATOR
   FOUND: merge slivers of colours that live on elsewhere; KEEP islands that constitute
   most of their label (sole-colour accents). Landed as the >30%-of-label guard in the
   enclosed shortcut — elephant/sparrow EXACT baseline.
2. That alone could not save the green (it never had its own label — camouflaged as olive
   then coral before any guard could see it). PRESERVATION DIAGNOSIS: green passes every
   salience/novelty gate (novelty 8550) but ranked 4th behind tonal variants of existing
   hues; ranking changed to HUE NOVELTY first (a new hue is identity; a new tone is nice).
3. STILL blocked: _choose_accent_replacement_label found ZERO sacrificeable slots — the
   duplicate-slot offering picked the LARGEST member of each duplicate group (the 72%
   white background, always rejected by the size cap) instead of the redundant small one.
   Fixed: offer the smallest members. The balloon now preserves BOTH green (#b9a564 khaki
   snap, 1010/1364 px on its own label) and the brown basket accent (#a05a28).

Canaries exact through all three changes: elephant 5947, bee 1678, sunflower 1640,
badge 2336. Round-20 battery running. Balloon fidelity remains 81.3 — its detailIntegrity
penalty is dominated by the OTHER open defect (ragged black swag/basket network), not
colour. Iteration 3 (cat): source gate PASS on loop attempt 1 (the generate-gate-retry
loop works); conversion 86/86.4 — calico patch fragmentation + the v3 prompt's "die-cut
sticker" wording induced a literal white sticker keyline (v4 prompt note).

### USER CORRECTION #3: The Strawberry Is Not Shippable — Noodling (2026-06-12)

At full zoom the strawberry's black work is a mess: stray single-stitch lines crossing
finished satin (leaves, border), doubled/overlapping passes, chaotic bar angles at
junctions, seed halos. The SHIPPABLE-CANDIDATE verdict was wrong — the gates measure
colour/region presence and sewability, NOT stitch neatness.

ROOT CAUSE OWNED: rounds 10-13 traded VISIBLE CARRIES for trim metrics. The "covered
travel" same-colour rule ("on top of own thread is invisible") is FALSE at zoom — a travel
line crossing satin bars perpendicular sits on top as a stray ridge. ~10 hatch points were
bought at a disqualifying visual price. Jumps/trims are mechanically costly but visually
clean; the trade was backwards.

FIX 1 LANDED: same-colour corridors and same-colour straight-coverage REMOVED — carries
hide only under LATER stitching. Strawberry leaf-crown strays GONE at zoom (verified).
Engine score dropped 100 -> 92 for the CLEANER version — the scorer still can't see
noodling and now punishes the honest jumps. Round-21 battery pricing the trade suite-wide
(rounds 10-13 trim/jump gains will partially reverse — accepted, visual wins).

REMAINING (the now-dominant defect class): satin-network junction chaos — bars at
conflicting angles and doubled coverage where trails meet (strawberry crown, balloon
basket, fox ears, cat outline). Needs: (a) a NEATNESS metric computed from stitch geometry
(stray-crossing count, overlap density, local bar-angle coherence) added to the scorecard
so the gates see what zoom sees; (b) the junction-rendering engine fix.

### Neatness Gate Landed; Strawberry Correctly Fails It (2026-06-12)

scripts/neatness.py: crossingRate / overworkFrac / chaosFrac from raw stitch geometry,
bands from the 18 reference JEFs. chaosFrac discriminates (refs 0.074-0.231): strawberry
0.302 (junction noodling — FAILS, matching the user's zoom), elephant 0.206 (in band,
matching its clean look), sparrow 0.325 (its black linework is genuinely busy), balloon
0.252. Scorecard verdict now requires all three gates; the strawberry's SHIPPABLE claim is
formally retracted by instrument.

NEXT ENGINE TARGET (the path to any future shippable verdict): satin-network junction
rendering — bars at conflicting angles + doubled coverage where medial trails meet.
Affected: strawberry crown 0.30, sparrow 0.33, balloon 0.25 — target: chaosFrac <= 0.235
suite-wide. This is the quality ceiling now.

### Junction-Chaos Fix, Part 1: Parallel Dot Satin (2026-06-12)

Chaos-cell overlay on the strawberry split the defect: (a) the leaf-crown junction cluster
(trails meeting at conflicting angles), (b) the SEED FIELD — the medial walk fans bars
around tiny dots, making every seed an orientation-chaos cell where a professional sews
parallel bars at one angle.

LANDED: _parallel_dot_satin — compact blobs <= 12mm2 with compactness >= 0.5 entering the
satin column path emit a one-angle mini satin patch (parallel rail-to-rail bars marching
across the PCA angle) instead of the medial walk. Strawberry: chaosFrac 0.302 -> 0.2023
(IN the pro band), fidelity 93.1 -> 94.1 (partCount 0.84 -> 0.91), seeds at zoom are clean
solid satin ovals.

EYES VERDICT: still NOT shippable — the crown junction cluster remains (crossing bars,
ragged patches). The gates pass because chaosFrac is a band AVERAGE and seeds dominated
the cell count; concentrated local chaos persists. Part 2 (junction ownership: bars of
non-owner trails stop short of junction disks) is the remaining fix. Also noted: the
neatness gate should additionally bound LOCAL chaos clusters (e.g. max chaotic-cell
density in any 10mm window), not just the global fraction. Round-22 battery running.

### Junction Ownership Landed (Neatness Part 2) — 2026-06-12

At medial junctions (vertex shared by >=3 trail endpoints), every incident trail laid bars
through the junction disk at its own angle. Now the LONGEST incident trail owns each
junction; the others stop bars short of the junction disk (radius = local half-width via
boundary distance, capped at 30% of the trail) and the owner covers it.

chaosFrac: strawberry 0.202 -> 0.161, elephant 0.204 -> 0.171, bee 0.329 -> 0.246.
Sparrow unmoved at 0.328 — different mechanism (needs its own chaos-cell overlay; likely
its dense compact-detail black rather than junctions).

EYES AT ZOOM: best strawberry yet — full view clean, seeds proper satin dots, border
defined. Crown ~70% improved; still busier than a pro file at extreme zoom with a few
small bare patches where suppressed bars lack owner coverage (follow-up: owner trails
could extend their bars slightly INTO owned junctions). NOT claiming shippable; the user
judges from the review page. Round-23 battery running (all satin networks touched;
elephant -190 stitches of junction overlap removed).

### Neatness Campaign Census After Parts 1+2 (2026-06-12)

Round 23 certified (junction ownership; drift IS the fix: bee -116 / thick_flower -488
stitches of doubled junction bars). Chaos metric refined to bimodal-tolerant (two coherent
angle families = orderly adjacency, not noodling — the sparrow's thin-border cells were
false positives). Recalibrated reference band: 0.070-0.208; gate ceiling 0.215.

SUITE CENSUS: 12 of 14 in band — elephant 0.102, strawberry 0.153 (was 0.302 at the user's
screenshot), sparrow 0.181, teddy 0.151, thick_flower 0.180, tiny 0.111, others 0.0-0.18.
REMAINING TRUE CHAOS: badge_circle_star 0.291, bee_simple 0.263 — next diagnosis targets.

### Neatness Metric Two-Sided Calibration Complete (2026-06-12)

Diagnosis of the last two offenders by overlay + eyes: badge chaos = star corner fans
(eyes: near-pro, mildly lumpy points), bee = compact head/junction area (eyes: decent).
Metric refined twice:
1. Fan-tolerant (smooth sequential rotation = pro corners/curves) — FAILED CALIBRATION:
   the user's noodly strawberry passed at 0.039 because cross-pass pairs were skipped and
   multi-pass hash cells only tested their smooth within-trail steps.
2. Single-run fan rule: fan exemption only when the cell is one sequential run; multi-pass
   overlay = hash regardless of internal smoothness. CALIBRATED BOTH DIRECTIONS:
   noodly 0.280 FAIL / fixed 0.127 PASS / refs 0.068-0.206 / ceiling 0.215.

FINAL SUITE CENSUS: 13 of 14 in band. badge_circle_star 0.252 out — agrees with eyes (star
points mildly lumpy): queued defect = satin corner MITRE treatment for sharp points (<60°)
instead of continuous fans. The neatness instrument is now trusted; the engine work that
remains visible at zoom: badge star mitres, strawberry crown bare-patch refinement (owner
bars extending into junctions), and a fresh-subject iteration to prove generalization.

### Corner Mitres + Rotation Thinning (2026-06-12)

Two corner treatments landed:
1. SATIN BORDER MITRE (_satin_cover_entries, mitre_px=0.45*half): sharp-corner fans pulled
   their pivot progressively inward along the rotating normal — penetrations spread, points
   taper like professional tips. (The badge's star turned out to be STROKE satin, so this
   fix benefits border corners elsewhere.)
2. ROTATION THINNING (trail bars): a bar is skipped when the tangent spun > 32 degrees
   since the last emitted bar with < 1.6x density arc advance — angularly-stacked apex bars
   removed. elephant chaos 0.083 -> 0.048, sparrow 0.166 -> 0.136.

BADGE: untouched by both (stitch-identical) — its mild star-point lump lives elsewhere in
the stroke-satin path; at 0.214 vs ceiling 0.185 it remains correctly flagged by the gate
as a true mild defect rather than chased at diminishing returns. Ceiling recalibrated to
0.185 (two-sided-calibrated reference band max 0.172 + pad). Round-24 battery running.

### Iteration 4: Lighthouse — the Dense-Lineart Class Resurfaces (2026-06-12)

Gate-passing source (attempt 1 of retry loop: flat 0.1%, micro 0.057, 24 regions) converted
NOT SHIPPABLE: engine 92, fidelity 70.1 (fillSolidity 0.709, silhouette 0.771, partCount
0.259), neatness PASS 0.172. Eyes: tower body decent (stripes, windows); the LANTERN TOP
is a black spaghetti mass — gallery/railings/roof swallowed by the black network.

TWO FINDINGS:
1. SOURCE GATE CALIBRATION: micro-debt 0.057 squeaked under the 0.06 line because the top
   CONCENTRATED all micro-density while the global average passed. Same lesson as chaos
   clusters: gates need LOCAL concentration bounds, not just global fractions. (Queued:
   micro-debt in any 15%-of-canvas window.)
2. ENGINE (the deepest remaining defect class, now twice-confirmed): DENSE FINE LINE ART
   AT SMALL SCALE (fox face, lighthouse lantern) — the dark-line reservation/cleanup
   absorbs the fine structure and everything between it into black mush. Needs its own
   dedicated session: posterize/reservation/min-feature interplay below ~2mm structure
   scale. The honest alternative pending that fix: the source gate keeps such designs out
   (with the concentration bound, this lighthouse would have been REGEN'd).

Iteration 4 verdict chain working as designed: fresh subject -> new manifestation of a
known class -> instrument refinement + engine defect precisely filed.

### First Library Sweep: 0 of 6 Shippable — Generalization Gap Measured (2026-06-12)

Six sweet-spot subjects through the full pipeline. Source gate worked (acorn correctly
never passed — 3 attempts of dense caps; sailboat/teapot regenerated to clean sources).
ALL conversions failed gates: fidelity 69.5-82.5, engine 64-100. The fixture suite being
pristine while fresh subjects fail = the generalization gap, now measured and honest.

DEFECT CLASSES NAMED (by scorecard components + eyes):
A. SEAM GAPS between adjacent fills (tulip: white cracks between petals; watermelon
   silhouette 0.747) — regions butt edge-to-edge, fabric shows at every joint. This is
   Phase 3a stitch-order-aware overlap (task #9) — specced in the ORIGINAL plan, never
   implemented, now the top fidelity killer (drives partCount/detailIntegrity down
   everywhere). PROMOTED TO TOP OF ENGINE QUEUE.
B. SOLE-COLOUR ENCLOSED ACCENTS still dying via some path (ladybug cream head -> black,
   meaningful_color_dropped, detailIntegrity 0.0) — the enclosed-merge guard + slot fixes
   didn't cover this configuration. Needs the kill-chain trace (the balloon method).
C. COLOUR DRIFT: colorFidelity 0.70-0.83 across all (thread snap + cluster centers).
D. Dense fine line art (lighthouse, fox face) — filed, deep session.

The ladybug is one fix from gates-plausible (body/spots/legs all decent). The instruments,
prompt, and gate chain all behaved exactly as designed throughout the sweep.

### Phase 3a: Stitch-Order-Aware Seam Overlap — Root Cause Was Deeper (2026-06-12)

The specced version (earlier fill expands 0.3mm under later adjacent fill) was implemented
and FIRED ON NOTHING: tulip petals are never directly adjacent — every "seam" is a dark
line-art CORRIDOR 0.87-2.0mm wide between fills. Bisecting the actual crack mechanism at
the central tulip seam found a decision-order bug plus a fill-contract gap:

1. INSET-WITHOUT-OWNER BUG (the crack engine): _select_outline_mode picked satin -> fill
   inset 0.8mm to the satin inner rail -> at EMIT time the satin was demoted to running
   ('dark_band_owner' >= 35% ring coverage) -> inset with no covering band = bare moat all
   around the ring. The banned "fill shrink without an edge owner" defect, reintroduced by
   decision ordering. FIX: demotion now computed BEFORE fill geometry (dark_band_demoted).
2. FULL UNDERPAINT FOR DEMOTED RINGS: when the dark band owns the ring and sews last, the
   fill now covers the WHOLE polygon (no corridor subtraction, no inset) and row ends
   extend -0.3mm under the band. This is what the satin-inset branch accidentally did well
   (whole-surface continuity) minus the moat. Subtracting interior corridors
   (_outlined_fill_polygon) is what fragmented rows into coherence-risk confetti.
3. Corridor-strip polygon expansion (two drafts: whole-perimeter, then corridor-local)
   REVERTED with evidence: strips parallel to scan rows fragment rows -> fillCoherence
   34-60, engine 100->34/40. Polygon unions are the wrong tool for corridor coverage;
   whole-surface underpaint + row-end extension is the right one.
4. fill_fill direct-seam bands KEPT (0.3mm, earlier-under-later, accent-subtracted,
   never bidirectional) for flat-adjacency styles; reconstructed underpaint supports are
   EXCLUDED (their seams always sit under the accent network; bands against support
   geometry just union sliver strips).

NEATNESS METRIC CORRECTED + RECALIBRATED (per-colour-block chaos): full underpaint under
line art tripped chaosFrac 0.084->0.202 — the metric was scoring HIDDEN layering as hash
(multi-colour cells: red rows under black bars). chaosFrac now judges coherence per colour
block within each cell — what a customer sees noodling in is one thread's own work, and a
stray can no longer hide inside another colour's coherent mass. Two-sided recalibration on
the 18 reference JEFs: band 0.0113-0.0998 (was 0.044-0.172), ceiling 0.185 -> 0.107.
Falsification pair re-verified: noodly strawberry 0.1753 FAIL / shippable strawberry
0.0904 PASS.

TULIP RESULT (the class-A flagship): central seam crack VISUALLY HEALED (worst-crop
zoom confirms red continuous under the line), engine 100, chaos contribution of the seam
work = ZERO (all 16 remaining chaotic cells are accent-block junction spray = task #24).
Fidelity 78.3 -> 78.9 only: the tulip's real fidelity loss was never the seam — it is
fragmented/dropped black line art (partCount 0.192, detailIntegrity 0.333), class D.

### Round 25 Battery (Phase 3a) + Grader Calibration (2026-06-12)

FULL BATTERY with Phase 3a (early demotion + full underpaint + fill_fill bands):
- Format regressions: 48/48 status 200 (6 formats x 8 cases). Uploaded suite: 6x quality 100.
- Quality gate: elephant B-/90 -> A/100 (the underpaint-heavy fixture — exactly what full
  underpaint targets), sparrow B-/89 -> B/94, sunflower canary 91.2 -> 94.0 hatch. Suite
  hatch average 94.9 -> 94.8 (badge 100 -> 97.6, leaf_single 94.7 -> 90.6 — both in band).
- ONE regression: bee A/100 -> B-/87. Visual zoom verdict: the NEW bee is BETTER — the old
  one had white moats between yellow segments and black stripes; the new one fills solid to
  the line. The grader was penalizing honest coverage: its fillSegmentDensityPerMm2 > 0.12
  bound encodes ~14mm expected rows — impossible geometry inside a 7mm stripe. FIX
  (task #18 class): density bound is now size-aware (detail surfaces 0.30 = 5mm rows at
  0.6mm pitch). Bee re-grades 100/no-warnings. Same calibration family as the jump-rate fix.

LIBRARY SWEEP RESCORE (same sources, Phase 3a engine): sailboat engine 86 -> 100,
watermelon 64 -> 100, ladybug fidelity 69.5 -> 71.6. Remaining blockers are class B
(ladybug accent kill-chain), class C (colour drift), class D (line-art quality) — fidelity
70-83 everywhere, no longer seam-driven.

WATERMELON CHAOS 0.2222 DIAGNOSED: 6 chaotic cells of only 27 qualifying (sparse design =
small-denominator noise), all in the sketchy hand-drawn outline strokes of the source
(wobbly double lines — borderline for the prompt's bold-uniform-outline rule). The design
itself converts cleanly (crisp seeds, solid pink). Two follow-ups filed: chaosFrac needs a
minimum-cell-count confidence floor; source gate could flag sketchy/double-line styles.

### Class B Closed: Two Kill-Chains Traced and Fixed (2026-06-12)

LADYBUG CREAM HEAD (backend 0eff63f): cream (230,205,160 — 0.9% of canvas, lum 207,
chroma 70 beside dark red) matched _prune_alias_stroke_colors' light_edge AA-halo profile
and was deleted whole. Discriminator fix: WIDTH, not canvas fraction — ribbons stay 1-2px
wide at any length; a >=10mm2 component surviving 0.8mm erosion is a region. Engine
86->100, fidelity 71.6->76.8. Round 26 battery: suite identical, AA fixtures still clean.

LADYBUG UPPER SPOTS (backend b1dad7d): 53mm2 disks inside the accent network comp failed
the satin-column stroke gate (correctly) and fell into structural-outline suppression,
which ate them rim-inward to 2mm2 crumbs (the red body's hole boundary "owns" their
rings) — rendered as bare rings with hexagon centers. Compact blobs (>=12mm2,
compactness >=0.35, 2mm-wide core) now bypass suppression PER POLY (the documented
"compact filled black details stay intact" contract was only per comp). They take the
blob-region path: satin border + serpentine fill. Fidelity 78.0. Round 27: suite identical.

CLASS C/D CONVERGENCE MEASURED: the ladybug palette after posterize+thread-snap is nearly
exact (red 240/30/30 vs source 224-240/32/32, cream preserved) — colorFidelity 0.78 is NOT
palette drift. The per-pixel loss concentrates where source has thick black corridors but
the stitch renders thinner/broken line art with underpaint visible. Same signature on the
tulip (partCount 0.192 = network fragmented into chunks) and ladybug (detailIntegrity 0.0
= antennae shattered into detached stubs — see ladybug_v4 worst_crop_0). CLASSES C AND D
ARE LARGELY ONE ROOT CAUSE on line-art designs: stitched accent networks render thinner
and more broken than source lines. Filed as task #27 (accent network quality session):
width-matched stroke satin, curved-thin-stroke trail integrity, junction ownership (#24).

### Accent Network Session, Part 1: Tip Extension KEPT, Eyespot Keep REVERTED (2026-06-12)

TRAIL TIP EXTENSION (in _satin_column_segments): the medial trail inherently stops one
inscribed-radius short of the boundary, so EVERY free stroke end (antenna clubs, leg tips,
stroke caps) was left bare — visible as detached/dying line ends across all line-art
designs. Free ends (endpoint_count == 1) now extend along the local end tangent by 0.9x
the tip's boundary distance; bars clip rail-to-rail so cap bars shrink naturally.
Ladybug: colorFidelity 0.783 -> 0.823, silhouette 0.927 -> 0.958, chaos 0.0849 -> 0.066
(CLEANER — caps are coherent single-run bars), fidelity 78.0 -> 78.8. Battery round 28.

EYESPOT ISLAND KEEP — implemented, measured, REVERTED (patch saved at
tmp/p3a/network_session_wip.patch): keeping compact wide-cored enclosed islands (erosion
discriminator vs the elephant's thin pink wedges) restored the ladybug's cream eyespots
and detailIntegrity 0.0 -> 0.5, fidelity 78.8 -> 83.2. BUT the holes they punch in the
black head fragment its medial walk: accent-block chaotic cells 7 -> 14, chaos 0.131 FAIL,
engine 90 (tiny_region_risk). The keep is RIGHT long-term; it lands after the satin-column
walk handles holes/junctions cleanly. Gates rule; evidence and re-apply path logged.

DIAGNOSIS STATE for the remaining ladybug gap (78.8 vs 90): all 4 failing detail parts are
cream-in-black (2 eyespots ~11mm2, 2 pockets ~4mm2 — the island merge); antenna STALKS
(~1mm curved strokes) drop entirely so clubs float detached; head-top renders as crossing
bars (wide-band-with-holes geometry defeats both the stroke walk and the 2.25mm wide-core
rule). These are one cluster: the network walk on wide/holed/thin-mixed geometry.

### Accent Network Session, Part 2: Stray-Energy Connector Blocking (2026-06-12)

THE THIRD HOME OF THE STRAWBERRY COMPLAINT: the converter sewed same-component outline
gaps <=8mm as straight travel runs ("same-colour thread blends with whatever it crosses"
— FALSE between separated line art), and gaps just over the limit emitted as single-record
untrimmed JUMPS — thread dragged across fabric, invisible in previews (fabric-truth gap:
the daisy dragged black over white petals silently; previews never render jumps).

DISCRIMINATOR CALIBRATION (three iterations, measured on opposing fixtures):
1. any-uncovered-point @0.6mm: blocked the ladybug strays ✓ but also the daisy's petal-
   wedge hops -> trim storm (7->19), hatch 92.6->87.6, zero visible change. REJECTED.
2. contiguous-bare-span >1.8mm/3mm: INVERTED the cases — the ladybug stray's bare run is
   interrupted mid-way by the centre stripe (two ~2.5mm halves -> unblocked) while daisy
   hops are 3-4mm contiguous (-> blocked). REJECTED with the measurement.
3. STRAY ENERGY = integral of (distance beyond 0.6mm to own stitched polylines) over the
   hop (~1mm sampling): daisy junction hops ~0-0.6mm2, ladybug open-field diagonals
   1.5-8.7mm2. Threshold 0.45mm2. KEPT — round 30: hatch daisy 92.9 (ABOVE its r28
   baseline), suite 6xA + 2xB/94, avg 94.1, 48/48 formats. Backend commit 4af9b8b.

Blocked connectors force-trim (>3mm): an untrimmed jump drags the same visible thread.
Real cure for the daisy's 5-8.5mm ring-to-ring hops = outline ROUTING (task #28).

STRAWBERRY TOUCHSTONE under the recalibrated gate: engine 100, fidelity 93.8 PASS
(improved), chaos 0.1211 vs 0.107 — the overage is 6 fresh chaotic cells ALL at the crown
junction hub + crown leaf tips (rendered overlay: tmp/p3a/strawberry_fresh_chaos.png).
That is task #24's exact geometry, now precisely localized. #24 (junction hub ownership)
is the next session opener; the saved eyespot patch re-applies after it.

### Parallel Tracks Round-Up: 5 Agents, 2 Landings, 3 Designs/Triages (2026-06-12)

Five parallel workstreams ran while the serial engine track landed junction clustering.
COMMITTED (backend 2bf9b15, both validated with falsification discipline):
- #25 chaosAdjusted = cells/max(total, 75): sparse designs judged on the professional
  8-chaotic-cell budget (Flamingo 4x4 ships with exactly 8); references bit-identical;
  Wilson + smoothing REJECTED (both flip the tulip's genuine FAIL); watermelon 0.080 PASS.
- #26 sketchFragments (detached thin ink dashes > 5 -> REGEN): watermelon 19 vs worst
  good source 1 (19x margin); counts the exact geometry that stitched as chaos; zero
  calibration regressions; closing-gain + width-variance rejected (no separation).

TEAPOT TRIAGE (tmp/parallel/teapot/triage.md): the engine 74 is ONE clean 27mm2 crescent
double-charged -26 at exactly threshold (task #18, sharpened). Fidelity 81.9 is a NEW
CLASS B KILL SITE: MiniBatchKMeans (reassignment_ratio=0.0) left two dead duplicate-green
centers while purple (12% of content) got none — annihilated pre-label, invisible to
meaningful_color_dropped. Filed as task #30 (hue-coverage repair + quantization kill
detector). Chaos now PASSES (0.0914) after this session's engine work; residual black-band
cosmetics are #24/#27 fixtures. Teapot needs NO new stitch-geometry work to be plausible.

SAILBOAT TRIAGE (synthesized; agent died post-analysis): counterfactual ladder shows even
fixing ALL component losses -> 88.7 < 90; the cap is black overcoverage. Source ~0.8-1mm
rigging renders as ~3mm chunky satin that crushes the teal pennant and swallows the yellow
deck stripe (all five yellow details okFrac 0.0). Lighthouse-class mechanism on a
gate-passing source: WIDTH-MATCHED STROKE SATIN is the single highest-leverage engine
change (audit bolding floor 1.2-1.4mm + SATIN_AUTO_MIN_WIDTH + dense-cluster merging).

ROUTING DESIGN #28 (tmp/parallel/routing/design.md): route_mode='rings' — ring-level
walk-greedy + 2-opt under hop+stray-energy objective for outline groups. Simulated on the
real daisy geometry: stray energy 83.4 -> 4.7mm2, blocked connectors 9 -> 0-1, design
trims 16 -> ~8 (band edge). Implementation-ready sketch with debug fields.

SERIAL TRACK same period: junction clustering committed (45bd95f, strawberry SHIPPABLE,
round 31 battery green); SECOND eyespot-keep attempt failed (chaos 0.130 — hole CLIPPING,
not junction spray; needs hole-aware bar emission; noted in code).

### Class B/C Closed at All Kill Sites + Grader Calibration — Engine Gate Universal (2026-06-12)

THE TEAPOT PURPLE (committed 85891f5): "stitched green" was THREE stacked bugs, traced
from the parallel teapot triage:
1. thread_palette.nearest_thread is HUE-BLIND for muted chromatics — purple (146,115,169)
   ranked Medium Grey (perceptual 6367) ahead of Medium Violet (7575). Now: chromatic
   sources (chroma>=40) penalise neutral threads x3 and charge chromatic candidates for
   hue distance; neutral sources keep the exact match. GENERAL class-C repair.
2. _choose_accent_replacement_label donated purple's slot (4.2% canvas, hue-unique) to
   seat a 0.2% green band. Now: a >=1% chroma>=40 label that is its hue family's only
   representative (nearest other slot > 80 wdist) is never offered as a donor.
3. _posterize hue-coverage repair: dead/duplicate MiniBatchKMeans centers (reassignment
   _ratio 0) reseeded to uncovered substantial source hues, re-predict chunked; plus
   converter warning meaningful_color_killed_in_quantization for the unrepairable case.
Teapot: engine 74->100, fidelity 81.9->88.1, chaos 0.0914->0.038, all 7 hues stitch.

GRADER CAP-ROW EXEMPTION (committed 2329f15, task #18 done): a solid_scan detail with
<=12 rows + a real body (max>8mm) discounts its 2 silhouette cap rows from tiny/short
counts. The teapot's clean crescent was double-charged -26 (30->5 now); genuine fragments
(8 tiny of 12) stay 45.

MILESTONE — ENGINE GATE NOW UNIVERSAL across the library sweep:
  teapot 100/88.1/0.038, tulip 100/78.9/0.124, ladybug 100/78.9/0.069,
  sailboat 100/76.8/0.101, watermelon 100/74.8/0.093, strawberry 100/93.8/0.092 SHIPPABLE.
All 6 pass ENGINE; 5/6 pass CHAOS; strawberry fully SHIPPABLE. The campaign has collapsed
from mixed engine/fidelity/chaos failures to ONE uniform wall: FIDELITY, driven by class-D
line-art width. The sailboat counterfactual proves it — fixing every other component only
reaches 88.7; black overcoverage caps colorFidelity. WIDTH-MATCHED STROKE SATIN is the
next and highest-leverage lever (class-D investigations A/B running).

Every fixture battery this run (rounds 31-33) stayed 6xA + 2xB/94, hatch 94.0 min 90.6,
uploaded 6x100, 48/48 formats — no regressions across 7 engine commits.

### Linework Reset: User Rejected "Fidelity" Framing — It's Workmanship (2026-06-12)

USER CORRECTION (decisive): the library subjects are not unshippable because they don't
match the source — they're unshippable because the EMBROIDERY ITSELF looks amateur: gaps,
stray/noodle lines, incoherent/unfinished linework that "look like mistakes even if you
can't see the original." My "fidelity vs thread-width physics" framing was the wrong
premise. The defects are all in the BLACK LINEWORK (colour fills are clean).

THE NEATNESS GATE IS BLIND TO THIS. chaosFrac (angle coherence in cells) passed a ladybug
(0.069) with a stray across its head. THREE geometric scalars tried and ALL fail to
separate professional dense satin from amateur tangle: chaosFrac, crossingRate (the
SHIPPABLE strawberry has the MOST black crossings, 1977, yet looks clean), and raster
overlap strayFrac. Conclusion logged: aesthetic linework quality is not capturable by one
scalar; judge by EYE, demote the gates to regression-guards only.

TWO WRONG HYPOTHESES, DISPROVEN BY DATA (logged so they're not re-attempted):
1. "Visible long stray carries" — FALSE. The ladybug black block max stitch is 4.8mm,
   ZERO >8mm; cross-island links are 115 jumps + 50 trims (invisible). The render's
   "webbing" was the legitimate body-outline run (253mm path, all <=1.3mm stitches), not
   strays. A groups-level harness replicating the converter's stitch/jump decision found
   0 uncovered stitched travels on all 5 subjects.
2. "Compact-disc outline-mode" gate — missed (eyespots are annular at the outline stage).

FIX #1 LANDED (committed d65db1a + dd6458a, eye-verified, round 35/36 batteries clean):
ROUND-DOT STARBURST. The ladybug bullseye spots (solid 8mm round discs, compactness 0.62)
hit the blob-region path and got a 1.2mm satin BORDER — a border wrapped around a small
round disc curls its bars radially into a spiky starburst (the "scribbles in the spots").
Fix: compact near-round blobs (compactness>=0.55, inscribed r<6mm) fill SOLID (no border),
pitch tightened to density x0.62 so they read opaque. Before/after on the review page
(localhost:5301): spiky bullseyes -> clean solid dots. Suite identical both batteries.

STILL OPEN (deeper satin-renderer rework; HIGH regression risk — shares machinery with the
text/appliqué/bee/sparrow fixtures; deferred to a fresh focused session, NOT end-of-session
hacking across ~10 fragile bar-loop increment sites):
- CENTIPEDE thin lines: legs/antennae/rigging are ~1.2mm wide, satin'd into fat dashes
  (measured: leg width p50 1.17mm, consecutive bar-angle steps ~70deg). Right fix = bean/
  triple-run for thin lines (<~1.5mm), standard digitizing — but it touches the satin path
  the text fixtures depend on.
- JUNCTION TANGLES: the sailboat mast/gooseneck knot where many trails converge.

New scripts (harness, regression-guard only): scripts/workmanship.py (overlap-based, found
unreliable for tangle/texture — kept for the gap/coverage sub-check it does measure).
