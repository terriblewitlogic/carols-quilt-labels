"""
Hatch-style stitch instruction sheet generator.

Produces a PDF with the metadata, recommended materials, and colour
sequence that an end-user needs to actually stitch out a design — the
same sheet a professional digitizer ships alongside their files.

Usage:
    from instruction_sheet import build_pdf
    pdf_bytes = build_pdf(
        pattern,                # pyembroidery.EmbPattern
        groups,                 # raster_to_stitch_groups output
        design_name='Sunflower',
        hoop_w_mm=100, hoop_h_mm=100,
        format='JEF',
        thread_brand='Madeira Polyneon',
        thread_codes=[{'code':'1005','name':'Black','hex':'#000000'}, ...],
    )
"""
from io import BytesIO
from typing import List, Dict, Optional
import math

from pyembroidery import STITCH, JUMP, COLOR_CHANGE, STOP, COLOR_BREAK


# ── Thread-length estimates (mm of thread per machine stitch) ────────────────
TOP_THREAD_PER_STITCH_MM    = 4.5    # going down, back up, plus cross-over
BOBBIN_THREAD_PER_STITCH_MM = 1.2    # only the underside of each penetration


def _count_stitches_per_block(pattern) -> List[int]:
    """
    Count STITCH commands inside each colour block.

    Block boundaries are signalled by COLOR_BREAK (the high-level command
    the encoder adds before each new colour) and the lower-level
    STOP/COLOR_CHANGE that the format writer would emit. Both 8-bit
    (COLOR_CHANGE / STOP) and high-byte (COLOR_BREAK) variants are checked
    because the in-memory pattern can carry either depending on whether
    we're inspecting before or after the file writer runs.
    """
    counts: List[int] = []
    cur = 0
    # Boundary command codes — pyembroidery uses COLOR_BREAK (0xE2) at the
    # high level and STOP/COLOR_CHANGE at the format-specific level.
    block_boundaries = {COLOR_CHANGE, STOP, COLOR_BREAK & 0xFF, COLOR_BREAK}
    for _, _, cmd in pattern.stitches:
        # Test against the full command (some are > 0xFF) and the low byte.
        if cmd in block_boundaries or (cmd & 0xFF) in (COLOR_CHANGE, STOP):
            counts.append(cur)
            cur = 0
            continue
        if (cmd & 0xFF) == STITCH:
            cur += 1
    if cur:
        counts.append(cur)
    return counts


def _estimate_thread_length_m(stitch_count: int, kind: str = 'top') -> float:
    """Rough total thread length in metres."""
    if kind == 'top':
        return stitch_count * TOP_THREAD_PER_STITCH_MM / 1000.0
    return stitch_count * BOBBIN_THREAD_PER_STITCH_MM / 1000.0


