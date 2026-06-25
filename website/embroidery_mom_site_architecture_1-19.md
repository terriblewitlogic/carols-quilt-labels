# Embroidery.mom Site Architecture

## Overview

This document captures the proposed site architecture for **Embroidery.mom**, assuming the product includes:

- Free text label generation with ad-gated download or subscription access
- A library of free embroidery machine files with ad-gated download or subscription access
- A free embroidery file of the day
- Dynamic custom file generation for subscribers
- Optional microtransactions via credits
- Subscriptions that provide a guaranteed monthly supply of credits at a steep discount

The goal is to create a site that feels like a useful embroidery utility first, not just a file dump.

**Core product promise:**

> Embroidery.mom helps you make, find, and download embroidery machine files quickly.

---

## 1. Home Page

The homepage should route people into the right job quickly.

### Hero

**Headline:**

> Make embroidery machine files without complicated software.

**Subhead:**

> Create text labels, download free designs, or generate custom embroidery-ready files for your machine.

### Primary calls to action

- **Make a Text Label**
- **Browse Free Designs**
- **Generate a Custom File**

### Homepage modules

#### A. Text Label Maker

> Create name labels, clothing tags, quilt labels, and simple text designs.

CTA: **Start a Free Label**

#### B. Free Embroidery Library

> Browse free designs ready for machine embroidery.

CTA: **Browse Free Files**

#### C. Free File of the Day

> Download today’s featured embroidery file.

CTA: **Get Today’s File**

#### D. Dynamic Generator

> Subscribers can generate custom files from templates, prompts, and simple artwork.

CTA: **Try the Generator**

#### E. Pricing strip

Simple framing:

```text
Free with ad view
Credits for one-off downloads
Subscription for unlimited/easier access
```

---

## 2. Label Maker

This is probably the strongest wedge. It is practical, easy to understand, SEO-friendly, and emotionally clear.

### URL structure

```text
/label-maker
/name-labels
/clothing-labels
/quilt-labels
/school-labels
/baby-blanket-labels
```

### Flow

```text
Choose label type
Enter text
Choose font/style
Choose size/hoop
Choose border/icon
Preview stitch file
Download
```

### Monetization

For non-subscribers:

```text
Free download after ad view
or
Use 1 credit
or
Subscribe for instant downloads
```

For subscribers:

```text
Instant downloads
Batch label generation
Saved projects
No ads
More fonts/styles
Commercial use if included
```

### Important feature: batch labels

Batch labels could be one of the strongest features.

Example:

```text
Enter:
Emma
Liam
Sophia
Noah

Generate matching labels for all names.
```

That is more valuable than a single text file.

### Label Maker feature tiers

#### Free

- Single text label
- Limited fonts
- Ad-gated download
- Limited file formats

#### Credit

- One-off export
- No ad
- More formats

#### Subscription

- Batch labels
- Saved presets
- All fonts/borders
- No ads
- Dynamic generation allowance

---

## 3. Free Embroidery File Library

This is the SEO and repeat-traffic engine.

### URL structure

```text
/free-embroidery-files
/free-embroidery-files/animals
/free-embroidery-files/flowers
/free-embroidery-files/holidays
/free-embroidery-files/baby
/free-embroidery-files/monograms
/free-embroidery-files/patches
/free-embroidery-files/labels
/free-embroidery-files/borders
```

Each file should have a detail page:

```text
/free-embroidery-files/daisy-heart-patch
/free-embroidery-files/cute-cat-face
/free-embroidery-files/simple-name-label-border
```

### File detail page contents

Each design page should include:

```text
Preview image
Stitch preview
Available formats
Hoop size
Thread colors
Stitch count
Difficulty
Suggested fabric
Download options
Related designs
```

### Download options

For free users:

```text
Watch ad to download
or
Use 1 credit
or
Subscribe for instant downloads
```

For subscribers:

```text
Download instantly
No ads
Save to library
```

### Why this matters

Free libraries create long-tail search pages. People search for very specific things:

```text
free flower PES file
free dog embroidery file
free name label embroidery design
free baby blanket embroidery pattern
free Christmas PES file
```

