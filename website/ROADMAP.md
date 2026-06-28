# Embroidery.mom — Product Roadmap

## Overview

The build is structured in four phases, each shipping a meaningful slice of the product.

| Phase | Name | Status | Goal |
|---|---|---|---|
| 1 | Shell | ✅ Complete | Full React + Vite site with all pages, design system, and mock data |
| 2 | Plumbing | 🔜 Next | Wire tools to real APIs, add auth and payments |
| 3 | Live data | — | Real design library, email, file-of-day scheduling |
| 4 | Growth | — | SEO, seller workflows, batch tools, API access |

---

## Phase 1 — Shell ✅

**Goal:** A structurally complete website that can be previewed, shared, and iterated on before any backend work.

### What was built

- **Design system** — CSS custom properties from logo colors, Playfair Display / Inter / Dancing Script fonts, full spacing/radius/shadow token set
- **Auth + Credits context** — `AuthContext` (user, tier, login/logout) and `CreditsContext` (balance, spend, earn) — stubs, ready to swap for real backends
- **API client stubs** — `src/api/label.js`, `library.js`, `generator.js`, `account.js` — each method has the right signature and returns mock data shaped to match the eventual real response
- **Mock data** — 12 library designs, 8 learn articles, 6 generator templates
- **8 shared components** — Nav, Footer, Button, DesignCard, DownloadGate, CategoryNav, PricingCard, CreditMeter
- **11 pages** — Home, Label Maker, Library, Library Detail, File of the Day, Generator, Pricing, Learn, Login, Signup, Account

### Dev server
```
cd website/embroidery-mom
npm run dev   # runs on port 5200
```

---

## Phase 2 — Plumbing 🔜

**Goal:** Every button in the UI does something real. A user can sign in, generate a label, download a file, buy credits, and subscribe.

### 2A — Label Maker wiring — ⚠️ SUPERSEDED

> **See `website/ttf-lettering-plan.md`.** The June 2026 stitch-engine campaign made
> arbitrary TTF letterforms satin-stitch professionally (the original pivot blocker —
> limited fonts — is gone). The Label Maker now ships as client-rendered TTF text fed
> through the same `/convert` endpoint as the Generator. The section below describes the
> pre-pivot approach and is kept for history only.

**What to do (historical):** Connect `LabelMakerPage.jsx` to the existing Python API functions.

The existing tool lives in `src/embroidery.jsx` and `src/image-embroidery/`. The Phase 2 job is to either:
- (a) Embed the existing `QuiltLabelMaker` component directly into `LabelMakerPage.jsx` by importing it, or
- (b) Route `/label-maker` to the existing React component and wrap it in the new Nav/Footer shell

The API already exists:
- `api/generate.py` — Gemini image generation (Vercel serverless)
- `api/export.py` — exports stitch file in requested format
- `api/preview.py` — returns stitch preview image

**Files to update:**
```
src/api/label.js          ← replace stubs with real fetch() calls
src/pages/LabelMakerPage.jsx  ← wire Generate Preview and Download buttons
```

**API call shapes (match existing Python handlers):**
```js
// Generate preview
POST /api/generate
{ text, font, size, border, hoopSize }
→ { previewUrl, stitchCount, colors }

// Export file
POST /api/export
{ text, font, size, border, hoopSize, format }
→ base64 file blob
```

---

### 2B — Image Generator wiring

**What to do:** Connect `GeneratorPage.jsx` to the existing AI generation pipeline.

Existing endpoints:
- `api/generate.py` — calls Gemini to produce an image from a prompt
- `api/posterize.py` — simplifies image into flat color zones
- `api/image_to_jef.py` — converts posterized image to stitch file
- `api/preview.py` — generates stitch preview PNG

**Files to update:**
```
src/api/generator.js          ← replace stubs
src/pages/GeneratorPage.jsx   ← wire each step of the flow
```

