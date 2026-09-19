import unittest

from result_tables import build_markdown


class ResultTableTests(unittest.TestCase):
    def test_markdown_uses_saved_scripted_evidence_and_marks_live_pending(self):
        text = build_markdown()
        self.assertIn("60 / 60", text)
        self.assertIn("251", text)
        self.assertIn("157", text)
        self.assertIn("LIVE RUN PENDING", text)
        self.assertIn("## Per-case grading map", text)
        self.assertIn("| CLM-8842 |", text)
        self.assertIn("Human judgement", text)


if __name__ == "__main__":
    unittest.main()