You want a page for every useful category and every design.

---

## 4. Free Embroidery File of the Day

This creates a daily habit without giving away the whole catalog.

### URL

```text
/file-of-the-day
```

### Mechanics

Every day:

```text
One free featured file
Ad-gated download for free users
Instant download for subscribers
Expires or rotates at midnight
Archive shown but gated
```

### User loop

Free user:

```text
Come back daily → watch ad → download file → build habit
```

Subscriber:

```text
Get daily file instantly → maybe email/push notification → higher perceived value
```

### Add email capture

This page should collect email:

> Get tomorrow’s free file in your inbox.

This creates a low-cost retention loop.

### Archive monetization

```text
Today’s file: free with ad view
Past daily files: subscriber or credit only
```

This creates urgency without feeling hostile.

---

## 5. Dynamic File Generation

This is the paid product.

Do not make this a generic “generate anything” tool at first. Make it template-driven and constrained.

### URL structure

```text
/generator
/ai-embroidery-generator
/custom-embroidery-file-generator
```

### Generator modes

#### A. Text-to-design

User enters:

```text
Cute daisy patch with the name Emma
```

The system generates artwork, simplifies it, converts it, and previews it.

#### B. Template generator

User chooses:

```text
Pet patch
School label
Baby blanket label
Floral monogram
Kitchen towel design
Christmas ornament
Quilt label
```

Then fills structured fields.

#### C. Upload-to-stitch

User uploads an image and gets:

```text
Cleaned preview
Reduced color version
Stitch preview
Export
```

#### D. Batch generator

For subscribers:

```text
Generate 20 name labels
Generate a family set
Generate Etsy-style variation set
```

This is more valuable than “one random AI file.”

---

## 6. Pricing / Monetization Architecture

The model should combine **ads, credits, and subscription**.

### Free user

Gets:

```text
Text label generation
Free library browsing
File of the day
Limited previews
Downloads after ad view
Limited daily downloads
```

Restrictions:

```text
Ad view required
Daily download cap
No batch generation
Limited formats/styles
Slower queue if needed
No saved project library
```

### Credit user

Buys credits for one-off use.

Credits can be spent on:

```text
Skip ad download
Premium library file
AI generation
Dynamic custom file
Batch export
Past file-of-the-day archive
```

Possible pricing:

```text
5 credits: $3
20 credits: $9
60 credits: $19
150 credits: $39
```

Avoid making every credit exactly equal to $1 psychologically. Let it feel like craft tokens.

### Subscriber

Subscription should be a **discounted supply of credits plus convenience**, not necessarily unlimited everything.

Unlimited AI generation can hurt margins.

#### Hobby Plan

```text
$9/month
No ads
30 credits/month
Instant free-library downloads
Daily file instant download
Saved projects
Batch labels up to X/month
```

#### Maker Plan

```text
$19/month
No ads
100 credits/month
Commercial-friendly license
Larger batch label generation
Priority generation
More formats/styles
```

#### Seller Plan

```text
$39/month
No ads
300 credits/month
Bulk/batch workflows
Commercial use
Early access to new templates
Possible API/export automation later
```

### Why this is better than unlimited

The subscription feels like a great deal, but you still control cost.

Position it this way:

> Subscribers get a monthly credit bundle at a steep discount, plus no ads and premium features.

That is much safer than:

> Unlimited AI embroidery generation.

---

## 7. Suggested Credit Costs

Credits should map to compute cost, perceived value, and support risk.

Example credit costs:

```text
Ad-skip library download: 1 credit
Text label export: 1 credit
Premium library file: 2 credits
Past file-of-day download: 2 credits
AI image generation preview: 1 credit
AI stitch-file export: 3–5 credits
Upload-to-stitch export: 2–4 credits
Batch label set: 5–20 credits depending on size
Large/dense design: higher credit cost
```

The product can show:

```text
This export uses 3 credits.
```

That gives you a pricing dial without constantly changing dollar prices.

---

## 8. Ad-Gated Download Architecture