**Generation flow to implement:**
```
1. User enters prompt or selects template + fills fields
2. POST /api/generate → returns imageUrl
3. Display image in preview area
4. POST /api/posterize { imageUrl, numColors } → returns posterizedUrl
5. POST /api/image_to_jef { imageUrl, hoopSize } → returns stitchPreviewUrl + JEF blob
6. Display stitch preview
7. Download button exports the file (deduct credits)
```

**Credit deduction:** Call `useCredits().spend(creditsNeeded)` before triggering the export. If `spend()` returns false (insufficient balance), show the credit purchase prompt instead.

**Backend quality checkpoint — 2026-06-27:** the stitch backend now has source-color acceptance lanes for real generated art before this is exposed to users. `real_strawberry` is accounted as intentional compact repeated detail, `real_teapot_card` is kept as a source-complexity guard with `4` retained multi-component colors / `22` disconnected retained pieces, `thick_outline_flower` now treats pruned gray outline antialiasing as sparse halo residue instead of semantic color loss, and `tiny_detail_icon` now treats multi-color compact dots as intentional source motifs (`candidate 88 -> clean 100`, repair opportunities `1 -> 0`) while preserving stitch output. Recent visible output wins reduced broad dark outline density, cleaned simple local material fills, reduced repeated seed-field overpacking, and tightened teapot-like local material panels without guarded risk regressions: `real_teapot_card` stitches `13541 -> 11761 -> 11711 -> 11664`, `thick_outline_flower` `6952 -> 6122 -> 6113`, `cartoon_elephant` `5725 -> 5191`, `sparrow_flat_app_icon` `5488 -> 5483`, and `real_strawberry` `7549 -> 7369` with trims `4 -> 3` and preserved colors. Strawberry source diagnostics now also avoid double-counting the compact seed field as generic fragmented line-art repair pressure (`sourceRepairOpportunities 1 -> 0`) while leaving the real many-region warning intact. Teapot source triage now also accounts its handled local material panels (`9` panels, `5` serpentine), moving it from `C / source_art_complexity` to `B / mostly_ok` with stitch output unchanged at `11664` stitches, `86` jumps, `14` trims, quality `100`, and preserved green/coral/purple/peach/black colors. The previous teapot output win kept jumps `86`, trims `14`, quality `100`, and all same-surface stitched/untrimmed long-span, high-risk, and broad-route-risk gates unchanged; the generic `70mm^2` local-patch gate and a too-aggressive `1.12` local-cluster density multiplier were rejected. Validation included `PYTHONPYCACHEPREFIX=tmp/pycache npm run check:python`, `npm run typecheck`, targeted source/color canaries, full uploaded strict source policy, full generated acceptance, full source-color acceptance, full underpaint benchmark, and regression-gated comparisons. Current validation artifacts:

- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_color_compare_local_detail_cluster_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_local_detail_cluster_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/generated_compare_local_detail_cluster_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/underpaint_compare_local_detail_cluster_20260627.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/source_art_triage_sparse_halo_policy_20260627/source-triage.html`
- `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/tmp/uploaded_compare_sparse_halo_policy_20260627.html`
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

Do not treat Generator wiring as real-user-ready until source/color triage has more accepted behavior wins, not just diagnostics.

---

### 2C — Authentication

**Provider recommendation:** Supabase Auth (free tier covers MVP scale, integrates with Supabase DB for Phase 3).

**What to implement:**

1. Install: `npm install @supabase/supabase-js`
2. Create `src/lib/supabase.js`:
   ```js
   import { createClient } from '@supabase/supabase-js'
   export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
   ```
3. Replace `AuthContext.jsx` login/signup/logout with real Supabase calls:
   ```js
   const { data, error } = await supabase.auth.signInWithPassword({ email, password })
   ```
4. Add Google OAuth (Supabase supports it with two config lines)
5. Persist session across page reloads using `supabase.auth.onAuthStateChange()`

**Files to update:**
```
src/context/AuthContext.jsx   ← replace mock login/signup with Supabase
src/api/account.js            ← replace stubs
src/pages/LoginPage.jsx       ← enable Google button
src/pages/SignupPage.jsx      ← enable Google button
```

---

### 2D — Credit purchase (Stripe)

**What to implement:**

Stripe Checkout is the fastest path — no custom payment UI needed.

1. Create a Vercel serverless function `api/create-checkout.py` (or `.js`):
   ```
   POST /api/create-checkout
   { packId, userId }
   → { checkoutUrl }
   ```
2. Redirect user to Stripe-hosted checkout page
3. On success, Stripe webhook → `api/webhook.py` → update credit balance in DB
4. Credit balance stored in Supabase `credit_balances` table, read on login

**Credit pack IDs** (already defined in `src/data/generator-templates.js`):
```
pack-5   → $3   → 5 credits
pack-20  → $9   → 20 credits
pack-60  → $19  → 60 credits
pack-150 → $39  → 150 credits
```

**Subscription plans** (map to Stripe Price IDs):
```
hobby  → $9/mo  → 30 credits on renewal
maker  → $19/mo → 100 credits on renewal
seller → $39/mo → 300 credits on renewal
```

**Files to create/update:**
```
api/create-checkout.py        ← new Vercel function
api/webhook.py                ← Stripe webhook handler
src/context/CreditsContext.jsx ← read balance from DB, not local state
src/pages/AccountPage.jsx     ← wire "Buy credits" buttons to checkout
src/pages/PricingPage.jsx     ← wire "Start plan" buttons to Stripe
```

---

### 2E — Download gate (real ad integration)

The `DownloadGate` modal already has the full UI shell including an ad progress bar animation. Phase 2 replaces the `setTimeout` simulation with a real rewarded ad network.

**Recommended provider:** Google AdSense rewarded ads or a specialist like Playwire (better CPM for niche craft content).

**Integration points in** `src/components/DownloadGate.jsx`:
```js
// Replace the setTimeout in handleAd() with:
window.adProvider.showRewardedAd({
  onComplete: () => setAdState('done'),
  onSkip: () => setAdState('idle'),
})
```

For users with ad blockers: the current UI already shows the credit/subscribe options as fallback — no extra work needed.

---

### Phase 2 checklist

```
[ ] 2A  Label Maker wiring → real generate + export API calls
[x] 2B  Generator wiring → generate → posterize → stitch → export  (DONE — GeneratorPage
        calls generateImage + convertImageBase64ToStitches against the Vercel stitch API;
        previews default to thread-realistic style)
[ ] 2C  Auth → Supabase email + Google OAuth
[ ] 2D  Payments → Stripe Checkout for credits + subscriptions
[ ] 2E  Stripe webhook → credit balance in DB
[ ] 2E  Download gate → real rewarded ad SDK
[ ] 2F  Email capture → save to Supabase, trigger welcome email (Resend or Postmark)
[ ] 2G  Account page → pull real credit balance + download history from DB
```

### Generator/stitch-engine status — 2026-06-27

Generator wiring is live enough for internal iteration, but the product is **not ready for real users**. The active work is still stitch-quality hardening for generated source art.

Recent backend/frontend progress:

- Simple connected generated icons with mild soft shading are accepted instead of blocked as “too detailed.”
- `gradient_elephant_simple` is now a regression fixture for this class.
- Tonal cleanup improved the gradient elephant output:
  - same-surface long spans `3 -> 0`
  - trims `8 -> 4`
  - jumps `14 -> 8`
  - stitches `6269 -> 5062`
- Large radial repeated motif routing improved `flower_sunflower_simple` trims `9 -> 7` without regressing `flower_daisy_simple`.
- Graph-aware component routing is now in the stitch engine for repeated/disconnected same-color islands; it compares nearest, angular, MST preorder, and 2-opt tours behind benchmark gates and records candidate diagnostics.
- Upload-style source/detail policy checks now expose tiny-detail accounting and guard against unresolved tiny decisions, lost accent colors, and detail-budget regressions.
- Upload-style tone/material policy checks now include a same-hue acorn fixture that preserves dark-brown, tan, and light tan thread colors.
- Same-hue faceted material stress coverage now preserves substantial darker end-members instead of flattening them into mid-tone facets.
- Same-hue light endpoint protection now preserves mushroom-like tan/light material regions instead of flattening them into dominant orange/pink body tones.
- Same-hue facet trim pressure now has acorn, mushroom, and shell stress fixtures; the accepted inter-component trim threshold is `16mm`, reducing `same_hue_acorn_facets` trims `11 -> 8` without long untrimmed jump diagnostics.
- Covered-travel routing now searches up to `35mm` only when later stitches prove the carry is hidden; `same_hue_acorn_facets` trims improved again `8 -> 7` with no actual-thread connector risk.
- Route fallback diagnostics now explain remaining same-hue acorn facet trims: exact small-cluster route candidates are scored, but the remaining `#a05a28` and `#c3915a` groups safely fall back to nearest because structural/no-flip underlay-sensitive surfaces block free reordering.
- Structural/no-flip-safe candidate routing is now active behind narrow gates:
  - explicit `same_hue_acorn_facets` trims `7 -> 6` and cross-surface trimmed long spans `3 -> 1`
  - generated/underpaint `sparrow_flat_app_icon` trims `3 -> 2`
  - default uploaded `thick_outline_flower` trims `7 -> 6`
