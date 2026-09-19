"""Problem A tool layer for PE6201 A2.

Each public tool returns one bounded business fact. The model never receives the
fixture tables directly. Tool signatures are designed so calls grouped in one
turn have no hidden data dependency.
"""
from __future__ import annotations

import hashlib
import fcntl
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import config

_CACHE: dict[tuple[str, str], Any] = {}


def reset_cache() -> None:
    """Clear fixture caches after regeneration or between isolated tests."""
    _CACHE.clear()


def _load(table: str) -> Any:
    key = ("A", table)
    if key not in _CACHE:
        path = os.path.join(config.data_root(), "data_A", f"{table}.json")
        with open(path, encoding="utf-8") as handle:
            _CACHE[key] = json.load(handle)
    return _CACHE[key]


def _member_and_policy(member_id: str) -> tuple[dict[str, Any], dict[str, Any]] | None:
    member = next((row for row in _load("members") if row["member_id"] == member_id), None)
    if member is None:
        return None
    policy = next(
        (row for row in _load("policies") if row["policy_id"] == member["policy_id"]),
        None,
    )
    if policy is None:
        return None
    return member, policy


def get_claim(claim_id: str) -> dict[str, Any] | None:
    """Return the claim queue row identified by ``claim_id``."""
    return next((row for row in _load("claims") if row["claim_id"] == claim_id), None)


def get_policy_context(
    member_id: str,
    date_of_service: str,
    claim_total: int | float,
) -> dict[str, Any] | None:
    """Return policy facts and explicit boundary checks for one claim."""
    resolved = _member_and_policy(member_id)
    if resolved is None:
        return None
    member, policy = resolved
    remaining = policy["annual_limit"] - policy["used_to_date"]
    return {
        "member_id": member_id,
        "policy_id": policy["policy_id"],
        "product": policy["product"],
        "status": policy["status"],
        "policy_active": policy["status"] == "active",
        "start_date": policy["start_date"],
        "end_date": policy["end_date"],
        "service_date_covered": policy["start_date"] <= date_of_service <= policy["end_date"],
        "annual_limit": policy["annual_limit"],
        "used_to_date": policy["used_to_date"],
        "remaining": remaining,
        "claim_total": claim_total,
        "annual_limit_exceeded": claim_total > remaining,
    }


def review_claim_line(
    member_id: str,
    procedure_code: str,
    attached_documents: list[str],
) -> dict[str, Any] | None:
    """Return all fixed system-of-record facts needed to resolve one claim line."""
    resolved = _member_and_policy(member_id)
    procedure = next(
        (row for row in _load("procedures") if row["code"] == procedure_code),
        None,
    )
    if resolved is None or procedure is None:
        return None
    _, policy = resolved
    exclusion = next(
        (row for row in policy.get("exclusions", []) if row["code"] == procedure_code),
        None,
    )
    document_rule = next(
        (
            row
            for row in _load("required_documents")
            if row["procedure_code"] == procedure_code
        ),
        None,
    )
    required_document = document_rule["document"] if document_rule else None
    return {
        "code": procedure_code,
        "description": procedure["description"],
        "policy_id": policy["policy_id"],
        "excluded": exclusion is not None,
        "exclusion_rule": exclusion["rule"] if exclusion else None,
        "requires_preauth": bool(procedure["requires_preauth"]),
        "required_document": required_document,
        "required_document_present": (
            True if required_document is None else required_document in attached_documents
        ),
    }


def get_preauthorisation(
    member_id: str,
    procedure_code: str,
    date_of_service: str,
) -> dict[str, Any]:
    """Return an explicit valid, expired, not-yet-valid or missing status."""
    matches = [
        row
        for row in _load("preauthorisations")
        if row["member_id"] == member_id and row["procedure_code"] == procedure_code
    ]
    valid = next(
        (
            row
            for row in matches
            if row["valid_from"] <= date_of_service <= row["valid_to"]
        ),
        None,
    )
    if valid:
        return {"status": "valid", **valid}
    if not matches:
        return {"status": "missing"}
    latest = sorted(matches, key=lambda row: (row["valid_to"], row["valid_from"]))[-1]
    status = "expired" if latest["valid_to"] < date_of_service else "not_yet_valid"
    return {"status": status, **latest}


