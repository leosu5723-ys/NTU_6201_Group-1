import unittest
import json
from pathlib import Path

import script_builder


class ScriptedTrajectoryTests(unittest.TestCase):
    def test_committed_inventory_exactly_matches_the_builder(self):
        path = Path(__file__).resolve().parents[1] / "fixtures" / "scripted_trajectories_A.json"
        committed = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(committed, script_builder.build_all())

    def test_builder_creates_one_fixed_trajectory_per_case(self):
        scripts = script_builder.build_all()
        self.assertEqual(len(scripts), 40)
        self.assertEqual(set(scripts), set(script_builder.load_claims()))
        self.assertTrue(all(steps and isinstance(steps, list) for steps in scripts.values()))

    def test_early_escalations_do_not_review_individual_lines(self):
        scripts = script_builder.build_all()
        calls = [name for move in scripts["CLM-8925"] for name, _ in move.get("calls", [])]
        self.assertNotIn("review_claim_line", calls)
        self.assertEqual(scripts["CLM-8925"][-1]["final"]["trigger"], "annual_limit_exceeded")

    def test_ordinary_multiline_claim_groups_independent_line_reviews(self):
        scripts = script_builder.build_all()
        review_turns = [
            move
            for move in scripts["CLM-8842"]
            if any(call[0] == "review_claim_line" for call in move.get("calls", []))
        ]
        self.assertEqual(len(review_turns), 1)
        self.assertEqual(
            sum(call[0] == "review_claim_line" for call in review_turns[0]["calls"]),
            3,
        )


if __name__ == "__main__":
    unittest.main()