- Structural safe-flip orientation scoring now compares legacy and reoriented safe flips during candidate routing:
  - `same_hue_mushroom_facets` preserves the tan material color while improving trims `7 -> 6` and same-surface trimmed long spans `1 -> 0`
  - `same_hue_acorn_facets` keeps the structural route win and improves trims `6 -> 5`
  - full generated, uploaded, and underpaint comparisons pass with `--fail-on-regression`
- Unsafe legacy structural safe-flip filtering now removes only safe-flip variants that create extreme internal underlay-to-cover handoffs:
  - `same_hue_shell_facets` same-surface trimmed long spans improved `1 -> 0`
  - jumps/trims stayed stable and broad generated/uploaded/underpaint comparisons had no top-line metric deltas
- Underpaint benchmark route coverage now includes:
  - `synthetic_component_route_ring` for plain disconnected-island candidate scoring and safe fallback
  - `synthetic_structural_route_facets` for structural-safe small-exact route wins
- Source/color quality grading now treats heavy source normalization as informational when it only removes noise and stitch/color diagnostics remain clean:
  - fresh uploaded/generated source-color baselines grade `A: 16`
  - `leaf_single_smooth` no longer appears as a false source-quality blocker after successful cleanup
- Default uploaded-art acceptance now includes `muted_accent_badge`:
  - protects soft lavender, soft pink, blue fill, and black linework under strict source-policy checks
  - requires muted-accent tiny-detail accounting
  - new source-color triage result is `A: 17`, with the new case at quality `100`
- Real source/color fixture lane added:
  - `npm run acceptance:source-color`
  - `real_teapot_card` and `real_strawberry` preserve key color families but remain C/C+ source-complexity targets for future compiler work
- Compact repeated-detail source accounting now recognizes strawberry-like seed fields as intentional motif repeats:
  - `real_strawberry` triage improved `C+ -> B`
  - motif-aware adjusted components improved to `20` while stitch output stayed unchanged
  - `real_teapot_card` remains the main source-complexity target
- Stitched near-white foreground accounting now treats preserved pale regions as accounted source evidence:
  - `bee_simple`, `flower_daisy_simple`, and `low_contrast_bird` repair opportunities improved `1 -> 0`
  - stitch output and route-risk metrics stayed unchanged
- Added generated-run HTML comparison tooling:
  - `/Users/partido/jeflabelmaker/website/embroidery-stitch-backend/scripts/compare_generated_runs.py`
  - `npm run compare:generated`

Current generator/stitch backlog:

- find a visible source/color behavior improvement rather than another diagnostic-only cleanup
- use `real_teapot_card` as the next source-complexity target only if a source simplifier can reduce disconnected color pieces without losing intended colors
- expand tone/color preservation fixtures with real generated/uploaded examples, especially remaining same-hue endpoint, trim, and fragmentation cases
- preserve meaningful accent colors without preserving noisy fragments, using strict source-policy checks; muted lavender/pink and compact repeated-detail guard coverage are now in place
- keep route broadening paused unless comparison reports show real stitched-span or same-surface relocation regressions
- keep future route broadening behind the new disconnected-island fixture gates plus daisy/sunflower/elephant/cutout benchmarks
- keep using generated-run comparison reports before accepting algorithm changes

---

## Phase 2H — Operational hardening (before payments go live)

**Goal:** The public API surface cannot generate surprise bills, melt the container, or get
quietly abused. This is a launch gate for Phase 2D (payments): never charge money on top of
an unprotected cost surface.

**Infrastructure reality:** `embroidery.mom` is a Cloudflare Worker (`embroidery-mom`)
serving the SPA + proxying `/api/generate` (Imagen/Gemini — the expensive call) and
`/api/stitch` (service binding → `embroidery-stitch-backend` Worker + Container,
max_instances 10). Deploys are manual `wrangler deploy`; backend CI runs checks only.

### Cost controls (highest priority — Gemini/Imagen is metered)
- [ ] Per-IP daily cap on `/api/generate` (KV counter; e.g. 10/day anon) returning a
      friendly "come back tomorrow / sign in" payload the UI can render
- [ ] Global daily generation budget kill-switch (KV counter + `DISABLE_GENERATE` var
      checked by the worker; flipping it degrades to upload-only mode, site stays up)
- [ ] Provider-side billing alerts (Google Cloud budget alert on the Gemini key;
      hard cap if the console supports it)
- [ ] Verify `GEMINI_API_KEY` lives in `wrangler secret` (not `[vars]`, not the repo)

### Rate limiting & abuse
- [ ] Cloudflare WAF rate rules: `/api/generate` strict (e.g. 6/min/IP),
      `/api/stitch` moderate (e.g. 20/min/IP), everything else default
- [ ] Origin/Referer check in the worker for `/api/*` (cheap pre-auth abuse filter;
      returns 403 for cross-site callers)
- [ ] Worker-level 429 with `Retry-After` when the container queue is saturated
      (the conversion can take 10-60s; backpressure beats pile-up)

### Payload & runtime guards
- [ ] Reject `imageBase64` over ~4MB and hoop dims outside 30-300mm before touching
      the container (fast 400s in the worker)
- [ ] Tighten `STITCH_BACKEND_TIMEOUT_MS` (currently 420s) to ~120s once the new
      engine's p95 is measured in production; the converter already emits per-phase
      timings in `metrics.phaseTimings` — log them
- [ ] Container request concurrency cap + memory ceiling review (max_instances=10 is
      the only guard today)

### Observability & rollback
- [ ] Workers Logs / Logpush on both workers; alert on error-rate spike and on
      conversion p95 regression
- [ ] Track daily: generations, conversions, failures by phase (the converter's
      `current_phase` error tagging makes this cheap)
- [ ] Practice `wrangler rollback` once; document the two-command rollback in this file
- [ ] Synthetic check: tiny conversion hitting prod every 15min (UptimeRobot/cron Worker)

### Checklist gate
Phase 2D (Stripe) does not start until every box above is checked.

---

## Phase 3 — Live data

**Goal:** The design library is real, the File of the Day rotates automatically, and SEO is generating organic traffic.

### 3A — Design library database

Store actual embroidery files and metadata in Supabase.