def get_hospital_status(hospital_id: str) -> dict[str, Any] | None:
    """Return the hospital row, including panel status."""
    return next(
        (row for row in _load("hospitals") if row["hospital_id"] == hospital_id),
        None,
    )


def _normalise_lines(lines: list[dict[str, Any]]) -> list[tuple[str, int | float]]:
    return sorted((line["code"], line["amount"]) for line in lines)


def find_prior_decision(
    member_id: str,
    hospital_id: str,
    date_of_service: str,
    lines: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Match a prior claim on all four business facts, not on claim ID."""
    normalised = _normalise_lines(lines)
    return next(
        (
            row
            for row in _load("decided_claims")
            if row["member_id"] == member_id
            and row["hospital_id"] == hospital_id
            and row["date_of_service"] == date_of_service
            and _normalise_lines(row["lines"]) == normalised
        ),
        None,
    )


def _validate_approval_evidence(
    claim: dict[str, Any],
    dispositions: list[dict[str, Any]],
    evidence_trace: list[dict[str, Any]],
) -> None:
    """Fail closed unless trusted prior calls support every approval fact."""
    by_name: dict[str, list[dict[str, Any]]] = {}
    for entry in evidence_trace:
        by_name.setdefault(str(entry.get("tool")), []).append(entry)
    required = {"get_claim", "get_policy_context", "find_prior_decision", "get_hospital_status", "review_claim_line"}
    missing = sorted(required - set(by_name))
    if missing:
        raise ValueError(f"approval evidence is incomplete; missing prior tools: {missing}")

    claim_total = sum(line["amount"] for line in claim["lines"])
    policy_args = {
        "member_id": claim["member_id"],
        "date_of_service": claim["date_of_service"],
        "claim_total": claim_total,
    }
    if not any(entry.get("args") == policy_args for entry in by_name["get_policy_context"]):
        raise ValueError("approval lacks the exact claim-level policy check")
    policy = get_policy_context(**policy_args)
    if not policy or not policy["policy_active"] or not policy["service_date_covered"] or policy["annual_limit_exceeded"]:
        raise ValueError("policy evidence does not permit approval")

    duplicate_args = {
        "member_id": claim["member_id"],
        "hospital_id": claim["hospital_id"],
        "date_of_service": claim["date_of_service"],
        "lines": claim["lines"],
    }
    if not any(entry.get("args") == duplicate_args for entry in by_name["find_prior_decision"]):
        raise ValueError("approval lacks the exact duplicate-claim check")
    if find_prior_decision(**duplicate_args) is not None:
        raise ValueError("a matching prior decision blocks approval")
    hospital_args = {"hospital_id": claim["hospital_id"]}
    if not any(entry.get("args") == hospital_args for entry in by_name["get_hospital_status"]):
        raise ValueError("approval lacks the exact hospital check")
    if get_hospital_status(**hospital_args) is None:
        raise ValueError("hospital evidence did not resolve")

    remaining_reviews = list(by_name["review_claim_line"])
    for claim_line, disposition in zip(claim["lines"], dispositions):
        expected_args = {
            "member_id": claim["member_id"],
            "procedure_code": claim_line["code"],
            "attached_documents": claim["documents"],
        }
        match_index = next(
            (index for index, entry in enumerate(remaining_reviews) if entry.get("args") == expected_args),
            None,
        )
        if match_index is None:
            raise ValueError(f"approval lacks line review for {claim_line['code']}")
        remaining_reviews.pop(match_index)
        review = review_claim_line(**expected_args)
        if review is None:
            raise ValueError(f"procedure {claim_line['code']} did not resolve")
        if disposition["status"] == "excluded":
            if not review["excluded"] or review["exclusion_rule"] not in str(disposition.get("evidence", "")):
                raise ValueError(f"excluded disposition for {claim_line['code']} is unsupported")
            continue
        if review["excluded"] or not review["required_document_present"]:
            raise ValueError(f"covered disposition for {claim_line['code']} is unsupported")
        if review["requires_preauth"]:
            expected_preauth = {
                "member_id": claim["member_id"],
                "procedure_code": claim_line["code"],
                "date_of_service": claim["date_of_service"],
            }
            if not any(
                entry.get("args") == expected_preauth
                for entry in by_name.get("get_preauthorisation", [])
            ):
                raise ValueError(f"approval lacks pre-authorisation lookup for {claim_line['code']}")
            if get_preauthorisation(**expected_preauth)["status"] != "valid":
                raise ValueError(f"valid pre-authorisation is absent for {claim_line['code']}")


def _evidence_by_name(
    evidence_trace: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    by_name: dict[str, list[dict[str, Any]]] = {}
    for entry in evidence_trace:
        by_name.setdefault(str(entry.get("tool")), []).append(entry)
    return by_name


def _require_claim_evidence(
    claim: dict[str, Any], evidence_trace: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    by_name = _evidence_by_name(evidence_trace)
    expected = {"claim_id": claim["claim_id"]}
    if not any(entry.get("args") == expected for entry in by_name.get("get_claim", [])):
        raise ValueError("decision evidence lacks the exact get_claim call")
    return by_name


def _validate_request_evidence(
    claim: dict[str, Any],
    dispositions: list[dict[str, Any]],
    missing: str | None,
    evidence_trace: list[dict[str, Any]],
) -> None:
    by_name = _require_claim_evidence(claim, evidence_trace)
    required = {
        "get_policy_context",
        "find_prior_decision",
        "get_hospital_status",
        "review_claim_line",
    }
    absent = sorted(required - set(by_name))
    if absent:
        raise ValueError(f"request evidence is incomplete; missing prior tools: {absent}")
    total = sum(line["amount"] for line in claim["lines"])
    policy_args = {
        "member_id": claim["member_id"],
        "date_of_service": claim["date_of_service"],
        "claim_total": total,
    }
    if not any(
        entry.get("args") == policy_args
        for entry in by_name["get_policy_context"]
    ):
        raise ValueError("request lacks the exact claim-level policy check")
    policy = get_policy_context(**policy_args)
    if not policy or not policy["policy_active"] or not policy["service_date_covered"] or policy["annual_limit_exceeded"]:
        raise ValueError("an eligibility trigger takes priority over a document request")
    duplicate_args = {
        "member_id": claim["member_id"],
        "hospital_id": claim["hospital_id"],
        "date_of_service": claim["date_of_service"],
        "lines": claim["lines"],
    }
    if not any(
        entry.get("args") == duplicate_args
        for entry in by_name["find_prior_decision"]
    ) or find_prior_decision(**duplicate_args) is not None:
        raise ValueError("a duplicate check is absent or takes priority over a request")
    hospital_args = {"hospital_id": claim["hospital_id"]}
    if not any(
        entry.get("args") == hospital_args
        for entry in by_name["get_hospital_status"]
    ) or get_hospital_status(**hospital_args) is None:
        raise ValueError("request lacks a resolved exact hospital check")

    claim_cursor = 0
    for disposition in dispositions:
        key = (disposition.get("code"), disposition.get("amount"))
        match_index = next(
            (
                index
                for index in range(claim_cursor, len(claim["lines"]))
                if (claim["lines"][index]["code"], claim["lines"][index]["amount"])
                == key
            ),
            None,
        )
        if match_index is None:
            raise ValueError("request disposition is foreign, duplicated, or out of claim order")
        claim_cursor = match_index + 1
        claim_line = claim["lines"][match_index]
        review_args = {
            "member_id": claim["member_id"],
            "procedure_code": claim_line["code"],
            "attached_documents": claim["documents"],
        }
        if not any(
            entry.get("args") == review_args
            for entry in by_name.get("review_claim_line", [])
        ):
            raise ValueError("request disposition lacks its exact line review")
        review = review_claim_line(**review_args)
        if review is None or not review["required_document_present"]:
            raise ValueError("request disposition includes an unresolved document line")
        expected_status = "excluded" if review["excluded"] else "covered"
        if disposition.get("status") != expected_status:
            raise ValueError("request disposition status is unsupported")
        if review["excluded"]:
            if review["exclusion_rule"] not in str(disposition.get("evidence", "")):
                raise ValueError("request exclusion evidence is unsupported")
            continue
        if review["requires_preauth"]:
            preauth_args = {
                "member_id": claim["member_id"],
                "procedure_code": claim_line["code"],
                "date_of_service": claim["date_of_service"],
            }
            if not any(
                entry.get("args") == preauth_args
                for entry in by_name.get("get_preauthorisation", [])
            ) or get_preauthorisation(**preauth_args)["status"] != "valid":
                raise ValueError("request disposition lacks valid pre-authorisation")
    candidates: list[str] = []
    for line in claim["lines"]:
        review_args = {
            "member_id": claim["member_id"],
            "procedure_code": line["code"],
            "attached_documents": claim["documents"],
        }
        if not any(
            entry.get("args") == review_args
            for entry in by_name.get("review_claim_line", [])
        ):
            continue
        review = review_claim_line(**review_args)
        if review is None or review["excluded"]:
            continue
        if not review["required_document_present"]:
            document = str(review["required_document"]).replace("_", " ")
            candidates.append(f"{document} for line {line['code']}")
            continue
        if review["requires_preauth"]:
            preauth_args = {
                "member_id": claim["member_id"],
                "procedure_code": line["code"],
                "date_of_service": claim["date_of_service"],
            }
            if not any(
                entry.get("args") == preauth_args
                for entry in by_name.get("get_preauthorisation", [])
            ):
                continue
            preauth = get_preauthorisation(**preauth_args)
            if preauth["status"] == "expired":
                candidates.append(
                    f"current pre-authorisation for line {line['code']}, valid on {claim['date_of_service']}"
                )
            elif preauth["status"] != "valid":
                candidates.append(
                    f"pre-authorisation reference for line {line['code']}, valid on {claim['date_of_service']}"
                )
    if not missing or missing not in candidates:
        raise ValueError(
            f"request_document is unsupported; expected one of {candidates!r}"
        )


def _validate_escalation_evidence(
    claim: dict[str, Any],
    trigger: str | None,
    escalate_to: str | None,
    evidence_trace: list[dict[str, Any]],
) -> None:
    by_name = _require_claim_evidence(claim, evidence_trace)
    if escalate_to != "human claims assessor":
        raise ValueError("escalation must name the human claims assessor")
    if trigger == "instruction_in_member_narrative":
        raise ValueError("hostile-input escalation must fail closed without a write")
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
    if trigger in {"policy_lapsed", "outside_policy_dates", "annual_limit_exceeded"}:
        if not any(
            entry.get("args") == policy_args
            for entry in by_name.get("get_policy_context", [])
        ):
            raise ValueError("escalation lacks the exact policy check")
        policy = get_policy_context(**policy_args)
        supported = bool(
            policy
            and (
                (trigger == "policy_lapsed" and not policy["policy_active"])
                or (
                    trigger == "outside_policy_dates"
                    and not policy["service_date_covered"]
                )
                or (
                    trigger == "annual_limit_exceeded"
                    and policy["annual_limit_exceeded"]
                )
            )
        )
    elif trigger == "duplicate_claim":
        if not any(
            entry.get("args") == policy_args
            for entry in by_name.get("get_policy_context", [])
        ):
            raise ValueError("duplicate escalation lacks the exact policy check")
        policy = get_policy_context(**policy_args)
        if not policy or not policy["policy_active"] or not policy["service_date_covered"] or policy["annual_limit_exceeded"]:
            raise ValueError("an eligibility trigger takes priority over duplicate escalation")
        if not any(
            entry.get("args") == duplicate_args
            for entry in by_name.get("find_prior_decision", [])
        ):
            raise ValueError("escalation lacks the exact duplicate check")
        supported = find_prior_decision(**duplicate_args) is not None
    else:
        supported = False
    if not supported:
        raise ValueError(f"escalation trigger {trigger!r} is unsupported")


def issue_decision_letter(
    *,
    claim_id: str,
    decision: str,
    lines: list[dict[str, Any]] | None = None,
    approved_total: int | float = 0,
    refused_total: int | float = 0,
    reason: str,
    missing: str | None = None,
    trigger: str | None = None,
    escalate_to: str | None = None,
    evidence: list[str],
    evidence_trace: list[dict[str, Any]],
    gate: dict[str, Any],
    log_path: str | Path,
    timestamp: str | None = None,
    telemetry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Append one supported first-response decision to a local JSONL log."""
    if decision not in {"approve_in_principle", "request_document", "escalate"}:
        raise ValueError(f"unsupported first-response decision {decision!r}")
    if not gate.get("approved"):
        raise PermissionError("the autonomy gate has not approved this action")
    claim = get_claim(claim_id)
    if claim is None:
        raise ValueError(f"unknown claim_id {claim_id}")
    lines = list(lines or [])
    if decision == "escalate" and lines:
        raise ValueError("business escalation must stop before line dispositions")
    supplied_order = [(line.get("code"), line.get("amount")) for line in lines]
    claim_order = [(line.get("code"), line.get("amount")) for line in claim["lines"]]
    if decision == "approve_in_principle" and supplied_order != claim_order:
        raise ValueError(
            "one disposition per claim line is required and must preserve claim line order"
        )
    supplied_facts = sorted(supplied_order)
    claim_facts = _normalise_lines(claim["lines"])
    if decision == "approve_in_principle" and (
        supplied_facts != claim_facts
        or any(line.get("status") not in {"covered", "excluded"} for line in lines)
    ):
        raise ValueError("one disposition per claim line is required")
    calculated_approved = sum(
        line["amount"] for line in lines if line["status"] == "covered"
    )
    calculated_refused = sum(
        line["amount"] for line in lines if line["status"] == "excluded"
    )
    if approved_total != calculated_approved or refused_total != calculated_refused:
        raise ValueError(
            "approved and refused totals must match the line dispositions"
        )
    if decision == "approve_in_principle":
        _validate_approval_evidence(claim, lines, evidence_trace)
    elif decision == "request_document":
        _validate_request_evidence(claim, lines, missing, evidence_trace)
    else:
        _validate_escalation_evidence(claim, trigger, escalate_to, evidence_trace)
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": timestamp or datetime.now(timezone.utc).isoformat(),
        "claim_id": claim_id,
        "decision": decision,
        "reason": reason,
        "lines": lines,
        "approved_total": approved_total,
        "refused_total": refused_total,
        "missing": missing,
        "trigger": trigger,
        "escalate_to": escalate_to,
        "evidence": list(evidence),
        "gate": dict(gate),
        "turns": (telemetry or {}).get("turns"),
        "tokens_in": (telemetry or {}).get("tokens_in"),
        "tokens_out": (telemetry or {}).get("tokens_out"),
        "cost_usd": (telemetry or {}).get("cost_usd"),
    }
    line = json.dumps(record, ensure_ascii=False, sort_keys=True)
    recovered_after_write_error = False
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.seek(0)
        existing = handle.read().splitlines()
        if any(
            raw.strip() and json.loads(raw).get("claim_id") == claim_id
            for raw in existing
        ):
            raise ValueError(f"a decision for {claim_id} is already recorded")
        handle.seek(0, os.SEEK_END)
        try:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        except OSError:
            handle.seek(0)
            rows = handle.read().splitlines()
            if not rows or rows[-1] != line:
                raise
            recovered_after_write_error = True
        handle.seek(0)
        persisted = handle.read().splitlines()[-1]
    if json.loads(persisted) != record:
        raise OSError("decision record read-back did not match the write payload")
    return {
        "recorded": True,
        "claim_id": claim_id,
        "decision": decision,
        "receipt_sha256": hashlib.sha256(persisted.encode("utf-8")).hexdigest(),
        "record": record,
        "recovered_after_write_error": recovered_after_write_error,
    }


