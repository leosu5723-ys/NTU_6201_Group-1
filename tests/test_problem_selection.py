import unittest

import config


class ProblemSelectionTest(unittest.TestCase):
    def test_submission_targets_problem_a(self):
        self.assertEqual(config.PROBLEM, "A")


if __name__ == "__main__":
    unittest.main()
