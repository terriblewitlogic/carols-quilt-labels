"""
Embroidery thread colour matching.

Supports three major brands:
  • Madeira Polyneon  (40wt polyester — codes 1001–1399)
  • Isacord           (40wt polyester — codes 0000–9999)
  • Robison-Anton     (40wt rayon     — codes 2222–2599)

Usage:
    from thread_palette import snap_palette
    threads = snap_palette(['#d4a060', '#3a2010'], brand='isacord')
    # → [{'original_hex':..., 'code':..., 'name':..., 'thread_hex':...}, ...]
"""

from typing import Tuple, Dict, List
import math

# ─── Madeira Polyneon ─────────────────────────────────────────────────────────
_MADEIRA_RAW: List[Tuple[str, str, int, int, int]] = [
    # Whites / off-whites
    ('1001', 'White',           255, 255, 255),
    ('1002', 'Antique White',   240, 234, 214),
    ('1003', 'Cream',           255, 248, 220),
    # Blacks / greys
    ('1005', 'Black',             0,   0,   0),
    ('1006', 'Dark Charcoal',    40,  40,  40),
    ('1007', 'Charcoal',         80,  80,  80),
    ('1008', 'Medium Grey',     128, 128, 128),
    ('1009', 'Light Grey',      192, 192, 192),
    # Browns / tans
    ('1034', 'Dark Brown',       80,  40,  10),
    ('1035', 'Brown',           120,  60,  20),
    ('1036', 'Medium Brown',    160,  90,  40),
    ('1037', 'Tan',             195, 145,  90),
    ('1038', 'Camel',           210, 170, 110),
    ('1039', 'Sand',            230, 205, 160),
    ('1040', 'Light Sand',      240, 220, 185),
    ('1058', 'Dark Khaki',      150, 130,  80),
    ('1059', 'Khaki',           185, 165, 100),
    # Reds
    ('1147', 'Dark Red',        140,   0,  10),
    ('1148', 'Red',             210,  20,  20),
    ('1149', 'Bright Red',      240,  30,  30),
    ('1150', 'Scarlet',         220,  50,  30),
    ('1151', 'Coral Red',       230,  80,  60),
    ('1152', 'Light Coral',     240, 120,  90),
    # Pinks
    ('1161', 'Dark Pink',       200,  50, 100),
    ('1162', 'Hot Pink',        230,  60, 130),
    ('1163', 'Pink',            240, 130, 160),
    ('1164', 'Light Pink',      250, 180, 200),
    ('1165', 'Blush',           255, 210, 215),
    # Oranges
    ('1170', 'Dark Orange',     200,  80,   0),
    ('1171', 'Orange',          240, 110,  10),
    ('1172', 'Bright Orange',   255, 140,  20),
    ('1173', 'Light Orange',    255, 175,  70),
    ('1174', 'Peach',           255, 200, 140),
    # Yellows
    ('1180', 'Gold',            210, 160,   0),
    ('1181', 'Dark Yellow',     230, 190,  20),
    ('1182', 'Yellow',          255, 220,  30),
    ('1183', 'Bright Yellow',   255, 240,  60),
    ('1184', 'Light Yellow',    255, 248, 140),
    # Greens
    ('1195', 'Dark Forest',      20,  70,  20),
    ('1196', 'Forest Green',     30, 100,  30),
    ('1197', 'Dark Green',       40, 130,  40),
    ('1198', 'Medium Green',     60, 160,  60),
    ('1199', 'Green',            80, 190,  70),
    ('1200', 'Bright Green',    100, 210,  80),
    ('1201', 'Light Green',     150, 220, 130),
    ('1202', 'Mint Green',      180, 230, 180),
    ('1203', 'Pale Green',      210, 240, 210),
    ('1210', 'Olive Green',      90, 110,  40),
    ('1211', 'Dark Olive',      100, 120,  50),
    ('1212', 'Olive',           140, 150,  60),
    ('1213', 'Yellow Green',    170, 190,  60),
    # Teals / Cyan
    ('1225', 'Dark Teal',        10,  90,  90),
    ('1226', 'Teal',             20, 130, 120),
    ('1227', 'Medium Teal',      30, 160, 150),
    ('1228', 'Light Teal',       80, 195, 185),
    ('1229', 'Aqua',            100, 215, 205),
    ('1230', 'Pale Aqua',       170, 230, 225),
    # Blues
    ('1241', 'Navy',             10,  20,  80),
    ('1242', 'Dark Navy',        15,  30, 100),
    ('1243', 'Dark Blue',        20,  50, 150),
    ('1244', 'Royal Blue',       40,  80, 200),
    ('1245', 'Blue',             60, 110, 220),
    ('1246', 'Medium Blue',      80, 140, 220),
    ('1247', 'Cornflower',      100, 150, 230),
    ('1248', 'Light Blue',      140, 185, 235),
    ('1249', 'Sky Blue',        170, 210, 240),
    ('1250', 'Pale Blue',       210, 230, 248),
    ('1258', 'Steel Blue',       70, 100, 140),
    ('1259', 'Slate Blue',       90, 110, 160),
    # Purples
    ('1271', 'Dark Purple',      80,  10, 100),
    ('1272', 'Purple',          120,  30, 140),
    ('1273', 'Medium Purple',   150,  60, 170),
    ('1274', 'Violet',          120,  70, 200),
    ('1275', 'Medium Violet',   150,  90, 210),
    ('1276', 'Lavender',        180, 150, 220),
    ('1277', 'Light Lavender',  210, 190, 235),
    ('1278', 'Lilac',           220, 180, 230),
    # Specialty
    ('1321', 'Dark Gold',       180, 130,   0),
    ('1322', 'Antique Gold',    200, 160,  40),
    ('1323', 'Champagne',       225, 200, 150),
]

