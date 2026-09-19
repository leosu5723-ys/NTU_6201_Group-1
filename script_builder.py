"""Compile frozen scripted trajectories from fixture facts.

This module is development tooling for the deterministic backend. It does not use
the answer key and is not the live agent. The generated trajectories are saved as
a reviewable JSON fixture and replayed without inference or network access.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import config
import tools
from guardrails import Guardrails

ROOT = Path(__file__).resolve().parent
SCRIPT_PATH = ROOT / "fixtures" / "scripted_trajectories_A.json"


def load_claim_rows() -> list[dict[str, Any]]:
    path = Path(config.data_root()) / "data_A" / "claims.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_claims() -> dict[str, dict[str, Any]]:
    return {row["claim_id"]: row for row in load_claim_rows()}


def _call(name: str, args: dict[str, Any]) -> list[Any]:
    return [name, args]


def _final_escalation(trigger: str, reason: str) -> dict[str, Any]:
    return {
        "thought": "A fixed escalation trigger has been established, so stop.",
        "final": {
            "decision": "escalate",
            "trigger": trigger,
            "escalate_to": "human claims assessor",
            "reason": reason,
        },
    }


def _recorded_decision_steps(
    case_id: str, final_step: dict[str, Any]
) -> list[dict[str, Any]]:
    final = final_step["final"]
    lines = list(final.get("line_dispositions", []))
    action_args = {
        "claim_id": case_id,
        "decision": final["decision"],
        "lines": lines,
        "approved_total": final.get(
            "approved_total",
            sum(row["amount"] for row in lines if row["status"] == "covered"),
        ),
        "refused_total": final.get(
            "refused_total",
            sum(row["amount"] for row in lines if row["status"] == "excluded"),
        ),
        "reason": final["reason"],
    }
    for field in ("missing", "trigger", "escalate_to"):
        if field in final:
            action_args[field] = final[field]
    return [
        {
            "thought": "The first-response facts are resolved. Record the decision behind the confirmation gate.",
            "calls": [_call("issue_decision_letter", action_args)],
        },
        {
            "thought": "The gated first-response record succeeded; return the structured decision.",
            "final": final,
        },
    ]


def _hostile(narrative: str) -> bool:
    guard = Guardrails(max_turns=1, max_tokens=1, autonomy="confirm")
    return bool(guard.inspect_untrusted_text(narrative))


def build_case(claim: dict[str, Any]) -> list[dict[str, Any]]:
    case_id = claim["claim_id"]
    lines = claim["lines"]
    total = sum(line["amount"] for line in lines)
    steps: list[dict[str, Any]] = [
        {
            "thought": "Fetch the claim. No decision is allowed before this lookup.",
            "calls": [_call("get_claim", {"claim_id": case_id})],
        }
    ]

    if _hostile(claim.get("narrative", "")):
        return steps

    policy_args = {
        "member_id": claim["member_id"],
        "date_of_service": claim["date_of_service"],
        "claim_total": total,
    }
    duplicate_args = {
        "member_id": claim["member_id"],
        "hospital_id": claim["hospital_id"],
        "date_of_service": claim["date_of_service"],
        "lines": lines,
    }
    steps.append(
        {
            "thought": "Policy eligibility and duplicate history can both terminate the run, so check them before pricing individual lines.",
            "calls": [
                _call("get_policy_context", policy_args),
                _call("find_prior_decision", duplicate_args),
            ],
        }
    )
    policy = tools.get_policy_context(**policy_args)
    prior = tools.find_prior_decision(**duplicate_args)
    if policy is None:
        return steps + _recorded_decision_steps(
            case_id,
            _final_escalation("broken_policy_join", "The member-policy join did not resolve."),
        )
    if not policy["policy_active"]:
        return steps + _recorded_decision_steps(
            case_id,
            _final_escalation(
                "policy_lapsed",
                f"{policy['policy_id']} status is lapsed; escalate without reviewing individual lines.",
            ),
        )
    if not policy["service_date_covered"]:
        return steps + _recorded_decision_steps(
            case_id,
            _final_escalation(
                "outside_policy_dates",
                f"Service date {claim['date_of_service']} is outside {policy['policy_id']} dates {policy['start_date']} to {policy['end_date']}.",
            ),
        )
    if policy["annual_limit_exceeded"]:
        return steps + _recorded_decision_steps(
            case_id,
            _final_escalation(
                "annual_limit_exceeded",
                f"Claim total {total} exceeds {policy['remaining']} remaining on {policy['policy_id']}; individual lines were not reviewed.",
            ),
        )
    if prior is not None:
        return steps + _recorded_decision_steps(
            case_id,
            _final_escalation(
                "duplicate_claim",
                f"Prior decision {prior['claim_id']} matches member, hospital, date of service and all lines.",
            ),
        )

    line_calls = [
        _call(
            "review_claim_line",
            {
                "member_id": claim["member_id"],
                "procedure_code": line["code"],
                "attached_documents": claim["documents"],
            },
        )
        for line in lines
    ]
    steps.append(
        {
            "thought": "Hospital status and all per-line reviews are independent after the decisive eligibility checks pass.",
            "calls": [
                _call("get_hospital_status", {"hospital_id": claim["hospital_id"]}),
                *line_calls,
            ],
        }
    )
    hospital = tools.get_hospital_status(claim["hospital_id"])
    reviews = [
        tools.review_claim_line(claim["member_id"], line["code"], claim["documents"])
        for line in lines
    ]
    if hospital is None or any(review is None for review in reviews):
        return steps + _recorded_decision_steps(
            case_id,
            _final_escalation(
                "broken_reference_join", "A hospital or procedure reference did not resolve."
            ),
        )

    dispositions: list[dict[str, Any]] = []
    missing_documents: list[tuple[dict[str, Any], dict[str, Any]]] = []
    preauth_candidates: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for line, review in zip(lines, reviews):
        assert review is not None
        if review["excluded"]:
            dispositions.append(
                {
                    "code": line["code"],
                    "amount": line["amount"],
                    "status": "excluded",
                    "evidence": review["exclusion_rule"],
                }
            )
        elif not review["required_document_present"]:
            missing_documents.append((line, review))
        elif review["requires_preauth"]:
            preauth_candidates.append((line, review))
        else:
            dispositions.append(
                {
                    "code": line["code"],
                    "amount": line["amount"],
                    "status": "covered",
                    "evidence": f"{line['code']} covered under {policy['policy_id']}",
                }
            )

    if missing_documents:
        line, review = missing_documents[0]
        document = str(review["required_document"])
        missing = f"{document.replace('_', ' ')} for line {line['code']}"
        return steps + _recorded_decision_steps(
            case_id,
            {
                "thought": "A required document is absent, so request it specifically and stop.",
                "final": {
                    "decision": "request_document",
                    "missing": missing,
                    "reason": f"{document} is required for line {line['code']} and is not attached.",
                    "line_dispositions": dispositions,
                },
            },
        )

    if preauth_candidates:
        preauth_calls = [
            _call(
                "get_preauthorisation",
                {
                    "member_id": claim["member_id"],
                    "procedure_code": line["code"],
                    "date_of_service": claim["date_of_service"],
                },
            )
            for line, _ in preauth_candidates
        ]
        steps.append(
            {
                "thought": "Only the non-excluded lines marked requires_preauth need this conditional lookup; those lookups are independent.",
                "calls": preauth_calls,
            }
        )
        for line, _ in preauth_candidates:
            result = tools.get_preauthorisation(
                claim["member_id"], line["code"], claim["date_of_service"]
            )
            if result["status"] != "valid":
                if result["status"] == "expired":
                    missing = f"current pre-authorisation for line {line['code']}, valid on {claim['date_of_service']}"
                    detail = f"{result['preauth_id']} ended {result['valid_to']} and does not cover service date {claim['date_of_service']}."
                else:
                    missing = f"pre-authorisation reference for line {line['code']}, valid on {claim['date_of_service']}"
                    detail = f"No valid pre-authorisation was found for line {line['code']} on {claim['date_of_service']}."
                return steps + _recorded_decision_steps(
                    case_id,
                    {
                        "thought": "A required valid pre-authorisation is unavailable, so request it specifically and stop.",
                        "final": {
                            "decision": "request_document",
                            "missing": missing,
                            "reason": detail,
                            "line_dispositions": dispositions,
                        },
                    },
                )
            dispositions.append(
                {
                    "code": line["code"],
                    "amount": line["amount"],
                    "status": "covered",
                    "evidence": f"{result['preauth_id']} valid {result['valid_from']} to {result['valid_to']}",
                }
            )

    order = {line["code"]: index for index, line in enumerate(lines)}
    dispositions.sort(key=lambda row: order[row["code"]])
    approved_total = sum(row["amount"] for row in dispositions if row["status"] == "covered")
    refused_total = sum(row["amount"] for row in dispositions if row["status"] == "excluded")
    panel_text = (
        f"{hospital['hospital_id']} is on panel"
        if hospital["panel"]
        else f"{hospital['hospital_id']} is non-panel in {hospital['country']}"
    )
    line_text = "; ".join(
        f"{row['code']} {row['status']} for {row['amount']} ({row['evidence']})"
        for row in dispositions
    )
    reason = (
        f"{len(dispositions)} lines resolved: {line_text}. {panel_text}. "
        f"approved_total {approved_total}; refused_total {refused_total}. "
        f"Policy {policy['policy_id']} has {policy['remaining']} remaining."
    )
    action_args = {
        "claim_id": case_id,
        "decision": "approve_in_principle",
        "lines": dispositions,
        "approved_total": approved_total,
        "refused_total": refused_total,
        "reason": reason,
    }
    steps.append(
        {
            "thought": "Every line is resolved. Take the single irreversible action behind the confirmation gate.",
            "calls": [_call("issue_decision_letter", action_args)],
        }
    )
    steps.append(
        {
            "thought": "The gated action succeeded; return the structured decision.",
            "final": {
                "decision": "approve_in_principle",
                "reason": reason,
                "approved_total": approved_total,
                "refused_total": refused_total,
                "line_dispositions": dispositions,
            },
        }
    )
    return steps


def build_all() -> dict[str, list[dict[str, Any]]]:
    tools.reset_cache()
    return {claim["claim_id"]: build_case(claim) for claim in load_claim_rows()}


def write_scripts(path: Path = SCRIPT_PATH) -> Path:
    scripts = build_all()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scripts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    output = write_scripts()
    print(f"Wrote {len(build_all())} scripted trajectories to {output}")