Ads should not make the site feel cheap or untrustworthy.

### Good places for ads

```text
Free file download gate
Free file library pages
Tutorial/blog pages
File detail pages
After successful preview
```

### Bad places for ads

```text
In the middle of the editor
Before preview generation
During text entry
Every page load
```

The creation flow needs to feel trustworthy.

### Free download gate

Flow:

```text
Click Download
Choose format
Prompt: Watch a short ad or use 1 credit
Ad completes
Download unlocks
```

For users with ad blockers:

```text
Use 1 free daily credit
or
Create account
or
Subscribe
```

Do not let ad tech break the core experience.

---

## 9. User Account Architecture

Users should be able to do some things without an account, but downloads should push toward account creation.

### Anonymous user

Can:

```text
Browse
Preview
Try label maker
Try limited generator
```

Cannot:

```text
Save projects
Access download history
Use credits
Build a library
```

### Registered free user

Can:

```text
Download with ads
Claim daily file
Save limited projects
Receive file-of-day emails
Track credits
```

### Paid user

Can:

```text
Download without ads
Use credits
Access premium workflows
Save projects
Batch generate
Download archive
```

---

## 10. Content / SEO Architecture

This business needs SEO. Paid ads may be hard unless average order value or lifetime value gets high enough.

Build pages around jobs-to-be-done.

### Converter pages

```text
/convert-image-to-embroidery-file
/png-to-pes
/jpg-to-pes
/svg-to-dst
/pes-file-maker
/dst-file-maker
/brother-embroidery-file-converter
```

### Label pages

```text
/name-label-maker
/embroidery-name-labels
/school-uniform-labels
/clothing-name-labels
/quilt-label-maker
/baby-blanket-embroidery-labels
```

### Library pages

```text
/free-pes-files
/free-dst-files
/free-jef-files
/free-brother-embroidery-files
/free-flower-embroidery-files
/free-christmas-embroidery-files
```

### Learning pages

```text
/learn/what-is-a-pes-file
/learn/pes-vs-dst
/learn/how-to-make-embroidery-files
/learn/best-image-types-for-embroidery
/learn/how-to-stitch-name-labels
/learn/how-to-use-stabilizer
```

Each learning page should point back into the product.

---

## 11. Database / Product Model

At a high level, the product likely needs these core entities:

```text
User
Subscription
CreditBalance
CreditTransaction
Design
DesignVersion
GeneratedFile
Download
AdView
Template
LibraryItem
DailyFreeFile
Project
MachineFormat
HoopSize
License
```

### Design

Represents the user-facing design.

Fields:

```text
id
owner_user_id
source_type: text_label | library | ai_generated | upload | template
title
status
created_at
updated_at
visibility
license_type
```

### GeneratedFile

Represents actual machine file outputs.

Fields:

```text
design_id
format: PES | DST | JEF | EXP | VP3 | XXX etc.
hoop_size
stitch_count
color_count
file_url
preview_url
created_at
```

### CreditTransaction

Fields:

```text
user_id
amount
type: purchase | subscription_grant | spend | refund | promo
reason
related_design_id
created_at
```

### AdView

Fields:

```text
user_id or anonymous_session_id
ad_provider
completed
reward_type
reward_amount
download_id
created_at
```

### DailyFreeFile

Fields:

```text
library_item_id
date
is_active
download_count
subscriber_claim_count
ad_unlock_count
```

---

## 12. Product Flow Architecture

### Text Label Flow

```text
Landing page
↓
Enter text
↓
Choose style / size / format
↓
Generate preview
↓
Download gate
↓
Ad view / credit / subscription
↓
Download file
↓
Email capture / account save
```

### Free Library Flow

```text
Browse category
↓
Open file detail
↓
Preview design
↓
Choose format
↓
Ad view / credit / subscription
↓
Download
↓
Recommended related files
```

### File of the Day Flow

```text
Visit file of the day
↓
See countdown / today’s design
↓
Download with ad or sub
↓
Prompt to get tomorrow’s file by email
↓
Archive upsell
```

### Dynamic Generator Flow

