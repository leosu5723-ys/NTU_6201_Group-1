import json
import unittest
import tempfile
from pathlib import Path

from verify_submission import (
    validate_case_author_signoff,
    validate_mandatory_deliverables,
    verify,
)


class VerificationTests(unittest.TestCase):
    def test_case_signoff_requires_case_linked_work_for_every_assignment(self):
        root = Path(__file__).resolve().parents[1]
        payload = json.loads(
            (root / "review/case_author_signoff_template.json").read_text()
        )
        for member in payload["members"]:
            member["signed"] = True
            member["date"] = "2026-09-08"
            member["case_records"] = [
                {
                    "case_id": case_id,
                    "decision_review": "Checked against Appendix A.",
                    "authorship_or_revision": "Added a case-specific rationale.",
                }
                for case_id in member["case_ids"]
            ]
        self.assertTrue(validate_case_author_signoff(payload))
        payload["members"][0]["case_records"] = payload["members"][0]["case_records"][:1]
        self.assertFalse(validate_case_author_signoff(payload))

    def test_empty_placeholder_files_do_not_satisfy_mandatory_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in (
                "submission/PE6201_A2_Report.pdf",
                "submission/PE6201_A2_Team_Self_Appraisal.pdf",
                "submission/VIDEO_LINK.txt",
                "submission/FINAL_APPROVAL.json",
                "submission/PE6201_A2_B-1.zip",
                "review/case_author_signoff.json",
            ):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"")
            failures = validate_mandatory_deliverables(root)
            self.assertIn("submission/VIDEO_LINK.txt: invalid or empty", failures)
            self.assertIn("submission/FINAL_APPROVAL.json: invalid approval", failures)
            self.assertIn("review/case_author_signoff.json: invalid sign-off", failures)

    def test_current_candidate_is_deterministically_ready_but_live_pending(self):
        report = verify(run_commands=False)
        self.assertTrue(report["deterministic_ready"])
        self.assertFalse(report["submission_ready"])
        self.assertEqual(report["live_batteries_found"], 0)
        self.assertEqual(report["judgement_checks_completed"], 0)
        self.assertFalse(report["judgement_checks_ready"])
        self.assertIn("submission/PE6201_A2_Report.pdf", report["mandatory_deliverables_missing"])
        self.assertGreater(report["report_placeholders"], 0)


if __name__ == "__main__":
    unittest.main()