# ─── Isacord ──────────────────────────────────────────────────────────────────
_ISACORD_RAW: List[Tuple[str, str, int, int, int]] = [
    # Whites / off-whites
    ('0101', 'White',           255, 255, 255),
    ('0270', 'Antique White',   240, 232, 210),
    ('0712', 'Cream',           255, 245, 210),
    # Blacks / greys
    ('0020', 'Black',             0,   0,   0),
    ('0022', 'Dark Charcoal',    45,  45,  45),
    ('0174', 'Charcoal',         78,  78,  78),
    ('0176', 'Medium Grey',     130, 130, 130),
    ('0182', 'Silver Grey',     195, 195, 195),
    # Browns
    ('0835', 'Dark Brown',       75,  38,  12),
    ('0853', 'Brown',           118,  58,  22),
    ('0855', 'Antique Brown',   155,  88,  42),
    ('0932', 'Tan',             198, 148,  88),
    ('0942', 'Camel',           212, 172, 108),
    ('1172', 'Sand',            228, 208, 162),
    ('0543', 'Khaki',           182, 162,  98),
    # Reds
    ('1704', 'Dark Red',        138,   8,  18),
    ('1705', 'Red',             208,  22,  28),
    ('1506', 'Bright Red',      238,  28,  36),
    ('1530', 'Scarlet',         218,  48,  32),
    ('1840', 'Coral',           232,  85,  65),
    # Pinks
    ('2011', 'Dark Pink',       198,  48,  98),
    ('2120', 'Hot Pink',        228,  58, 128),
    ('2210', 'Pink',            238, 128, 158),
    ('2250', 'Light Pink',      248, 178, 198),
    ('2260', 'Blush',           252, 208, 212),
    # Oranges
    ('1300', 'Dark Orange',     198,  78,   8),
    ('1312', 'Orange',          238, 108,  18),
    ('1332', 'Bright Orange',   252, 138,  28),
    ('1362', 'Light Orange',    252, 172,  68),
    ('1532', 'Peach',           252, 198, 138),
    # Yellows
    ('0640', 'Gold',            208, 158,   8),
    ('0660', 'Dark Yellow',     228, 188,  28),
    ('0720', 'Yellow',          252, 218,  38),
    ('0702', 'Bright Yellow',   255, 238,  58),
    ('0660', 'Pale Yellow',     252, 245, 138),
    # Greens
    ('5633', 'Dark Forest',      22,  68,  22),
    ('5534', 'Forest Green',     32,  98,  32),
    ('5613', 'Dark Green',       42, 128,  42),
    ('5522', 'Medium Green',     62, 158,  58),
    ('5210', 'Green',            78, 188,  68),
    ('5220', 'Bright Green',     98, 208,  78),
    ('5510', 'Light Green',     148, 218, 128),
    ('5770', 'Mint',            178, 228, 178),
    ('5650', 'Pale Mint',       208, 238, 208),
    ('0542', 'Olive',           138, 148,  58),
    ('0543', 'Yellow Green',    168, 188,  58),
    # Teals
    ('4515', 'Dark Teal',        12,  88,  88),
    ('4516', 'Teal',             22, 128, 118),
    ('4620', 'Medium Teal',      32, 158, 148),
    ('4250', 'Aqua',             98, 212, 202),
    # Blues
    ('3355', 'Navy',             12,  22,  78),
    ('3543', 'Dark Blue',        22,  48, 148),
    ('3620', 'Royal Blue',       42,  78, 198),
    ('3510', 'Blue',             58, 108, 218),
    ('3552', 'Medium Blue',      78, 138, 218),
    ('3600', 'Cornflower',       98, 148, 228),
    ('3510', 'Light Blue',      138, 182, 232),
    ('3640', 'Sky Blue',        168, 208, 238),
    ('3770', 'Pale Blue',       208, 228, 245),
    # Purples
    ('2715', 'Dark Purple',      78,  12,  98),
    ('2720', 'Purple',          118,  28, 138),
    ('2750', 'Medium Purple',   148,  58, 168),
    ('2830', 'Violet',          118,  68, 198),
    ('3040', 'Lavender',        178, 148, 218),
    ('3042', 'Light Lavender',  208, 188, 232),
    # Specialty
    ('0874', 'Dark Gold',       178, 128,   8),
    ('0892', 'Antique Gold',    198, 158,  42),
    ('0882', 'Champagne',       222, 198, 148),
]

