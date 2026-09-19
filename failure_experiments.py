"""D7 reproducible failure experiments on the scripted backend."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import tools
import config
from agent import run_case
from backends import SCRIPTS
from guardrails import Guardrails
from harness import code_check, load_key, run_set, summarise


def _compact(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision": record.get("decision"),
        "trigger": record.get("trigger"),
        "turns": record.get("turns"),
        "tool_calls": len(record.get("evidence", [])),
        "tokens_in": record.get("tokens_in"),
        "tokens_out": record.get("tokens_out"),
        "cost_usd": record.get("cost_usd"),
        "stopped_by": record.get("stopped_by"),
    }


def _loop_failure() -> dict[str, Any]:
    case_id = "CLM-8842"
    working = run_case(case_id, backend_name="scripted", scripted_scripts=SCRIPTS)
    looping = copy.deepcopy(SCRIPTS)
    repeated = copy.deepcopy(looping[case_id][1])
    repeated["thought"] = "Re-read the same evidence because the loop forgot it already did so."
    looping[case_id] = looping[case_id][:2] + [repeated, copy.deepcopy(repeated)] + looping[case_id][2:]

    # Hold the fault-inducing trajectory constant. With the working code, the
    # first repeated action is named and stopped. Removing only the duplicate
    # guard lets the same trajectory burn two extra turns and still look like a
    # correct business result.
    real_check = Guardrails.check_duplicate
    real_token_cap = config.MAX_TOKENS_PER_RUN
    config.MAX_TOKENS_PER_RUN = 100_000
    try:
        injected_with_guard = run_case(
            case_id,
            backend_name="scripted",
            scripted_scripts=looping,
        )
        Guardrails.check_duplicate = lambda self, tool, args: None
        minus_guard = run_case(
            case_id,
            backend_name="scripted",
            scripted_scripts=looping,
        )
    finally:
        Guardrails.check_duplicate = real_check
        config.MAX_TOKENS_PER_RUN = real_token_cap

    return {
        "case_id": case_id,
        "layer": "code / loop control",
        "deleted_component": "action de-duplication",
        "controlled_failure_trajectory": "identical in the guarded and minus-guard conditions",
        "instrumentation": "turns, ordered tool calls, tokens and cost recorded per run",
        "working": _compact(working),
        "fault_injected_with_guard": _compact(injected_with_guard),
        "minus_guard": _compact(minus_guard),
        "finding": "The faulty run still reached the same decision, so pass rate alone would miss the extra turns and cost.",
        "why_other_layers_are_wrong": "A prompt cannot reliably remember for the model; a step cap bounds damage later but does not identify the repeated action.",
    }


class DocumentReactiveBackend:
    """One deterministic backend used unchanged in both interface conditions."""

    name = "scripted"

    def __init__(self):
        self.state = 0
        self.last_usage = {"input_tokens": 0, "output_tokens": 0, "request_id": None}

    def _return(self, move, transcript):
        self.state += 1
        self.last_usage = {
            "input_tokens": 1200 + sum(len(str(item)) for item in transcript) // 4,
            "output_tokens": max(1, len(json.dumps(move)) // 4),
            "request_id": f"scripted:document-interface:{self.state}",
        }
        return move

    def next_move(self, transcript):
        case_id = "CLM-8901"
        claim = tools.get_claim(case_id)
        assert claim is not None
        if self.state == 0:
            return self._return(
                {"thought": "Fetch the claim.", "calls": [["get_claim", {"claim_id": case_id}]]},
                transcript,
            )
        if self.state == 1:
            return self._return(
                {
                    "thought": "Check decisive eligibility and duplicate history.",
                    "calls": [
                        ["get_policy_context", {"member_id": "M-5502", "date_of_service": "2026-09-10", "claim_total": 1150}],
                        ["find_prior_decision", {"member_id": "M-5502", "hospital_id": "H-114", "date_of_service": "2026-09-10", "lines": claim["lines"]}],
                    ],
                },
                transcript,
            )
        if self.state == 2:
            return self._return(
                {
                    "thought": "Read hospital and line facts.",
                    "calls": [
                        ["get_hospital_status", {"hospital_id": "H-114"}],
                        ["review_claim_line", {"member_id": "M-5502", "procedure_code": "45378", "attached_documents": []}],
                    ],
                },
                transcript,
            )
        if self.state == 3:
            observations = json.loads(transcript[-1]["content"])
            line_result = next(
                row["observation"]
                for row in observations
                if row["tool"] == "review_claim_line"
            )
            if line_result.get("required_document_present") is False:
                return self._return(
                    {
                        "thought": "The bounded tool return names a missing itemised bill, so record the request.",
                        "calls": [["issue_decision_letter", {
                            "claim_id": case_id,
                            "decision": "request_document",
                            "lines": [],
                            "approved_total": 0,
                            "refused_total": 0,
                            "missing": "itemised bill for line 45378",
                            "reason": "itemised_bill is required for line 45378 and is not attached.",
                        }]],
                    },
                    transcript,
                )
        if self.state == 4:
            prior_move = json.loads(transcript[-2]["content"])
            prior_decision = prior_move["calls"][0][1]["decision"]
            if prior_decision == "request_document":
                return self._return(
                    {
                        "thought": "The gated request was recorded; return it.",
                        "final": {
                            "decision": "request_document",
                            "missing": "itemised bill for line 45378",
                            "reason": "itemised_bill is required for line 45378 and is not attached.",
                            "line_dispositions": [],
                        },
                    },
                    transcript,
                )
        covered_line = {
            "code": "45378",
            "amount": 1150,
            "status": "covered",
            "evidence": "No document requirement was exposed by the faulty interface.",
        }
        reason = "Line 45378 appeared covered because the tool return omitted its required-document fields."
        if self.state == 3:
            return self._return(
                {
                    "thought": "The missing field is interpreted as no requirement, causing an unsafe approval.",
                    "calls": [["issue_decision_letter", {
                        "claim_id": case_id,
                        "decision": "approve_in_principle",
                        "lines": [covered_line],
                        "approved_total": 1150,
                        "refused_total": 0,
                        "reason": reason,
                    }]],
                },
                transcript,
            )
        return self._return(
            {
                "thought": "Return the approval produced by the missing interface fact.",
                "final": {
                    "decision": "approve_in_principle",
                    "reason": reason,
                    "approved_total": 1150,
                    "refused_total": 0,
                    "line_dispositions": [covered_line],
                },
            },
            transcript,
        )


def _tool_interface_failure() -> dict[str, Any]:
    case_id = "CLM-8901"
    expected = load_key("A")[case_id]
    working_record = run_case(
        case_id,
        backend_name="scripted",
        backend_instance=DocumentReactiveBackend(),
    )
    working_passed, working_failures = code_check(working_record, expected)

    real_function = tools.review_claim_line
    real_registry = tools.REGISTRY["A"]["review_claim_line"]

    def without_document_rule(member_id, procedure_code, attached_documents):
        result = real_function(member_id, procedure_code, attached_documents)
        if result is None:
            return None
        faulty = dict(result)
        faulty["required_document"] = None
        faulty["required_document_present"] = True
        return faulty

    tools.review_claim_line = without_document_rule
    tools.REGISTRY["A"]["review_claim_line"] = without_document_rule
    try:
        faulty_record = run_case(
            case_id,
            backend_name="scripted",
            backend_instance=DocumentReactiveBackend(),
        )
    finally:
        tools.review_claim_line = real_function
        tools.REGISTRY["A"]["review_claim_line"] = real_registry
    faulty_passed, faulty_failures = code_check(faulty_record, expected)

    return {
        "case_id": case_id,
        "layer": "tool interface",
        "deleted_component": "the 45378 required-document rule from review_claim_line",
        "same_reactive_backend_in_both_conditions": True,
        "working": {
            "passed": working_passed,
            "failures": working_failures,
            "record": working_record,
        },
        "minus_document_fields": {
            "passed": faulty_passed,
            "failures": faulty_failures,
            "record": faulty_record,
        },
        "finding": "Removing the document rule converted a required-document request into a longer, more expensive and unsafe approval.",
        "why_other_layers_are_wrong": "A prompt cannot use a fact the tool never returns; loop controls do not repair missing ground truth. The fix belongs in the bounded return schema.",
    }


def run_failure_experiments() -> dict[str, Any]:
    loop = _loop_failure()
    interface = _tool_interface_failure()
    restored_results, _ = run_set(problem="A", backend_name="scripted")
    restoration = summarise(restored_results)
    real_check = Guardrails.check_duplicate
    Guardrails.check_duplicate = lambda self, tool, args: None
    try:
        without_guard_results, _ = run_set(problem="A", backend_name="scripted")
    finally:
        Guardrails.check_duplicate = real_check
    without_guard_summary = summarise(without_guard_results)
    restoration["full_set_without_guard"] = without_guard_summary
    restoration["valid_trajectory_decisions_identical"] = [
        (row["record"].get("decision"), row["record"].get("trigger"))
        for row in restored_results
    ] == [
        (row["record"].get("decision"), row["record"].get("trigger"))
        for row in without_guard_results
    ]
    return {
        "loop_control": loop,
        "tool_interface": interface,
        "restoration": restoration,
    }


def save_failures(path: str | Path = "artifacts/failure_experiments.json") -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(run_failure_experiments(), indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    return destination


if __name__ == "__main__":
    result = run_failure_experiments()
    print(json.dumps(result, indent=2, default=str))
    print(save_failures())
