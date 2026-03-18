# JEF embroidery format: binary spec, tools, and pipelines

**The JEF file format is a proprietary Janome embroidery format that encodes stitch data as delta-encoded signed byte pairs, with a 116-byte fixed header, indexed color tables, and escaped command sequences for jumps, color changes, and end-of-file.** No official specification exists — everything known comes from community reverse-engineering, principally documented in the KDE Community Wiki, EduTech Wiki, and the source code of pyembroidery and libembroidery. The open source ecosystem has mature, production-ready JEF support: pyembroidery (Python) can read and write JEF files in a single line of code, and Ink/Stitch provides a full SVG-to-JEF digitizing pipeline inside Inkscape.

---

## The 116-byte header and what every field means

All multi-byte values in JEF are **little-endian**. The file has no magic number or signature — identification relies on internal consistency between the stitch offset and color count fields. The overall structure is: **File Header (116 bytes) → Thread Color List → Thread Type List → [JEF+ Plus-Header] → Stitch Data → [JEF+ Plus-Detail]**.

The complete header layout:

| Offset | Size | Type | Field | Description |
|--------|------|------|-------|-------------|
| **0x00** | 4 | uint32 LE | `stitch_offset` | Byte offset to first stitch record. Computed as `116 + (8 × color_count)` for plain JEF. |
| **0x04** | 4 | uint32 LE | `flags` | Unknown flags. Observed values: 1, 10, or **20 (0x14)**. |
| **0x08** | 8 | ASCII | `date` | Date string `"YYYYMMDD"` (e.g., `"20180712"`). |
| **0x10** | 8 | ASCII | `time` | Time string `"HHMMSSvp"`. Byte 22 encodes a machine version letter: `m`=MC12000, `n`=MC11000, `o`=MC10000v3, `p`=MC10000v2.2, `q`=MC9000, `r`=MC350E, `s`=MC200E, `t`=MB4. Byte 23 is typically `0x20` (space). |
| **0x18** | 4 | uint32 LE | `color_count` | Number of thread changes = number of color sections. |
| **0x1C** | 4 | uint32 LE | `stitch_count` | Number of 2-byte stitch records = `stitch_data_byte_length / 2`. |
| **0x20** | 4 | uint32 LE | `hoop_code` | Hoop identifier (see hoop table below). |
| **0x24** | 16 | 4 × int32 LE | `extent_1` | Design bounding box: left, top, right, bottom distances from hoop center in **0.1 mm units**. Left/top are negative; right/bottom positive. |
| **0x34** | 16 | 4 × int32 LE | `extent_2` | Margin to edges of the **110×110 mm hoop (A)**. Set to `-1, -1, -1, -1` if design doesn't fit. |
| **0x44** | 16 | 4 × int32 LE | `extent_3` | Margin to edges of the **50×50 mm hoop (C)**. `-1` if doesn't fit. |
| **0x54** | 16 | 4 × int32 LE | `extent_4` | Margin to edges of the **140×200 mm hoop (B)**. `-1` if doesn't fit. |
| **0x64** | 16 | 4 × int32 LE | `extent_5` | Margin to a custom hoop, or `-1` if not applicable. |

Hoop codes are: **0** = Standard A (126×110 mm), **1** = Free Arm C (50×50 mm), **2** = Large B (140×200 mm), **3** = Spring-Loaded F (126×110 mm), **4** = Giga D (230×200 mm).

Immediately after the 116-byte header come two parallel lists, each containing `color_count` entries of 4 bytes (uint32 LE). The **Thread Color List** at offset `0x74` stores JEF palette indices (1–78) referencing Janome's fixed 79-color palette. The **Thread Type List** follows at offset `0x74 + 4 × color_count`, where every entry is the constant value **13 (0x0D)** — its precise meaning is undocumented but may indicate thread weight or type.

---

## Stitch data: delta bytes, escapes, and command encoding

Stitch data begins at the byte offset stored in `stitch_offset` (field at offset 0x00). It consists of a stream of **2-byte normal stitch records** and **2- or 4-byte escaped command records**.