def _hex_to_rgb01(hex_color: str):
    """Hex → (r, g, b) in 0..1 floats for reportlab."""
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def build_pdf(
    pattern,
    groups: List[dict],
    design_name: str,
    hoop_w_mm: float,
    hoop_h_mm: float,
    format: str = 'JEF',
    thread_brand: str = 'Madeira Polyneon',
    thread_codes: Optional[List[dict]] = None,
    fabric: str = 'Cotton or quilting cotton',
    stabilizer: str = 'Tear Away ×2 (medium)',
    topping: str = 'None — add water-soluble film for fleece',
) -> bytes:
    """
    Build a single-page (or two-page for many colours) instruction PDF.

    `groups` is the raster_to_stitch_groups output; each group corresponds
    to one colour stop in the order they were emitted to the JEF.
    `thread_codes`, if provided, maps group order to thread metadata
    (code/name/hex) — typically from thread_palette.snap_palette but
    aligned to the group sequence rather than the unique-colour palette.
    """
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.units import mm, inch
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor, Color

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    page_w, page_h = LETTER

    # ── Per-block stitch counts ──────────────────────────────────────────
    block_counts = _count_stitches_per_block(pattern)
    # The encoder also adds a final END after the last block; trim to len(groups).
    while len(block_counts) > len(groups):
        block_counts.pop()
    while len(block_counts) < len(groups):
        block_counts.append(0)

    total_stitches = sum(block_counts)

    # ── Page 1 — Header + summary + color sequence ───────────────────────
    margin = 0.75 * inch
    y = page_h - margin

    # Wordmark
    c.setFont('Times-Italic', 22)
    c.setFillColor(HexColor('#8b5830'))
    c.drawString(margin, y, 'Embroidery.mom')
    c.setFont('Helvetica', 9)
    c.setFillColor(HexColor('#7a6050'))
    c.drawRightString(page_w - margin, y + 4, 'Stitch Instructions')

    y -= 18
    c.setStrokeColor(HexColor('#e8ddd2'))
    c.line(margin, y, page_w - margin, y)
    y -= 30

    # Design title
    c.setFont('Helvetica-Bold', 18)
    c.setFillColor(HexColor('#3d2b1a'))
    c.drawString(margin, y, design_name)
    y -= 26

    # Two-column metadata block
    col_left = margin
    col_right = margin + (page_w - 2 * margin) / 2
    label_color = HexColor('#7a6050')
    value_color = HexColor('#3d2b1a')

    def _label_value(x, y, label, value, label_w=85):
        c.setFont('Helvetica', 9)
        c.setFillColor(label_color)
        c.drawString(x, y, label)
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(value_color)
        c.drawString(x + label_w, y, str(value))

    _label_value(col_left,  y, 'Total stitches',  f'{total_stitches:,}')
    _label_value(col_right, y, 'Format',          format.upper())
    y -= 16
    _label_value(col_left,  y, 'Hoop size',       f'{hoop_w_mm:.0f} × {hoop_h_mm:.0f} mm')
    _label_value(col_right, y, 'Colour stops',    str(len(groups)))
    y -= 16
    _label_value(col_left,  y, 'Total thread (top)',
                 f'{_estimate_thread_length_m(total_stitches, "top"):.1f} m')
    _label_value(col_right, y, 'Bobbin thread',
                 f'{_estimate_thread_length_m(total_stitches, "bobbin"):.1f} m')
    y -= 28

    # Materials
    c.setFont('Helvetica-Bold', 11)
    c.setFillColor(HexColor('#3d2b1a'))
    c.drawString(margin, y, 'Recommended materials')
    y -= 16
    _label_value(col_left,  y, 'Fabric',     fabric, label_w=70)
    y -= 14
    _label_value(col_left,  y, 'Stabilizer', stabilizer, label_w=70)
    y -= 14
    _label_value(col_left,  y, 'Topping',    topping, label_w=70)
    y -= 28

    # Color sequence header
    c.setFont('Helvetica-Bold', 11)
    c.setFillColor(HexColor('#3d2b1a'))
    c.drawString(margin, y, 'Colour sequence')
    y -= 18

    # Header row
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(label_color)
    cols = [
        ('STOP',    margin),
        ('',        margin + 35),    # swatch column (no header text)
        ('CODE',    margin + 60),
        ('NAME',    margin + 110),
        ('ROLE',    margin + 240),
        ('STITCHES', margin + 300),
        ('THREAD',  margin + 370),
    ]
    for label, x in cols:
        c.drawString(x, y, label)
    y -= 6
    c.setStrokeColor(HexColor('#e8ddd2'))
    c.line(margin, y, page_w - margin, y)
    y -= 14

    # Sequence rows
    c.setFont('Helvetica', 9)
    for i, (g, count) in enumerate(zip(groups, block_counts)):
        if y < margin + 60:
            # Spill onto a second page if the table runs long
            c.showPage()
            y = page_h - margin
            c.setFont('Helvetica', 9)

        stop_n = i + 1
        color_hex = g.get('color', '#000000')

        thread_code = '—'
        thread_name = '—'
        if thread_codes and i < len(thread_codes):
            thread_code = thread_codes[i].get('code', '—')
            thread_name = thread_codes[i].get('name', '—')

        role = g.get('role', g.get('type', 'fill')).title()
        thread_m = _estimate_thread_length_m(count, 'top')

        # Stop number
        c.setFillColor(value_color)
        c.drawString(cols[0][1], y, str(stop_n))

        # Colour swatch
        try:
            swatch_color = HexColor(color_hex)
        except Exception:
            swatch_color = HexColor('#000000')
        c.setFillColor(swatch_color)
        c.setStrokeColor(HexColor('#e8ddd2'))
        c.rect(cols[1][1], y - 2, 18, 12, fill=1, stroke=1)

        # Code, name, role, stitches, thread
        c.setFillColor(value_color)
        c.drawString(cols[2][1], y, str(thread_code))
        c.drawString(cols[3][1], y, thread_name[:24])
        c.drawString(cols[4][1], y, role)
        c.drawRightString(cols[5][1] + 50, y, f'{count:,}')
        c.drawRightString(cols[6][1] + 35, y, f'{thread_m:.1f} m')

        y -= 16

    # ── Footer ───────────────────────────────────────────────────────────
    c.setFont('Helvetica', 7.5)
    c.setFillColor(HexColor('#b09a88'))
    footer_y = margin - 24
    c.drawString(margin, footer_y,
                 'Stitch counts and thread estimates are calculated from the file. '
                 'Real-world thread use may vary by ±15% depending on fabric and tension.')
    c.drawRightString(page_w - margin, footer_y - 12,
                      'Generated by Embroidery.mom')

    c.showPage()
    c.save()
    return buffer.getvalue()
