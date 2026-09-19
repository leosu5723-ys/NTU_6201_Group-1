#!/usr/bin/env python3
"""Preflight and execute one member's frozen OpenRouter battery."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Callable

import config
import prompt
from harness import (
    JUDGEMENT_CASE_IDS,
    code_check,
    is_negative,
    load_cases,
    load_key,
    prepare_judgement_check,
    run_set,
    save_run,
    summarise,
)

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "config" / "model_catalog.json"


def _check_budget(
    *, estimated_run_cost: float, spent_to_date: float, budget_cap: float, label: str
) -> float:
    if min(estimated_run_cost, spent_to_date, budget_cap) < 0:
        raise ValueError("budget values must be non-negative")
    remaining_after_plan = budget_cap - spent_to_date - estimated_run_cost
    if remaining_after_plan < 0:
        raise ValueError(f"planned run exceeds the member's {label}")
    return remaining_after_plan


def check_member_budget(*, estimated_run_cost: float, spent_to_date: float) -> float:
    """Enforce the immutable assignment budget; callers cannot widen the cap."""
    return _check_budget(
        estimated_run_cost=estimated_run_cost,
        spent_to_date=spent_to_date,
        budget_cap=config.A2_API_BUDGET_PER_MEMBER_USD,
        label="US$3 A2 API budget",
    )


def check_live_budgets(
    *, estimated_run_cost: float, a2_spent_to_date: float, monthly_spent_to_date: float
) -> dict[str, float]:
    a2_remaining = check_member_budget(
        estimated_run_cost=estimated_run_cost,
        spent_to_date=a2_spent_to_date,
    )
    try:
        monthly_remaining = _check_budget(
            estimated_run_cost=estimated_run_cost,
            spent_to_date=monthly_spent_to_date,
            budget_cap=config.MONTHLY_API_BUDGET_PER_MEMBER_USD,
            label="US$25 monthly API budget",
        )
    except ValueError as error:
        raise ValueError(f"monthly member budget: {error}") from error
    return {
        "a2_remaining_after": a2_remaining,
        "monthly_remaining_after": monthly_remaining,
    }


def artifact_hashes(prompt_version: str) -> dict[str, str]:
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


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def validate_catalog(catalog: dict[str, Any]) -> None:
    models = catalog.get("models") or {}
    if len(models) != 5:
        raise ValueError("The v2 battery must contain five model families")
    families = {row["family"] for row in models.values()}
    tiers = {row["tier"] for row in models.values()}
    if len(families) != len(models):
        raise ValueError("Two v2 models share a family")
    if len(tiers) < 2:
        raise ValueError("The battery must span at least two price tiers")
    if not all(row.get("supports_tools") for row in models.values()):
        raise ValueError("Every selected model must support tool use")


def plan_battery(model: str, prompt_version: str) -> dict[str, Any]:
    catalog = load_catalog()
    validate_catalog(catalog)
    if model not in catalog["models"]:
        raise KeyError(f"Model is not in the frozen catalogue: {model}")
    if prompt_version not in {"v1", "v2"}:
        raise ValueError("prompt_version must be v1 or v2")
    results, _ = run_set(
        problem="A",
        backend_name="scripted",
        prompt_version=prompt_version,
    )
    summary = summarise(results)
    price = catalog["models"][model]
    estimated = (
        summary["tokens_in"] / 1_000_000 * price["input_per_million"]
        + summary["tokens_out"] / 1_000_000 * price["output_per_million"]
    )
    return {
        "model": model,
        "prompt_version": prompt_version,
        "cases": len(load_cases("A")),
        "trials": len(results),
        "ordinary_cases": sum(
            row["expected_decision"] == "approve_in_principle"
            for row in load_key("A").values()
        ),
        "negative_cases": sum(
            row["expected_decision"] != "approve_in_principle"
            for row in load_key("A").values()
        ),
        "catalog_checked_at_utc": catalog["checked_at_utc"],
        "price_input_per_million": price["input_per_million"],
        "price_output_per_million": price["output_per_million"],
        "estimated_cost_usd_from_scripted_tokens": round(estimated, 4),
        "executes_network_calls": False,
        "warning": "The estimate uses scripted token counts. Final cost must use API usage blocks from the live run.",
    }


def _git_state() -> dict[str, Any]:
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    status = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).splitlines()
    return {"commit": commit, "dirty": bool(status), "changed_paths": status}


def normalise_git_state_for_run(
    git: dict[str, Any], *, generated_only: bool
) -> dict[str, Any]:
    """Record source cleanliness separately from resumable generated outputs."""
    return {
        **git,
        "dirty": bool(git.get("dirty")) and not generated_only,
        "generated_outputs_present": bool(git.get("dirty")) and generated_only,
    }


def dirty_paths_are_only_run_outputs(status: list[str], output: Path) -> bool:
    output_text = output.as_posix()
    checkpoint_text = output.with_name(output.name + ".checkpoint").as_posix()
    temporary_text = output.with_name(output.name + ".tmp").as_posix()
    log_prefix = (output.parent / (output.stem + "-logs")).as_posix() + "/"
    allowed_exact = {output_text, checkpoint_text, temporary_text}
    collection_prefix = None
    if output.parent.as_posix().rstrip("/").endswith("results/live"):
        collection_prefix = output.parent.as_posix().rstrip("/") + "/"
    for row in status:
        path = row[3:].strip().strip('"')
        if (
            path not in allowed_exact
            and not path.startswith(log_prefix)
            and not (collection_prefix and path.startswith(collection_prefix))
        ):
            return False
    return bool(status)


def _write_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def run_resumable_battery(
    case_ids: list[str],
    trials_for: Callable[[str], int],
    run_one: Callable[[str, int], tuple[dict[str, Any], dict[str, Any] | None]],
    checkpoint: Path,
    resume_metadata: dict[str, Any],
    *,
    validate_existing: Callable[[dict[str, Any]], None] | None = None,
    before_run: Callable[[list[dict[str, Any]]], None] | None = None,
    after_run: Callable[[list[dict[str, Any]]], None] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    judgement_queue: list[dict[str, Any]] = []
    if checkpoint.exists():
        existing = json.loads(checkpoint.read_text(encoding="utf-8"))
        if existing.get("resume_metadata") != resume_metadata:
            raise ValueError("checkpoint does not match the frozen run configuration")
        results = list(existing.get("results", []))
        judgement_queue = list(existing.get("judgement_queue", []))
    allowed = {
        (case_id, trial)
        for case_id in case_ids
        for trial in range(1, trials_for(case_id) + 1)
    }
    pairs = [(row.get("case_id"), row.get("trial")) for row in results]
    if len(pairs) != len(set(pairs)) or not set(pairs).issubset(allowed):
        raise ValueError("checkpoint trial matrix is duplicated or unknown")
    if validate_existing is not None:
        for row in results:
            validate_existing(row)
    completed = {(row["case_id"], int(row["trial"])) for row in results}
    for case_id in case_ids:
        for trial in range(1, trials_for(case_id) + 1):
            if (case_id, trial) in completed:
                continue
            if before_run is not None:
                before_run(results)
            row, judgement = run_one(case_id, trial)
            row["case_id"] = case_id
            row["trial"] = trial
            results.append(row)
            if judgement is not None:
                judgement_queue.append(judgement)
            _write_checkpoint(
                checkpoint,
                {
                    "resume_metadata": resume_metadata,
                    "results": results,
                    "judgement_queue": judgement_queue,
                },
            )
            if after_run is not None:
                after_run(results)
    return results, judgement_queue


def _validate_live_checkpoint_row(
    row: dict[str, Any],
    *,
    model: str,
    prompt_version: str,
    answer_key: dict[str, dict[str, Any]],
) -> None:
    case_id = row.get("case_id")
    if case_id not in answer_key or not isinstance(row.get("trial"), int):
        raise ValueError("checkpoint row has an unknown case or malformed trial")
    record = row.get("record")
    if not isinstance(record, dict):
        raise ValueError("checkpoint row has no decision record")
    if (
        record.get("case_id") != case_id
        or record.get("backend") != "live"
        or record.get("model") != model
        or record.get("prompt_version") != prompt_version
    ):
        raise ValueError("checkpoint row metadata does not match the frozen run")
    passed, failures = code_check(record, answer_key[case_id])
    if row.get("passed") is not passed or row.get("failures") != failures:
        raise ValueError("checkpoint row score does not match the frozen oracle")
    action_count = int(record.get("action_count", 0))
    receipt = record.get("action_receipt")
    persisted = record.get("persisted_decision")
    if action_count == 0:
        if receipt is not None or persisted is not None:
            raise ValueError("checkpoint row has a receipt without a recorded action")
        return
    if action_count != 1 or not isinstance(receipt, dict) or not isinstance(persisted, dict):
        raise ValueError("checkpoint row lacks a valid decision receipt")
    if receipt.get("record") != persisted:
        raise ValueError("checkpoint decision receipt does not match its record")
    encoded = json.dumps(persisted, ensure_ascii=False, sort_keys=True).encode("utf-8")
    if receipt.get("receipt_sha256") != hashlib.sha256(encoded).hexdigest():
        raise ValueError("checkpoint decision receipt hash is invalid")


def _completed_cost(results: list[dict[str, Any]]) -> float:
    return sum(float(row.get("record", {}).get("cost_usd", 0)) for row in results)


def execute_battery(
    model: str,
    prompt_version: str,
    *,
    output: Path,
    smoke_case: str | None = None,
    allow_dirty: bool = False,
    spent_to_date: float | None = None,
    monthly_spent_to_date: float | None = None,
) -> Path:
    catalog = load_catalog()
    validate_catalog(catalog)
    if model not in catalog["models"]:
        raise KeyError(model)
    checkpoint = output.with_name(output.name + ".checkpoint")
    git = _git_state()
    generated_only_dirty_state = dirty_paths_are_only_run_outputs(
        git["changed_paths"], output.relative_to(ROOT) if output.is_absolute() else output
    )
    if git["dirty"] and not allow_dirty and not generated_only_dirty_state:
        raise RuntimeError("Final live batteries require a clean frozen git commit")
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise RuntimeError("Set OPENROUTER_API_KEY in the environment; never put it in a file")
    plan = plan_battery(model, prompt_version)
    if spent_to_date is None or monthly_spent_to_date is None:
        raise ValueError(
            "Formal execution requires both A2 and monthly spend-to-date inputs"
        )
    budget_status = check_live_budgets(
        estimated_run_cost=plan["estimated_cost_usd_from_scripted_tokens"],
        a2_spent_to_date=spent_to_date,
        monthly_spent_to_date=monthly_spent_to_date,
    )

    selected = catalog["models"][model]
    config.API_KEY = key
    config.MODEL = model
    config.BACKEND = "live"
    config.PROMPT_VERSION = prompt_version
    config.PRICE_IN = float(selected["input_per_million"])
    config.PRICE_OUT = float(selected["output_per_million"])

    metadata = {
        "kind": "smoke" if smoke_case else "measured_battery",
        "model": model,
        "prompt_version": prompt_version,
        "artifact_hashes": artifact_hashes(prompt_version),
        "git": normalise_git_state_for_run(
            git, generated_only=generated_only_dirty_state
        ),
        "catalog_checked_at_utc": catalog["checked_at_utc"],
        "price": selected,
        "smoke_case": smoke_case,
        "api_key_recorded": False,
        "member_a2_api_budget_usd": config.A2_API_BUDGET_PER_MEMBER_USD,
        "member_spend_to_date_usd": spent_to_date,
        "estimated_budget_remaining_after_plan_usd": budget_status["a2_remaining_after"],
        "monthly_api_budget_usd": config.MONTHLY_API_BUDGET_PER_MEMBER_USD,
        "monthly_spend_to_date_usd": monthly_spent_to_date,
        "estimated_monthly_budget_remaining_after_plan_usd": budget_status["monthly_remaining_after"],
    }
    case_ids = [smoke_case] if smoke_case else load_cases("A")
    key_by_case = load_key("A")
    conservative_next_trial_cost = (
        config.MAX_TOKENS_PER_RUN
        / 1_000_000
        * max(config.PRICE_IN, config.PRICE_OUT)
    )

    def trial_policy(case_id: str) -> int:
        return 1 if smoke_case else (3 if is_negative(key_by_case[case_id]) else 1)

    log_root = output.parent / (output.stem + "-logs")

    def run_one(case_id: str, trial: int):
        rows, judgements = run_set(
            [case_id],
            problem="A",
            backend_name="live",
            prompt_version=prompt_version,
            trials_for=lambda _case_id: 1,
            output_dir=log_root / f"{case_id}-trial-{trial}",
        )
        return rows[0], judgements[0] if trial == 1 and judgements else None

    def enforce_runtime_budget(
        completed: list[dict[str, Any]], reserve: float
    ) -> None:
        actual = _completed_cost(completed)
        check_live_budgets(
            estimated_run_cost=reserve,
            a2_spent_to_date=spent_to_date + actual,
            monthly_spent_to_date=monthly_spent_to_date + actual,
        )

    resume_metadata = {
        "model": model,
        "prompt_version": prompt_version,
        "git_commit": git["commit"],
        "artifact_hashes": metadata["artifact_hashes"],
        "smoke_case": smoke_case,
    }
    results, queue = run_resumable_battery(
        case_ids,
        trial_policy,
        run_one,
        checkpoint,
        resume_metadata,
        validate_existing=lambda row: _validate_live_checkpoint_row(
            row,
            model=model,
            prompt_version=prompt_version,
            answer_key=key_by_case,
        ),
        before_run=lambda completed: enforce_runtime_budget(
            completed, conservative_next_trial_cost
        ),
        after_run=lambda completed: enforce_runtime_budget(completed, 0.0),
    )
    queue = [
        prepare_judgement_check(row["record"], key_by_case[row["case_id"]])
        for row in results
        if row["trial"] == 1 and row["case_id"] in JUDGEMENT_CASE_IDS
    ]
    temporary_output = output.with_name(output.name + ".tmp")
    save_run(temporary_output, results, queue, metadata)
    temporary_output.replace(output)
    checkpoint.unlink(missing_ok=True)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt-version", choices=["v1", "v2"], default="v2")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--execute", action="store_true", help="Actually send paid API requests")
    parser.add_argument("--smoke", metavar="CASE_ID")
    parser.add_argument("--allow-dirty", action="store_true", help="Allowed only for a labelled smoke test")
    parser.add_argument("--spent-to-date", type=float)
    parser.add_argument("--monthly-spent-to-date", type=float)

    args = parser.parse_args()

    plan = plan_battery(args.model, args.prompt_version)
    print(json.dumps(plan, indent=2))
    if not args.execute:
        print("DRY RUN ONLY. Add --execute after the frozen-commit and budget checks.")
        return 0
    if args.allow_dirty and not args.smoke:
        raise SystemExit("--allow-dirty is permitted only with --smoke")
    safe_model = args.model.replace("/", "__").replace(":", "_")
    output = args.output or ROOT / "results" / "live" / f"{safe_model}__{args.prompt_version}.json"
    destination = execute_battery(
        args.model,
        args.prompt_version,
        output=output,
        smoke_case=args.smoke,
        allow_dirty=args.allow_dirty,
        spent_to_date=args.spent_to_date,
        monthly_spent_to_date=args.monthly_spent_to_date,
    )
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
