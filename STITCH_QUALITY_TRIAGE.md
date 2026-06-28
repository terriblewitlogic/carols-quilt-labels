# Stitch Quality Triage

Last updated: 2026-06-28

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
- Same-hue tonal stress coverage now includes `same_hue_acorn_facets`, and the posterizer protects substantial darker end-members so dark caps/bases are not flattened into mid-tone facets.
- Same-hue tonal cleanup also protects substantial light end-members, so mushroom-like material art keeps tan/light regions instead of collapsing them into the dominant orange/pink body tone.
- Same-hue facet trim pressure now has explicit acorn, mushroom, and shell stress coverage; modest inter-component carries trim at `16mm` instead of `8mm`, reducing faceted acorn trims without introducing long untrimmed jump diagnostics.
- Covered-travel routing now considers longer `2-35mm` carries only when later stitch geometry proves the path is hidden; this reduces faceted acorn trims again while leaving exposed long moves as jumps/trims.
- Structural/no-flip-safe routing now preserves `_StitchChain` metadata only inside candidate-graph evaluation, allowing safe component reordering without changing ordinary nearest routing.
- Structural safe-flip orientation now compares legacy and reoriented underlay/cover-safe reversals during candidate scoring, reducing internal handoff risk while keeping the acorn structural route win.
- Structural safe-flip filtering now rejects the legacy "safe" reversal only when it creates an extreme internal underlay-to-cover handoff that a reoriented variant removes; this clears the remaining shell same-surface material relocation without broad-suite metric churn.
- Underpaint route coverage now includes targeted disconnected-island fixtures for plain candidate scoring and structural-safe candidate wins.
- Source/color triage grading now treats heavy source normalization as informational when diagnostics prove it only removed noise and all stitch/color risk gates are clean.
- Upload-style muted accent coverage now includes `muted_accent_badge`: low-chroma lavender, soft pink tiny details, blue fill, and black linework must all survive strict source-policy checks.
- Real source/color fixture coverage now has a separate file-backed lane via `npm run acceptance:source-color`, seeded with teapot and strawberry examples that are known source-complexity targets rather than default acceptance blockers.
- Compact repeated detail motifs are now accounted in source-design diagnostics: `real_strawberry` recognizes the black seed field plus green leaf repeat as intentional motifs, improving triage from `C+` to `B` without changing stitch output.
- Teapot-like local detail clusters are now explicitly accounted in source-design diagnostics: `real_teapot_card` reports `4` retained multi-component colors / `22` disconnected retained components and keeps the case classified as source-art complexity rather than a stitch-routing failure.
- Sparse low-chroma outline halos are now accounted as pruned source residue instead of visible color loss: `thick_outline_flower` now has source suitability `100 / clean`, repair count `0`, and unchanged stitch output.
- Stitched near-white foreground shapes are now explicitly accounted instead of reported as repair opportunities: `bee_simple`, `flower_daisy_simple`, and `low_contrast_bird` keep their pale stitched regions with repair count `0` and unchanged stitch output.
- Large dark stroke-satin outline networks now use a wider density multiplier when the source stroke area is broad, reducing thread buildup on generated/uploaded icon line art while keeping risk gates clean.
- Simple medium local material patches can now use a proved-safe serpentine fill when they have no holes, structural sensitivity, silhouette role, stem/center-disk role, or satin-zone role. This trims small fill clutter in teapot, flower, sparrow, and structural-facet fixtures while keeping jump/trim and long-span risk gates clean.
- Cross-color compact tiny detail motifs are now recognized in source suitability before stitching: `tiny_detail_icon` keeps the same colored dots and stitch output, but source repair opportunities improve `1 -> 0` and suitability improves `candidate 88 -> clean 100`.
- Repeated compact dark detail fields now use a slightly looser detail-fill density than isolated compact details: `real_strawberry` keeps its seed field readable while reducing stitches `7549 -> 7369`, trims `4 -> 3`, and trimmed preview relocations `2 -> 1`.
- Teapot-like local material panels inside multi-color detail clusters now use a guarded local serpentine density path: `real_teapot_card` stitches improve `11711 -> 11664`, local-patch-serpentine surfaces improve `3 -> 5`, and jumps/trims/risk gates stay unchanged.
- Repeated compact motif fields no longer double-count as generic fragmented line-art repair pressure: `real_strawberry` source repair opportunities improve `1 -> 0` with stitch output unchanged.
- Teapot-like satin-width local material panels can now still try the proved-safe local serpentine path when they are not stems/holes/silhouettes: `real_teapot_card` fill-coherence risk improves `1 -> 0`, local-patch-serpentine panels improve `5 -> 8`, stitches improve `11664 -> 11612`, and trims/jumps/risk gates stay unchanged.
- Compact low-chroma pastel accents now have a narrow preservation lane. New uploaded fixture `muted_flower_pin` keeps lavender `#b496dc`, yellow `#ffaf46`, blue fill, and black details with quality `100`, detail budget `ok`, and explicit `preserve_compact_pastel_accent_label:detail_component` accounting, while existing `tiny_detail_icon` and `muted_accent_badge` metrics stay unchanged.
- Bookended same-hue material families now protect substantial dark/mid/light tones during source cleanup. New strict uploaded fixture `same_hue_purple_shell_facets` keeps `#7846c8`, `#965ad2`, `#b496dc`, and black; the no-guard baseline dropped dark purple and had one same-surface relocation, while the accepted run keeps all tones with quality `100`, trims `6 -> 4`, jumps `20 -> 19`, and same-surface trimmed spans `1 -> 0`.
- Small mid-tone muted chromatic details now use a narrow hue-preserving thread snap before cleanup. New uploaded fixture `muted_sage_detail_badge` keeps the sage mark as chromatic Madeira `#1ea096` instead of neutral `#808080`; quality stays `100`, stitches/jumps/trims are `4147 / 26 / 2`, and existing uploaded/generated/source-color/underpaint fixtures stay unchanged under regression-gated comparisons.

The remaining quality problems are mostly in generated icon art:

- repeated-island designs still have too many jumps/trims, especially `flower_daisy_simple`
- source-generation detail overload: too many small regions, low-contrast tones, or embroidery-like source imagery
- meaningful small accent colors must be preserved without preserving noisy fragments
- same-hue material colors must stay preserved when source evidence is broad and ordered, but gradient cleanup must still collapse mild disposable bands
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
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_trim16_20260626.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_trim16_20260626.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_covered_travel35_same_hue_20260626.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_covered_travel35_20260626.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_covered_travel35_20260626.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_route_diag_full_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_route_diag_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_route_diag_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_structural_route_fixed_acorn_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_structural_route_fixed_full_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_structural_route_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_structural_route_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_route_fixture_coverage_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_light_endpoint_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_light_endpoint_full_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_light_endpoint_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_light_endpoint_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_structural_orientation_dp_same_hue_strict_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_structural_orientation_dp_full_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_structural_orientation_dp_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_structural_orientation_dp_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_structural_unsafe_legacy_filter_same_hue_strict_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_structural_unsafe_legacy_filter_full_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_structural_unsafe_legacy_filter_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_structural_unsafe_legacy_filter_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_source_color_grading_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_source_color_baseline_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_source_color_baseline_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_source_color_grading_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_muted_accent_guard_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_muted_accent_guard_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_muted_accent_guard_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_muted_accent_guard_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_real_fixture_lane_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_source_color_real_fixtures_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_motif_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_motif_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_motif_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_motif_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_local_detail_cluster_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_local_detail_cluster_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_local_detail_cluster_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_local_detail_cluster_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_local_detail_cluster_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_sparse_halo_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_sparse_halo_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_sparse_halo_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_sparse_halo_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_sparse_halo_policy_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_motif_policy_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_near_white_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_near_white_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_near_white_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_near_white_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_near_white_policy_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_large_stroke_spacing_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_large_stroke_spacing_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_large_stroke_spacing_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_large_stroke_spacing_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_large_stroke_spacing_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_local_patch_serpentine_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_local_patch_serpentine_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_local_patch_serpentine_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_local_patch_serpentine_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_local_patch_serpentine_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_cross_color_tiny_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_cross_color_tiny_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_cross_color_tiny_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_cross_color_tiny_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_cross_color_tiny_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_repeated_detail_density_target_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_repeated_detail_density_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_repeated_detail_density_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_repeated_detail_density_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_repeated_detail_density_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_repeated_detail_density_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_local_cluster_density106_teapot_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_local_cluster_density106_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_local_cluster_density106_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_local_cluster_density106_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_local_cluster_density106_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_local_cluster_density106_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_strawberry_motif_repair_guard_target_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_strawberry_motif_repair_guard_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_strawberry_motif_repair_guard_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_strawberry_motif_repair_guard_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_strawberry_motif_repair_guard_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_strawberry_motif_repair_guard_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_material_panel_accounting_teapot_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_material_panel_accounting_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_material_panel_accounting_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_material_panel_accounting_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_material_panel_accounting_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_material_panel_accounting_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_satin_local_patch_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_satin_local_patch_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_satin_local_patch_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_satin_local_patch_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_muted_flower_pin_pastel_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_pastel_accent_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_pastel_accent_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_pastel_accent_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_pastel_accent_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_pastel_accent_fix_20260628/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_purple_shell_bookend_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_bookend_material_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_bookend_material_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_bookend_material_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_bookend_material_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_bookend_material_fix_20260628/source-triage.html`

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
- dark- and light-endpoint tonal-family protection for substantial same-hue material fields

Implemented now:

- graph-aware component routing for disconnected same-color fill islands, inspired by embroidery/sewing path-ordering work, geometric TSP/MST heuristics, and 2-opt. The production adaptation compares nearest, angular, MST preorder, and 2-opt component tours, then keeps a new route only when predicted trims/jumps improve without increasing long-span or visible-carry risk.
- route-decision diagnostics for structural fallbacks: `surface-plan.json` now records candidate-route gates, component counts, spread, raw-component fallback checks, and `structural_no_flip_component` rejections when route reordering would conflict with underlay-sensitive surfaces.
- exact small-cluster route scoring for 3-7 disconnected components, aligned to the converter's `16mm` inter-component trim threshold. This keeps route scoring honest for tiny facet clusters without changing accepted output unless the candidate is strictly safer.
- structural/no-flip-safe candidate routing: broad underlay+fill chains now expose safe flip spans, candidate-graph routing preserves `_StitchChain` metadata only while scoring candidates, and equal-travel-only route wins are rejected. This lets small exact routes improve structural same-color clusters without changing unrelated nearest-route output.
- structural safe-flip orientation DP: candidate scoring now considers both legacy and internally reoriented safe flips for structural `_StitchChain` components, choosing by external trim/long-span pressure first and internal handoff trim/long-span pressure second. This keeps the acorn structural improvement while removing the same-hue mushroom material relocation.
- unsafe legacy structural flip filter: structural candidate scoring suppresses the legacy safe-flip variant when it creates an extreme internal underlay-to-cover handoff (`>=45mm`) and the reoriented variant removes internal trim/long-span risk. This keeps accepted structural route wins while eliminating the remaining shell same-surface material relocation.
- disconnected-island route fixture coverage: `underpaint_benchmark.py` now includes `synthetic_component_route_ring` for plain candidate scoring/fallback and `synthetic_structural_route_facets` for structural-safe small-exact route wins.
- source/detail decision diagnostics for upload-style fixtures: `surface-plan.json` records tiny-component decision counts and `uploaded_art_acceptance.py --strict-source-policy` fails on unresolved tiny decisions, bad detail budgets, lost accent colors, or detail-fill risk regressions.
- muted-accent source guard: `muted_accent_badge` is now part of default uploaded acceptance and fails strict source-policy if low-chroma lavender `#b496dc`, soft pink `#f082a0`, blue fill `#8cb9eb`, black linework, or muted-accent tiny-detail accounting disappears.
- same-hue material preservation fixture: `same_hue_acorn` verifies the posterizer/thread snap keeps `#783c14`, `#c3915a`, and `#d2aa6e` instead of collapsing a dark cap, tan body, and light highlight into one family.
- same-hue faceted stress fixture: `same_hue_acorn_facets` is available by explicit `--case` but excluded from default uploaded acceptance; the current result is quality `100`, `0` broad/detail risk surfaces, and preserved `#783c14`, `#a05a28`, `#c3915a`, and `#d2aa6e`.
- same-hue light endpoint guard: `same_hue_mushroom_facets` now preserves `#d2aa6e` as a substantial light material region instead of flattening the stem/highlight into `#f0785a`.
- same-hue facet trim reduction: `same_hue_acorn_facets`, `same_hue_mushroom_facets`, and `same_hue_shell_facets` exercise same-hue material fields with internal facets. Inter-component trims now use a `16mm` threshold, which reduced acorn facet trims while keeping long untrimmed jump diagnostics at zero.
- covered travel extension: `_merge_covered_travel` now considers hidden carries up to `35mm`, but only when a later fill/outline directly covers the route or offers a covered detour. It removes one remaining faceted-acorn relocation without raising the global trim threshold.
- source/color grading calibration: `grade_stitch_quality.py` now discounts heavy source-normalization pressure only when source cleanup is explicitly noise-removal, quality is high, no meaningful colors were dropped, and there is no stitched/long-span/fill risk.
- real source/color fixture lane: `fixtures/source_color` plus `npm run acceptance:source-color` runs file-backed generated/uploaded-style troublemakers outside the default generated suite. The first cases are `real_teapot_card` and `real_strawberry`.
- compact repeated-detail motif accounting: source-design diagnostics now recognize small uniform repeated fields, such as strawberry seed dots, as intentional motif groups. `generated_acceptance.py` exposes motif counts and guards `real_strawberry` so future source policy changes do not reclassify the seed field as generic source complexity.
- repeated compact-detail density: compact dark detail fields with at least `12` repeated islands now use a guarded `0.68` detail-density multiplier while isolated compact details keep the denser `0.55` multiplier. `real_strawberry` uses this to reduce seed overpacking without dropping colors, changing strategies, or widening routing gates.
- local cluster material panel density: non-repeated multi-color local detail clusters can mark simple `70-220mm^2` foundation panels as local material panels. Only those panels get the lower local-patch area floor and `1.06` local serpentine density multiplier, improving `real_teapot_card` without broadening the generic local-patch gate or route behavior.
- repeated compact motif repair accounting: source-design diagnostics now suppress `fragmented_line_art` repair opportunities when the same label is already recognized as a same-color compact detail repeat. `real_strawberry` keeps the same stitches/colors/risks while source repair opportunities improve `1 -> 0`.
- local material-panel accounting: acceptance summaries and source triage now expose teapot-like material-panel handling (`9` panels, `5` serpentine) and discount the `22` retained local-cluster regions only when colors are preserved and blocking stitch-risk gates are clean. `real_teapot_card` moves from `C / source_art_complexity` to `B / mostly_ok` with stitch output unchanged.
- compact pastel accent preservation: a narrow low-chroma pastel label lane preserves small sewable lavender/pastel accents through source regularization, low-value partition absorption, and repeated compact-detail promotion without changing vivid repeated-dot simplification or the older muted-accent guard.
- bookended same-hue material preservation: substantial connected same-hue families with dark/mid/light members now protect all three labels during low-value partition absorption and tonal-family collapse. `same_hue_purple_shell_facets` is the new cool-hue guard, while `gradient_elephant_simple` remains collapsed to the accepted two-tone result (`5062` stitches, `4` trims, `8` jumps, no same-surface spans).

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

