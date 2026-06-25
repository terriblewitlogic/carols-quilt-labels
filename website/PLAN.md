# Embroidery.mom — Website Implementation Plan

## Color Palette (extracted from logo)

| Token | Hex | Usage |
|---|---|---|
| `--color-cream` | `#FAF5EE` | Page backgrounds |
| `--color-cream-dark` | `#F0E8DC` | Section backgrounds, cards |
| `--color-teal` | `#7AADA0` | Primary brand, links, outlines |
| `--color-teal-dark` | `#5C9080` | Hover states |
| `--color-coral` | `#F07868` | Primary CTAs, accents |
| `--color-coral-dark` | `#D65E4E` | Hover states |
| `--color-brown` | `#8B5830` | Headings, logo wordmark |
| `--color-brown-dark` | `#5C3A20` | Deep heading color |
| `--color-green` | `#52826A` | ".mom" script accent, success |
| `--color-gold` | `#C49660` | Decorative stars, highlights |
| `--color-pink` | `#F4B8B0` | Soft badges, accents |
| `--color-text` | `#3D2B1A` | Body text |
| `--color-text-muted` | `#7A6050` | Secondary / helper text |
| `--color-border` | `#E8DDD2` | Dividers, card borders |

## Typography

- **Headings:** Playfair Display (Google Fonts) — elegant serif matching the wordmark
- **Body/UI:** Inter (Google Fonts) — clean, readable sans-serif
- **Logo/Brand text:** Dancing Script (Google Fonts) — script matching the logo

## Architecture

### Project location
`website/embroidery-mom/` — standalone Vite + React SPA, separate from the label maker tool codebase. In a later phase the label maker tool will be embedded/linked from here.

### Routing (React Router v6)

| Path | Page | MVP Phase |
|---|---|---|
| `/` | Home | 1 |
| `/label-maker` | Label Maker (tool shell) | 1 |
| `/free-embroidery-files` | Library index | 1 |
| `/free-embroidery-files/:category` | Library by category | 1 |
| `/free-embroidery-files/:category/:slug` | Design detail | 1 |
| `/file-of-the-day` | Daily free file | 1 |
| `/pricing` | Pricing | 1 |
| `/login` | Login | 1 |
| `/signup` | Sign up | 1 |
| `/account` | Account dashboard | 1 |
| `/generator` | Custom file generator | 2 |
| `/learn` | Learn hub | 2 |
| `/learn/:slug` | Learn article | 2 |

### State architecture

- **AuthContext** — user session, subscription tier (`free` / `hobby` / `maker` / `seller`)
- **CreditsContext** — credit balance and spend/earn actions
- All API calls abstracted behind `src/api/` client modules (stubs in Phase 1, real calls in Phase 2)

### Component hierarchy

```
App (BrowserRouter + AuthContext + CreditsContext)
├── Nav                      — sticky, all pages
├── <Routes>
│   ├── HomePage
│   ├── LabelMakerPage       — tool shell (embeds QuiltLabelMaker in Phase 2)
│   ├── LibraryPage          — design grid with category nav
│   ├── LibraryDetailPage    — single design + DownloadGate
│   ├── FileOfDayPage        — featured design + countdown + email capture
│   ├── GeneratorPage        — mode selector + template picker + preview area
│   ├── PricingPage          — 5-tier pricing table
│   ├── LearnPage            — article index
│   ├── LoginPage            — auth form
│   ├── SignupPage           — auth form
│   └── AccountPage         — user dashboard
└── Footer                   — sitemap, all pages
```

### Shared components

| Component | Description |
|---|---|
| `Button` | Variants: primary (coral), secondary (teal), ghost. Sizes: sm/md/lg. `as` prop for router Link. |
| `DesignCard` | Thumbnail + title + stitch count + hoop size + format badges. Links to detail page. |
| `DownloadGate` | Modal: ad-watch / credit-spend / subscribe flow |
| `CategoryNav` | Horizontal scroll pill nav for library categories |
| `PricingCard` | Tier display with feature list and CTA |
| `CreditMeter` | Nav credit balance chip (shown when logged in) |

