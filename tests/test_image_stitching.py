import base64
import io
import sys
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'functions' / 'image_to_jef'))

import pyembroidery  # noqa: E402
from image_to_jef import _build_pattern  # noqa: E402
from raster_to_stitches import (  # noqa: E402
    _mask_to_polygons,
    _route_components,
    raster_to_stitch_groups,
)


def _png_b64(draw_fn, size=(80, 80)):
    img = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(img)
    draw_fn(draw)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')


class ImageStitchingTests(unittest.TestCase):
    def test_conversion_is_deterministic(self):
        image_b64 = _png_b64(lambda d: d.ellipse((12, 10, 52, 58), fill='red'))

        first, first_svg, first_palette = raster_to_stitch_groups(
            image_b64, 40, 40, num_colors=2, density_mm=0.9, min_feature_mm=1.0
        )
        second, second_svg, second_palette = raster_to_stitch_groups(
            image_b64, 40, 40, num_colors=2, density_mm=0.9, min_feature_mm=1.0
        )

        self.assertEqual(first_palette, second_palette)
        self.assertEqual(first, second)
        self.assertEqual(first_svg, second_svg)

    def test_mask_to_polygons_preserves_holes(self):
        import numpy as np

        mask = np.zeros((60, 60), dtype=bool)
        mask[8:52, 8:52] = True
        mask[22:38, 22:38] = False

        polys = _mask_to_polygons(mask, min_area=20)

        self.assertEqual(len(polys), 1)
        self.assertGreaterEqual(len(polys[0].interiors), 1)

    def test_route_components_keeps_component_boundaries(self):
        components = [
            [[(100.0, 0.0), (105.0, 0.0)], [(106.0, 0.0), (110.0, 0.0)]],
            [[(-20.0, 0.0), (-15.0, 0.0)]],
        ]

        segments, component_ids = _route_components(components)

        self.assertEqual(len(segments), 3)
        self.assertEqual(len(component_ids), 3)
        self.assertEqual(component_ids.count(0), 2)
        self.assertEqual(component_ids.count(1), 1)

    def test_foundation_fill_can_carry_between_distant_components(self):
        groups = [{
            'color': '#ff0000',
            'type': 'fill',
            'role': 'foundation',
            'segments': [
                [{'x': 0, 'y': 0}, {'x': 10, 'y': 0}],
                [{'x': 350, 'y': 0}, {'x': 360, 'y': 0}],
            ],
            'componentIds': [0, 1],
        }]

        pattern, stitch_count = _build_pattern(groups)
        commands = [stitch[2] for stitch in pattern.stitches]

        self.assertGreaterEqual(stitch_count, 4)
        self.assertNotIn(pyembroidery.TRIM, commands)

    def test_export_trims_long_outline_carries(self):
        groups = [{
            'color': '#ff0000',
            'type': 'outline',
            'role': 'outline',
            'segments': [
                [{'x': 0, 'y': 0}, {'x': 10, 'y': 0}],
                [{'x': 950, 'y': 0}, {'x': 960, 'y': 0}],
            ],
            'componentIds': [0, 1],
        }]

        pattern, stitch_count = _build_pattern(groups)
        commands = [stitch[2] for stitch in pattern.stitches]

        self.assertGreaterEqual(stitch_count, 4)
        self.assertIn(pyembroidery.TRIM, commands)


if __name__ == '__main__':
    unittest.main()