## Current Patch: Bookended Same-Hue Material Preservation

The latest source/color sprint win preserves cool same-hue material facets without reopening gradient cleanup or route behavior.

What changed:

- Added uploaded stress fixture `same_hue_purple_shell_facets`, a compact purple material sample with dark, mid, and light same-hue facets.
- Added `_bookended_same_hue_material_labels` to protect substantial ordered dark/mid/light same-hue families during low-value partition absorption and oversegmented tonal-family collapse.
- Strict uploaded source policy now requires the purple guard to preserve `#7846c8`, `#965ad2`, `#b496dc`, and `#000000`, maintain separated purple luminance bands, and avoid same-surface material relocations.

Current outcome:

- No-guard baseline: `colors ['#965ad2', '#b496dc', '#000000']`, trims `6`, jumps `20`, stitches `3714`, same-surface trimmed spans `1`.
- Accepted run: `colors ['#7846c8', '#965ad2', '#b496dc', '#000000']`, trims `4`, jumps `19`, stitches `4620`, same-surface trimmed spans `0`, quality `100`.
- Same-hue warm canaries pass: acorn, mushroom, shell, and purple all quality `100` with no same-surface trimmed/untrimmed long spans.
- Gradient elephant remains stable and still collapses disposable gradient bands: `5062` stitches, `8` jumps, `4` trims, quality `100`, no same-surface spans.

Validation:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_purple_shell_bookend_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_bookend_material_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_bookend_material_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_bookend_material_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_bookend_material_fix_20260628.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_bookend_material_fix_20260628/source-triage.html`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- full uploaded strict source policy plus targeted purple strict guard
- full generated acceptance `--strict`
- full source-color acceptance
- full underpaint benchmark

Verdict:

- Keep. This is a narrow semantic material-color win with deterministic cool-hue coverage and no guarded regression.
- Next work should target visible strawberry output behavior or add a new real generated/uploaded fixture with semantic color/detail loss. The refreshed triage still has `real_strawberry` as the only source-complexity target; teapot remains `B / mostly_ok`.

## Previous Patch: Local Material-Panel Accounting

This source/color sprint win makes the report stack recognize teapot-like local material clusters that are already handled by the stitch planner. This is a diagnostic/source-policy change only; stitch output is intentionally unchanged.

What changed:

- Acceptance summaries now expose local material-panel counts from `surface-plan.json`: `sourceLocalMaterialPanelSurfaceCount`, `sourceLocalMaterialPanelSerpentineSurfaceCount`, and `sourceLocalMaterialPanelScanSurfaceCount`.
- `generated_acceptance.py --strict` now guards `real_teapot_card` so local-detail-cluster source accounting and material-panel stitch accounting remain present.
- `grade_stitch_quality.py` discounts local-cluster region pressure only when the case has enough material panels, no meaningful dropped colors, no stitched long spans, no untrimmed long jumps, no broad-route risk, and no detail-fill risk.
- `source_art_triage_report.py` uses the same gate, so handled material clusters show as visual-review candidates instead of "repair source before stitching".
- Pixel cleanup, palette selection, stitch geometry, routing, public APIs, frontend behavior, and file formats are unchanged.

Current outcome:

- `real_teapot_card`: grade/root improves `C / source_art_complexity -> B / mostly_ok`.
- `real_teapot_card`: material-panel accounting reports `9` local material panels: `5` local-patch-serpentine and `4` scan/solid-scan panels.
- `real_teapot_card`: stitch output stayed unchanged at `11664` stitches, `86` jumps, `14` trims, color stops `6`, quality `100`.
- `real_teapot_card`: colors stayed `#50be46`, `#f0785a`, `#965ad2`, `#ffc88c`, and `#000000`.
- `real_teapot_card`: same-surface stitched long spans, same-surface untrimmed jump long spans, high-risk surfaces, and broad-route-risk surfaces stayed `0`.
- Combined triage now ranks `real_strawberry` as the only non-`mostly_ok` source-color target; teapot remains visible as `B` with a visual-review recommendation.

Validation:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_material_panel_accounting_teapot_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_material_panel_accounting_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_material_panel_accounting_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_material_panel_accounting_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_material_panel_accounting_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_material_panel_accounting_20260627/source-triage.html`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- targeted teapot source-color acceptance
- full source-color acceptance
- full generated acceptance `--strict`
- full uploaded strict source policy
- full underpaint benchmark

Verdict:

- Keep. This removes false "repair source first" pressure for a handled material cluster without hiding stitch-risk gates or changing output.
- Next work should prioritize a real behavior win. The refreshed queue leaves `real_strawberry` as the only source-complexity target, but its remaining warning is real; either improve strawberry output behavior visibly or add another real fixture with semantic color/detail loss.

## Previous Patch: Repeated Compact Motif Repair Accounting

The latest source/color sprint win removes a false source-repair warning for intentional repeated compact motif fields. This is a diagnostic/source-policy change only; stitch output is intentionally unchanged.

What changed:

- Source-design diagnostics now find repeated motif groups before final repair-opportunity accounting.
- When a stitched color label is already classified as `same_color_compact_detail_repeat`, a generic `fragmented_line_art` repair opportunity for that same label is suppressed.
- `generated_acceptance.py --strict` now guards `real_strawberry` so the compact seed field must keep repeated motif accounting and must not create generic source repair pressure.
- Pixel cleanup, palette selection, stitch geometry, routing, public APIs, frontend behavior, and file formats are unchanged.

Current outcome:

- `real_strawberry`: source repair opportunities `1 -> 0`.
- `real_strawberry`: stitch output unchanged at `7369` stitches, `65` jumps, `3` trims, quality `100`.
- `real_strawberry`: colors stayed `#64d250`, `#f0785a`, `#dc321e`, and `#000000`.
- `real_strawberry`: repeated motif accounting stayed `2` groups / `26` components, adjusted source component count stayed `20`, and source suitability stayed `candidate 88` with `many_regions`.
- `real_teapot_card`, uploaded acceptance, generated acceptance, and underpaint benchmark stayed unchanged in full comparisons.
- Full uploaded, generated, source-color, and underpaint comparisons passed with no guarded status, acceptance issue, quality score, same-surface stitched long-span, same-surface untrimmed jump long-span, high-risk-surface, or broad-route-risk regression.