### Data layer

Static mock data in `src/data/` during Phase 1. Each file mirrors the eventual API response shape so the swap in Phase 2 is a one-liner replacing the import with a fetch call.

- `library-catalog.js` — design entries with category, slug, metadata
- `learn-articles.js` — article stubs with category, slug, excerpt
- `generator-templates.js` — template definitions (pet patch, quilt label, etc.)

### API client stubs (`src/api/`)

| File | Methods |
|---|---|
| `label.js` | `generatePreview()`, `exportLabel()` |
| `library.js` | `getDesigns()`, `getDesign()` |
| `generator.js` | `generateImage()`, `convertToStitches()`, `exportFile()` |
| `account.js` | `login()`, `signup()`, `logout()`, `getUser()` |

## File structure

```
website/embroidery-mom/
├── package.json
├── vite.config.js
├── index.html
├── public/
│   └── logo.png
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── styles/
    │   ├── tokens.css
    │   └── global.css
    ├── context/
    │   ├── AuthContext.jsx
    │   └── CreditsContext.jsx
    ├── hooks/
    │   ├── useAuth.js
    │   └── useCredits.js
    ├── api/
    │   ├── label.js
    │   ├── library.js
    │   ├── generator.js
    │   └── account.js
    ├── data/
    │   ├── library-catalog.js
    │   ├── learn-articles.js
    │   └── generator-templates.js
    ├── components/
    │   ├── Nav.jsx + Nav.module.css
    │   ├── Footer.jsx + Footer.module.css
    │   ├── Button.jsx + Button.module.css
    │   ├── DesignCard.jsx + DesignCard.module.css
    │   ├── DownloadGate.jsx + DownloadGate.module.css
    │   ├── CategoryNav.jsx + CategoryNav.module.css
    │   ├── PricingCard.jsx + PricingCard.module.css
    │   └── CreditMeter.jsx + CreditMeter.module.css
    └── pages/
        ├── HomePage.jsx + HomePage.module.css
        ├── LabelMakerPage.jsx + LabelMakerPage.module.css
        ├── LibraryPage.jsx + LibraryPage.module.css
        ├── LibraryDetailPage.jsx + LibraryDetailPage.module.css
        ├── FileOfDayPage.jsx + FileOfDayPage.module.css
        ├── GeneratorPage.jsx + GeneratorPage.module.css
        ├── PricingPage.jsx + PricingPage.module.css
        ├── LearnPage.jsx + LearnPage.module.css
        ├── LoginPage.jsx + LoginPage.module.css
        ├── SignupPage.jsx + SignupPage.module.css
        └── AccountPage.jsx + AccountPage.module.css
```

## Implementation phases

### Phase 1 — Shell (this session)
- Project scaffolding (Vite + React Router + Google Fonts)
- Design tokens + global styles
- Nav + Footer
- All pages as complete UI shells with real copy, mock data, placeholder imagery
- Auth + Credits context stubs
- API client stubs

### Phase 2 — Plumbing
- Wire LabelMakerPage to existing `api/` Python functions
- Wire GeneratorPage to `api/generate.py` + `api/image_to_jef.py`
- Ad-gate modal real ad integration
- Auth (Supabase or Clerk)
- Credit purchase (Stripe)

### Phase 3 — Live data
- Library: real design file database (Supabase or PlanetScale)
- File of the Day: scheduled rotation (Vercel cron)
- Generator: full credit-gated AI flow
- SEO: meta tags, sitemap, OG images, structured data

## Monetization flow (reference)

```
Anonymous user:   Browse → Preview → Download gate → Watch ad OR create account
Free user:        Browse → Preview → Watch ad → Download
Credit user:      Browse → Preview → Spend credit → Instant download
Subscriber:       Browse → Preview → Instant download (no gate)
```

## Key build-to metrics

- Visitor → label started
- Label started → preview generated
- Preview generated → download clicked
- Download clicked → ad completed / credit used / subscription started
- Free library page → download clicked
- File of day page → email signup
- Generator started → export completed
