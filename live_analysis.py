#!/usr/bin/env python3
"""Validate and analyse the frozen six-run live evidence package."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import prompt
from cost_model import (
    break_even_success_rate,
    cost_to_serve,
    sensitivity_grid,
)
from harness import JUDGEMENT_CASE_IDS, code_check, is_negative, load_key, summarise
from reliability import implied_step_reliability

ROOT = Path(__file__).resolve().parent
EXPECTED_V2 = {
    "google/gemini-2.5-flash-lite",
    "qwen/qwen3-30b-a3b-instruct-2507",
    "anthropic/claude-haiku-4.5",
    "meta-llama/llama-4-maverick",
    "deepseek/deepseek-v3.2",
}
CONTROL_MODEL = "google/gemini-2.5-flash-lite"


def _current_artifact_hashes(prompt_version: str) -> dict[str, str]:
    paths = {
        "claims": ROOT / "A2_reference_data" / "data_A" / "claims.json",
        "answer_key": ROOT / "A2_reference_data" / "expected_outcomes_A.json",
        "scripts": ROOT / "fixtures" / "scripted_trajectories_A.json",
    }
    hashes = {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in paths.items()
    }
    hashes["system_prompt"] = hashlib.sha256(
        prompt.build_system_prompt("A", prompt_version).encode("utf-8")
    ).hexdigest()
    return hashes


def _committed_bytes(commit: str, path: str) -> bytes:
    """Read one named input from the commit that produced a battery."""
    try:
        return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)
    except subprocess.CalledProcessError as error:
        raise ValueError(f"recorded commit lacks required source: {path}") from error


def _artifact_hashes_at_commit(commit: str, prompt_version: str) -> dict[str, str]:
    """Rebuild frozen inputs from the recorded commit, never from analysis HEAD."""
    try:
        subprocess.check_call(
            ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as error:
        raise ValueError("recorded commit is unavailable locally") from error
    paths = {
        "claims": "A2_reference_data/data_A/claims.json",
        "answer_key": "A2_reference_data/expected_outcomes_A.json",
        "scripts": "fixtures/scripted_trajectories_A.json",
    }
    hashes = {name: hashlib.sha256(_committed_bytes(commit, path)).hexdigest() for name, path in paths.items()}
    with tempfile.TemporaryDirectory() as directory:
        with (Path(directory) / "source.tar").open("wb") as archive:
            subprocess.check_call(
                ["git", "archive", commit, "config.py", "tools.py", "prompt.py"],
                cwd=ROOT,
                stdout=archive,
            )
        subprocess.check_call(["tar", "-xf", "source.tar"], cwd=directory)
        prompt_bytes = subprocess.check_output(
            [
                "python3", "-c",
                "import prompt, sys; sys.stdout.buffer.write(prompt.build_system_prompt('A', sys.argv[1]).encode('utf-8'))",
                prompt_version,
            ],
            cwd=directory,
        )
    hashes["system_prompt"] = hashlib.sha256(prompt_bytes).hexdigest()
    return hashes


def _catalog_at_commit(commit: str) -> dict[str, Any]:
    """Load the price catalogue frozen with the measured source commit."""
    try:
        return json.loads(_committed_bytes(commit, "config/model_catalog.json"))
    except json.JSONDecodeError as error:
        raise ValueError("recorded commit has an invalid model catalogue") from error


def _outcome_projection(payload: dict[str, Any], *, persisted: bool) -> dict[str, Any]:
    decision = payload.get("decision")
    result: dict[str, Any] = {"decision": decision, "reason": payload.get("reason")}
    if decision == "approve_in_principle":
        result.update(
            {
                "approved_total": payload.get("approved_total"),
                "refused_total": payload.get("refused_total"),
                "line_dispositions": payload.get("lines" if persisted else "line_dispositions"),
            }
        )
    elif decision == "request_document":
        result.update(
            {
                "missing": payload.get("missing"),
                "line_dispositions": payload.get("lines" if persisted else "line_dispositions"),
            }
        )
    elif decision == "escalate":
        result.update(
            {"trigger": payload.get("trigger"), "escalate_to": payload.get("escalate_to")}
        )
    return result


def _validate_item_rows(payload: dict[str, Any]) -> None:
    results = payload["results"]
    key = load_key("A")
    expected_pairs = {
        (case_id, trial)
        for case_id, expected in key.items()
        for trial in range(1, (3 if is_negative(expected) else 1) + 1)
    }
    actual_pairs = [(row.get("case_id"), row.get("trial")) for row in results]
    if len(actual_pairs) != len(set(actual_pairs)) or set(actual_pairs) != expected_pairs:
        raise ValueError("item-level trial matrix is incomplete, duplicated, or unknown")

    model = payload["summary"].get("model")
    version = payload["summary"].get("prompt_version")
    for row in results:
        case_id = row["case_id"]
        record = row.get("record")
        if not isinstance(record, dict):
            raise ValueError("item-level record is missing")
        if (
            record.get("case_id") != case_id
            or record.get("backend") != "live"
            or record.get("model") != model
            or record.get("prompt_version") != version
        ):
            raise ValueError("item-level record metadata does not match its battery")
        recomputed_passed, recomputed_failures = code_check(record, key[case_id])
        if (
            row.get("passed") is not recomputed_passed
            or row.get("failures") != recomputed_failures
            or row.get("negative") is not is_negative(key[case_id])
            or row.get("family") != key[case_id].get("family")
        ):
            raise ValueError("item-level score does not match the frozen oracle")

        action_count = int(record.get("action_count", 0))
        receipt = record.get("action_receipt")
        persisted_decision = record.get("persisted_decision")
        if action_count == 0:
            if receipt is not None or persisted_decision is not None:
                raise ValueError("decision receipt exists without a recorded action")
            continue
        if action_count != 1 or not isinstance(receipt, dict) or not isinstance(persisted_decision, dict):
            raise ValueError("decision receipt is missing or action count is invalid")
        if receipt.get("record") != persisted_decision:
            raise ValueError("decision receipt record does not match persisted decision")
        persisted_text = json.dumps(persisted_decision, ensure_ascii=False, sort_keys=True)
        expected_receipt = hashlib.sha256(persisted_text.encode("utf-8")).hexdigest()
        if receipt.get("receipt_sha256") != expected_receipt:
            raise ValueError("decision receipt hash is invalid")
        if (
            record.get("stopped_by") is None
            and _outcome_projection(record, persisted=False)
            != _outcome_projection(persisted_decision, persisted=True)
        ):
            raise ValueError("returned outcome does not match decision receipt")

    if payload.get("summary") != summarise(results):
        raise ValueError("self-declared summary does not match item-level results")
    queue_ids = [row.get("case_id") for row in payload.get("judgement_queue", [])]
    if len(queue_ids) != len(JUDGEMENT_CASE_IDS) or set(queue_ids) != JUDGEMENT_CASE_IDS:
        raise ValueError("judgement queue does not match the frozen review set")


def case_balanced_metrics(
    results: list[dict[str, Any]], price: dict[str, Any] | None = None
) -> dict[str, float]:
    """Give each case one vote after averaging its repeated negative trials."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in results:
        grouped.setdefault(row["case_id"], []).append(row)
    if not grouped:
        raise ValueError("case-balanced analysis requires item-level results")

    case_success = []
    case_cost = []
    case_catalog_cost = []
    for rows in grouped.values():
        case_success.append(sum(bool(row["passed"]) for row in rows) / len(rows))
        costs = [float(row["record"].get("cost_usd", 0)) for row in rows]
        if price is None:
            catalog = [
                float(row["record"].get("catalog_cost_usd", row["record"].get("cost_usd", 0)))
                for row in rows
            ]
        else:
            catalog = [
                (float(row["record"]["tokens_in"]) / 1_000_000 * float(price["input_per_million"]))
                + (float(row["record"]["tokens_out"]) / 1_000_000 * float(price["output_per_million"]))
                for row in rows
            ]
        case_cost.append(sum(costs) / len(costs))
        case_catalog_cost.append(sum(catalog) / len(catalog))
    return {
        "cases": float(len(grouped)),
        "success_rate": sum(case_success) / len(case_success),
        "variable_cost_per_task": sum(case_cost) / len(case_cost),
        "catalog_cost_per_task": sum(case_catalog_cost) / len(case_catalog_cost),
    }


