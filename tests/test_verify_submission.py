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

    def test_reported_readiness_matches_the_repository_state(self):
        """Readiness must describe the tree as it actually is, at any stage.

        The suite runs both before and after the six live batteries and the ten
        judgement verdicts land, so the reported counts are compared with the
        files present rather than pinned to one stage. Submission must never be
        reported ready while a required gate is still open.
        """
        root = Path(__file__).resolve().parents[1]
        report = verify(run_commands=False)

        self.assertTrue(report["deterministic_ready"])
        self.assertEqual(report["scripted_trials"], 60)
        self.assertEqual(report["scripted_passed"], 60)

        measured = 0
        for path in sorted((root / "results" / "live").glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("metadata", {}).get("kind") == "measured_battery":
                measured += 1
        self.assertEqual(report["live_batteries_found"], measured)

        verdicts = json.loads(
            (root / "review" / "judgement_verdicts.json").read_text(encoding="utf-8")
        )["cases"]
        completed = sum(
            1
            for row in verdicts
            if row.get("verdict") in {"pass", "fail"} and row.get("graded_by")
        )
        self.assertEqual(report["judgement_checks_completed"], completed)

        if report["submission_ready"]:
            self.assertEqual(report["live_batteries_found"], 6)
            self.assertTrue(report["live_set_valid"])
            self.assertTrue(report["judgement_checks_ready"])
            self.assertEqual(report["report_placeholders"], 0)
            self.assertLessEqual(report["report_prose_word_count"], 2000)
            self.assertEqual(report["mandatory_deliverables_missing"], [])
        else:
            self.assertTrue(
                report["live_batteries_found"] < 6
                or not report["live_set_valid"]
                or not report["judgement_checks_ready"]
                or report["report_placeholders"] > 0
                or report["report_prose_word_count"] > 2000
                or bool(report["mandatory_deliverables_missing"])
            )


if __name__ == "__main__":
    unittest.main()