Validation:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_strawberry_motif_repair_guard_target_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_strawberry_motif_repair_guard_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_strawberry_motif_repair_guard_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_strawberry_motif_repair_guard_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_strawberry_motif_repair_guard_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_strawberry_motif_repair_guard_20260627/source-triage.html`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- targeted strawberry and teapot source-color canaries
- targeted daisy, sunflower, sparrow, tiny-detail, and thick-outline canaries
- full uploaded strict source policy
- full generated acceptance `--strict`
- full source-color acceptance
- full underpaint benchmark

Verdict:

- Keep. This makes source diagnostics agree with the repeated motif classifier without hiding remaining real source complexity.
- Next work should not spend more time on strawberry diagnostics unless output changes are possible. The best source/color target remains teapot-like over-fragmented material art or adding a new real generated/uploaded fixture with visible semantic color loss.

## Previous Patch: Local Cluster Material Panel Density

The latest source/color sprint win reduces stitch clutter in teapot-like local material panels while keeping repeated motifs, isolated details, routing, and source cleanup stable.

What changed:

- Source surface planning now identifies repeated motif families separately from non-repeated multi-color local detail clusters.
- Repeated motif families are guarded out of this path so seed/dot fields do not get treated as material panels.
- Non-repeated local detail clusters with at least `3` retained colors and `14` broad disconnected components can mark eligible foundation surfaces as `local_material_panel_candidate`.
- Eligible panels must be foundation surfaces owned by an accent outline band, use `surface_stable_scan`, have no holes, avoid reconstructed/repeated surfaces, and stay within `65-220mm^2` with conservative width, extent, and compactness gates.
- Local material panels lower the local-patch serpentine area floor from `90mm^2` to `70mm^2` only for that tagged path and use a `1.06` local density multiplier.
- `surface-plan.json` exposes `repeatedMotifFamily`, `localDetailClusterFamily`, `localMaterialPanelCandidate`, `localMaterialPanel`, and `densityMult`.
- Public APIs, frontend behavior, file formats, routing gates, source cleanup, and the generic local-patch gate are unchanged.

Current outcome:

- `real_teapot_card`: stitches `11711 -> 11664`.
- `real_teapot_card`: local-patch-serpentine surfaces `3 -> 5`; `solid_scan` surfaces `5 -> 3`.
- `real_teapot_card`: jumps stayed `86`; trims stayed `14`; quality stayed `100`.
- `real_teapot_card`: colors stayed preserved, color stops stayed `6`, and local detail-cluster accounting stayed `4` colors / `22` components.
- `real_teapot_card`: same-surface long spans, same-surface stitched long spans, same-surface untrimmed jump long spans, high-risk surfaces, and broad-route-risk surfaces all stayed `0`.
- Full uploaded, generated, source-color, and underpaint comparisons passed with no guarded status, acceptance issue, quality score, same-surface stitched long-span, same-surface untrimmed jump long-span, high-risk-surface, or broad-route-risk regression.
- `flower_daisy_simple`, `flower_sunflower_simple`, `real_strawberry`, `tiny_detail_icon`, `sparrow_flat_app_icon`, and `thick_outline_flower` stayed unchanged in targeted canaries.

Rejected variants:

- Lowering the generic local-patch-serpentine area gate from `90mm^2` to `70mm^2` caused `flower_daisy_simple` churn: stitches `2444 -> 2435`, jumps `26 -> 27`. Rejected.
- Using a `1.12` local-cluster density multiplier improved teapot stitches more (`11711 -> 11625`) but worsened trims `14 -> 15` and added trimmed preview risk on a purple panel. Rejected.

Validation:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_local_cluster_density106_teapot_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_local_cluster_density106_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_local_cluster_density106_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_local_cluster_density106_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_local_cluster_density106_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_local_cluster_density106_20260627/source-triage.html`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- targeted teapot, daisy, sunflower, strawberry, tiny-detail, sparrow, and thick-outline canaries
- full uploaded strict source policy
- full generated acceptance `--strict`
- full source-color acceptance
- full underpaint benchmark

Verdict:

- Keep. This is a narrow teapot/source-complexity output-density win with no route broadening and no broad-suite metric churn.
- Next work should keep source/color focus. The next likely win is source simplification or semantic material grouping for over-fragmented real generated art, not more generic routing or local-patch gate widening.

## Earlier Patch: Repeated Compact Detail Density

The latest source/color sprint win reduces overpacking in intentional repeated dark detail fields while keeping isolated icon details dense enough to read.

What changed:

- Compact forced-detail fills now receive a `repeated_detail_field` signal only when they are accent details, use forced detail fill, and belong to a same-color repeated island field with at least `12` islands.
- Repeated compact detail fields use a `0.68` density multiplier instead of the isolated-detail `0.55` multiplier.
- Isolated pupils, eyes, and the strict `tiny_detail_icon` dots keep the previous denser behavior.
- `surface-plan.json` exposes `repeatedDetailDensityMult` / `repeatedDetailDensityMults` for affected surfaces.
- Routing, source cleanup, public APIs, frontend behavior, and file formats are unchanged.

Current outcome:

- `real_strawberry`: stitches `7549 -> 7369`.
- `real_strawberry`: trims `4 -> 3`; jumps stayed `65`.
- `real_strawberry`: cross-surface trimmed preview relocations `2 -> 1`.
- `real_strawberry`: quality stayed `100`; colors stayed `#64d250/#f0785a/#dc321e/#000000`.
- `real_strawberry`: fill strategy counts stayed unchanged, including `compact_accent_fill: 30` and `compact_satin_column: 30`.
- `real_teapot_card` stayed unchanged at `11711` stitches, `86` jumps, `14` trims, quality `100`, and `3` local-patch-serpentine surfaces.
- `tiny_detail_icon`, `bee_simple`, and `sparrow_flat_app_icon` stayed unchanged in targeted canaries.
- Full uploaded, generated, source-color, and underpaint comparisons passed with no guarded status, acceptance issue, quality score, same-surface stitched long-span, same-surface untrimmed jump long-span, high-risk-surface, or broad-route-risk regression.

Validation:

- `PYTHONPYCACHEPREFIX=tmp/pycache npm run acceptance:source-color -- --case real_strawberry --out tmp/source_color_acceptance_repeated_detail_density_strawberry2_20260627`
- `python3 scripts/compare_generated_runs.py tmp/source_color_acceptance_cross_color_tiny_20260627 tmp/source_color_acceptance_repeated_detail_density_strawberry2_20260627 --case real_strawberry --out tmp/source_color_compare_repeated_detail_density_target_20260627.html --title "Repeated compact detail density - strawberry target" --fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache python3 scripts/uploaded_art_acceptance.py --case tiny_detail_icon --out tmp/uploaded_art_acceptance_repeated_detail_density_tiny_20260627 --strict-no-500 --strict-source-policy`
- `PYTHONPYCACHEPREFIX=tmp/pycache python3 scripts/generated_acceptance.py --case bee_simple --out tmp/generated_acceptance_repeated_detail_density_bee_20260627 --strict`
- `PYTHONPYCACHEPREFIX=tmp/pycache python3 scripts/generated_acceptance.py --case sparrow_flat_app_icon --out tmp/generated_acceptance_repeated_detail_density_sparrow_20260627 --strict`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- `PYTHONPYCACHEPREFIX=tmp/pycache python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_repeated_detail_density_20260627 --strict-no-500 --strict-source-policy`
- `PYTHONPYCACHEPREFIX=tmp/pycache python3 scripts/generated_acceptance.py --out tmp/generated_acceptance_repeated_detail_density_20260627 --strict`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run acceptance:source-color -- --out tmp/source_color_acceptance_repeated_detail_density_20260627`
- `PYTHONPYCACHEPREFIX=tmp/pycache python3 scripts/underpaint_benchmark.py --out tmp/underpaint_benchmark_repeated_detail_density_20260627 --format jef`
- Regression-gated uploaded, generated, source-color, and underpaint comparisons all passed.

Next recommended direction:

- Continue source/color behavior work using the refreshed triage report. `real_teapot_card` remains the top source-complexity guard; avoid broadening local-patch gates unless repeated-motif metadata can make the target narrower than the rejected sub-`90mm^2` experiment.

## Previous Patch: Cross-Color Compact Tiny Detail Accounting

The latest source/color sprint win makes source suitability agree with the planner for intentional multi-color tiny dot details.

What changed:

- Source repeated-motif detection now recognizes compact similarly sized tiny detail components across multiple stitched colors, not only within one color.
- The compact-detail width floor relaxed from `3.0mm` to `2.6mm`, matching the existing sewable compact-detail planner threshold for tiny dot fixtures.
- Source-design summaries now distinguish `repeatedMotifTinyComponentCount` from `unaccountedTinyComponentCount`; suitability scoring and `many_tiny_regions` repair pressure use only unaccounted tiny components.
- Uploaded strict source-policy now guards `tiny_detail_icon` so intentional compact dots must be source-suitability clean and have repeated compact-dot source accounting.
- Stitch generation is unchanged.

Current outcome:

- `tiny_detail_icon`: source repair opportunities `1 -> 0`.
- `tiny_detail_icon`: source suitability `candidate 88 -> clean 100`.
- `tiny_detail_icon`: repeated source motif components `0 -> 9`; adjusted source components `13 -> 7`.
- `tiny_detail_icon`: stitches, jumps, trims, quality, and colors stayed unchanged at `3520`, `23`, `2`, `100`, and `#8cb9eb/#64d250/#e63c82/#fff03c/#000000`.
- Full uploaded, generated, source-color, and underpaint comparisons passed with no guarded status, acceptance issue, quality score, same-surface stitched long-span, same-surface untrimmed jump long-span, high-risk-surface, or broad-route-risk regression.

Validation:

- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- `PYTHONPYCACHEPREFIX=tmp/pycache python3 scripts/uploaded_art_acceptance.py --case tiny_detail_icon --out tmp/uploaded_art_acceptance_cross_color_tiny_target2_20260627 --strict-no-500 --strict-source-policy`
- `PYTHONPYCACHEPREFIX=tmp/pycache python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_cross_color_tiny_20260627 --strict-no-500 --strict-source-policy`
- `PYTHONPYCACHEPREFIX=tmp/pycache python3 scripts/generated_acceptance.py --out tmp/generated_acceptance_cross_color_tiny_20260627 --strict`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run acceptance:source-color -- --out tmp/source_color_acceptance_cross_color_tiny_20260627`
- `PYTHONPYCACHEPREFIX=tmp/pycache python3 scripts/underpaint_benchmark.py --out tmp/underpaint_benchmark_cross_color_tiny_20260627 --format jef`
- Regression-gated uploaded, generated, source-color, and underpaint comparisons all passed.

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_cross_color_tiny_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_cross_color_tiny_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_cross_color_tiny_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_cross_color_tiny_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_cross_color_tiny_20260627/source-triage.html`

Next recommended direction:

- Continue looking for actual source/color behavior wins, especially safe simplification of over-fragmented real generated art, but do not merge away meaningful teapot panels.
- `real_teapot_card` remains the main source-art complexity guard after the local-fill win.
- Keep broad routing paused unless comparison reports show actual stitched-span or same-surface relocation risk.

## Previous Patch: Local Patch Serpentine Fill

The next source/color sprint win reduces clutter inside simple local material patches while keeping route and risk gates narrow.

What changed:

- Simple outlined local material patches from `90-220mm^2` can use a single serpentine fill when gap scoring proves the candidate has no long gaps and no trim gaps.
- The gate excludes source silhouettes, forced silhouettes, center disks, stems, satin zones, hole-bearing regions, and underlay-sensitive structural/no-flip groups.
- The selector tries deterministic angle nudges around the planned angle, PCA angle, and cardinal/diagonal fallbacks, then accepts only a no-risk candidate.
- `surface-plan.json` records `localPatchSerpentine` diagnostics with angle, area, and gap-score evidence.
- No API, frontend, file-format, route-threshold, or public behavior changes were made.

Current outcome:

- `real_teapot_card`: stitches `11761 -> 11711`; three local patch serpentine fills; jumps/trims unchanged at `86 / 14`; quality `100`.
- `thick_outline_flower`: stitches `6122 -> 6113`; jumps/trims unchanged at `53 / 7`; quality `100`.
- `sparrow_flat_app_icon`: stitches `5488 -> 5483`; jumps/trims unchanged at `17 / 2`; quality `100` in generated and underpaint suites.
- `synthetic_structural_route_facets`: stitches `5883 -> 5792`; jump/trim and guarded route-risk metrics unchanged.
- `flower_daisy_simple` stayed unchanged after the `90mm^2` lower gate, avoiding earlier warn-level jump churn.
- Across source-color, uploaded, generated, and underpaint full suites, regression-gated comparisons passed with no status, acceptance issue, quality score, same-surface stitched long-span, same-surface untrimmed jump long-span, high-risk-surface, or broad-route-risk regression.

Validation:

- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run acceptance:source-color -- --out tmp/source_color_acceptance_local_patch_serpentine_20260627`
- `PYTHONPYCACHEPREFIX=tmp/pycache python3 scripts/generated_acceptance.py --out tmp/generated_acceptance_local_patch_serpentine_20260627 --strict`
- `PYTHONPYCACHEPREFIX=tmp/pycache python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_local_patch_serpentine_20260627 --strict-no-500 --strict-source-policy`
- `PYTHONPYCACHEPREFIX=tmp/pycache python3 scripts/underpaint_benchmark.py --out tmp/underpaint_benchmark_local_patch_serpentine_20260627 --format jef`
- Regression-gated source-color, uploaded, generated, and underpaint comparisons all passed.

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_local_patch_serpentine_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_local_patch_serpentine_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_local_patch_serpentine_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_local_patch_serpentine_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_local_patch_serpentine_20260627/source-triage.html`

Next recommended direction:

- Continue source/color behavior work, with `real_teapot_card` still the main source-art complexity target after the local-fill improvement.
- Prefer conservative source simplification or over-fragmentation fixes that preserve intended colors, rather than broad repeated-petal or routing changes.
- Keep broad routing paused unless comparison reports show actual stitched-span or same-surface relocation risk.

## Previous Patch: Large Dark Stroke Satin Spacing

The first visible source/color sprint win reduces over-dense generated/uploaded icon outlines without changing public APIs, source policy, routing thresholds, or file formats.

What changed:

- Dark stroke-satin fills keep the existing `0.55` density multiplier for narrow/small outlines.
- Broad dark stroke networks at or above `250mm²` use a `0.72` multiplier, producing fewer satin steps while preserving coverage.
- `surface-plan.json` records `strokeSatinDensityMult` / `strokeSatinDensityMults` so broad-outline behavior is explainable in diagnostics.

Current outcome:

- `real_teapot_card`: stitches `13541 -> 11761`, trims `15 -> 14`, jumps `84 -> 86`; quality `100`, no acceptance/risk regression.
- `real_strawberry`: stitches `8323 -> 7549`, jumps `62 -> 65`, trims unchanged at `4`; quality `100`, no acceptance/risk regression.
- `thick_outline_flower`: stitches `6952 -> 6122`, jumps `54 -> 53`, trims `6 -> 7`; quality `100`, no stitched-span/risk regression.
- `same_hue_acorn`: stitches `5296 -> 4915`, jumps `23 -> 21`.
- `cartoon_elephant`: stitches `5725 -> 5191`, jumps `29 -> 27`.
- `badge_circle_star`: stitches `2080 -> 1893`.
- `synthetic_structural_route_facets`: stitches `6235 -> 5883`.
- Across uploaded, generated, source-color, and underpaint full suites, regression-gated comparisons passed with no status, acceptance issue, quality score, same-surface stitched long-span, same-surface untrimmed long-span, high-risk-surface, or broad-route-risk regression.

Validation:

- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- `python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_large_stroke_spacing_20260627 --strict-no-500 --strict-source-policy`
- `python3 scripts/generated_acceptance.py --out tmp/generated_acceptance_large_stroke_spacing_20260627 --strict`
- `npm run acceptance:source-color -- --out tmp/source_color_acceptance_large_stroke_spacing_20260627`
- `python3 scripts/underpaint_benchmark.py --out tmp/underpaint_benchmark_large_stroke_spacing_20260627 --format jef`
- Regression-gated uploaded/generated/source-color/underpaint comparisons all passed.

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_large_stroke_spacing_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_large_stroke_spacing_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_large_stroke_spacing_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_large_stroke_spacing_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_large_stroke_spacing_20260627/source-triage.html`

Next recommended direction:

- Continue source/color behavior work against real visible targets, especially a conservative simplifier for `real_teapot_card` that can reduce disconnected color pieces without dropping intended colors.
- Keep broad routing paused unless comparison reports show actual stitched-span or same-surface relocation risk.

## Previous Patch: Stitched Near-White Foreground Accounting

The latest source/color triage had no clear semantic color-loss behavior bug after sparse halo cleanup, but it still showed false repair opportunities for pale foreground regions that were already retained as stitches: bee wings, daisy petals, and a low-contrast bird belly.

What changed:

- Added `stitchedNearWhiteForegroundColorCount` to source-design diagnostics.
- Kept `near_white_foreground` as a repair opportunity only when the near-white foreground color is not retained as a stitch color.
- Exposed `sourceStitchedNearWhiteForegroundColorCount` in generated and uploaded acceptance summaries.
- Added guards for `bee_simple`, `flower_daisy_simple`, and `low_contrast_bird` so pale foreground colors cannot disappear quietly.
- No stitch generation, routing, fill strategy, API, frontend, or file-format behavior changed.

Current outcome:

- `bee_simple`: source repair opportunities `1 -> 0`, stitched near-white count `1`, stitch output unchanged at `1730` stitches, `17` jumps, `5` trims.
- `flower_daisy_simple`: source repair opportunities `1 -> 0`, stitched near-white count `1`, stitch output unchanged at `2444` stitches, `26` jumps, `6` trims.
- `low_contrast_bird`: source repair opportunities `1 -> 0`, stitched near-white count `1`, stitch output unchanged at `2502` stitches, `26` jumps, `3` trims.
- `synthetic_underpaint_cutout_lane_trap`: source repair opportunities `2 -> 1` because the stitched white cutout is now accounted; stitch output unchanged at `3033` stitches, `15` jumps, `7` trims.
- Generated acceptance now has `0` source repair opportunities across the default generated suite.
- No status, quality, acceptance issue, same-surface stitched long-span, same-surface untrimmed long-span, high-risk-surface, or broad-route-risk regression was introduced.

Validation:

- `python3 scripts/generated_acceptance.py --out tmp/generated_acceptance_near_white_policy_target_20260627 --strict --case bee_simple --case flower_daisy_simple`
- `python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_near_white_policy_target_20260627 --strict-no-500 --strict-source-policy --case low_contrast_bird`
- `python3 scripts/compare_generated_runs.py tmp/generated_acceptance_sparse_halo_policy_20260627 tmp/generated_acceptance_near_white_policy_target_20260627 --case bee_simple --case flower_daisy_simple --out tmp/generated_compare_near_white_policy_target_20260627.html --title "Generated near-white foreground policy target" --fail-on-regression`
- `python3 scripts/compare_generated_runs.py tmp/uploaded_art_acceptance_sparse_halo_policy_20260627 tmp/uploaded_art_acceptance_near_white_policy_target_20260627 --case low_contrast_bird --out tmp/uploaded_compare_near_white_policy_target_20260627.html --title "Uploaded near-white foreground policy target" --fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- `python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_near_white_policy_20260627 --strict-no-500 --strict-source-policy`
- `python3 scripts/generated_acceptance.py --out tmp/generated_acceptance_near_white_policy_20260627 --strict`
- `npm run acceptance:source-color -- --out tmp/source_color_acceptance_near_white_policy_20260627`
- `python3 scripts/underpaint_benchmark.py --out tmp/underpaint_benchmark_near_white_policy_20260627 --format jef`
- Regression-gated uploaded/generated/source-color/underpaint comparisons all passed.

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_near_white_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_near_white_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_near_white_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_near_white_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_near_white_policy_20260627/source-triage.html`

Next recommended direction:

- Stop spending time on diagnostic-only source repairs unless they hide a true color/detail defect.
- Continue looking for a real behavior target: semantic accent loss, same-hue material over-fragmentation, or a source-complexity simplifier for `real_teapot_card` that reduces disconnected pieces without dropping intended colors.

## Previous Patch: Compact Repeated Detail Motif Accounting

The real source/color fixture lane showed a useful false-positive in source complexity scoring. `real_strawberry` has `40` raw source regions, but most of the extra regions are intentional, uniform, compact black seed details. The detail-budget layer already treated this as a uniform detail field, but the source-design diagnostics only discounted the green leaf repeat and still counted the seed field as generic source complexity.

What changed:

- Added `bboxFill` to source region components so compact repeated details can be distinguished from narrow scraps.
- Split repeated motif diagnostics into broad motif groups and compact detail motif groups.
- Added generated-acceptance summary fields for source component counts, repeated motif counts, adjusted motif-aware component counts, and source suitability.
- Added a `real_strawberry` guard requiring both leaf and compact seed motif groups.
- No stitch generation, routing, fill strategy, API, frontend, or file-format behavior changed.

Current outcome:

- `real_strawberry`: triage improved `C+ -> B`.
- Raw source components stayed `40`, but motif-aware adjusted components improved to `20`.
- Repeated motif accounting improved to `2` groups / `26` components.
- Source repair opportunities improved `2 -> 1`.
- Stitch output stayed stable: `8323` stitches, `62` jumps, `4` trims, colors `[#64d250, #f0785a, #dc321e, #000000]`, `0` same-surface stitched long spans, `0` broad route risk surfaces.
- `real_teapot_card` stayed correctly flagged as `C / source_art_complexity`; the earlier probe showed its small pieces are distant separated regions, not safe absorption candidates.

Validation:

- `python3 scripts/generated_acceptance.py --fixture-dir fixtures/source_color --case real_strawberry --out tmp/source_color_acceptance_strawberry_motif_policy_20260627 --strict`
- `python3 scripts/generated_acceptance.py --fixture-dir fixtures/source_color --out tmp/source_color_acceptance_motif_policy_20260627 --strict`
- `python3 scripts/compare_generated_runs.py tmp/source_color_acceptance_real_fixtures_20260627 tmp/source_color_acceptance_motif_policy_20260627 --out tmp/source_color_compare_motif_policy_20260627.html --title "Source Color Motif Policy" --fail-on-regression`
- `python3 scripts/source_art_triage_report.py --input tmp/uploaded_art_acceptance_source_color_resume_20260627 --input tmp/generated_acceptance_source_color_resume_20260627 --input tmp/source_color_acceptance_motif_policy_20260627 --out tmp/source_art_triage_motif_policy_20260627`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- `python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_motif_policy_20260627 --strict-no-500 --strict-source-policy`
- `python3 scripts/generated_acceptance.py --out tmp/generated_acceptance_motif_policy_20260627 --strict`
- `npm run benchmark:underpaint -- --out tmp/underpaint_benchmark_motif_policy_20260627`
- Regression-gated uploaded/generated/underpaint comparisons all passed.

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_motif_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_motif_policy_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_motif_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_motif_policy_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_motif_policy_20260627.html`

Next recommended direction:

- Keep source compiler behavior stable until a report shows actual color loss or stitch-risk movement.
- Use `real_teapot_card` as the next source-complexity target, but do not widen absorption blindly: its rejected fragments are `10-44mm` from same-family parent regions and appear to be real separated color pieces.
- Look for a source-side simplification that preserves colors while reducing teapot fill-coherence/routing pressure, probably through generator/source scoring rather than geometry absorption.

## Previous Patch: Real Source/Color Fixture Lane

The source/color sprint needed real failure examples before another compiler change. Historical balloon, teapot, ladybug, and strawberry notes were rechecked against the current engine. The current engine now preserves the old teapot color families and the ladybug cream/red/black colors, but teapot and strawberry still expose a repeatable source-complexity class that the default synthetic/uploaded fixtures do not exercise.

What changed:

- Added `fixtures/source_color/real_teapot_card.png` and prompt sidecars.
- Added `fixtures/source_color/real_strawberry.png` and prompt sidecars.
- Added `npm run acceptance:source-color`, which runs `generated_acceptance.py` against `fixtures/source_color` with `--strict`.
- Kept these fixtures out of the default generated acceptance suite because they are deliberately C-grade source-complexity targets.
- No stitch engine, routing, API, frontend, or file-format behavior changed.

Current outcome:

- `real_teapot_card`: `C / 77`, root cause `source_art_complexity`, colors `[#50be46, #f0785a, #965ad2, #ffc88c, #000000]`, `25` regions, `13541` stitches, `84` jumps, `15` trims.
- Teapot triage reasons: local detail cluster, too many tones, one source repair opportunity, one fill-coherence hint without stitched-web/broad-route risk, and three preview-only trimmed relocations.
- `real_strawberry`: `C+ / 84`, root cause `source_art_complexity`, colors `[#64d250, #f0785a, #dc321e, #000000]`, `40` regions, `8323` stitches, `62` jumps, `4` trims.
- Strawberry triage reasons: too many tones, seven intentional repeated motifs, two source repair opportunities, and three explicitly accounted tiny components.
- The regression-gated comparison against the local probe passed with no regression.

Validation:

- `python3 scripts/generated_acceptance.py --fixture-dir fixtures/source_color --out tmp/source_color_acceptance_real_fixtures_20260627 --strict`
- `npm run acceptance:source-color -- --out tmp/source_color_acceptance_npm_script_20260627`
- `python3 scripts/source_art_triage_report.py --input tmp/source_color_acceptance_real_fixtures_20260627 --out tmp/source_art_triage_source_color_real_fixtures_20260627`
- `python3 scripts/compare_generated_runs.py tmp/real_source_color_probe_20260627 tmp/source_color_acceptance_real_fixtures_20260627 --case real_teapot_card --case real_strawberry --out tmp/source_color_compare_real_fixture_lane_20260627.html --title "Source Color Real Fixture Lane" --fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_source_color_real_fixtures_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_real_fixture_lane_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_acceptance_real_fixtures_20260627/review.md`

Next direction: work from the real fixture lane before touching compiler policy. The highest-value next patch is likely source simplification or fixture-specific preflight/source scoring for teapot-like local detail clusters, not route broadening and not color forcing.

## Previous Patch: Muted Accent Source Guard

The source/color sprint found that the historical accent probes already preserve soft pink and lavender accents, but that behavior was not locked into the default uploaded-art acceptance suite. The new `muted_accent_badge` fixture turns that implicit success into a strict guard for user-upload-like art with low-chroma accent patches and one tiny soft-pink detail component.

What changed:

- `uploaded_art_acceptance.py` now includes `muted_accent_badge` in default `SAMPLES`.
- Strict source-policy checks require stitched `#8cb9eb`, `#b496dc`, `#f082a0`, and `#000000`.
- Strict source-policy checks also require the tiny muted accent component to be accounted for and the `preserve_muted_accent_label:detail_component` decision to remain present.
- No stitch engine, routing, API, frontend, or file-format behavior changed.

Current outcome:

- New case added: absent before, now `A / 100`, `status 200`.
- `muted_accent_badge`: colors `[#b496dc, #8cb9eb, #f082a0, #000000]`, stitch count `3864`, jumps `27`, trims `3`.
- Tiny/source policy: `sourceTinyComponentCount 1`, `tinyPolicyAccountedCount 1`, `preserve_muted_accent_label:detail_component 2`, detail budget `ok`.
- Risk gates: `0` same-surface untrimmed long spans, `0` broad-fill route risk surfaces, `0` detail-fill risk surfaces.
- Combined uploaded/generated source triage now reports `A: 17` and `mostly_ok: 17`.
- Generated and underpaint comparisons passed with `--fail-on-regression`; no engine-output regression was introduced.

Validation:

- `python3 scripts/uploaded_art_acceptance.py --case muted_accent_badge --out tmp/uploaded_art_acceptance_muted_accent_case_20260627 --strict-no-500 --strict-source-policy`
- `python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_muted_accent_full_20260627 --strict-no-500 --strict-source-policy`
- `python3 scripts/generated_acceptance.py --out tmp/generated_acceptance_muted_accent_guard_20260627 --strict`
- `python3 scripts/source_art_triage_report.py --input tmp/uploaded_art_acceptance_muted_accent_full_20260627 --input tmp/generated_acceptance_muted_accent_guard_20260627 --out tmp/source_art_triage_muted_accent_guard_20260627`
- `python3 scripts/compare_generated_runs.py tmp/uploaded_art_acceptance_source_color_baseline_20260627 tmp/uploaded_art_acceptance_muted_accent_full_20260627 --out tmp/uploaded_compare_muted_accent_guard_20260627.html --title "Muted Accent Guard Uploaded" --fail-on-regression`
- `python3 scripts/compare_generated_runs.py tmp/generated_acceptance_source_color_baseline_20260627 tmp/generated_acceptance_muted_accent_guard_20260627 --out tmp/generated_compare_muted_accent_guard_20260627.html --title "Muted Accent Guard Generated" --fail-on-regression`
- `python3 scripts/underpaint_benchmark.py --out tmp/underpaint_benchmark_muted_accent_guard_20260627 --format jef`
- `python3 scripts/compare_generated_runs.py tmp/underpaint_benchmark_source_color_grading_20260627 tmp/underpaint_benchmark_muted_accent_guard_20260627 --out tmp/underpaint_compare_muted_accent_guard_20260627.html --title "Muted Accent Guard Underpaint" --fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_muted_accent_guard_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_muted_accent_guard_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_muted_accent_guard_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_muted_accent_guard_20260627/source-triage.html`

Next direction: keep this as a guardrail, not a reason to broaden color forcing. The next useful source/color work still needs a real failure example: visible accent loss, same-hue material collapse, or tiny/detail clutter that survives these strict checks.

## Previous Patch: Source/Color Triage Grading Calibration

The fresh source/color sprint established uploaded and generated baselines, then ran `source_art_triage_report.py`. The report found no current source/color case that justified a risky stitch-engine change: all rows were `mostly_ok`, and the only non-A grade was `leaf_single_smooth`, where heavy local cleanup removed raw antialias/noise fragments and produced clean stitch output.

What changed:

- `grade_stitch_quality.py` now recognizes benign source normalization when diagnostics show clean output, no source repair opportunities, no meaningful dropped colors, no surface connector/fill risk, and explicit `source_tiny_regions_cleaned` noise cleanup.
- In that case the finding becomes informational (`source_normalization_cleaned_noise`) instead of the old `source_normalization_pressure` penalty.
- No stitch engine, API, frontend, routing, file-format, or fixture behavior changed.

Current outcome:

- `leaf_single_smooth` product grade improved `B / 94 -> A / 100` in the quality gate.
- The combined uploaded/generated source-color triage now reports `A: 16` and `mostly_ok: 16`.
- Uploaded/generated/underpaint conversion comparisons passed with `--fail-on-regression`; there were no conversion metric changes.

Validation:

- `python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_source_color_baseline_20260627 --strict-no-500 --strict-source-policy`
- `python3 scripts/generated_acceptance.py --out tmp/generated_acceptance_source_color_baseline_20260627 --strict`
- `python3 scripts/source_art_triage_report.py --input tmp/uploaded_art_acceptance_source_color_baseline_20260627 --input tmp/generated_acceptance_source_color_baseline_20260627 --out tmp/source_art_triage_source_color_grading_20260627`
- `python3 scripts/grade_stitch_quality.py --input tmp/uploaded_art_acceptance_source_color_baseline_20260627 --input tmp/generated_acceptance_source_color_baseline_20260627 --out tmp/quality_gate_source_color_grading_20260627`
- uploaded/generated/underpaint comparisons with `--fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- `python3 scripts/underpaint_benchmark.py --out tmp/underpaint_benchmark_source_color_grading_20260627 --format jef`

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_source_color_grading_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/quality_gate_source_color_grading_20260627/quality-gate.md`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_source_color_baseline_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_source_color_baseline_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_source_color_grading_20260627.html`

Next direction: do not force a source/compiler patch against the current fixtures. Add or collect real source-color failures first: visible accent loss, same-hue material collapse, or tiny/detail clutter that survives strict source-policy checks.

## Recent Patch: Unsafe Structural Safe-Flip Filter

The structural safe-flip orientation DP fixed the mushroom same-surface relocation and preserved the acorn route win, but `same_hue_shell_facets` still had one same-surface trimmed relocation. Investigation showed the shell raw chain was fine; the legacy structural `safe_flip()` variant created a bad internal underlay-to-cover handoff of roughly `58mm`, while the reoriented variant kept that internal handoff short.

What changed:

- Structural flip variant generation now measures each chain's internal long-gap key.
- If the legacy safe flip introduces an extreme internal long handoff and the reoriented flip removes internal trim/long-span risk, candidate scoring keeps only the reoriented variant.
- Structural original components now carry their own internal handoff cost into orientation scoring, so the DP can compare "do nothing" against structural variants honestly.
- `same_hue_shell_facets` strict source policy now requires preserved dark/mid/light warm shell tones, no same-surface material relocations, and `trimCount <= 5`.

Current outcome:

- `same_hue_shell_facets`: same-surface trimmed long spans `1 -> 0`, stitches `7814 -> 7810`, jumps stable at `37`, trims stable at `5`.
- The one remaining long relocation is cross-surface and preview-only, not a same-surface material relocation.
- `same_hue_acorn_facets` and `same_hue_mushroom_facets` stayed metric-stable against the accepted orientation-DP run.
- Full uploaded, generated, and underpaint comparisons passed with `--fail-on-regression` and no top-line metric changes.

Validation:

- `python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_structural_unsafe_legacy_filter_same_hue_strict_20260627 --case same_hue_acorn_facets --case same_hue_mushroom_facets --case same_hue_shell_facets --strict-no-500 --strict-source-policy`
- `python3 scripts/compare_generated_runs.py tmp/uploaded_art_acceptance_structural_orientation_dp_same_hue_strict_20260627 tmp/uploaded_art_acceptance_structural_unsafe_legacy_filter_same_hue_strict_20260627 --out tmp/uploaded_compare_structural_unsafe_legacy_filter_same_hue_strict_20260627.html --title "Structural Unsafe Legacy Filter Same-Hue Strict" --fail-on-regression`
- `python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_structural_unsafe_legacy_filter_full_20260627 --strict-no-500 --strict-source-policy`
- `python3 scripts/generated_acceptance.py --out tmp/generated_acceptance_structural_unsafe_legacy_filter_20260627 --strict`
- `python3 scripts/underpaint_benchmark.py --out tmp/underpaint_benchmark_structural_unsafe_legacy_filter_20260627 --format jef`
- full uploaded/generated/underpaint comparisons with `--fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- `npm run benchmark:underpaint`

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_structural_unsafe_legacy_filter_same_hue_strict_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_structural_unsafe_legacy_filter_full_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_structural_unsafe_legacy_filter_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_structural_unsafe_legacy_filter_20260627.html`

Next direction: route work is now at a good stopping point. The next highest-value pass should return to source-art/color triage with real generated/uploaded examples, especially meaningful accents and same-hue material preservation under strict source-policy checks.

## Recent Patch: Structural Safe-Flip Orientation DP

The light-endpoint patch correctly preserved the mushroom's tan material color, but the added real material region exposed a same-surface trimmed relocation inside a structural underlay+cover chain. Disabling structural safe flips fixed the mushroom but lost the acorn routing win, so the accepted fix keeps structural candidate routing and gives it safer orientation choices.

What changed:

- `safe_flip()` keeps its legacy structural reversal for backward-compatible candidate behavior.
- Structural candidate scoring can also consider a reoriented safe flip that reverses cover bars and then orients underlay segments toward the new cover start.
- Component-route orientation DP now supports multiple orientation options per component instead of a simple original/flipped bit.
- The DP ranks external trim/long-span pressure first, then internal structural handoff trim/long-span pressure, then travel distance.
- `same_hue_mushroom_facets` strict source policy now requires no same-surface material relocations and `trimCount <= 6`.

Current outcome:

- `same_hue_mushroom_facets`: jumps `20 -> 19`, trims `7 -> 6`, same-surface trimmed long spans `1 -> 0`, with `#d2aa6e` still preserved.
- `same_hue_acorn_facets`: trims `6 -> 5`, cross-surface trimmed long spans `1 -> 0`, preserving the earlier structural route win.
- `same_hue_shell_facets`: jumps `39 -> 37`, trims `7 -> 5`, same-surface trimmed long spans `2 -> 1`, cross-surface trimmed long spans `1 -> 0`.
- Full generated/underpaint comparisons passed with `--fail-on-regression`; generated only changed `sparrow_flat_app_icon` stitch count `5504 -> 5488`, and underpaint additionally improved `synthetic_structural_route_facets` trims `6 -> 5`.
- Full uploaded comparison passed with `--fail-on-regression`; `no_outline_teddy` jumps improved `14 -> 12`, while `thick_outline_flower` had one extra jump with stable trim/risk metrics.

Validation:

- `python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_structural_orientation_dp_same_hue_strict_20260627 --case same_hue_acorn_facets --case same_hue_mushroom_facets --case same_hue_shell_facets --strict-no-500 --strict-source-policy`
- `python3 scripts/compare_generated_runs.py tmp/uploaded_art_acceptance_light_endpoint_20260627 tmp/uploaded_art_acceptance_structural_orientation_dp_same_hue_strict_20260627 --out tmp/uploaded_compare_structural_orientation_dp_same_hue_strict_20260627.html --title "Structural Orientation DP Same-Hue Strict" --fail-on-regression`
- `python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_structural_orientation_dp_full_20260627 --strict-no-500 --strict-source-policy`
- `python3 scripts/compare_generated_runs.py tmp/uploaded_art_acceptance_light_endpoint_full_20260627 tmp/uploaded_art_acceptance_structural_orientation_dp_full_20260627 --out tmp/uploaded_compare_structural_orientation_dp_full_20260627.html --title "Structural Orientation DP Full Uploaded" --fail-on-regression`
- `python3 scripts/generated_acceptance.py --out tmp/generated_acceptance_structural_orientation_dp_20260627 --strict`
- `python3 scripts/underpaint_benchmark.py --out tmp/underpaint_benchmark_structural_orientation_dp_20260627 --format jef`
- `python3 scripts/compare_generated_runs.py tmp/generated_acceptance_light_endpoint_20260627 tmp/generated_acceptance_structural_orientation_dp_20260627 --out tmp/generated_compare_structural_orientation_dp_20260627.html --title "Structural Orientation DP Generated" --fail-on-regression`
- `python3 scripts/compare_generated_runs.py tmp/underpaint_benchmark_light_endpoint_20260627 tmp/underpaint_benchmark_structural_orientation_dp_20260627 --out tmp/underpaint_compare_structural_orientation_dp_20260627.html --title "Structural Orientation DP Underpaint" --fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_structural_orientation_dp_same_hue_strict_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_structural_orientation_dp_full_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_structural_orientation_dp_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_structural_orientation_dp_20260627.html`

Next direction completed by the unsafe legacy structural flip filter above.

## Recent Patch: Same-Hue Light Endpoint Preservation

The dark-endpoint guard fixed same-hue material fields where a dark cap/base was being flattened into a mid-tone. The mushroom stress case exposed the symmetric problem: a substantial light tan material region could collapse into the dominant orange/pink body tone because the oversegmented tonal-family cleanup only protected the darkest endpoint.

What changed:

- `_collapse_oversegmented_tonal_families(...)` now finds both the darkest and lightest active members of a same-hue family.
- The lightest member is protected only when it is substantial, chromatic, clearly lighter than the dominant family member, and not near-white antialias residue.
- `uploaded_art_acceptance.py --strict-source-policy --case same_hue_mushroom_facets` now requires `#783c14`, `#f0785a`, `#d2aa6e`, and black, plus at least three warm tones with enough luminance spread.

Current outcome:

- `same_hue_mushroom_facets` colors improved from `#783c14`, `#f0785a`, black to `#783c14`, `#f0785a`, `#d2aa6e`, black.
- Source normalization changed-pixel fraction dropped from `0.10942 -> 0.03885`.
- Quality stays `100`, with `0` high-risk surfaces, `0` broad-route-risk surfaces, and no same-surface stitched or untrimmed long spans.
- The preserved material costs real route pressure in the stress-only case: jumps `15 -> 20`, trims `5 -> 7`, and one preview/trimmed same-surface long-span diagnostic appears. Default uploaded, generated, and underpaint suites are unchanged.

Validation:

- `python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_light_endpoint_20260627 --case same_hue_acorn_facets --case same_hue_mushroom_facets --case same_hue_shell_facets --strict-no-500 --strict-source-policy`
- `python3 scripts/compare_generated_runs.py tmp/uploaded_art_acceptance_same_hue_stress_probe_20260627 tmp/uploaded_art_acceptance_light_endpoint_20260627 --out tmp/uploaded_compare_light_endpoint_20260627.html --title "Same-Hue Light Endpoint" --fail-on-regression`
- `python3 scripts/uploaded_art_acceptance.py --out tmp/uploaded_art_acceptance_light_endpoint_full_20260627 --strict-no-500 --strict-source-policy`
- `python3 scripts/compare_generated_runs.py tmp/uploaded_art_acceptance_structural_route_fixed_full_20260627 tmp/uploaded_art_acceptance_light_endpoint_full_20260627 --out tmp/uploaded_compare_light_endpoint_full_20260627.html --title "Light Endpoint Full Uploaded" --fail-on-regression`
- `python3 scripts/generated_acceptance.py --out tmp/generated_acceptance_light_endpoint_20260627 --strict`
- `python3 scripts/underpaint_benchmark.py --out tmp/underpaint_benchmark_light_endpoint_20260627 --format jef`
- `python3 scripts/compare_generated_runs.py tmp/generated_acceptance_structural_route_20260627 tmp/generated_acceptance_light_endpoint_20260627 --out tmp/generated_compare_light_endpoint_20260627.html --title "Light Endpoint Generated" --fail-on-regression`
- `python3 scripts/compare_generated_runs.py tmp/underpaint_benchmark tmp/underpaint_benchmark_light_endpoint_20260627 --out tmp/underpaint_compare_light_endpoint_20260627.html --title "Light Endpoint Underpaint" --fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_light_endpoint_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_light_endpoint_full_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_light_endpoint_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_light_endpoint_20260627.html`

Next direction: keep the color win. The next useful pass is reducing the extra stress-case route pressure created by preserving the mushroom light material, but only if it does not hide the newly preserved tan region or introduce stitched/untrimmed long-span risk.

## Recent Patch: Disconnected-Island Route Fixture Coverage

The structural-safe routing change needed dedicated benchmark fixtures before any broader route optimization. Daisy and sunflower still matter, but they are flower-specific; this patch adds route-specific synthetic fixtures to `underpaint_benchmark.py`.

What changed:

- Added `synthetic_component_route_ring`: eight same-color disconnected islands plus a center field. It asserts a clean candidate-graph decision with nearest/angular/MST candidates, no structural components, no same-surface long spans, no high-risk surfaces, and no broad route risk.
- Added `synthetic_structural_route_facets`: an acorn-like same-hue faceted source that asserts structural-safe route scoring. It requires a structural candidate route to beat nearest, all structural components to be safely flippable, no orientation locks, trims `<= 8`, and no same-surface long spans/high-risk/broad-route-risk regressions.
- Added helpers for reading `componentRouteDecisions` and selected/nearest route scores from `surface-plan.json`.

Current outcome:

- targeted fixture benchmark passes.
- full `npm run benchmark:underpaint` passes with both new fixtures in the default set.
- comparison against the previous route-diagnostic underpaint benchmark passes with `--fail-on-regression`; the new fixtures appear as added coverage.

Validation:

- `python3 scripts/underpaint_benchmark.py --out tmp/underpaint_benchmark_route_fixtures_assert_20260627 --format jef --case synthetic_component_route_ring --case synthetic_structural_route_facets`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- `npm run benchmark:underpaint`
- `python3 scripts/compare_generated_runs.py tmp/underpaint_benchmark_route_diag_20260627 tmp/underpaint_benchmark --out tmp/underpaint_compare_route_fixture_coverage_20260627.html --title "Route Fixture Coverage" --fail-on-regression`

Key report:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_route_fixture_coverage_20260627.html`

Next direction: route broadening now has better fixture gates, but the highest-value next pass should return to color/detail preservation unless a comparison report shows a true route regression. Keep metadata-preserving routing limited to candidate scoring.

## Recent Patch: Structural-Safe Component Routing

The previous route diagnostics showed the acorn facet candidates were blocked because broad underlay+fill surfaces were `no_flip`. This patch makes those structural chains safely routable inside candidate-graph scoring only: the route scorer can preserve `_StitchChain` metadata, use safe flips when chunk spans exist, and still leave ordinary nearest routing byte-for-byte stable for unrelated groups.

What changed:

- Broad underlay+fill `_StitchChain` components now get a single chunk span so `safe_flip()` can reverse the component while still sewing underlay before cover.
- Candidate-graph routing preserves `_StitchChain` metadata; plain nearest routing keeps the old copied-list behavior to avoid broad fixture churn.
- Structural route debug now reports `structuralComponentCount`, `safeFlipComponentCount`, and `orientationLockedCount`.
- Route candidates no longer win just because max gap or total travel improves; they must improve predicted trim or jump pressure.

Current outcome:

- explicit `same_hue_acorn_facets`: trims `7 -> 6`, jumps stay `20`, cross-surface trimmed long spans `3 -> 1`, quality stays `100`.
- generated and underpaint `sparrow_flat_app_icon`: trims `3 -> 2`, jumps `18 -> 17`, cross-surface trimmed long spans `3 -> 2`.
- default uploaded `thick_outline_flower`: trims `7 -> 6`, jumps `56 -> 53`, cross-surface trimmed long spans `1 -> 0`.
- no quality, acceptance, same-surface stitched long-span, high-risk-surface, or broad-route-risk regressions in uploaded, generated, or underpaint comparisons.

Validation:

- targeted `same_hue_acorn_facets` uploaded acceptance and comparison with `--fail-on-regression`
- full uploaded strict source policy and comparison with `--fail-on-regression`
- full generated acceptance and comparison with `--fail-on-regression`
- underpaint benchmark and underpaint comparison with `--fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- `npm run benchmark:underpaint`

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_structural_route_fixed_acorn_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_structural_route_fixed_full_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_structural_route_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_structural_route_20260627.html`

Next direction completed by the fixture-coverage patch above. Do not make metadata-preserving routing the default for nearest routes; an attempted broad version regressed unrelated upload fixtures.

## Recent Patch: Route Diagnostics And Small Exact Component Tours

The graph-aware route selector needed one more diagnostic layer before touching the remaining same-hue facet trims. Direct route experiments showed small exact tours can find better predicted ordering for tiny disconnected clusters, but the real uploaded acceptance path auto-tunes the same-hue acorn into structural/no-flip surfaces. Those surfaces should not be freely reordered yet because underlay/cover relationships matter more than raw centroid distance.

What changed:

- `candidate_graph` scoring now includes `small_exact` for 3-7 component clusters.
- Candidate scoring uses `ROUTE_INTER_COMPONENT_TRIM_MM = 16.0`, matching the converter's inter-component trim threshold.
- `_component_route_analysis()` records why a group did or did not enter candidate routing.
- Fill groups can fall back to raw-component centroid analysis when planned surfaces collapse the route signal.
- `surface-plan.json` records nearest fallbacks when a candidate was available but rejected, including `basis`, component counts, centroid spread, raw-component gate details, and rejection reason.

Current outcome:

- `same_hue_acorn_facets` remains quality `100`, trims `7`, jumps `20`, and stitches `6214`.
- The two remaining route candidates for `#a05a28` and `#c3915a` request `candidate_graph` but select `nearest` with `rejectionReason: structural_no_flip_component`.
- Full uploaded, generated, and underpaint comparisons show no key metric movement versus the covered-travel baseline.
- This confirms the next trim step should be structural-aware ordering or surface-stop splitting, not a broader trim threshold or unsafe global component reorder.

Validation:

- targeted `same_hue_acorn_facets` uploaded acceptance
- full uploaded strict source policy
- full generated acceptance
- generated comparison with `--fail-on-regression`
- underpaint benchmark and underpaint comparison with `--fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- `npm run benchmark:underpaint`

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_route_diag_full_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_route_diag_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_route_diag_20260627.html`

Next direction: add a structural/no-flip-safe route variant that preserves per-surface orientation and underlay order, or split same-color structural surfaces into smaller stops so exposed relocations shorten without flipping or reordering sensitive stitch geometry.

## Recent Patch: Covered Travel Window For Same-Hue Facets

The last patch deliberately stopped at a `16mm` inter-component trim threshold because looser global thresholds created long untrimmed jump diagnostics. The safer next step was to extend the existing covered-travel pass, which only stitches a carry when later geometry proves it will be hidden under a subsequent fill/outline.

What changed:

- `COVERED_TRAVEL_MAX_GAP_EMB = 350.0` (`35mm`) replaces the old implicit `20mm` candidate ceiling in `_merge_covered_travel`.
- The coverage test is unchanged: exposed long carries still stay as jumps/trims.
- The accepted acorn improvement came from one additional covered merge, not from allowing untrimmed exposed jumps.

Current outcome:

- `same_hue_acorn_facets`: trims `8 -> 7`
- `same_hue_acorn_facets`: jumps `21 -> 20`
- `same_hue_acorn_facets`: stitches `6205 -> 6214`
- `same_hue_acorn_facets`: cross-surface trimmed long spans `4 -> 3`
- `same_hue_acorn_facets`: covered travel merges `38 -> 39`
- quality stays `100`; colors stay `#783c14`, `#a05a28`, `#c3915a`, `#d2aa6e`, and black
- no actual-thread connector risk, stitched long spans, or untrimmed jump long spans
- generated and underpaint full comparisons are unchanged versus the `trim16` baseline

Validation:

- targeted same-hue uploaded acceptance
- same-hue uploaded comparison with `--fail-on-regression`
- full uploaded strict source policy
- full generated acceptance
- generated comparison with `--fail-on-regression`
- underpaint benchmark and underpaint comparison with `--fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- `npm run benchmark:underpaint`

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_covered_travel35_same_hue_20260626.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_covered_travel35_20260626.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_covered_travel35_20260626.html`

Next direction: the remaining acorn facet trims are still exposed `23-43mm` relocations. Do not solve those by raising the global trim threshold; the next option is route-local ordering or same-color surface grouping that shortens the exposed moves before command generation.

## Recent Patch: Same-Hue Facet Trim Reduction

The dark-endpoint guard fixed color preservation for faceted same-hue material art, but it exposed the next issue: the now-preserved material facets created extra trim pressure. The acorn fixture improved visually, but trims rose from `7 -> 11` because formerly flattened mid-tone facets became real stitched regions.

The converter now allows modest inter-component same-color carries before trimming:

- `_TRIM_GAP_INTER_COMPONENT_EMB`: `8mm -> 16mm`
- `16mm` was chosen because higher experimental thresholds (`25mm+`) reduced trim count further but introduced long untrimmed jump diagnostics.
- The graph-route gate also evaluates 3-component fill groups, keeping candidate diagnostics available for small disconnected same-color material fields.

Current outcome:

- `same_hue_acorn_facets`: trims `11 -> 8`
- `same_hue_acorn_facets`: stitches `6217 -> 6205`
- `same_hue_acorn_facets`: quality stays `100`
- `same_hue_acorn_facets`: preserved colors stay `#783c14`, `#a05a28`, `#c3915a`, `#d2aa6e`, and black
- `same_hue_acorn_facets`: no untrimmed long-span diagnostics, broad-fill route risk, or detail-fill risk
- `same_hue_mushroom_facets`: quality `100`, trims `5`, no broad/detail risk
- `same_hue_shell_facets`: quality `100`, trims `5`, no broad/detail risk
- full uploaded strict acceptance picked up collateral trim improvements in several uploaded fixtures without strict source-policy regressions

Validation:

- targeted faceted + clean acorn uploaded acceptance
- full uploaded strict source policy
- full generated acceptance
- generated comparison with `--fail-on-regression`
- underpaint comparison with `--fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- `npm run benchmark:underpaint`

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_trim16_20260626.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_trim16_20260626.html`

Next direction from this patch was smarter covered travel or component merging rather than raising the trim threshold. The first covered-travel extension is now implemented above.

## Recent Patch: Same-Hue Dark Endpoint Guard

The acorn facet stress case showed that oversegmented same-hue families could keep a mid-tone facet as the dominant stitch color while collapsing the darker material field into it. That made the design technically convert, but it produced a review-quality result: quality `50`, one broad-fill route risk surface, heavy source normalization, and the dark cap color lost.

The posterizer now protects a substantial darker end-member inside an oversegmented tonal family when it has enough area and luminance separation from the dominant mid-tone. This keeps real materials such as caps, shells, bases, and dark body fields from being flattened into same-hue shading facets.

Current outcome:

- `same_hue_acorn_facets`: quality `50 -> 100`
- `same_hue_acorn_facets`: broad-fill route risk `1 -> 0`
- `same_hue_acorn_facets`: source normalization changed fraction `0.06482 -> 0.00315`
- `same_hue_acorn_facets`: preserved colors `#783c14`, `#a05a28`, `#c3915a`, `#d2aa6e`, and black
- tradeoff: trims `7 -> 11`, jumps `18 -> 21`, stitches `5696 -> 6217`, because the mid-tone facets now stitch as real regions instead of being flattened away
- `same_hue_acorn`: unchanged at quality `100`, `23 jumps / 3 trims`, no broad/detail risk

Validation:

- targeted faceted + clean acorn uploaded acceptance
- full uploaded strict source policy
- full generated acceptance
- generated comparison with `--fail-on-regression`
- underpaint comparison with `--fail-on-regression`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`
- `npm run benchmark:underpaint`

Key reports:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_dark_endpoint_20260626.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_dark_endpoint_20260626.html`

## Recent Patch: Graph-Aware Component Routing

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
   The clean same-hue material guard is live (`same_hue_acorn`, quality `100`) and faceted same-hue stress coverage now protects both dark and light material endpoints. The next broad quality pass should add real generated/uploaded examples where same-hue materials still collapse, over-fragment, or create exposed long relocations.

2. Keep route broadening behind the new disconnected-island fixtures.
   `synthetic_component_route_ring` and `synthetic_structural_route_facets` now cover plain candidate scoring, structural-safe route wins, and safe fallback. Future route changes should improve real cases without breaking those guards.

3. Continue color preservation on upload-style art.
   The strict source-policy suite now catches lost accent/material colors, but real uploaded examples can still expose cases where visible colors are too small, too close to neighboring tones, or too expensive to route. Preserve intentional colors first, then reduce the route pressure they create.

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

## 2026-06-28 — Uploaded Source/Color Reporting Guard

Target: upload-style source/color acceptance coverage.

Change accepted:

- `scripts/uploaded_art_acceptance.py` now records `sourceColorLayers`, `segmentationColors`, `droppedColors`, `segmentationComponentCount`, and `segmentationTinyComponents`, matching the generated acceptance evidence used by comparison and triage tooling.
- Strict uploaded source policy now includes a generic source-color-family preservation guard, so broad visible red/green/blue/yellow source families must survive into stitched thread families.

Validation and reports:

- Uploaded strict source policy: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_source_color_layers_20260628`
- Uploaded regression comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_source_color_layers_20260628.html`
- Generated strict acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_source_color_layers_reporting_20260628`
- Generated regression comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_source_color_layers_reporting_20260628.html`
- Underpaint benchmark: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_benchmark_source_color_layers_reporting_20260628`
- Underpaint regression comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_source_color_layers_reporting_20260628.html`
- Combined source triage: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_source_color_layers_reporting_20260628/source-triage.html`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`

Before/after:

- Stitch geometry is unchanged; this is acceptance/reporting coverage only.
- Uploaded strict suite remains all status `200`, quality `100`, no unresolved tiny decisions, no detail-fill risk.
- New source-layer evidence exposes meaningful dropped/noise colors in uploaded reports, for example JPEG badge residue and thick-outline halo pruning.

Next recommended direction:

- Use the richer uploaded report fields to add a real uploaded/generated fixture where a meaningful semantic color is lost or over-fragmented, then fix source normalization or color preservation around that case.

## 2026-06-28 — Neutral Alias Black Stroke Retention

Target: `synthetic_underpaint_cutout_lane_trap`.

Change accepted:

- Fixed neutral low-chroma alias pruning so grayscale labels only collapse as same-hue aliases when their luminance is close. This keeps long black source strokes from being pruned merely because a larger white/near-white cutout label also has undefined hue.
- Updated the underpaint benchmark to require the fixture's long black stroke to stitch and to fail if black appears in `droppedColors`.
- The fixture now accepts the safer stable-scan outcome once the black stroke is retained, instead of requiring the older lane-route acceptance detail.

Before/after:

- `colors`: `['#2850c8', '#ffffff'] -> ['#2850c8', '#ffffff', '#000000']`
- black dropped color: present -> absent
- `trimCount`: `7 -> 3`
- `jumpCount`: `15 -> 12`
- `stitchCount`: `3033 -> 7450`
- `sameSurfaceLongSpans`: `1 -> 0`
- `sameSurfaceTrimmedLongSpans`: `1 -> 0`
- quality stayed `100`; high-risk and broad-route-risk surfaces stayed `0`
- `scan_lanes` is no longer selected for this fixture because preserving the stroke changes the broad-fill geometry; the guarded outcome is better on trims and same-surface spans.

Validation and reports:

- Targeted guard failure reproduced: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_black_stroke_guard_probe_20260628`
- Targeted fixed run: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_black_stroke_fix_probe_20260628`
- Targeted comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_black_stroke_fix_probe_20260628.html`
- Uploaded strict source policy: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_black_stroke_fix_20260628`
- Uploaded comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_black_stroke_fix_20260628.html`
- Generated strict acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_black_stroke_fix_20260628`
- Generated comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_black_stroke_fix_20260628.html`
- Full underpaint benchmark: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_benchmark_black_stroke_fix_20260628`
- Underpaint comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_black_stroke_fix_20260628.html`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`

Next recommended direction:

- Continue source/color behavior work with real generated or uploaded examples. The next useful target should be semantic color/detail loss or over-fragmentation in a user-like source, not another diagnostic-only accounting change.

## 2026-06-28 — Satin-Width Local Material Panel Fill

Target: `real_teapot_card`.

Change accepted:

- Added local-patch serpentine rejection diagnostics to `surface-plan.json` so local material panels explain why a continuous patch path was not selected.
- Allowed local material panels inside teapot-like multi-color detail clusters to attempt the existing proved-safe local serpentine path even when the geometry is satin-width.
- Kept stem-like, holed, silhouette, center-disk, and non-material satin-zone surfaces blocked from this exception.

Before/after:

- `sourceLocalMaterialPanelSerpentineSurfaceCount`: `5 -> 8`
- `sourceLocalMaterialPanelScanSurfaceCount`: `4 -> 1`
- `fillCoherenceRiskSurfaces`: `1 -> 0`
- `stitchCount`: `11664 -> 11612`
- `jumpCount`: `86 -> 86`
- `trimCount`: `14 -> 14`
- quality stayed `100`
- same-surface long spans, stitched long spans, untrimmed jump long spans, high-risk surfaces, and broad-route-risk surfaces stayed `0`

Validation and reports:

- Targeted diagnostic comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_teapot_satin_local_patch_20260628.html`
- Full source-color comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_satin_local_patch_20260628.html`
- Uploaded strict source policy: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_satin_local_patch_20260628`
- Uploaded comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_satin_local_patch_20260628.html`
- Generated strict acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_satin_local_patch_20260628`
- Generated comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_satin_local_patch_20260628.html`
- Full underpaint benchmark: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_benchmark_satin_local_patch_20260628`
- Underpaint comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_satin_local_patch_20260628.html`
- Combined source triage: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_satin_local_patch_20260628/source-triage.html`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`

Next recommended direction:

- Continue source/color behavior work, but stop mining teapot unless the next change visibly improves output beyond the now-cleared fill-coherence issue. Best next target is a real uploaded/generated fixture with semantic color loss, same-hue material collapse, or stubborn over-fragmented detail that survives current guards.

## 2026-06-28 — Dark Repeated Detail Policy Diagnostics

Target: `muted_sage_detail_badge`.

Change accepted:

- Added uploaded fixture coverage for a small sage semantic detail that ordinary thread snapping converted to neutral grey.
- Added optional `prefer_chromatic` thread matching and gated it from `_posterize` only for small mid-tone low-chroma labels.
- Strict uploaded source policy now requires `#1ea096` for the sage detail, rejects `#808080`, and requires tiny/detail accounting.

Before/after:

- Probe baseline colors: `['#808080', '#ffc88c', '#000000']`
- Accepted colors: `['#ffc88c', '#1ea096', '#000000']`
- `stitchCount`: `4147`
- `jumpCount`: `26`
- `trimCount`: `2`
- quality stayed `100`
- same-surface stitched/untrimmed long-span, high-risk, and broad-route-risk gates stayed `0`
- Existing uploaded fixtures stayed stable after narrowing the gate; `thick_outline_flower` stayed `6113 / 53 / 7`.
- Full generated, source-color, and underpaint comparisons had no existing-case metric/color changes.

Validation and reports:

- Uploaded strict source policy: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_muted_sage_snap_20260628`
- Uploaded comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_muted_sage_snap_20260628.html`
- Generated strict acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_muted_sage_snap_20260628`
- Generated comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_muted_sage_snap_20260628.html`
- Source-color strict acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_acceptance_muted_sage_snap_20260628`
- Source-color comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_muted_sage_snap_20260628.html`
- Full underpaint benchmark: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_benchmark_muted_sage_snap_20260628`
- Underpaint comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_muted_sage_snap_20260628.html`
- Triage review: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_muted_sage_snap_20260628/source-triage.html`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`

Rejected/narrowed variant:

- The first luminance gate converted a dark outline/halo label in `thick_outline_flower` into brown and changed metrics. Raising the gate to mid-tones restored the accepted baseline.

Next recommended direction:

- Find another visible source/color behavior gap, preferably same-hue over-fragmentation or semantic color loss outside the new sage lane. Keep strawberry/teapot as guards unless output visibly improves.

Target: `real_strawberry`.

Change accepted:

- Generated acceptance now includes tiny/detail policy fields, matching uploaded-art acceptance.
- The strawberry source-color guard now requires the black seed field to be planner-accounted as compact repeated detail.
- The planner can classify compact dark detail islands inside the accent/outline label without promoting the broad black outline.
- Uniform repeated fields no longer take an extra detail-budget penalty just because their compact details are explicitly promoted.

Before/after:

- `real_strawberry` `tinyPolicyPromotedCompactCount`: absent in old generated summary fields -> `30`
- `tinySourceDetailDecisionCounts`: now includes `repeated_compact_detail: 30`
- `stitchCount`: `7369 -> 7369`
- `jumpCount`: `65 -> 65`
- `trimCount`: `3 -> 3`
- quality stayed `100`
- same-surface stitched/untrimmed long-span, high-risk, and broad-route-risk gates stayed `0`

Validation and reports:

- Source-color strict acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_acceptance_dark_repeat_policy_20260628`
- Source-color comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_dark_repeat_policy_20260628.html`
- Uploaded strict source policy: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_art_acceptance_dark_repeat_policy_20260628`
- Uploaded comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_dark_repeat_policy_20260628.html`
- Generated strict acceptance: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_acceptance_dark_repeat_policy_20260628`
- Generated comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_dark_repeat_policy_20260628.html`
- Full underpaint benchmark: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_benchmark_dark_repeat_policy_20260628`
- Underpaint comparison: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_dark_repeat_policy_20260628.html`
- Triage review: `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_next_source_color_20260628/source-triage.html`
- `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`
- `npm run typecheck`

Rejected next targets:

- `real_teapot_card`: dropped pale green is a low-value tonal highlight; preserving it would likely add thread/color complexity without improving the preview.
- `leaf_single_smooth`: dropped gray/near-white layers are halo/fabric texture.
- `tiny_detail_icon`: excess-dot simplification is intentional and guarded.

Next recommended direction:

- Find or add a realistic generated/uploaded source fixture with visible semantic color/detail loss. The next source/color backend change should improve output, not only diagnostics.