REGISTRY = {
    "A": {
        "get_claim": get_claim,
        "get_policy_context": get_policy_context,
        "review_claim_line": review_claim_line,
        "get_preauthorisation": get_preauthorisation,
        "get_hospital_status": get_hospital_status,
        "find_prior_decision": find_prior_decision,
        "issue_decision_letter": issue_decision_letter,
    }
}

GATED_ACTION = {"A": "issue_decision_letter"}


def _descriptor(
    name: str,
    signature: str,
    purpose: str,
    when: str,
    arguments: dict[str, str],
    returns: str,
    failure: str,
    irreversible: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "signature": signature,
        "purpose": purpose,
        "when": when,
        "args": arguments,
        "returns": returns,
        "failure": failure,
        "irreversible": irreversible,
    }


DESCRIPTORS = {
    "get_claim": _descriptor(
        "get_claim",
        "get_claim(claim_id: str)",
        "Fetch the claim that must receive a first response.",
        "Turn 1, alone. Every later call depends on this record.",
        {"claim_id": "the case ID supplied to the agent"},
        "At most one claim object: 7 top-level fields, no more than 4 lines and a narrative capped at 500 characters.",
        "None means a broken case ID, not a business outcome. A malformed argument stops loudly as tool_or_schema_error.",
        "No. Read-only.",
    ),
    "get_policy_context": _descriptor(
        "get_policy_context",
        "get_policy_context(member_id: str, date_of_service: str, claim_total: number)",
        "Resolve the member's policy and expose status, date and remaining-limit checks.",
        "After get_claim. May run with hospital, duplicate and line reviews.",
        {
            "member_id": "from get_claim",
            "date_of_service": "from get_claim",
            "claim_total": "sum of all claim line amounts",
        },
        "At most one policy-context object with 13 fields, approximately 250 tokens maximum.",
        "None means the member-policy join is broken. Invalid dates, totals or argument types stop loudly.",
        "No. Read-only.",
    ),
    "review_claim_line": _descriptor(
        "review_claim_line",
        "review_claim_line(member_id: str, procedure_code: str, attached_documents: list[str])",
        "Return coverage, exclusion, pre-authorisation and document facts for exactly one line.",
        "Once per line after get_claim. Calls for different lines are independent and may share a turn.",
        {
            "member_id": "from get_claim; avoids an unknown same-turn policy_id",
            "procedure_code": "one line code from get_claim",
            "attached_documents": "the claim documents list, unchanged",
        },
        "Exactly one 8-field line object, approximately 160 tokens maximum; no unrelated policy fields.",
        "None means the member-policy join or procedure code is broken; malformed documents stop loudly. An excluded line is not a failure and does not escalate the whole claim.",
        "No. Read-only.",
    ),
    "get_preauthorisation": _descriptor(
        "get_preauthorisation",
        "get_preauthorisation(member_id: str, procedure_code: str, date_of_service: str)",
        "Check whether one required pre-authorisation is valid on the service date.",
        "Only after review_claim_line returns requires_preauth=true for that line.",
        {
            "member_id": "from get_claim",
            "procedure_code": "the line requiring pre-authorisation",
            "date_of_service": "from get_claim",
        },
        "Exactly one object of at most 6 fields and approximately 100 tokens: valid, expired, not_yet_valid or missing.",
        "Malformed identifiers or dates stop loudly. missing or expired means request the exact pre-authorisation; it never means the procedure is excluded.",
        "No. Read-only.",
    ),
    "get_hospital_status": _descriptor(
        "get_hospital_status",
        "get_hospital_status(hospital_id: str)",
        "Return whether the treating hospital is on the insurer's panel.",
        "After get_claim; independent of policy, duplicate and line reviews, and required before any line-based approval or request.",
        {"hospital_id": "from get_claim"},
        "At most one 4-field hospital object, approximately 80 tokens maximum.",
        "None means a broken hospital ID; malformed arguments stop loudly. panel=false remains decidable and must be recorded.",
        "No. Read-only.",
    ),
    "find_prior_decision": _descriptor(
        "find_prior_decision",
        "find_prior_decision(member_id: str, hospital_id: str, date_of_service: str, lines: list[object])",
        "Detect a resubmission by matching all four business facts.",
        "After get_claim; independent of other lookups and required before any ordinary first response unless an earlier policy trigger ends retrieval.",
        {
            "member_id": "from get_claim",
            "hospital_id": "from get_claim",
            "date_of_service": "from get_claim",
            "lines": "the complete get_claim lines list, unchanged",
        },
        "The prior decided claim or None; at most one 7-field object and approximately 160 tokens.",
        "Malformed line objects stop loudly. None is normal and means carry on. Never match on claim ID or on only three facts.",
        "No. Read-only.",
    ),
    "issue_decision_letter": _descriptor(
        "issue_decision_letter",
        "issue_decision_letter(claim_id: str, decision: 'approve_in_principle|request_document|escalate', lines: list[object], approved_total: number, refused_total: number, reason: str, missing?: str, trigger?: str, escalate_to?: str)",
        "Record one supported simulated first-response decision.",
        "Mandatory last tool for every non-hostile outcome, after all evidence is collected. Knowing the answer is not completion: call this tool, wait for recorded=true, then return an exactly matching final object. Never call it for hostile-input escalation.",
        {
            "claim_id": "the case ID",
            "decision": "one of the three supported first-response outcomes",
            "lines": "approve: every claim line in original order. request_document: only fully resolved lines; OMIT the unresolved line. escalate: []. Every supplied status is exactly covered or excluded. Evidence quotes the exact policy_id for ordinary coverage, preauth_id for pre-authorised coverage, or exclusion_rule for exclusion; generic text such as 'review_claim_line' is insufficient",
            "approved_total": "exact sum of covered amounts in lines; use 0 when lines has no covered items",
            "refused_total": "exact sum of excluded amounts in lines; use 0 when lines has no excluded items",
            "reason": "bounded evidence-grounded explanation",
            "missing": "request_document only. Exact form: 'itemised bill for line CODE'; absent/not-yet-valid: 'pre-authorisation reference for line CODE, valid on YYYY-MM-DD'; expired: 'current pre-authorisation for line CODE, valid on YYYY-MM-DD'",
            "trigger": "escalate only; one of policy_lapsed, outside_policy_dates, annual_limit_exceeded or duplicate_claim",
            "escalate_to": "escalate only; exactly 'human claims assessor'",
        },
        "A confirmation object no longer than 30 tokens; the local log holds the decision payload and gate, while the run record holds turns, tokens and cost.",
        "Blocked when confirmation is absent, trusted evidence does not support the exact outcome, the claim was already written, required outcome fields are absent, or an approval leaves a line unresolved.",
        "Yes. This is the gated action and the only local write exposed to the agent.",
    ),
}


