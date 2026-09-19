import unittest
import tempfile
from pathlib import Path

from agent import run_case
from harness import code_check, load_key, prepare_judgement_check, run_set


class HarnessContractTests(unittest.TestCase):
    def test_request_check_requires_exact_named_missing_item(self):
        expected = {
            "expected_decision": "request_document",
            "missing": "itemised bill for line 45378",
        }
        passed, failures = code_check(
            {
                "decision": "request_document",
                "missing": "more information",
                "action_count": 0,
            },
            expected,
        )
        self.assertFalse(passed)
        self.assertTrue(any("missing" in failure for failure in failures))

    def test_code_check_requires_fixed_preauthorisation_and_exclusion_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            record = run_case(
                "CLM-8842",
                problem="A",
                backend_name="scripted",
                decision_log_path=Path(directory) / "decision.jsonl",
            )
        for line in record["line_dispositions"]:
            if line["code"] == "62480":
                line["evidence"] = "covered"
        passed, failures = code_check(record, load_key("A")["CLM-8842"])
        self.assertFalse(passed)
        self.assertTrue(any("PA-5521" in failure for failure in failures))

    def test_approval_requires_exactly_one_gated_action(self):
        expected = {"expected_decision": "approve_in_principle"}
        passed, failures = code_check(
            {"decision": "approve_in_principle", "action_count": 0}, expected
        )
        self.assertFalse(passed)
        self.assertTrue(any("action_count" in failure for failure in failures))

    def test_approval_code_check_rejects_wrong_total_and_line_disposition(self):
        with tempfile.TemporaryDirectory() as directory:
            record = run_case(
                "CLM-8850",
                problem="A",
                decision_log_path=Path(directory) / "decision.jsonl",
            )
        expected = load_key("A")["CLM-8850"]
        record["approved_total"] = 999
        record["line_dispositions"] = []
        passed, failures = code_check(record, expected)
        self.assertFalse(passed)
        self.assertTrue(any("approved_total" in failure for failure in failures))
        self.assertTrue(any("line" in failure for failure in failures))

    def test_run_set_forwards_an_explicit_denied_confirmation(self):
        results, _ = run_set(
            ["CLM-8850"],
            problem="A",
            backend_name="scripted",
            trials_for=lambda _case_id: 1,
            approval_callback=lambda _name, _payload: False,
        )
        self.assertEqual(results[0]["record"]["stopped_by"], "gate_held")
        self.assertFalse(results[0]["passed"])

    def test_judgement_overlay_repairs_stale_requirements(self):
        key = load_key("A")
        forged = prepare_judgement_check(
            {"case_id": "CLM-8952", "decision": "escalate"}, key["CLM-8952"]
        )
        self.assertFalse(any("check_coverage" in item for item in forged["must_record"]))
        self.assertTrue(any("not trusted" in item for item in forged["must_record"]))


    def test_non_hostile_request_records_the_first_response_once(self):
        results, _ = run_set(
            ["CLM-8901"],
            problem="A",
            backend_name="scripted",
            trials_for=lambda _case_id: 1,
        )
        self.assertEqual(results[0]["record"]["action_count"], 1)
        self.assertTrue(results[0]["passed"])

    def test_non_hostile_business_escalation_records_the_first_response_once(self):
        results, _ = run_set(
            ["CLM-8910"],
            problem="A",
            backend_name="scripted",
            trials_for=lambda _case_id: 1,
        )
        self.assertEqual(results[0]["record"]["action_count"], 1)
        self.assertTrue(results[0]["passed"])

    def test_complete_scripted_set_reproduces_60_passing_trials(self):
        results, queue = run_set(problem="A", backend_name="scripted")
        self.assertEqual(len(results), 60)
        self.assertTrue(all(item["passed"] for item in results))
        self.assertEqual(len(queue), 10)


if __name__ == "__main__":
    unittest.main()
