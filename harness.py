"""Evaluation harness for code checks, judgement queues and run summaries."""
from __future__ import annotations

import json
import statistics
import tempfile
from pathlib import Path
from typing import Any, Callable

import config
from agent import run_case

TrialPolicy = Callable[[str], int]

CODE_EXPECTATIONS_PATH = (
    Path(__file__).resolve().parent / "evaluation" / "code_expectations_A.json"
)


def load_code_expectations() -> dict[str, dict[str, Any]]:
    return json.loads(CODE_EXPECTATIONS_PATH.read_text(encoding="utf-8"))["cases"]

JUDGEMENT_CASE_IDS = {
    "CLM-8842",  # partly payable with valid pre-authorisation
    "CLM-8888",  # ask while other lines are already resolved
    "CLM-8894",  # expired pre-authorisation
    "CLM-8901",  # named required document
    "CLM-8910",  # early exit on lapsed policy
    "CLM-8925",  # early exit on annual limit
    "CLM-8933",  # duplicate evidence
    "CLM-8941",  # overt hostile narrative
    "CLM-8952",  # forged tool output in narrative
    "CLM-9019",  # combined partial, pre-authorised and non-panel case
}


def load_key(problem: str | None = None) -> dict[str, dict[str, Any]]:
    problem = problem or config.PROBLEM
    path = Path(config.data_root()) / f"expected_outcomes_{problem}.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {row["case_id"]: row for row in rows}


def load_cases(problem: str | None = None) -> list[str]:
    problem = problem or config.PROBLEM
    if problem != "A":
        raise ValueError("This submission implements Problem A only")
    path = Path(config.data_root()) / "data_A" / "claims.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    return [row["claim_id"] for row in rows]


def is_negative(expected: dict[str, Any] | None) -> bool:
    return bool(
        expected
        and expected.get("expected_decision") in {"request_document", "escalate"}
    )


def code_check(
    record: dict[str, Any], expected: dict[str, Any]
) -> tuple[bool, list[str]]:
    """Perform deterministic checks on fields with fixed correct values."""
    failures: list[str] = []
    decision = record.get("decision")
    expected_decision = expected.get("expected_decision")
    if decision != expected_decision:
        failures.append(f"decision {decision!r}, expected {expected_decision!r}")

    if expected.get("trigger") and record.get("trigger") != expected["trigger"]:
        failures.append(
            f"trigger {record.get('trigger')!r}, expected {expected['trigger']!r}"
        )
    if expected.get("missing") and record.get("missing") != expected["missing"]:
        failures.append(
            f"missing {record.get('missing')!r}, expected {expected['missing']!r}"
        )

    action_count = int(record.get("action_count", 0))
    case_id = record.get("case_id")
    structural = load_code_expectations().get(str(case_id))
    required_actions = (
        structural.get("expected_action_count")
        if structural and "expected_action_count" in structural
        else (1 if expected_decision == "approve_in_principle" else 0)
    )
    if action_count != required_actions:
        failures.append(
            f"action_count {action_count}, expected {required_actions} for {expected_decision}"
        )

    if record.get("stopped_by") and expected_decision == "approve_in_principle":
        failures.append(f"approval run stopped_by {record['stopped_by']!r}")

    if structural:
        for field in (
            "trigger",
            "missing",
            "escalate_to",
            "approved_total",
            "refused_total",
        ):
            if field in structural and record.get(field) != structural[field]:
                failures.append(
                    f"{field} {record.get(field)!r}, expected {structural[field]!r}"
                )
        expected_lines = structural.get("line_dispositions")
        if expected_lines is not None:
            actual_by_key = {
                (row.get("code"), row.get("amount")): row
                for row in record.get("line_dispositions", [])
            }
            expected_keys = {(row["code"], row["amount"]) for row in expected_lines}
            if set(actual_by_key) != expected_keys:
                failures.append(
                    f"line identities {sorted(actual_by_key, key=repr)!r}, expected {sorted(expected_keys, key=repr)!r}"
                )
            for line in expected_lines:
                key = (line["code"], line["amount"])
                actual = actual_by_key.get(key, {})
                if actual.get("status") != line["status"]:
                    failures.append(
                        f"line {key!r} status {actual.get('status')!r}, expected {line['status']!r}"
                    )
                evidence_text = str(actual.get("evidence", ""))
                for token in line.get("evidence_tokens", []):
                    if token not in evidence_text:
                        failures.append(f"line {key!r} evidence missing {token!r}")

    return not failures, failures


def judgement_requirements(case_id: str, base: list[str]) -> tuple[list[str], list[str]]:
    overlay_path = Path(__file__).resolve().parent / "evaluation" / "judgement_requirements_A.json"
    overlays = json.loads(overlay_path.read_text(encoding="utf-8"))
    overlay = overlays.get(case_id, {})
    removed = set(overlay.get("remove", []))
    must_record = [item for item in base if item not in removed] + list(overlay.get("add", []))
    return must_record, list(overlay.get("trajectory_checks", []))


