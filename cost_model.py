"""Class 5 three-layer cost-to-serve calculations for A2."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def token_cost(
    input_tokens: int,
    output_tokens: int,
    price_in_per_million: float,
    price_out_per_million: float,
) -> float:
    return (input_tokens / 1_000_000) * price_in_per_million + (
        output_tokens / 1_000_000
    ) * price_out_per_million


def cost_to_serve(
    *,
    variable_cost: float,
    success_rate: float,
    failure_cost: float,
    monthly_volume: int,
    fixed_monthly: float,
) -> dict[str, float]:
    if not 0 <= success_rate <= 1:
        raise ValueError("success_rate must be between 0 and 1")
    expected_fallback = (1 - success_rate) * failure_cost
    per_task = variable_cost + expected_fallback
    monthly_variable_and_fallback = per_task * monthly_volume
    return {
        "per_task_variable": variable_cost,
        "expected_fallback_per_task": expected_fallback,
        "cost_to_serve_per_task": per_task,
        "monthly_variable_and_fallback": monthly_variable_and_fallback,
        "fixed_monthly": fixed_monthly,
        "monthly_total": monthly_variable_and_fallback + fixed_monthly,
    }


def break_even_success_rate(
    *,
    cheap_variable_cost: float,
    expensive_cost_to_serve: float,
    failure_cost: float,
) -> float:
    if failure_cost <= 0:
        raise ValueError("failure_cost must be positive")
    rate = 1 - (expensive_cost_to_serve - cheap_variable_cost) / failure_cost
    return max(0.0, min(1.0, rate))


def sensitivity_table(
    *,
    variable_cost: float,
    success_rate: float,
    failure_cost: float,
    monthly_volume: int,
    fixed_monthly: float,
) -> list[dict[str, float]]:
    rates = [max(0.0, success_rate - 0.10), success_rate, min(1.0, success_rate + 0.10)]
    rows = []
    for rate in rates:
        row = {"success_rate": round(rate, 10), "failure_cost": failure_cost}
        row.update(
            cost_to_serve(
                variable_cost=variable_cost,
                success_rate=rate,
                failure_cost=failure_cost,
                monthly_volume=monthly_volume,
                fixed_monthly=fixed_monthly,
            )
        )
        rows.append(row)
    return rows


def sensitivity_grid(
    *,
    variable_cost: float,
    success_rate: float,
    failure_cost: float,
    monthly_volume: int = 8_000,
    fixed_monthly: float = 0.0,
) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for factor in (0.75, 1.0, 1.25):
        rows.extend(
            sensitivity_table(
                variable_cost=variable_cost,
                success_rate=success_rate,
                failure_cost=failure_cost * factor,
                monthly_volume=monthly_volume,
                fixed_monthly=fixed_monthly,
            )
        )
    return rows


def load_measured_live_run(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    summary = payload.get("summary") or {}
    if summary.get("backend") != "live":
        raise ValueError(f"{path} is not a measured live run")
    if not summary.get("trials") or summary.get("tokens_in", 0) <= 0:
        raise ValueError(f"{path} has no measured token evidence")
    return payload


def analyse_live_runs(
    paths: Iterable[str | Path],
    prices: dict[str, dict[str, float]],
    *,
    failure_cost: float = 7.60,
    monthly_volume: int = 8_000,
    fixed_monthly: float = 400.0,
) -> dict[str, Any]:
    models: list[dict[str, Any]] = []
    for path in paths:
        payload = load_measured_live_run(path)
        summary = payload["summary"]
        model = summary["model"]
        if model not in prices:
            raise KeyError(f"No checked price for {model}")
        trials = int(summary["trials"])
        variable = token_cost(
            int(summary["tokens_in"]) // trials,
            int(summary["tokens_out"]) // trials,
            prices[model]["input_per_million"],
            prices[model]["output_per_million"],
        )
        service = cost_to_serve(
            variable_cost=variable,
            success_rate=float(summary["pass_rate"]),
            failure_cost=failure_cost,
            monthly_volume=monthly_volume,
            fixed_monthly=fixed_monthly,
        )
        models.append(
            {
                "model": model,
                "trials": trials,
                "pass_rate": summary["pass_rate"],
                "negative_pass_rate": summary.get("negative_pass_rate"),
                "mean_variable_cost": variable,
                **service,
                "sensitivity": sensitivity_grid(
                    variable_cost=variable,
                    success_rate=float(summary["pass_rate"]),
                    failure_cost=failure_cost,
                    monthly_volume=monthly_volume,
                    fixed_monthly=fixed_monthly,
                ),
            }
        )
    models.sort(key=lambda row: row["mean_variable_cost"])
    return {
        "volume_per_month": monthly_volume,
        "failure_cost": failure_cost,
        "fixed_monthly": fixed_monthly,
        "models": models,
        "status": "measured" if models else "awaiting live run files",
    }
