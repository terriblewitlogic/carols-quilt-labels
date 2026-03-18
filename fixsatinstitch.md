Three distinct problems to fix, each with different complexity:

---

### Problem 1: Always-vertical columns (most visible issue)

**What's wrong:** Columns are always scanned top-to-bottom regardless of stroke direction. A diagonal stroke in `A`, `V`, `W`, `X` etc. produces a stair-step of stitches rather than clean perpendicular coverage.

**What a fix requires:** Rotate the scan axis, same way `tatamiStitches` already does. Instead of scanning at `x = constant`, scan at a fixed angle (default 45° is standard for satin). The tatami rotation math is directly reusable — the difference is that satin needs the *full extent* of the stroke in the perpendicular direction per scan line, not just evenly-spaced points.

**Complexity: Medium.** The transform math is already in the codebase. Maybe 30–50 lines refactoring `satinStitches` to use the same rotated coordinate approach as `tatamiStitches`.

---

### Problem 2: No jumps between disconnected glyph parts (correctness issue)

**What's wrong:** Letters with separate parts — the dot of `i`/`j`, accented characters, or any two letter shapes close together — get stitched as one continuous run. The needle travels across open space creating a visible connecting thread on the fabric.

**What a fix requires:** After column scanning, group the resulting stitch pairs into connected regions (check if the gap between consecutive stitches exceeds a threshold, e.g. 2mm). Emit a jump stitch between groups. This is the JEF encoder already supports — we just need to split the stitch list into segments with jumps.

However, jumps within a single color group aren't currently handled — the encoder treats each `groups[g]` as one continuous run with only the first stitch as a jump. Supporting mid-group jumps would require either splitting into sub-groups or adding trim (`0x80 0x02 0x00 0x00`) + jump pairs between segments.

**Complexity: Medium.** Two parts: detect disconnected segments in the stitch output, and extend the encoder to support mid-group trims.

---

### Problem 3: Split-satin direction logic (minor correctness issue)

**What's wrong:** When a stroke is wider than 12.7mm, it splits into two halves. The alternation direction (`pts.length % 2`) uses the total stitch count, which changes depending on what came before in the word — it can produce two columns going the same direction rather than alternating.

**What a fix requires:** Track a local `parity` variable within the column scan loop, independent of `pts.length`.

**Complexity: Trivial.** 2-line fix.

---

### Priority order

| Fix | Impact | Effort |
|-----|--------|--------|
| Disconnected jumps | High — prevents rogue threads | Medium |
| Angle-based columns | Medium — diagonal letters look better | Medium |
| Split-satin parity | Low — only affects wide strokes >12.7mm | Trivial |

The disconnected jump fix is the most important for correctness. The angle fix is the most important for visual quality. Neither requires changes to the JEF encoder's color group structure — jumps can be encoded as trim+jump pairs within the existing stitch data.

Want me to implement any or all of these?