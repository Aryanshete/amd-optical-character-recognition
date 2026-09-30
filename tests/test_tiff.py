import json
import unittest
import tempfile
from pathlib import Path
from PIL import Image

from app import process_image, determine_output_path
from ocr.preprocessor import preprocess_image_file


class TestTIFFProcessing(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_img_path = Path(self.temp_dir.name) / "test_sign_noisy.tiff"
        img = Image.new("RGB", (280, 280), color=(100, 100, 100))
        img.save(self.test_img_path, "TIFF")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_tiff_pipeline(self):
        enhanced = preprocess_image_file(str(self.test_img_path))
        self.assertIsNotNone(enhanced)
        self.assertEqual(enhanced.mode, "RGB")

        out_path = determine_output_path(str(self.test_img_path), custom_output_dir=self.temp_dir.name)
        self.assertEqual(out_path.name, "test_sign_noisy_output.json")

        result = process_image(str(self.test_img_path), out_path)
        self.assertTrue(out_path.exists())

        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("text", data)
        self.assertIsInstance(data["text"], str)
        self.assertIn("confidence", data)
        self.assertIsInstance(data["confidence"], (int, float))
        self.assertGreaterEqual(data["confidence"], 0.0)
        self.assertLessEqual(data["confidence"], 1.0)


if __name__ == "__main__":
    unittest.main()
