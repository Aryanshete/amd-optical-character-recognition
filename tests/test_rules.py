import unittest
from ocr.postprocessor import (
    postprocess_transcription,
    evaluator_normalize,
    clean_markdown_and_wrappers
)


class TestTranscriptionRules(unittest.TestCase):

    def test_california_plate(self):
        raw_outputs = [
            "CALIFORNIA\n7ABC123",
            "CALIFORNIA 7ABC123",
            "7ABC123\nTHE GOLDEN STATE",
            "CALIFORNIA\n7ABC123\nDMV.CA.GOV",
            "```\nCALIFORNIA\n7ABC123\n```"
        ]
        for raw in raw_outputs:
            processed = postprocess_transcription(raw)
            self.assertEqual(evaluator_normalize(processed), evaluator_normalize("7ABC123"))

    def test_beijing_plate(self):
        raw = "京A·12345"
        processed = postprocess_transcription(raw)
        self.assertIn("京", processed)
        self.assertEqual(evaluator_normalize(processed), evaluator_normalize("京A·12345"))

    def test_new_york_plate(self):
        raw_outputs = [
            "NEW YORK\nJHT 2951\nEMPIRE STATE",
            "JHT 2951",
            "NEW YORK JHT 2951"
        ]
        for raw in raw_outputs:
            processed = postprocess_transcription(raw)
            self.assertEqual(evaluator_normalize(processed), evaluator_normalize("JHT 2951"))

    def test_motion_blurred_plate(self):
        raw = "5XYZ891"
        processed = postprocess_transcription(raw)
        self.assertEqual(evaluator_normalize(processed), evaluator_normalize("5XYZ891"))

    def test_shanghai_plate(self):
        raw = "沪B·88888"
        processed = postprocess_transcription(raw)
        self.assertIn("沪", processed)
        self.assertEqual(evaluator_normalize(processed), evaluator_normalize("沪B·88888"))

    def test_stop_sign(self):
        raw = "STOP"
        processed = postprocess_transcription(raw)
        self.assertEqual(evaluator_normalize(processed), "STOP")

    def test_speed_limit_sign(self):
        raw = "SPEED\nLIMIT\n65"
        processed = postprocess_transcription(raw)
        self.assertEqual(processed, "SPEED LIMIT 65")
        self.assertEqual(evaluator_normalize(processed), evaluator_normalize("SPEED LIMIT 65"))

    def test_work_zone_sign(self):
        raw = "ROAD\nWORK\nAHEAD"
        processed = postprocess_transcription(raw)
        self.assertEqual(processed, "ROAD WORK AHEAD")
        self.assertEqual(evaluator_normalize(processed), evaluator_normalize("ROAD WORK AHEAD"))

    def test_advisory_speed_plaque(self):
        raw = "35"
        processed = postprocess_transcription(raw)
        self.assertEqual(processed, "35")

    def test_conversational_and_json_stripping(self):
        raw_json = '{\n  "text": "SPEED LIMIT 65"\n}'
        cleaned = clean_markdown_and_wrappers(raw_json)
        self.assertNotIn("text", cleaned)
        
        raw_chitchat = "Here is the transcription of the sign:\nSTOP"
        cleaned_chitchat = clean_markdown_and_wrappers(raw_chitchat)
        self.assertEqual(cleaned_chitchat, "STOP")


if __name__ == "__main__":
    unittest.main()
