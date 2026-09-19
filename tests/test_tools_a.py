import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools


class ProblemAToolContractTests(unittest.TestCase):
    def setUp(self):
        if hasattr(tools, "reset_cache"):
            tools.reset_cache()

    def _approval_trace(self, claim_id):
        claim = tools.get_claim(claim_id)
        assert claim is not None
        total = sum(line["amount"] for line in claim["lines"])
        policy_args = {
            "member_id": claim["member_id"],
            "date_of_service": claim["date_of_service"],
            "claim_total": total,
        }
        duplicate_args = {
            "member_id": claim["member_id"],
            "hospital_id": claim["hospital_id"],
            "date_of_service": claim["date_of_service"],
            "lines": claim["lines"],
        }
        line_args = {
            "member_id": claim["member_id"],
            "procedure_code": claim["lines"][0]["code"],
            "attached_documents": claim["documents"],
        }
        return [
            {"tool": "get_claim", "args": {"claim_id": claim_id}, "observation": claim},
            {"tool": "get_policy_context", "args": policy_args, "observation": tools.get_policy_context(**policy_args)},
            {"tool": "find_prior_decision", "args": duplicate_args, "observation": tools.find_prior_decision(**duplicate_args)},
            {"tool": "get_hospital_status", "args": {"hospital_id": claim["hospital_id"]}, "observation": tools.get_hospital_status(claim["hospital_id"])},
            {"tool": "review_claim_line", "args": line_args, "observation": tools.review_claim_line(**line_args)},
        ]

    def test_policy_context_exposes_machine_checkable_boundaries(self):
        result = tools.get_policy_context("M-2214", "2026-09-02", 2480)
        self.assertEqual(result["policy_id"], "POL-3310")
        self.assertEqual(result["remaining"], 9200)
        self.assertTrue(result["policy_active"])
        self.assertTrue(result["service_date_covered"])
        self.assertFalse(result["annual_limit_exceeded"])

    def test_line_review_exposes_required_document_status(self):
        result = tools.review_claim_line("M-5502", "45378", [])
        self.assertEqual(result["required_document"], "itemised_bill")
        self.assertFalse(result["required_document_present"])
        self.assertFalse(result["excluded"])

    def test_line_review_keeps_exclusion_at_line_level(self):
        result = tools.review_claim_line("M-2214", "31255", ["itemised_bill"])
        self.assertTrue(result["excluded"])
        self.assertEqual(result["exclusion_rule"], "EX-14 cosmetic dermatology")
        self.assertFalse(result["requires_preauth"])

    def test_v1_line_return_is_larger_and_less_poka_yoke_than_v2(self):
        args = {
            "member_id": "M-5502",
            "procedure_code": "45378",
            "attached_documents": [],
        }
        v1 = tools.call("A", "review_claim_line", args, internal={"interface_version": "v1"})
        v2 = tools.call("A", "review_claim_line", args, internal={"interface_version": "v2"})
        self.assertNotIn("required_document_present", v1)
        self.assertIn("required_document_present", v2)
        self.assertGreater(len(json.dumps(v1)), len(json.dumps(v2)))

    def test_preauthorisation_distinguishes_valid_expired_and_missing(self):
        valid = tools.get_preauthorisation("M-2214", "62480", "2026-09-02")
        expired = tools.get_preauthorisation("M-6118", "29881", "2026-09-09")
        missing = tools.get_preauthorisation("M-6118", "62480", "2026-09-08")
        self.assertEqual(valid["status"], "valid")
        self.assertEqual(valid["preauth_id"], "PA-5521")
        self.assertEqual(expired["status"], "expired")
        self.assertEqual(expired["preauth_id"], "PA-5640")
        self.assertEqual(missing, {"status": "missing"})

    def test_duplicate_requires_all_four_business_facts(self):
        duplicate = tools.find_prior_decision(
            "M-2214", "H-114", "2026-08-20",
            [{"code": "47120", "amount": 1500}],
        )
        near_miss = tools.find_prior_decision(
            "M-5502", "H-114", "2026-09-15",
            [
                {"code": "99213", "amount": 180},
                {"code": "80053", "amount": 90},
                {"code": "70553", "amount": 620},
                {"code": "45378", "amount": 1100},
            ],
        )
        self.assertEqual(duplicate["claim_id"], "CLM-8710")
        self.assertIsNone(near_miss)

    def test_irreversible_action_appends_one_structured_record(self):
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "decisions.jsonl"
            result = tools.issue_decision_letter(
                claim_id="CLM-8850",
                decision="approve_in_principle",
                lines=[{"code": "99213", "status": "covered", "amount": 180}],
                approved_total=180,
                refused_total=0,
                reason="One covered line.",
                evidence=["get_claim", "get_policy_context", "review_claim_line"],
                evidence_trace=self._approval_trace("CLM-8850"),
                gate={"autonomy": "confirm", "approved": True},
                telemetry={"turns": 4, "tokens_in": 900, "tokens_out": 100, "cost_usd": 0.0012},
                log_path=log_path,
            )
            rows = [json.loads(line) for line in log_path.read_text().splitlines()]
            self.assertEqual(result["recorded"], True)
            self.assertEqual(len(result["receipt_sha256"]), 64)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["claim_id"], "CLM-8850")
            self.assertEqual(rows[0]["approved_total"], 180)
            self.assertEqual(rows[0]["gate"]["autonomy"], "confirm")
            self.assertEqual(rows[0]["turns"], 4)
            self.assertEqual(rows[0]["cost_usd"], 0.0012)

    def test_post_write_fsync_error_recovers_the_exact_persisted_receipt(self):
        trace = self._approval_trace("CLM-8850")
        with tempfile.TemporaryDirectory() as directory:
            with patch("tools.os.fsync", side_effect=OSError("simulated fsync error")):
                result = tools.issue_decision_letter(
                    claim_id="CLM-8850",
                    decision="approve_in_principle",
                    lines=[
                        {
                            "code": "99213",
                            "amount": 180,
                            "status": "covered",
                            "evidence": "POL-6001",
                        }
                    ],
                    approved_total=180,
                    refused_total=0,
                    reason="The line is covered.",
                    evidence=[entry["tool"] for entry in trace],
                    evidence_trace=trace,
                    gate={"autonomy": "confirm", "approved": True},
                    log_path=Path(directory) / "decisions.jsonl",
                )
        self.assertTrue(result["recorded"])
        self.assertTrue(result["recovered_after_write_error"])

    def test_irreversible_action_accepts_a_supported_document_request(self):
        claim = tools.get_claim("CLM-8901")
        assert claim is not None
        policy_args = {
            "member_id": claim["member_id"],
            "date_of_service": claim["date_of_service"],
            "claim_total": sum(line["amount"] for line in claim["lines"]),
        }
        duplicate_args = {
            "member_id": claim["member_id"],
            "hospital_id": claim["hospital_id"],
            "date_of_service": claim["date_of_service"],
            "lines": claim["lines"],
        }
        line_args = {
            "member_id": claim["member_id"],
            "procedure_code": "45378",
            "attached_documents": claim["documents"],
        }
        trace = [
            {"tool": "get_claim", "args": {"claim_id": claim["claim_id"]}, "observation": claim},
            {"tool": "get_policy_context", "args": policy_args, "observation": tools.get_policy_context(**policy_args)},
            {"tool": "find_prior_decision", "args": duplicate_args, "observation": tools.find_prior_decision(**duplicate_args)},
            {"tool": "get_hospital_status", "args": {"hospital_id": claim["hospital_id"]}, "observation": tools.get_hospital_status(claim["hospital_id"])},
            {"tool": "review_claim_line", "args": line_args, "observation": tools.review_claim_line(**line_args)},
        ]
        with tempfile.TemporaryDirectory() as directory:
            result = tools.issue_decision_letter(
                claim_id=claim["claim_id"],
                decision="request_document",
                lines=[],
                approved_total=0,
                refused_total=0,
                missing="itemised bill for line 45378",
                reason="The required itemised bill is absent.",
                evidence=[entry["tool"] for entry in trace],
                evidence_trace=trace,
                gate={"autonomy": "confirm", "approved": True},
                log_path=Path(directory) / "decisions.jsonl",
            )
        self.assertTrue(result["recorded"])
        self.assertEqual(result["decision"], "request_document")

    def test_document_request_rejects_fabricated_resolved_lines(self):
        claim = tools.get_claim("CLM-8901")
        assert claim is not None
        policy_args = {
            "member_id": claim["member_id"],
            "date_of_service": claim["date_of_service"],
            "claim_total": sum(line["amount"] for line in claim["lines"]),
        }
        duplicate_args = {
            "member_id": claim["member_id"],
            "hospital_id": claim["hospital_id"],
            "date_of_service": claim["date_of_service"],
            "lines": claim["lines"],
        }
        line_args = {
            "member_id": claim["member_id"],
            "procedure_code": "45378",
            "attached_documents": claim["documents"],
        }
        trace = [
            {"tool": "get_claim", "args": {"claim_id": claim["claim_id"]}, "observation": claim},
            {"tool": "get_policy_context", "args": policy_args, "observation": tools.get_policy_context(**policy_args)},
            {"tool": "find_prior_decision", "args": duplicate_args, "observation": tools.find_prior_decision(**duplicate_args)},
            {"tool": "get_hospital_status", "args": {"hospital_id": claim["hospital_id"]}, "observation": tools.get_hospital_status(claim["hospital_id"])},
            {"tool": "review_claim_line", "args": line_args, "observation": tools.review_claim_line(**line_args)},
        ]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "request disposition"):
                tools.issue_decision_letter(
                    claim_id=claim["claim_id"],
                    decision="request_document",
                    lines=[
                        {
                            "code": "99213",
                            "amount": 180,
                            "status": "covered",
                            "evidence": "fabricated",
                        }
                    ],
                    approved_total=180,
                    refused_total=0,
                    missing="itemised bill for line 45378",
                    reason="The required itemised bill is absent.",
                    evidence=[entry["tool"] for entry in trace],
                    evidence_trace=trace,
                    gate={"autonomy": "confirm", "approved": True},
                    log_path=Path(directory) / "decisions.jsonl",
                )

    def test_document_request_rejects_skipped_eligibility_checks(self):
        claim = tools.get_claim("CLM-8901")
        assert claim is not None
        line_args = {
            "member_id": claim["member_id"],
            "procedure_code": "45378",
            "attached_documents": claim["documents"],
        }
        trace = [
            {"tool": "get_claim", "args": {"claim_id": claim["claim_id"]}, "observation": claim},
            {"tool": "review_claim_line", "args": line_args, "observation": tools.review_claim_line(**line_args)},
        ]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                tools.issue_decision_letter(
                    claim_id=claim["claim_id"],
                    decision="request_document",
                    lines=[],
                    approved_total=0,
                    refused_total=0,
                    missing="itemised bill for line 45378",
                    reason="The required itemised bill is absent.",
                    evidence=[entry["tool"] for entry in trace],
                    evidence_trace=trace,
                    gate={"autonomy": "confirm", "approved": True},
                    log_path=Path(directory) / "decisions.jsonl",
                )

    def test_document_request_rejects_totals_not_supported_by_resolved_lines(self):
        claim = tools.get_claim("CLM-8901")
        assert claim is not None
        line_args = {
            "member_id": claim["member_id"],
            "procedure_code": "45378",
            "attached_documents": claim["documents"],
        }
        trace = [
            {"tool": "get_claim", "args": {"claim_id": claim["claim_id"]}, "observation": claim},
            {"tool": "review_claim_line", "args": line_args, "observation": tools.review_claim_line(**line_args)},
        ]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                tools.issue_decision_letter(
                    claim_id=claim["claim_id"],
                    decision="request_document",
                    lines=[],
                    approved_total=1150,
                    refused_total=0,
                    missing="itemised bill for line 45378",
                    reason="The required itemised bill is absent.",
                    evidence=[entry["tool"] for entry in trace],
                    evidence_trace=trace,
                    gate={"autonomy": "confirm", "approved": True},
                    log_path=Path(directory) / "decisions.jsonl",
                )

    def test_business_escalation_rejects_line_amounts(self):
        claim = tools.get_claim("CLM-8910")
        assert claim is not None
        policy_args = {
            "member_id": claim["member_id"],
            "date_of_service": claim["date_of_service"],
            "claim_total": sum(line["amount"] for line in claim["lines"]),
        }
        trace = [
            {"tool": "get_claim", "args": {"claim_id": claim["claim_id"]}, "observation": claim},
            {"tool": "get_policy_context", "args": policy_args, "observation": tools.get_policy_context(**policy_args)},
        ]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                tools.issue_decision_letter(
                    claim_id=claim["claim_id"],
                    decision="escalate",
                    lines=[{"code": "99213", "amount": 160, "status": "covered"}],
                    approved_total=160,
                    refused_total=0,
                    trigger="policy_lapsed",
                    escalate_to="human claims assessor",
                    reason="The member policy is lapsed.",
                    evidence=[entry["tool"] for entry in trace],
                    evidence_trace=trace,
                    gate={"autonomy": "confirm", "approved": True},
                    log_path=Path(directory) / "decisions.jsonl",
                )

    def test_duplicate_escalation_rejects_skipped_policy_check(self):
        claim = tools.get_claim("CLM-8933")
        assert claim is not None
        duplicate_args = {
            "member_id": claim["member_id"],
            "hospital_id": claim["hospital_id"],
            "date_of_service": claim["date_of_service"],
            "lines": claim["lines"],
        }
        trace = [
            {"tool": "get_claim", "args": {"claim_id": claim["claim_id"]}, "observation": claim},
            {"tool": "find_prior_decision", "args": duplicate_args, "observation": tools.find_prior_decision(**duplicate_args)},
        ]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                tools.issue_decision_letter(
                    claim_id=claim["claim_id"],
                    decision="escalate",
                    lines=[],
                    approved_total=0,
                    refused_total=0,
                    trigger="duplicate_claim",
                    escalate_to="human claims assessor",
                    reason="The claim duplicates a prior decision.",
                    evidence=[entry["tool"] for entry in trace],
                    evidence_trace=trace,
                    gate={"autonomy": "confirm", "approved": True},
                    log_path=Path(directory) / "decisions.jsonl",
                )

    def test_irreversible_action_accepts_a_supported_business_escalation(self):
        claim = tools.get_claim("CLM-8910")
        assert claim is not None
        policy_args = {
            "member_id": claim["member_id"],
            "date_of_service": claim["date_of_service"],
            "claim_total": sum(line["amount"] for line in claim["lines"]),
        }
        trace = [
            {"tool": "get_claim", "args": {"claim_id": claim["claim_id"]}, "observation": claim},
            {"tool": "get_policy_context", "args": policy_args, "observation": tools.get_policy_context(**policy_args)},
        ]
        with tempfile.TemporaryDirectory() as directory:
            result = tools.issue_decision_letter(
                claim_id=claim["claim_id"],
                decision="escalate",
                lines=[],
                approved_total=0,
                refused_total=0,
                trigger="policy_lapsed",
                escalate_to="human claims assessor",
                reason="The member policy is lapsed.",
                evidence=[entry["tool"] for entry in trace],
                evidence_trace=trace,
                gate={"autonomy": "confirm", "approved": True},
                log_path=Path(directory) / "decisions.jsonl",
            )
        self.assertTrue(result["recorded"])
        self.assertEqual(result["decision"], "escalate")

    def test_approval_rejects_reordered_line_dispositions(self):
        claim = tools.get_claim("CLM-9009")
        assert claim is not None
        total = sum(line["amount"] for line in claim["lines"])
        policy_args = {
            "member_id": claim["member_id"],
            "date_of_service": claim["date_of_service"],
            "claim_total": total,
        }
        duplicate_args = {
            "member_id": claim["member_id"],
            "hospital_id": claim["hospital_id"],
            "date_of_service": claim["date_of_service"],
            "lines": claim["lines"],
        }
        trace = [
            {"tool": "get_claim", "args": {"claim_id": claim["claim_id"]}, "observation": claim},
            {"tool": "get_policy_context", "args": policy_args, "observation": tools.get_policy_context(**policy_args)},
            {"tool": "find_prior_decision", "args": duplicate_args, "observation": tools.find_prior_decision(**duplicate_args)},
            {"tool": "get_hospital_status", "args": {"hospital_id": claim["hospital_id"]}, "observation": tools.get_hospital_status(claim["hospital_id"])},
        ]
        dispositions = []
        for line in claim["lines"]:
            args = {
                "member_id": claim["member_id"],
                "procedure_code": line["code"],
                "attached_documents": claim["documents"],
            }
            review = tools.review_claim_line(**args)
            assert review is not None
            trace.append({"tool": "review_claim_line", "args": args, "observation": review})
            excluded = bool(review["excluded"])
            dispositions.append(
                {
                    "code": line["code"],
                    "amount": line["amount"],
                    "status": "excluded" if excluded else "covered",
                    "evidence": review["exclusion_rule"] if excluded else f"{line['code']} covered",
                }
            )
        rotated_facts = claim["lines"][1:] + claim["lines"][:1]
        mislabelled = [
            {**disposition, "code": fact["code"], "amount": fact["amount"]}
            for disposition, fact in zip(dispositions, rotated_facts)
        ]
        approved = sum(
            line["amount"] for line in mislabelled if line["status"] == "covered"
        )
        refused = sum(
            line["amount"] for line in mislabelled if line["status"] == "excluded"
        )
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "claim line order"):
                tools.issue_decision_letter(
                    claim_id=claim["claim_id"],
                    decision="approve_in_principle",
                    lines=mislabelled,
                    approved_total=approved,
                    refused_total=refused,
                    reason="All lines resolved.",
                    evidence=[entry["tool"] for entry in trace],
                    evidence_trace=trace,
                    gate={"autonomy": "confirm", "approved": True},
                    log_path=Path(directory) / "decisions.jsonl",
                )

    def test_irreversible_action_rejects_incomplete_or_inconsistent_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            common = {
                "claim_id": "CLM-8842",
                "decision": "approve_in_principle",
                "reason": "Incomplete.",
                "evidence": [],
                "evidence_trace": [],
                "gate": {"autonomy": "confirm", "approved": True},
                "log_path": Path(directory) / "decisions.jsonl",
            }
            with self.assertRaisesRegex(ValueError, "one disposition per claim line"):
                tools.issue_decision_letter(
                    lines=[{"code": "47120", "amount": 1400, "status": "covered"}],
                    approved_total=1400,
                    refused_total=0,
                    **common,
                )
            with self.assertRaisesRegex(ValueError, "totals"):
                tools.issue_decision_letter(
                    lines=[
                        {"code": "47120", "amount": 1400, "status": "covered"},
                        {"code": "62480", "amount": 780, "status": "covered"},
                        {"code": "31255", "amount": 300, "status": "excluded"},
                    ],
                    approved_total=999,
                    refused_total=300,
                    **common,
                )


if __name__ == "__main__":
    unittest.main()