**`designs` table schema:**
```sql
id            uuid primary key
slug          text unique not null
category      text not null
title         text not null
description   text
stitch_count  int
hoop_size     text
colors        int
difficulty    text   -- beginner | intermediate | advanced
formats       text[] -- ['PES', 'DST', 'JEF']
thread_colors text[]
suggested_fabric text
preview_url   text   -- hosted on Supabase Storage or Cloudflare R2
file_urls     jsonb  -- { PES: 'url', DST: 'url', ... }
is_free       bool default true
credit_cost   int default 0
created_at    timestamptz default now()
```

Replace `src/api/library.js` stubs with Supabase queries:
```js
export async function getDesigns(category) {
  const q = supabase.from('designs').select('*')
  if (category && category !== 'all') q.eq('category', category)
  const { data } = await q
  return data
}
```

**File hosting:** Store the actual `.pes`, `.dst`, `.jef` files in Supabase Storage (or Cloudflare R2 for cheaper egress). Generate signed URLs at download time so files aren't publicly indexable.

---

### 3B — File of the Day scheduling

**`daily_files` table:**
```sql
id              uuid primary key
design_id       uuid references designs(id)
date            date unique not null
download_count  int default 0
subscriber_claims int default 0
ad_unlock_count int default 0
```

**Rotation:** A Vercel Cron job runs at midnight and inserts the next day's entry. Alternatively, pre-schedule a month at a time from the admin.

**`/file-of-the-day` API call:**
```
GET /api/file-of-day
→ { design, expiresAt }
```

---

### 3C — Email

Use **Resend** (simple API, generous free tier) or **Postmark**.

Triggered emails to build:
- Welcome email on signup
- Daily file notification (opt-in, from the email capture form)
- Credit purchase receipt
- Subscription confirmation and renewal

**Email capture** is already wired in `FileOfDayPage.jsx` and `HomePage.jsx` — Phase 3 just sends the form data to `POST /api/subscribe` instead of logging it.

---

### 3D — SEO foundations

Each design detail page, library category page, and learn article already has the right URL structure from Phase 1. Phase 3 adds:

1. **Dynamic `<title>` and `<meta description>`** per page — use `react-helmet-async` or move to a framework with native SSR (see below)
2. **`sitemap.xml`** — generated at build time from the Supabase design catalog
3. **`robots.txt`** — allow all, point to sitemap
4. **OpenGraph images** — one per design (Vercel OG or Cloudinary auto-generate from the stitch preview)
5. **Structured data** — `Product` schema on design detail pages for Google Shopping
6. **Framework consideration:** React SPA is bad for SEO. Phase 3 should evaluate migrating to **Next.js** or **Astro** for SSR/SSG on public pages. The component and design system are already portable — it would be a routing + rendering change, not a rewrite.

---

### Phase 3 checklist

```
[ ] 3A  Supabase designs table + file storage
[ ] 3A  Replace library API stubs with real Supabase queries
[ ] 3A  Signed download URLs (files not publicly accessible)
[ ] 3B  daily_files table + Vercel Cron rotation
[ ] 3C  Email: Resend integration for welcome + daily file notifications
[ ] 3D  react-helmet-async for dynamic page titles and meta
[ ] 3D  sitemap.xml generation at build
[ ] 3D  OG images per design
[ ] 3D  Evaluate Next.js or Astro migration for SSR/SEO
```

---

## Phase 4 — Growth

**Goal:** Seller-grade workflows, commercial licensing, API access, and the content/SEO engine running at scale.

### 4A — Seller workflows

- **Batch label generation** — upload a CSV of names, receive a ZIP of matching stitch files
- **Project folders** — organise saved designs into collections
- **Design variation sets** — generate a family of related designs from one template (e.g. 12 holiday ornament variations)
- **Etsy seller landing pages** — curated pages targeting search terms like "PES files for Etsy sellers"

### 4B — Commercial licensing

- Introduce a `license_type` field on designs: `personal` | `commercial-single` | `commercial-unlimited`
- Maker and Seller plan users get commercial-friendly access
- Generate a PDF license certificate on commercial download

### 4C — API access

