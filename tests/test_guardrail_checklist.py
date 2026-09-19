import unittest

from guardrail_harness import run_checklist


class GuardrailChecklistTests(unittest.TestCase):
    def test_checklist_has_ten_passing_cases_and_three_hostile_inputs(self):
        rows = run_checklist()
        self.assertEqual(len(rows), 10)
        self.assertTrue(all(row["passed"] for row in rows))
        self.assertGreaterEqual(sum(row["category"] == "hostile_input" for row in rows), 3)
        self.assertTrue(all(row["wrong_behaviour_caught"] for row in rows))
        self.assertTrue(all(row["observed"] for row in rows))


if __name__ == "__main__":
    unittest.main()
