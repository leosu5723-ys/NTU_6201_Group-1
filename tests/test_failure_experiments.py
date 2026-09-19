import unittest

from failure_experiments import run_failure_experiments


class FailureExperimentTests(unittest.TestCase):
    def test_two_distinct_failures_are_reproduced_and_recovered(self):
        result = run_failure_experiments()
        self.assertEqual(set(result), {"loop_control", "tool_interface", "restoration"})

        loop = result["loop_control"]
        self.assertEqual(loop["fault_injected_with_guard"]["stopped_by"], "duplicate_action")
        self.assertEqual(loop["minus_guard"]["stopped_by"], None)
        self.assertEqual(loop["working"]["decision"], loop["minus_guard"]["decision"])
        self.assertGreater(loop["minus_guard"]["turns"], loop["working"]["turns"])
        self.assertGreater(loop["minus_guard"]["cost_usd"], loop["working"]["cost_usd"])

        interface = result["tool_interface"]
        self.assertTrue(interface["same_reactive_backend_in_both_conditions"])
        self.assertTrue(interface["working"]["passed"])
        self.assertFalse(interface["minus_document_fields"]["passed"])
        self.assertEqual(interface["minus_document_fields"]["record"]["decision"], "approve_in_principle")

        self.assertEqual(result["restoration"]["passed"], 60)
        self.assertEqual(result["restoration"]["trials"], 60)
        self.assertTrue(result["restoration"]["valid_trajectory_decisions_identical"])
        self.assertEqual(result["restoration"]["full_set_without_guard"]["passed"], 60)


if __name__ == "__main__":
    unittest.main()