def validate_battery_set(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    if len(payloads) != 6:
        raise ValueError("A measured evidence set must contain exactly six batteries")
    commits = {
        payload.get("metadata", {}).get("git", {}).get("commit") for payload in payloads
    }
    if None in commits or len(commits) != 1:
        raise ValueError("Every measured battery must use the same commit")
    if any(payload.get("metadata", {}).get("git", {}).get("dirty") for payload in payloads):
        raise ValueError("Measured batteries must come from a clean commit")
    for payload in payloads:
        summary = payload.get("summary", {})
        if payload.get("metadata", {}).get("kind") != "measured_battery":
            raise ValueError("Smoke results cannot enter measured analysis")
        if summary.get("backend") != "live":
            raise ValueError("Every battery must use the live backend")
        if summary.get("trials") != 60:
            raise ValueError("Every battery must contain exactly 60 trials")
        results = payload.get("results")
        if not isinstance(results, list) or len(results) != 60:
            raise ValueError("Every battery requires 60 item-level result rows")
        if (
            payload.get("metadata", {}).get("model") != summary.get("model")
            or payload.get("metadata", {}).get("prompt_version")
            != summary.get("prompt_version")
        ):
            raise ValueError("Battery metadata does not match its item summary")
        if summary.get("tokens_in", 0) <= 0 or summary.get("tokens_out", 0) <= 0:
            raise ValueError("Measured API usage is missing")
        _validate_item_rows(payload)

    required_hashes = {"claims", "answer_key", "scripts", "system_prompt"}
    hashes = [payload.get("metadata", {}).get("artifact_hashes", {}) for payload in payloads]
    if any(set(item) != required_hashes for item in hashes):
        raise ValueError("Every battery must record the same artifact hash fields")
    for name in ("claims", "answer_key", "scripts"):
        if len({item[name] for item in hashes}) != 1:
            raise ValueError("Fixture and answer-key artifact hashes must match across batteries")
    for version in ("v1", "v2"):
        version_hashes = {
            payload["metadata"]["artifact_hashes"]["system_prompt"]
            for payload in payloads
            if payload["summary"].get("prompt_version") == version
        }
        if len(version_hashes) != 1:
            raise ValueError(f"System-prompt artifact hashes drifted within {version}")
    recorded_commit = next(iter(commits))
    for payload, recorded_hashes in zip(payloads, hashes):
        version = payload["summary"]["prompt_version"]
        if recorded_hashes != _artifact_hashes_at_commit(recorded_commit, version):
            raise ValueError("Recorded artifact hashes do not match the recorded commit")

    v2 = {
        payload["summary"]["model"]
        for payload in payloads
        if payload["summary"].get("prompt_version") == "v2"
    }
    v1 = [
        payload
        for payload in payloads
        if payload["summary"].get("prompt_version") == "v1"
    ]
    if v2 != EXPECTED_V2:
        raise ValueError(f"Expected five frozen v2 models, found {sorted(v2)}")
    if len(v1) != 1 or v1[0]["summary"].get("model") != CONTROL_MODEL:
        raise ValueError("Exactly one Gemini 2.5 Flash Lite v1 battery is required")
    return {
        "commit": recorded_commit,
        "v2_models": sorted(v2),
        "v1_model": CONTROL_MODEL,
        "fixture_hashes": {name: hashes[0][name] for name in ("claims", "answer_key", "scripts")},
    }


def load_live_payloads(directory: Path | None = None) -> list[dict[str, Any]]:
    directory = directory or ROOT / "results" / "live"
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(directory.glob("*.json"))
        if json.loads(path.read_text(encoding="utf-8")).get("metadata", {}).get("kind")
        == "measured_battery"
    ]


