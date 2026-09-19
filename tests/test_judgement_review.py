import unittest
import json
from pathlib import Path

import judgement_review
from harness import JUDGEMENT_CASE_IDS


class JudgementReviewTests(unittest.TestCase):
    def test_review_surface_includes_trajectory_checks(self):
        text = judgement_review.build()
        self.assertIn("Trajectory checks", text)
        self.assertIn("the run exits before review_claim_line", text)

    def test_overlay_requirements_are_not_applied_twice(self):
        text = judgement_review.build()
        block = text.split("## CLM-8925", 1)[1].split("## ", 1)[0]
        bullets = [line for line in block.splitlines() if line.startswith("- [ ]")]
        self.assertEqual(len(bullets), len(set(bullets)))

    def test_every_judgement_overlay_is_reachable(self):
        root = Path(__file__).resolve().parents[1]
        overlays = json.loads(
            (root / "evaluation/judgement_requirements_A.json").read_text()
        )
        self.assertTrue(set(overlays).issubset(JUDGEMENT_CASE_IDS))


if __name__ == "__main__":
    unittest.main()