**Normal stitches** are two signed bytes (two's complement int8): the first is the X delta, the second is the Y delta, each ranging from **-127 to +127** in 0.1 mm units. This means the maximum single-stitch displacement is **±12.7 mm** per axis. The machine moves to the new position and performs a needle strike. The coordinates are purely relative — absolute position is tracked by accumulating deltas from the origin (hoop center).

When the first byte equals **0x80 (-128)**, it is an escape code and the record is a command:

| Bytes | Command | Description |
|-------|---------|-------------|
| `0x80 0x10` | **END** | Terminates stitch data. 2 bytes total, no displacement follows. |
| `0x80 0x01 dx dy` | **COLOR_CHANGE** | Advance to next thread in color list. Machine pauses for thread swap. `dx, dy` (signed int8) specify movement to the start of the next section. 4 bytes total. |
| `0x80 0x02 dx dy` | **JUMP** | Move without stitching (needle bar blocked). 4 bytes total. Chain multiple jumps for moves exceeding ±12.7 mm. |
| `0x80 0x02 0x00 0x00` | **TRIM** | A jump with zero displacement is conventionally interpreted as a trim (thread cut). Actual machine behavior depends on trim settings. |

The format has **no separate STOP command** — a stop (machine pause) and a color change share the same `0x80 0x01` code. PyEmbroidery handles standalone STOP commands by encoding them as a color change to color code 0 with an alternating pattern.

A parsing algorithm in pseudocode:

```
position = (0, 0)
while not EOF:
    b0, b1 = read_two_bytes()
    if b0 == 0x80:
        if b1 == 0x10: break                    # END
        elif b1 == 0x01:                         # COLOR_CHANGE
            dx, dy = read_two_bytes()
            advance_color_index()
            position += (dx, dy)
        elif b1 == 0x02:                         # JUMP or TRIM
            dx, dy = read_two_bytes()
            if dx == 0 and dy == 0: trim()
            else: position += (dx, dy)           # move, no stitch
    else:
        position += (b0, b1)                     # normal stitch
        needle_strike(position)
```

---

## The 78-color Janome palette and thread indexing

JEF uses a **fixed indexed palette of 78 colors** (codes 1–78; code 0 is "unknown"). These correspond to Janome's proprietary thread color catalog. Two slightly different RGB lookup tables exist in documentation — the KDE Wiki version (reverse-engineered from actual machines) is considered more authoritative than the EduTech Wiki version (from pyembroidery). Key entries include: **1** = Black (#000000), **2** = White (#F0F0F0), **42** = Red (#FF0000), **48** = Yellow (#FFFF17), **26** = Blue (#0B2F84), **6** = Green (#237336).

When converting from formats with arbitrary RGB colors (like PES), the converter must find the nearest palette match for each thread. This is a significant limitation — JEF offers only 78 possible thread colors. When converting from colorless formats like DST or EXP, the converter must invent colors entirely, making manual color reassignment necessary post-conversion.

Each color entry in the Thread Color List is a **4-byte uint32 LE** value. The Thread Type List mirrors it with constant `0x0D` entries. Together these two lists occupy `8 × color_count` bytes between the fixed header and the stitch data.

---

## JEF+ extends the format for multi-design layouts

JEF+ is used by newer Janome machines (MC9900, MC11000, HMC12000, HMC15000, MB4) when designs are exported from the machine's built-in editor after combining, repositioning, or resizing multiple JEF designs. The stitch encoding is identical to plain JEF.

The difference is a **24-byte Plus-Header** inserted between the Thread Type List and the stitch data. It contains: two 4-byte zero fields, an 8-byte ASCII signature **"JANOME\0\0"**, a uint32 `plus_detail_count` (typically 1), and a uint32 `plus_detail_offset` pointing to extra data after the stitch end marker. The Plus-Detail section (not fully documented) apparently stores individual design positioning, rotation, and scaling data.

**Identifying the variant:** For plain JEF, `stitch_offset` equals `116 + 8 × color_count`. For JEF+, `stitch_offset` is **24 bytes larger** (`140 + 8 × color_count`), and the "JANOME\0\0" signature is present at offset `116 + 8 × color_count + 8`. Readers can safely ignore the Plus-Header and Plus-Detail — seeking directly to `stitch_offset` works for both variants.

---

## PyEmbroidery dominates the open source ecosystem

**PyEmbroidery is the single most important library in open source embroidery tooling.** It reads 46 formats and writes 20 formats (including JEF for both read and write), is pure Python with zero compiled dependencies, and installs via `pip install pyembroidery`. It is the backend for Ink/Stitch, vpype-embroidery, the EmbroidePy desktop editor, and most web-based embroidery converters. JEF is one of pyembroidery's **5 mandated core formats** (alongside PES, DST, EXP, VP3).

Creating a JEF file from scratch requires just a few lines:

```python
import pyembroidery

pattern = pyembroidery.EmbPattern()
thread = pyembroidery.EmbThread()
thread.set_hex_color("#FF0000")
pattern.add_thread(thread)

# Coordinates in 1/10 mm (100 = 10mm)
pattern.add_stitch_absolute(pyembroidery.STITCH, 0, 0)
pattern.add_stitch_absolute(pyembroidery.STITCH, 100, 0)
pattern.add_stitch_absolute(pyembroidery.STITCH, 100, 100)
pattern.add_stitch_absolute(pyembroidery.STITCH, 0, 100)
pattern.add_stitch_absolute(pyembroidery.STITCH, 0, 0)
pattern.add_command(pyembroidery.END)

pyembroidery.write_jef(pattern, "square.jef")
```

PyEmbroidery's encoder automatically handles format-specific constraints: it splits long stitches exceeding the **127-unit maximum**, converts middle-level commands (COLOR_BREAK, SEQUENCE_BREAK) to proper low-level escape sequences, maps arbitrary RGB colors to the nearest JEF palette entry, and computes all header fields including hoop extents. Format conversion is a one-liner: `pyembroidery.convert("design.pes", "design.jef")`.

For multi-color designs, use `COLOR_BREAK` between stitch sections — pyembroidery converts this to the appropriate `0x80 0x01` color change command with displacement. Optional encoding settings include `tie_on` and `tie_off` (adds small securing stitches at start/end of sections) and `translate` for repositioning.

The other major tools and their JEF status:

- **Ink/Stitch** (Inkscape extension): Full JEF read/write. Actively developed. Uses a pyembroidery fork internally. Provides complete SVG → stitch plan → JEF pipeline with fill, satin, running, ripple, contour, meander, and tartan stitch types.
- **libembroidery** (C library): JEF read/write as part of 45+ format support. Includes the `embroider` CLI tool for batch conversion. Actively maintained (updated November 2025). Licensed under zlib.
- **EmbroideryIO** (Java/Android): Direct port of pyembroidery. JEF read/write. Available via JitPack.
- **PEmbroider** (Processing/Java): JEF write-only. Excellent for generative/creative coding embroidery designs. Includes TSP path optimizer.

---

## Practical pipeline: SVG to valid JEF in four steps

The simplest end-to-end open source pipeline uses **Inkscape + Ink/Stitch**:

1. Create or open an SVG in Inkscape. Convert all objects to paths (Path → Object to Path).
2. Set stitch parameters via Extensions → Ink/Stitch → Params (choose fill type, density, underlay, etc.).
3. Preview the stitch plan with Extensions → Ink/Stitch → Simulator.
4. Export via File → Save a Copy → select `.jef` format.

For programmatic workflows, pyembroidery alone is sufficient. For batch conversion of existing embroidery files: `pyembroidery.convert("input.pes", "output.jef")`. For command-line use, libembroidery's `embroider` tool supports `embroider --convert input.pes output.jef`.

**Critical gotchas to avoid:**

- **USB formatting**: Janome machines require FAT32. Drives over 32 GB may cause problems. Files must reside in the `EMB/Embf/` folder — insert a blank USB into the machine first to auto-create this structure.
- **Hoop size validation**: If the design exceeds all standard Janome hoop sizes (all extent fields set to -1), some machines will refuse to load the file. Always verify design dimensions fit your target hoop.
- **Color fidelity loss**: Converting from PES (arbitrary RGB) to JEF (78-color palette) inevitably changes colors. Converting from DST or EXP (no color data) requires manual color assignment afterward.
- **File naming**: Keep filenames short with no spaces or special characters. Some older Janome firmware is restrictive.
- **Stitch count limits**: Some machines cap at approximately **100,000 stitches** per design.
- **JEF+ compatibility**: Older machines (e.g., MC 500E) only read standard JEF, not JEF+ or JPX. If in doubt, export plain JEF.
- **PyEmbroidery's JEF+ support** is functional for reading but described as needing further testing. Plain JEF read/write is mature and stable.

## Conclusion

The JEF format is straightforward once you understand its three-part structure: a 116-byte header encoding metadata and hoop margins, followed by indexed color/type lists, followed by delta-encoded stitch pairs with 0x80-prefixed escape commands. The **±127 unit stitch limit** (12.7 mm) and **78-color fixed palette** are the two fundamental constraints that all conversion tools must handle. PyEmbroidery has emerged as the de facto standard library, powering virtually every open source embroidery tool from Ink/Stitch to web converters. For anyone building a JEF generation pipeline, the most reliable path is pyembroidery for file I/O combined with Ink/Stitch for digitizing — this combination handles header construction, stitch splitting, color matching, and hoop validation automatically, leaving only USB formatting and machine-specific quirks as manual concerns.