import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
from ocr_engine import clean_text, strip_us_banners, fix_cn_plate, norm


def process_transcription(raw: str) -> str:
    return fix_cn_plate(strip_us_banners(clean_text(raw)))


class TestTranscriptionRules(unittest.TestCase):

    def test_california_plate(self):
        raw_outputs = [
            "CALIFORNIA\n7ABC123",
            "CALIFORNIA 7ABC123",
            "7ABC123\nTHE GOLDEN STATE",
            "CALIFORNIA\n7ABC123\ndmv.ca.gov",
            "```\nCALIFORNIA\n7ABC123\n```"
        ]
        for raw in raw_outputs:
            processed = process_transcription(raw)
            self.assertEqual(norm(processed), norm("7ABC123"))

    def test_beijing_plate(self):
        raw = "京A·12345"
        processed = process_transcription(raw)
        self.assertIn("京", processed)
        self.assertEqual(norm(processed), norm("京A·12345"))

    def test_new_york_plate(self):
        raw_outputs = [
            "NEW YORK\nJHT 2951\nEMPIRE STATE",
            "JHT 2951",
            "NEW YORK JHT 2951"
        ]
        for raw in raw_outputs:
            processed = process_transcription(raw)
            self.assertEqual(norm(processed), norm("JHT 2951"))

    def test_motion_blurred_plate(self):
        raw = "5XYZ891"
        processed = process_transcription(raw)
        self.assertEqual(norm(processed), norm("5XYZ891"))

    def test_shanghai_plate(self):
        raw = "沪B·88888"
        processed = process_transcription(raw)
        self.assertIn("沪", processed)
        self.assertEqual(norm(processed), norm("沪B·88888"))

    def test_stop_sign(self):
        raw = "STOP"
        processed = process_transcription(raw)
        self.assertEqual(norm(processed), "STOP")

    def test_speed_limit_sign(self):
        raw = "SPEED\nLIMIT\n65"
        processed = process_transcription(raw)
        self.assertEqual(norm(processed), norm("SPEED LIMIT 65"))

    def test_work_zone_sign(self):
        raw = "ROAD\nWORK\nAHEAD"
        processed = process_transcription(raw)
        self.assertEqual(norm(processed), norm("ROAD WORK AHEAD"))

    def test_advisory_speed_plaque(self):
        raw = "35"
        processed = process_transcription(raw)
        self.assertEqual(processed, "35")

    def test_conversational_and_json_stripping(self):
        raw_json = '{\n  "text": "SPEED LIMIT 65"\n}'
        cleaned = clean_text(raw_json)
        self.assertEqual(norm(cleaned), norm("SPEED LIMIT 65"))
        
        raw_chitchat = "Here is the transcription of the sign:\nSTOP"
        cleaned_chitchat = clean_text(raw_chitchat)
        self.assertEqual(norm(cleaned_chitchat), "STOP")


if __name__ == "__main__":
    unittest.main()
