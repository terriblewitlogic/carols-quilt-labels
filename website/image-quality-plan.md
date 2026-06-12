# Image Quality Plan — From "Sews Cleanly" to "Shippable"

**Status:** Draft for review · 2026-06-11
**Trigger:** Generated designs scored q100 mechanically while being visibly unshippable
(washed fills, lost details, mangled regions). The instruments measured sewability, not
appearance, and progress reports overstated quality. This plan fixes the instruments, the
process, and the improvement loop.

---

## 1. Composite rating system (keep mechanical, add visual)

The existing gates stay — they protect real things:

| Existing gate | What it protects | Keep as |
|---|---|---|
| Engine quality score | sewability risks (webbing, fragments, travel) | hard floor ≥ 96 |
| Hatch-likeness | professional stitch statistics vs reference designs | floor ≥ 90 |
| Format regression | all 6 formats encode correctly | zero errors |

New visual components (in `scripts/visual_fidelity.py`, v1 built and calibrated):

| Component | What it catches | v1 status |
|---|---|---|
| colorFidelity | washed-out / wrong colors | ✅ built (caught washed fox at 0.50) |
| regionRecall | lost petals, dropped regions | ✅ built (caught broken sunflower at 0.37) |
| silhouetteIoU | shape mangling | ✅ built |
| **detailIntegrity** (v2) | face mush, small-feature fidelity — fine-grid scoring over detected small source regions (the 48×48 grid is too coarse for a 2mm eye) | to build |
| **partCount** (v2) | fragmentation/merging — per-color connected-component count, source vs stitched | to build |
| **fillSolidity** (v2) | background showing through solid regions | to build |
| **paletteAgreement** (v2) | 6 source colors collapsing to 4 threads | to build |

**Verdict shape:** a scorecard, not one number. `shippable = engine ≥ 96 AND hatch ≥ 90
AND fidelity ≥ 90 AND no critical defect flags`. Composite used only for ranking candidates.

**The verdict is owned, not outsourced.** Gates are assistants, not arbiters: they rank,
flag, and catch regressions, but the shippable call is made by eyes at full zoom against
the professional reference designs in `example files/` — the same bar a customer applies.
No rating sessions, no asking the user to grade slop: if a result needs a committee to
decide whether it's good, it isn't.

## 2. Testing process — never overstate quality again

1. **No quality claim without the scorecard + zoomed eyes.** Every reported result carries
   the full gate scorecard AND was reviewed at full resolution side-by-side with source.
   "Looks good" without numbers is banned from reports.
2. **Worst-crop rule.** Before presenting any result, find the most embarrassing zoom
   (faces, small details, edges) and present it proactively. The user should never be the
   one to discover the bad crop.
3. **Review page is the reporting medium.** Every round auto-publishes source / stitched /
   scorecard to the local review site. Claims reference what the user can see there.
4. **Production parity.** Test through the deployed conversion path with production
   settings (auto-tune on), not just the local handler — customers get the prod path.
5. **Preview honesty.** The preview is the customer's quality perception; it must neither
   flatter nor slander the file (thread-width fills fixed; fabric sew-out remains the
   final ground truth whenever machine time exists).

## 3. Fresh-image generalization loop (no more fixture overfitting)

The old loop optimized against 14 fixed fixtures — the engine got great at those images.
New loop, per iteration:

```
1. GENERATE a brand-new subject (rotating category list: animal, floral, food,
   seasonal, object, badge…) with the current prompt — never reuse last round's image
2. CONVERT through production path
3. SCORE with the full scorecard; review at zoom
4. TRIAGE the worst defect; tag it in the defect taxonomy
5. FIX the root cause (engine or prompt — diagnosis must say which)
6. REGRESS: fixed-fixture battery still passes (mechanical floor protected)
7. NEXT iteration: a totally different subject
```

- The fixed fixtures become a pure **regression suite** — they protect the floor, they are
  no longer the optimization target.
- Every fresh failure joins the **failure museum** (image + defect tags). The museum is
  re-run after fixes as a growing regression set — confirming fixes generalize — but never
  iterated on directly.

## 4. Additional objectives (proposed)

**4a. Source-side gate (separate prompt failures from engine failures).**
Score the *generated image* before conversion: flatness (posterize residual), region count
within budget, no gradients/AA halos, no rendered stitch texture. Bad sources get
regenerated, not converted — engine diagnosis stops being polluted by prompt slop, and
each failure is attributed to the right layer.

**4b. Defect taxonomy.**
Name the failure modes and tag every failure: `washout · region-loss · detail-mush ·
fragmentation · color-drift · counter-fill (holes) · mockup-source · overcomplex-source ·
solidity-gap`. Priorities then come from defect frequency across fresh generations —
data-driven engine roadmap instead of whack-a-mole.

**4c. Known engine defects already on the board.**
- Small-region color fidelity (fox face whites/oranges posterized into dark mush)
- Region topology: interior holes (counters, donuts, wreaths) lost before polygon stage —
  affects images, not just text
- Sunflower-class fragmentation of many-part designs

**4d. Multi-candidate generation in the product.**
Generate 2–3 candidates per user prompt, auto-score all, surface the best (or offer the
user the choice). Turns generation variance from a liability into a feature. Cost-bounded
by the per-image price; gate scores make the selection free.

**4e. Periodic fabric truth.**
When machine time exists: sew gate-passing designs, photograph, compare against preview.
Validates that the gate chain actually predicts fabric. Until then, every report carries
the caveat that fabric is unverified.

---

## Sequence

1. Fidelity gate v2 (detailIntegrity, partCount, fillSolidity, paletteAgreement) + scorecard runner
2. Source-side gate + defect taxonomy tagging
3. Fresh-image loop begins (v3 prompt, new subject each round, museum accumulates)
4. Engine fixes in defect-frequency order (small-region color, holes, fragmentation first candidates)
5. Multi-candidate selection lands in product once the gate chain is trusted