Power users (Etsy sellers, small studios) who want to automate file generation:
```
POST /v1/label      → generate a label file
POST /v1/generate   → AI generate from prompt
POST /v1/convert    → upload-to-stitch
GET  /v1/library    → search the design catalog
```

Rate-limited by API key, billed per credit. Seller plan includes a monthly API credit allowance.

### 4D — Content engine

The `learn/` section needs enough articles to generate meaningful long-tail organic traffic. Target is 50+ articles covering:
- Every major file format (PES, DST, JEF, EXP, VP3, HUS, XXX, VIP...)
- Every common machine brand (Brother, Janome, Singer, Husqvarna, Baby Lock, Bernina, Pfaff...)
- Technique guides (stabilizer types, thread tension, hooping, lettering, patches)
- Comparison pages (Brother vs Janome, PES vs DST, digitizing software comparisons)

Each article links back into the product (Label Maker, Library, Generator).

### 4E — Analytics and metrics

Instrument from day one, report weekly:

| Metric | Target (90 days post-launch) |
|---|---|
| Visitor → label started | > 25% |
| Label started → preview generated | > 60% |
| Preview → download clicked | > 40% |
| Download clicked → ad completed | > 50% |
| Download clicked → credit used | > 15% |
| Download clicked → subscription started | > 3% |
| Free library page → download clicked | > 20% |
| File of day page → email signup | > 10% |
| Credit purchase conversion (of visitors) | > 1% |
| Subscriber churn (monthly) | < 8% |

Recommended stack: **PostHog** (open source, self-hostable, free tier) for product analytics. **Plausible** or **Fathom** for privacy-friendly page views.

---

## Technical debt to address before Phase 3

| Item | Notes |
|---|---|
| SSR / framework migration | React SPA with client-side routing is not indexable by Google. Evaluate Next.js or Astro before the content/SEO push. |
| Error boundaries | Add React error boundaries around each page so one broken component doesn't crash the whole app. |
| Loading states | All API calls need skeleton loading UI, not just spinner-on-button. |
| Accessibility audit | Nav keyboard trap, modal focus management, ARIA labels — do a full a11y pass before public launch. |
| Rate limiting | All API endpoints need rate limiting before the free tier is public (prompt injection, abuse). |
| File size validation | Upload-to-stitch endpoint needs server-side file type and size validation. |
| Environment variables | `GEMINI_API_KEY` and Supabase/Stripe keys need to be in Vercel environment settings, not committed. |

---

## Dependencies map

```
Phase 1 (done)
    ↓
Phase 2A (Label Maker wiring) ← no new dependencies, uses existing Python API
Phase 2B (Generator wiring)   ← no new dependencies, uses existing Python API
Phase 2C (Auth)               ← Supabase
Phase 2D (Payments)           ← Stripe
Phase 2E (Ads)                ← ad network SDK
    ↓
Phase 3A (Library DB)         ← requires Supabase (2C)
Phase 3B (Daily file cron)    ← requires Supabase (2C)
Phase 3C (Email)              ← requires auth (2C) + Resend/Postmark
Phase 3D (SEO)                ← independent, but more valuable after 3A
    ↓
Phase 4 (Growth)              ← requires all of Phase 3
```

The cleanest Phase 2 order: **2C (auth) → 2D (payments) → 2A (label wiring) → 2B (generator wiring) → 2E (ads)**. Auth and payments first because they're the dependency for everything else.

---

## Stitch Backend Checkpoint — 2026-06-28

Recent backend-only source/color tooling improvement:

- Uploaded-art acceptance now includes source color layers, segmentation colors, dropped colors, and segmentation component counts in `summary.json`.
- Uploaded strict source policy now checks generic source color-family preservation, not only named fixture colors.
- No public API, frontend, or stitch file-format change.

Validated with full uploaded strict source policy, generated strict acceptance, underpaint benchmark, regression-gated comparisons, Python checks, and TypeScript typecheck.

Next stitch work: add or identify a real generated/uploaded fixture with semantic color loss or over-fragmentation, then make a narrow source compiler fix.