```text
Choose template or prompt
↓
Generate artwork preview
↓
Simplify / tune design
↓
Stitch preview
↓
Export gate
↓
Spend credits or use subscription credits
↓
Download and save project
```

---

## 13. Homepage Product Framing

The monetization should be transparent.

Example copy:

> Free downloads are supported by short ads. Subscribers skip ads and get monthly credits for custom file generation. Need just one file? Buy a small credit pack anytime.

That is clear and fair.

---

## 14. Subscription as Discounted Microtransaction Supply

This is the right framing.

The subscription should not be “unlimited.” It should be:

```text
No ads
Monthly credit allowance
Discounted extra credits
Premium tools
Saved projects
Batch generation
Commercial-friendly access
```

Example:

```text
Free: Watch ads to download free files
Credits: Pay as you go
Subscriber: Get credits every month at 60–80% discount + skip ads
```

### Why it works

Casual users monetize through ads.

One-off users monetize through credits.

Heavy users monetize through subscription.

Power users still buy extra credits.

That gives multiple revenue streams without making any one user type feel punished.

---

## 15. Suggested Pricing Page Layout

```text
Free
$0
- Watch ads to download free files
- Create text labels
- File of the day
- Limited daily downloads
- Basic formats

Credit Packs
From $3
- Skip ads
- Generate custom files
- Download premium designs
- No subscription required

Hobby
$9/mo
- No ads
- 30 credits/month
- Instant free library downloads
- Saved projects
- Batch labels

Maker
$19/mo
- No ads
- 100 credits/month
- Commercial-friendly downloads
- Larger batches
- Priority generation

Seller
$39/mo
- No ads
- 300 credits/month
- Bulk tools
- Commercial use
- Early access templates
```

The exact credit numbers should be tuned based on real cost and usage, but this is the right shape.

---

## 16. Launch MVP Scope

Do not launch everything at once.

### MVP 1: utility + library

Launch with:

```text
Text Label Maker
Free file library
File of the day
Ad-gated downloads
Account creation
Credit purchase
Basic subscription
```

Delay:

```text
Full AI generator
Advanced dynamic generation
Batch seller tools
Commercial licensing complexity
Large template library
```

### MVP 2: dynamic generation

Add:

```text
Template-based custom generation
Credit spending
Saved projects
Stitch preview
Prompt-to-design
Upload-to-stitch
```

### MVP 3: seller workflows

Add:

```text
Batch labels
Commercial plan
Bulk downloads
Project folders
Design collections
Etsy seller landing pages
```

---

## 17. What to Build First

Recommended priority order:

### 1. Label Maker

This is the clearest free utility.

### 2. File of the Day

This creates daily habit and email capture.

### 3. Free Library

This creates SEO pages and ad-supported inventory.

### 4. Credits

This lets people pay without subscription friction.

### 5. Subscription

This gives regular users a better deal.

### 6. Dynamic Generation

This is the premium magic, but it should sit on top of proven conversion flows.

---

## 18. Key Metrics

Track these from day one:

```text
Visitor → label started
Label started → preview generated
Preview generated → download clicked
Download clicked → ad completed
Download clicked → credit used
Download clicked → subscription started
Free library page → download clicked
File of day page → email signup
Generator started → export completed
Credit purchase conversion
Subscriber monthly credit usage
Ad completion rate
Refund/support rate
Repeat downloads per user
```

The most important metric:

```text
preview → download intent
```

If people create previews but do not want the files, there is a quality or value problem.

---

## 19. Strategic Recommendation

The cleanest version of the business is:

> Free embroidery utility supported by ads, with credits and subscription for people who want convenience, custom generation, and volume.

Do not lead with “AI.” Lead with concrete jobs:

```text
Text labels
Free embroidery files
Daily free file
Custom machine files
```

Then use AI/dynamic generation as the premium feature.

People search for concrete jobs, not abstract AI novelty.

The strongest wedge is probably:

> Make embroidery name labels in your browser.

Then expand into:

> Download free files.

Then:

> Generate custom files.

That path gives you traffic, trust, and monetization in the right order.