def analyse(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    validation = validate_battery_set(payloads)
    catalog = _catalog_at_commit(validation["commit"])
    prices = catalog["models"]
    rows: list[dict[str, Any]] = []
    for payload in payloads:
        summary = payload["summary"]
        model = summary["model"]
        trials = summary["trials"]
        if model not in prices:
            raise ValueError(f"recorded commit catalogue has no price for {model}")
        price = prices[model]
        recorded_price = payload.get("metadata", {}).get("price", {})
        if any(recorded_price.get(field) != price.get(field) for field in ("input_per_million", "output_per_million")):
            raise ValueError("battery metadata price does not match its recorded commit catalogue")
        balanced = case_balanced_metrics(payload["results"], price)
        catalog_variable = balanced["catalog_cost_per_task"]
        variable = balanced["variable_cost_per_task"]
        provider_costs = [row["record"].get("provider_cost_usd") for row in payload["results"]]
        provider_priced = [float(cost) for cost in provider_costs if cost is not None]
        provider_priced_requests = len(provider_priced)
        provider_unpriced_requests = len(provider_costs) - provider_priced_requests
        provider_complete = provider_unpriced_requests == 0
        # List-price token costs are the comparable baseline; provider billing is coverage-limited evidence.
        variable = catalog_variable
        service = cost_to_serve(
            variable_cost=variable,
            success_rate=balanced["success_rate"],
            failure_cost=7.60,
            monthly_volume=8_000,
            fixed_monthly=400.0,
        )
        rows.append(
            {
                "model": model,
                "prompt_version": summary["prompt_version"],
                "trials": trials,
                "pass_rate": summary["pass_rate"],
                "case_balanced_success_rate_for_cost": balanced["success_rate"],
                "negative_pass_rate": summary["negative_pass_rate"],
                "median_turns": summary["median_turns"],
                "tokens_in": summary["tokens_in"],
                "tokens_out": summary["tokens_out"],
                "mean_observation_tokens_estimate_per_call": summary.get(
                    "mean_observation_tokens_estimate_per_call"
                ),
                "measured_battery_cost": summary["cost_usd"],
                "provider_billed_subtotal_usd": sum(provider_priced) if provider_priced else None,
                "provider_billed_priced_requests": provider_priced_requests,
                "provider_billed_unpriced_requests": provider_unpriced_requests,
                "provider_billed_request_coverage": provider_priced_requests / len(provider_costs),
                "mean_provider_billed_cost": sum(provider_priced) / provider_priced_requests if provider_complete else None,
                "mean_catalog_cost": catalog_variable,
                "mean_provider_minus_catalog": (
                    (sum(provider_priced) / provider_priced_requests) - catalog_variable
                    if provider_complete else None
                ),
                "mean_variable_cost": catalog_variable,
                "implied_step_reliability": (
                    implied_step_reliability(summary["pass_rate"], summary["median_turns"])
                    if summary["median_turns"] > 0 else None
                ),
                "implied_step_reliability_note": (
                    None if summary["median_turns"] > 0
                    else "null because median turns is zero; a per-step reliability is undefined"
                ),
                **service,
                "sensitivity": sensitivity_grid(
                    variable_cost=variable,
                    success_rate=balanced["success_rate"],
                    failure_cost=7.60,
                    monthly_volume=8_000,
                    fixed_monthly=400.0,
                ),
            }
        )
    v2_rows = [row for row in rows if row["prompt_version"] == "v2"]
    cheap = min(v2_rows, key=lambda row: row["mean_variable_cost"])
    best_service = min(v2_rows, key=lambda row: row["cost_to_serve_per_task"])
    alternatives = [row for row in v2_rows if row["model"] != cheap["model"]]
    reference = min(alternatives, key=lambda row: row["cost_to_serve_per_task"])
    break_even = break_even_success_rate(
        cheap_variable_cost=cheap["mean_variable_cost"],
        expensive_cost_to_serve=reference["cost_to_serve_per_task"],
        failure_cost=7.60,
    )
    return {
        "validation": validation,
        "catalog_checked_at_utc": catalog["checked_at_utc"],
        "models": sorted(rows, key=lambda row: (row["prompt_version"], row["model"])),
        "cheapest_v2_model": cheap["model"],
        "lowest_cost_to_serve_v2_model": best_service["model"],
        "break_even_reference_v2_model": reference["model"],
        "cheap_model_break_even_success_rate_against_reference": break_even,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=ROOT / "results" / "live")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payloads = load_live_payloads(args.directory)
    if not payloads:
        raise SystemExit("No measured live batteries found. Nothing was fabricated.")
    result = analyse(payloads)
    destination = args.output or ROOT / "artifacts" / "live_analysis.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(destination)
