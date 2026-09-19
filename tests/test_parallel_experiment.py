import unittest

from parallel_experiment import run_parallel_experiment


class ParallelExperimentTests(unittest.TestCase):
    def test_parallel_mode_reduces_turns_and_tokens_without_changing_correctness(self):
        result = run_parallel_experiment()
        self.assertEqual(result["parallel"]["passed"], result["sequential"]["passed"])
        self.assertEqual(result["parallel"]["trials"], 40)
        self.assertEqual(result["parallel"]["pass_rate"], 1.0)
        self.assertLess(result["parallel"]["total_turns"], result["sequential"]["total_turns"])
        self.assertLess(result["parallel"]["tokens_in"], result["sequential"]["tokens_in"])
        self.assertLess(result["parallel"]["cost_usd"], result["sequential"]["cost_usd"])


if __name__ == "__main__":
    unittest.main()