# ─── Robison-Anton ────────────────────────────────────────────────────────────
_RA_RAW: List[Tuple[str, str, int, int, int]] = [
    # Whites / off-whites
    ('2297', 'Super White',     255, 255, 255),
    ('2222', 'White',           250, 248, 240),
    ('2516', 'Antique White',   238, 230, 208),
    # Blacks / greys
    ('2296', 'Black',             8,   8,   8),
    ('2516', 'Dark Charcoal',    48,  48,  48),
    ('2424', 'Med Pewter',       88,  88,  88),
    ('2423', 'Lt Pewter',       138, 138, 138),
    ('2415', 'Silver',          192, 192, 192),
    # Browns
    ('2338', 'Dark Brown',       78,  38,  14),
    ('2337', 'Brown',           122,  62,  24),
    ('2225', 'Dk Antique Gold', 152,  90,  44),
    ('2337', 'Tan',             195, 148,  90),
    ('2225', 'Camel',           208, 168, 108),
    ('2516', 'Sand',            225, 205, 162),
    ('2344', 'Khaki',           180, 162,  98),
    # Reds
    ('2255', 'Dk Christmas Red',135,  10,  18),
    ('2254', 'Christmas Red',   205,  22,  28),
    ('2253', 'Red',             238,  28,  35),
    ('2252', 'Scarlet',         215,  48,  30),
    ('2430', 'Coral',           228,  82,  62),
    # Pinks
    ('2431', 'Dk Dusty Rose',   195,  50,  95),
    ('2432', 'Hot Pink',        225,  60, 125),
    ('2433', 'Pink',            235, 128, 155),
    ('2434', 'Lt Pink',         245, 175, 195),
    ('2282', 'Blush',           250, 205, 210),
    # Oranges
    ('2278', 'Pumpkin',         195,  78,   8),
    ('2277', 'Orange',          235, 108,  18),
    ('2276', 'Bright Orange',   250, 138,  28),
    ('2275', 'Tangerine',       250, 172,  68),
    ('2274', 'Peach',           250, 195, 135),
    # Yellows
    ('2240', 'Old Gold',        205, 155,  10),
    ('2239', 'Dark Yellow',     225, 185,  28),
    ('2238', 'Yellow',          250, 215,  38),
    ('2237', 'Pale Yellow',     250, 242, 138),
    # Greens
    ('2370', 'Dk Hunter Green',  20,  65,  20),
    ('2369', 'Hunter Green',     30,  95,  30),
    ('2368', 'Christmas Green',  40, 125,  40),
    ('2367', 'Dk Grass Green',   58, 155,  55),
    ('2366', 'Grass Green',      75, 185,  65),
    ('2365', 'Bright Green',     95, 205,  75),
    ('2364', 'Lt Green',        145, 215, 125),
    ('2363', 'Mint Green',      175, 225, 175),
    ('2344', 'Olive',           135, 145,  55),
    ('2345', 'Yellow Green',    165, 185,  55),
    # Teals
    ('2393', 'Dk Teal',          10,  85,  85),
    ('2392', 'Teal',             20, 125, 115),
    ('2391', 'Med Teal',         30, 155, 145),
    ('2390', 'Aqua',             95, 208, 198),
    # Blues
    ('2326', 'Navy',             10,  20,  75),
    ('2325', 'Dk Royal Blue',    20,  45, 145),
    ('2324', 'Royal Blue',       40,  75, 195),
    ('2323', 'Blue',             55, 105, 215),
    ('2322', 'Med Blue',         75, 135, 215),
    ('2321', 'Cornflower Blue',  95, 145, 225),
    ('2320', 'Lt Blue',         135, 178, 228),
    ('2319', 'Sky Blue',        165, 205, 235),
    ('2318', 'Pale Blue',       205, 225, 242),
    # Purples
    ('2359', 'Dk Purple',        75,  10,  95),
    ('2358', 'Purple',          115,  28, 135),
    ('2357', 'Med Purple',      145,  55, 165),
    ('2356', 'Violet',          115,  65, 195),
    ('2355', 'Lavender',        175, 145, 215),
    ('2354', 'Lt Lavender',     205, 185, 228),
    # Specialty
    ('2229', 'Dk Old Gold',     175, 125,  10),
    ('2228', 'Antique Gold',    195, 155,  40),
    ('2227', 'Champagne',       218, 195, 145),
]

