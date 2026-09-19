import unittest

import prompt
import tools


class PromptContractTests(unittest.TestCase):
    def test_every_callable_tool_has_complete_descriptor(self):
        required = {
            "name",
            "signature",
            "purpose",
            "when",
            "args",
            "returns",
            "failure",
            "irreversible",
        }
        self.assertEqual(set(tools.REGISTRY["A"]), set(tools.DESCRIPTORS))
        for name, descriptor in tools.DESCRIPTORS.items():
            self.assertTrue(required.issubset(descriptor), name)

    def test_system_prompt_marks_narrative_untrusted_and_defines_output(self):
        text = prompt.build_system_prompt("A", version="v2")
        self.assertIn("UNTRUSTED", text)
        self.assertIn("instruction_in_member_narrative", text)
        self.assertIn("issue_decision_letter", text)
        self.assertIn("irreversible", text.lower())
        self.assertIn("request_document", text)

    def test_shared_descriptors_state_nonapproval_prerequisites(self):
        text = prompt.build_system_prompt("A", version="v2")
        self.assertIn("before any ordinary first response", text)
        self.assertIn("before any line-based approval or request", text)

    def test_prompt_records_every_supported_non_hostile_first_response(self):
        text = prompt.build_system_prompt("A", version="v2")
        for decision in ("approve_in_principle", "request_document", "escalate"):
            self.assertIn(f"record {decision}", text)
        self.assertIn("do not call issue_decision_letter", text)

    def test_v1_and_v2_are_distinct_auditable_artifacts(self):
        v1 = prompt.build_system_prompt("A", version="v1")
        v2 = prompt.build_system_prompt("A", version="v2")
        self.assertNotEqual(v1, v2)
        self.assertLess(len(v1), len(v2))

    def test_only_review_claim_line_aci_changes_between_versions(self):
        v1 = prompt.build_system_prompt("A", version="v1")
        v2 = prompt.build_system_prompt("A", version="v2")
        restored = v1.replace(
            prompt.V1_REVIEW_DESCRIPTOR,
            prompt.format_descriptor(tools.DESCRIPTORS["review_claim_line"]),
        )
        self.assertEqual(restored, v2)


if __name__ == "__main__":
    unittest.main()
