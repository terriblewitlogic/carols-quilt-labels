import base64
import io
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'functions' / 'image_to_jef'))
sys.path.insert(0, str(ROOT / 'tests'))

import pyembroidery  # noqa: E402
from pyembroidery import EmbPattern  # noqa: E402
from benchmark_stitch import measure  # noqa: E402
from image_to_jef import READ_ONLY_FORMATS, SUPPORTED_FORMATS, _build_pattern, handler  # noqa: E402
from raster_to_stitches import raster_to_stitch_groups  # noqa: E402


def _sample_image_b64():
    img = Image.new('RGB', (120, 90), '#f5f0eb')
    d = ImageDraw.Draw(img)
    d.ellipse((12, 10, 62, 62), fill='#d04170')
    d.polygon([(70, 12), (110, 32), (92, 78), (58, 64)], fill='#3a7a9a')
    d.ellipse((80, 28, 88, 36), fill='#101010')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def _roundtrip(pattern, fmt):
    with tempfile.NamedTemporaryFile(suffix=f'.{fmt}', delete=False) as tmp:
        path = Path(tmp.name)
    try:
        pyembroidery.write(pattern, str(path))
        return measure(EmbPattern(str(path)))
    finally:
        try:
            path.unlink()
        except OSError:
            pass


class MultiFormatExportTests(unittest.TestCase):
    def test_supported_formats_preserve_stitch_geometry(self):
        groups, _svg, _palette = raster_to_stitch_groups(
            _sample_image_b64(),
            hoop_w_mm=55,
            hoop_h_mm=45,
            num_colors=4,
            density_mm=0.7,
            min_feature_mm=0.8,
            outline='running',
            outline_policy='selective',
        )
        pattern, _stitch_count = _build_pattern(groups)

        baseline = _roundtrip(pattern, 'jef')
        for fmt in sorted(SUPPORTED_FORMATS - {'jef'}):
            with self.subTest(fmt=fmt):
                metrics = _roundtrip(pattern, fmt)

                self.assertLessEqual(abs(metrics['stitch_count'] - baseline['stitch_count']), 8)
                self.assertLessEqual(abs(metrics['color_blocks'] - baseline['color_blocks']), 1)
                self.assertLessEqual(abs(metrics['bbox_w_mm'] - baseline['bbox_w_mm']), 0.5)
                self.assertLessEqual(abs(metrics['bbox_h_mm'] - baseline['bbox_h_mm']), 0.5)
                self.assertLessEqual(abs(metrics['p99_mm'] - baseline['p99_mm']), 0.5)

    def test_read_only_formats_return_actionable_error(self):
        for fmt in sorted(READ_ONLY_FORMATS):
            with self.subTest(fmt=fmt):
                result = handler({
                    'httpMethod': 'POST',
                    'body': (
                        '{"imageBase64": "%s", "format": "%s", '
                        '"hoop_w_mm": 55, "hoop_h_mm": 45}'
                    ) % (_sample_image_b64(), fmt),
                }, {})

                self.assertEqual(result['statusCode'], 400)
                self.assertIn('not exportable', result['body'])


if __name__ == '__main__':
    unittest.main()
