import json
import unittest
from pathlib import Path

import config

ROOT = Path(__file__).resolve().parents[1]


class EvaluationSetContractTests(unittest.TestCase):
    def test_label_first_plan_has_25_unique_new_cases(self):
        plan = json.loads((ROOT / "design/additional_cases_A.json").read_text())
        ids = [item["claim"]["claim_id"] for item in plan]
        self.assertEqual(len(plan), 25)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(item["label"]["case_id"] == item["claim"]["claim_id"] for item in plan))
        self.assertEqual(
            sum(item["label"]["expected_decision"] != "approve_in_principle" for item in plan),
            1,
        )

    def test_generated_set_has_40_cases_and_exactly_10_negatives(self):
        data_root = Path(config.data_root())
        claims = json.loads((data_root / "data_A/claims.json").read_text())
        labels = json.loads((data_root / "expected_outcomes_A.json").read_text())
        self.assertEqual(len(claims), 40)
        self.assertEqual(len(labels), 40)
        self.assertEqual({c["claim_id"] for c in claims}, {x["case_id"] for x in labels})
        negatives = [x for x in labels if x["expected_decision"] != "approve_in_principle"]
        self.assertEqual(len(negatives), 10)
        hostile = [x for x in labels if x.get("trigger") == "instruction_in_member_narrative"]
        self.assertGreaterEqual(len(hostile), 3)

    def test_every_planned_addition_matches_generated_claim_label_and_code_oracle(self):
        plan = json.loads((ROOT / "design/additional_cases_A.json").read_text())
        data_root = Path(config.data_root())
        claims = {
            row["claim_id"]: row
            for row in json.loads((data_root / "data_A/claims.json").read_text())
        }
        labels = {
            row["case_id"]: row
            for row in json.loads((data_root / "expected_outcomes_A.json").read_text())
        }
        oracle = json.loads(
            (ROOT / "evaluation/code_expectations_A.json").read_text()
        )["cases"]
        for item in plan:
            case_id = item["claim"]["claim_id"]
            self.assertEqual(item["claim"], claims[case_id])
            self.assertEqual(item["label"], labels[case_id])
            self.assertEqual(
                oracle[case_id]["decision"], item["label"]["expected_decision"]
            )


if __name__ == "__main__":
    unittest.main()
