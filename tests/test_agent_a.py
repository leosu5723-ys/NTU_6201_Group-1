import copy
import tempfile
import unittest
from pathlib import Path

import config
import prompt
from backends import ScriptedBackend, _parse_move
from agent import _validate_move, run_case


class AgentContractTests(unittest.TestCase):
    def test_parser_accepts_exactly_one_json_fence_without_prose(self):
        move = _parse_move(
            '```json\n{"final":{"decision":"escalate","trigger":"manual_review",'
            '"escalate_to":"human claims assessor","reason":"Needs review."}}\n```'
        )
        self.assertEqual(move["final"]["decision"], "escalate")

        rejected = _parse_move(
            'Here is the result:\n```json\n{"final":{"decision":"escalate",'
            '"trigger":"manual_review","escalate_to":"human claims assessor",'
            '"reason":"Needs review."}}\n```'
        )
        self.assertIn("parse_error", rejected)

    def test_move_schema_rejects_both_calls_and_final(self):
        with self.assertRaises(ValueError):
            _validate_move({"thought": "bad", "calls": [], "final": {"decision": "escalate"}})

    def test_final_schema_requires_decision_specific_fields(self):
        with self.assertRaises(ValueError):
            _validate_move({"final": {"decision": "approve_in_principle"}})

    def test_partly_payable_claim_runs_end_to_end_in_five_safe_turns(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_case(
                "CLM-8842",
                problem="A",
                decision_log_path=Path(directory) / "decisions.jsonl",
            )
        self.assertEqual(result["decision"], "approve_in_principle")
        self.assertEqual(result["turns"], 5)
        self.assertEqual(result["approved_total"], 2180)
        self.assertEqual(result["refused_total"], 300)
        self.assertEqual(result["action_count"], 1)
        self.assertEqual(result["stopped_by"], None)
        self.assertTrue(result["action_receipt"]["recorded"])
        self.assertEqual(
            result["persisted_decision"]["decision"], "approve_in_principle"
        )
        self.assertIn("get_preauthorisation", result["evidence"])
        self.assertEqual(len(result["line_dispositions"]), 3)
        self.assertEqual(len(result["observation_metrics"]), len(result["evidence"]))
        self.assertGreater(result["observation_tokens_estimate"], 0)

    def test_premature_final_gets_one_bounded_action_recovery_turn(self):
        class PrematureFinalBackend:
            name = "scripted"
            raw_responses = []

            def __init__(self):
                self.inner = ScriptedBackend(
                    "CLM-8850", prompt.build_system_prompt("A", version="v2")
                )
                self.last_usage = self.inner.last_usage
                self.postponed = None
                self.injected = False

            def next_move(self, transcript):
                if self.postponed is not None:
                    move, self.postponed = self.postponed, None
                    return move
                move = self.inner.next_move(transcript)
                self.last_usage = self.inner.last_usage
                if not self.injected and "calls" in move and move["calls"][0][0] == "issue_decision_letter":
                    self.injected = True
                    self.postponed = move
                    args = move["calls"][0][1]
                    return {
                        "final": {
                            "decision": args["decision"],
                            "reason": args["reason"],
                            "approved_total": args["approved_total"],
                            "refused_total": args["refused_total"],
                            "line_dispositions": args["lines"],
                        }
                    }
                return move

        result = run_case(
            "CLM-8850", backend_instance=PrematureFinalBackend()
        )
        self.assertEqual(result["decision"], "approve_in_principle")
        self.assertEqual(result["action_count"], 1)
        self.assertIsNone(result["stopped_by"])

    def test_correctable_decision_tool_error_is_returned_to_model(self):
        class CorrectingBackend:
            name = "scripted"
            raw_responses = []

            def __init__(self):
                self.inner = ScriptedBackend(
                    "CLM-8850", prompt.build_system_prompt("A", version="v2")
                )
                self.last_usage = self.inner.last_usage
                self.correct_call = None
                self.injected = False

            def next_move(self, transcript):
                if self.correct_call is not None:
                    move, self.correct_call = self.correct_call, None
                    return move
                move = self.inner.next_move(transcript)
                self.last_usage = self.inner.last_usage
                if not self.injected and "calls" in move and move["calls"][0][0] == "issue_decision_letter":
                    self.injected = True
                    self.correct_call = move
                    broken = copy.deepcopy(move)
                    broken["calls"][0][1]["approved_total"] = 0
                    return broken
                return move

        result = run_case("CLM-8850", backend_instance=CorrectingBackend())
        self.assertEqual(result["decision"], "approve_in_principle")
        self.assertEqual(result["action_count"], 1)
        self.assertIsNone(result["stopped_by"])

    def test_one_invalid_move_schema_is_returned_for_correction(self):
        class CorrectingMoveBackend:
            name = "scripted"
            raw_responses = []

            def __init__(self):
                self.inner = ScriptedBackend(
                    "CLM-8850", prompt.build_system_prompt("A", version="v2")
                )
                self.last_usage = self.inner.last_usage
                self.first = True

            def next_move(self, transcript):
                if self.first:
                    self.first = False
                    return {"thought": "Malformed empty call.", "calls": []}
                move = self.inner.next_move(transcript)
                self.last_usage = self.inner.last_usage
                return move

        result = run_case("CLM-8850", backend_instance=CorrectingMoveBackend())
        self.assertEqual(result["decision"], "approve_in_principle")
        self.assertEqual(result["action_count"], 1)
        self.assertIsNone(result["stopped_by"])

    def test_hostile_narrative_escalates_before_irreversible_action(self):
        result = run_case("CLM-8941", problem="A")
        self.assertEqual(result["decision"], "escalate")
        self.assertEqual(result["trigger"], "instruction_in_member_narrative")
        self.assertEqual(result["action_count"], 0)
        self.assertIn("hostile_input", [x["guardrail"] for x in result["guardrails_fired"]])

    def test_scripted_timing_is_normalised_for_reproducible_artifacts(self):
        first = run_case("CLM-8850", problem="A", backend_name="scripted")
        second = run_case("CLM-8850", problem="A", backend_name="scripted")
        self.assertEqual(first["seconds"], 0.0)
        self.assertEqual(second["seconds"], 0.0)

    def test_live_preflight_blocks_oversized_request_before_spending(self):
        class OversizedBackend:
            name = "live"
            raw_responses = []
            last_usage = {}
            called = False

            def estimated_next_input_tokens(self, transcript):
                return config.MAX_TOKENS_PER_RUN + 1

            def next_move(self, transcript):
                self.called = True
                raise AssertionError("paid call should not happen")

        backend = OversizedBackend()
        result = run_case("CLM-8850", problem="A", backend_instance=backend)
        self.assertFalse(backend.called)
        self.assertEqual(result["stopped_by"], "budget_ceiling")

    def test_live_run_preserves_provider_billed_cost_and_usage_details(self):
        class CostBackend:
            name = "live"
            raw_responses = []
            last_usage = {
                "input_tokens": 100,
                "output_tokens": 20,
                "request_id": "req-cost",
                "provider_cost_usd": 0.0042,
                "usage_details": {"cost": 0.0042, "prompt_tokens": 100},
                "http_attempts": 1,
            }

            def next_move(self, transcript):
                return {
                    "final": {
                        "decision": "escalate",
                        "trigger": "manual_review",
                        "escalate_to": "human claims assessor",
                        "reason": "Test final.",
                    }
                }

        result = run_case("CLM-8850", problem="A", backend_instance=CostBackend())
        # A premature final receives one bounded corrective turn; both provider
        # calls remain fully accounted for.
        self.assertEqual(result["provider_cost_usd"], 0.0084)
        self.assertEqual(result["provider_usage"][0]["cost"], 0.0042)

    def test_action_first_approval_is_rejected_without_trusted_evidence(self):
        scripts = {
            "CLM-8850": [
                {
                    "thought": "Unsafe shortcut.",
                    "calls": [["issue_decision_letter", {
                        "claim_id": "CLM-8850",
                        "decision": "approve_in_principle",
                        "lines": [{"code": "99213", "amount": 180, "status": "covered", "evidence": "guessed"}],
                        "approved_total": 180,
                        "refused_total": 0,
                        "reason": "guessed",
                    }]],
                }
            ]
        }
        confirmations = []
        result = run_case(
            "CLM-8850",
            problem="A",
            scripted_scripts=scripts,
            approve=lambda name, payload: confirmations.append((name, payload)) or True,
        )
        self.assertEqual(result["stopped_by"], "tool_or_schema_error")
        self.assertEqual(result["action_count"], 0)
        self.assertEqual(confirmations, [])

    def test_only_one_recoverable_tool_validation_error_is_allowed(self):
        scripts = {
            "CLM-8850": [
                {"calls": [["unknown_tool", {}]]},
                {"calls": [["another_unknown_tool", {}]]},
            ]
        }
        result = run_case("CLM-8850", problem="A", scripted_scripts=scripts)
        self.assertEqual(result["stopped_by"], "recoverable_tool_error_cap")
        self.assertEqual(result["action_count"], 0)

    def test_final_outcome_must_match_the_recorded_gated_action(self):
        class MismatchBackend:
            name = "scripted"
            raw_responses = []

            def __init__(self):
                self.inner = ScriptedBackend(
                    "CLM-8850", prompt.build_system_prompt("A", version="v2")
                )
                self.last_usage = self.inner.last_usage

            def next_move(self, transcript):
                move = self.inner.next_move(transcript)
                self.last_usage = self.inner.last_usage
                if "final" in move:
                    move["final"] = {
                        "decision": "escalate",
                        "trigger": "manual_review",
                        "escalate_to": "human claims assessor",
                        "reason": "Contradicts the recorded approval.",
                    }
                return move

        result = run_case(
            "CLM-8850", problem="A", backend_instance=MismatchBackend()
        )
        self.assertEqual(result["decision"], "escalate")
        self.assertEqual(result["trigger"], "action_integrity_error")
        self.assertEqual(result["stopped_by"], "action_integrity_error")

    def test_unexpected_live_response_error_becomes_scored_failure(self):
        class BrokenPayloadBackend:
            name = "live"
            last_usage = {}
            raw_responses = []

            def next_move(self, transcript):
                raise IndexError("missing choice")

        result = run_case("CLM-8850", problem="A", backend_instance=BrokenPayloadBackend())
        self.assertEqual(result["decision"], "escalate")
        self.assertEqual(result["trigger"], "backend_error")

    def test_backend_error_becomes_a_scored_failure_instead_of_crashing_batch(self):
        class FailingBackend:
            name = "live"
            last_usage = {"input_tokens": 0, "output_tokens": 0, "request_id": None}
            raw_responses = []

            def next_move(self, transcript):
                raise RuntimeError("provider unavailable")

        result = run_case(
            "CLM-8850",
            problem="A",
            backend_name="live",
            backend_instance=FailingBackend(),
        )
        self.assertEqual(result["decision"], "escalate")
        self.assertEqual(result["trigger"], "backend_error")
        self.assertEqual(result["stopped_by"], "backend_error")


if __name__ == "__main__":
    unittest.main()