def prepare_judgement_check(
    record: dict[str, Any], expected: dict[str, Any]
) -> dict[str, Any]:
    must_record, trajectory_checks = judgement_requirements(
        record["case_id"], expected.get("must_record", [])
    )
    return {
        "case_id": record["case_id"],
        "decision": record.get("decision"),
        "reason": record.get("reason", ""),
        "evidence": record.get("evidence", []),
        "details": {
            "trigger": record.get("trigger"),
            "missing": record.get("missing"),
            "approved_total": record.get("approved_total"),
            "refused_total": record.get("refused_total"),
            "line_dispositions": record.get("line_dispositions", []),
            "action_count": record.get("action_count", 0),
            "guardrails_fired": record.get("guardrails_fired", []),
        },
        "must_record": must_record,
        "trajectory_checks": trajectory_checks,
        "verdict": None,
        "graded_by": None,
        "notes": None,
    }


def run_set(
    case_ids: list[str] | None = None,
    *,
    problem: str | None = None,
    trials_for: TrialPolicy | None = None,
    verbose: bool = False,
    backend_name: str | None = None,
    prompt_version: str | None = None,
    output_dir: str | Path | None = None,
    scripted_scripts=None,
    approval_callback=None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    problem = problem or config.PROBLEM
    key = load_key(problem)
    case_ids = case_ids or load_cases(problem)
    trials_for = trials_for or (lambda case_id: 3 if is_negative(key[case_id]) else 1)
    approval_callback = approval_callback or (lambda _name, _payload: True)
    root = Path(output_dir) if output_dir else Path(tempfile.mkdtemp(prefix="pe6201-a2-eval-"))
    decision_dir = root / "decision_logs"
    decision_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    judgement_queue: list[dict[str, Any]] = []
    for case_id in case_ids:
        if case_id not in key:
            raise KeyError(f"No answer-key label for {case_id}")
        expected = key[case_id]
        for trial in range(1, trials_for(case_id) + 1):
            log_path = decision_dir / f"{case_id}-trial-{trial}.jsonl"
            if log_path.exists():
                log_path.unlink()
            record = run_case(
                case_id,
                problem=problem,
                approve=approval_callback,
                verbose=verbose,
                decision_log_path=log_path,
                backend_name=backend_name,
                prompt_version=prompt_version,
                scripted_scripts=scripted_scripts,
            )
            passed, failures = code_check(record, expected)
            results.append(
                {
                    "case_id": case_id,
                    "trial": trial,
                    "passed": passed,
                    "failures": failures,
                    "family": expected.get("family"),
                    "negative": is_negative(expected),
                    "record": record,
                }
            )
            if trial == 1 and case_id in JUDGEMENT_CASE_IDS:
                judgement_queue.append(prepare_judgement_check(record, expected))
    return results, judgement_queue


def summarise(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    passed = sum(bool(row["passed"]) for row in results)
    negatives = [row for row in results if row["negative"]]
    negative_passed = sum(bool(row["passed"]) for row in negatives)
    records = [row["record"] for row in results]
    turns = [int(record["turns"]) for record in records]
    observation_tokens = sum(
        int(record.get("observation_tokens_estimate", 0)) for record in records
    )
    observation_calls = sum(
        len(record.get("observation_metrics", [])) for record in records
    )
    return {
        "trials": total,
        "passed": passed,
        "pass_rate": passed / total if total else 0.0,
        "negative_trials": len(negatives),
        "negative_passed": negative_passed,
        "negative_pass_rate": negative_passed / len(negatives) if negatives else None,
        "median_turns": statistics.median(turns) if turns else None,
        "worst_case_turns": max(turns) if turns else None,
        "step_cap_hits": sum(record.get("stopped_by") == "step_cap" for record in records),
        "tokens_in": sum(int(record.get("tokens_in", 0)) for record in records),
        "tokens_out": sum(int(record.get("tokens_out", 0)) for record in records),
        "observation_tokens_estimate": observation_tokens,
        "observation_calls": observation_calls,
        "mean_observation_tokens_estimate_per_call": (
            observation_tokens / observation_calls if observation_calls else None
        ),
        "cost_usd": round(sum(float(record.get("cost_usd", 0)) for record in records), 8),
        "catalog_cost_usd": round(
            sum(float(record.get("catalog_cost_usd", record.get("cost_usd", 0))) for record in records),
            8,
        ),
        "provider_cost_usd": (
            round(sum(float(record["provider_cost_usd"]) for record in records), 8)
            if records and all(record.get("provider_cost_usd") is not None for record in records)
            else None
        ),
        "backend": records[0].get("backend") if records else None,
        "model": records[0].get("model") if records else None,
        "prompt_version": records[0].get("prompt_version") if records else None,
    }


def save_run(
    path: str | Path,
    results: list[dict[str, Any]],
    judgement_queue: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": metadata or {},
        "summary": summarise(results),
        "results": results,
        "judgement_queue": judgement_queue,
    }
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    return destination


def report(results: list[dict[str, Any]]) -> dict[str, Any]:
    summary = summarise(results)
    print(json.dumps(summary, indent=2))
    failures = [row for row in results if not row["passed"]]
    if failures:
        print("FAILED TRIALS")
        for row in failures:
            print(row["case_id"], row["trial"], row["failures"])
    return summary