# ─── Build lookup tables ──────────────────────────────────────────────────────
def _build(raw):
    return [
        {'code': c, 'name': n,
         'hex': '#{:02x}{:02x}{:02x}'.format(r, g, b),
         'rgb': (r, g, b)}
        for c, n, r, g, b in raw
    ]

PALETTES = {
    'madeira':  _build(_MADEIRA_RAW),
    'isacord':  _build(_ISACORD_RAW),
    'robison-anton': _build(_RA_RAW),
}

PALETTE_LABELS = {
    'madeira':       'Madeira Polyneon',
    'isacord':       'Isacord',
    'robison-anton': 'Robison-Anton',
}


# ─── Colour matching ──────────────────────────────────────────────────────────
def _perceptual_dist(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """Weighted Euclidean RGB distance (approximates human perception)."""
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2
    return 2*(r1-r2)**2 + 4*(g1-g2)**2 + 3*(b1-b2)**2


def nearest_thread(
    rgb: Tuple[int, int, int],
    brand: str = 'madeira',
) -> Dict:
    """Return the closest thread from the given brand palette."""
    threads = PALETTES.get(brand, PALETTES['madeira'])
    best, best_d = threads[0], float('inf')
    for t in threads:
        d = _perceptual_dist(rgb, t['rgb'])
        if d < best_d:
            best_d, best = d, t
    return best


def snap_palette(
    palette_hex: List[str],
    brand: str = 'madeira',
) -> List[Dict]:
    """
    Match a list of hex colours to real threads.
    Returns [{original_hex, code, name, thread_hex, brand}, ...]
    """
    result = []
    for h in palette_hex:
        h = h.lstrip('#')
        rgb = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        t = nearest_thread(rgb, brand)
        result.append({
            'original_hex': '#' + h,
            'code':         t['code'],
            'name':         t['name'],
            'thread_hex':   t['hex'],
            'brand':        PALETTE_LABELS.get(brand, brand),
        })
    return result