def call(
    problem: str,
    name: str,
    args: dict[str, Any],
    *,
    internal: dict[str, Any] | None = None,
) -> Any:
    """Dispatch a validated tool call and inject private write metadata safely."""
    if problem != "A" or name not in REGISTRY["A"]:
        raise KeyError(f"Unknown Problem {problem} tool: {name}")
    payload = dict(args)
    if name == "issue_decision_letter":
        private = internal or {}
        payload["evidence"] = private.get("evidence", [])
        payload["evidence_trace"] = private.get("evidence_trace", [])
        payload["gate"] = private.get("gate", {})
        payload["log_path"] = private.get("log_path", "artifacts/decisions.jsonl")
        payload["telemetry"] = private.get("telemetry", {})
        if "timestamp" in private:
            payload["timestamp"] = private["timestamp"]
    result = REGISTRY["A"][name](**payload)
    if (
        name == "review_claim_line"
        and (internal or {}).get("interface_version") == "v1"
        and result is not None
    ):
        # Deliberately weak ACI baseline: raw nested records, no explicit
        # document-present boolean and a larger return the model must interpret.
        procedure = next(
            row for row in _load("procedures") if row["code"] == args["procedure_code"]
        )
        resolved = _member_and_policy(args["member_id"])
        assert resolved is not None
        _, policy = resolved
        return {
            "procedure": procedure,
            "policy": {
                "policy_id": policy["policy_id"],
                "exclusions": policy["exclusions"],
            },
            "required_document_rules": _load("required_documents"),
            "attached_documents": list(args["attached_documents"]),
            "note": "Use these records to work out whether the line is complete.",
        }
    return result
