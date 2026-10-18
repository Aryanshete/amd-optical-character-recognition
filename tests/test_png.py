import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
from ocr_engine import load_image


class TestPNGProcessing(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_img_path = Path(self.temp_dir.name) / "test_plate.png"
        img = Image.new("RGBA", (320, 160), color=(255, 255, 255, 255))
        img.save(self.test_img_path, "PNG")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_png_loading(self):
        loaded = load_image(str(self.test_img_path))
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.mode, "RGB")
        self.assertGreaterEqual(max(loaded.size), 640)


if __name__ == "__main__":
    unittest.main()
