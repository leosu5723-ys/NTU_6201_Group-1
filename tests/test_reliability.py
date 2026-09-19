import unittest

from reliability import implied_step_reliability, projected_run_success


class ReliabilityTests(unittest.TestCase):
    def test_implied_step_reliability_works_backwards_from_run_pass_rate(self):
        step = implied_step_reliability(0.78, 6)
        self.assertAlmostEqual(step, 0.9594354633, places=9)
        self.assertAlmostEqual(projected_run_success(step, 3), step ** 3)
        self.assertAlmostEqual(projected_run_success(step, 12), step ** 12)

    def test_invalid_inputs_fail_loudly(self):
        with self.assertRaises(ValueError):
            implied_step_reliability(0.9, 0)
        with self.assertRaises(ValueError):
            implied_step_reliability(1.1, 4)


if __name__ == "__main__":
    unittest.main()
