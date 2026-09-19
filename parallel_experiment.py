"""D2(c) sequential-versus-parallel experiment on identical scripted cases."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from backends import SCRIPTS
from harness import run_set, summarise


def sequentialise(
    scripts: dict[str, list[dict[str, Any]]]
) -> dict[str, list[dict[str, Any]]]:
    """Split only independent same-turn calls; preserve dependencies and finals."""
    result: dict[str, list[dict[str, Any]]] = {}
    for case_id, moves in scripts.items():
        expanded: list[dict[str, Any]] = []
        for move in moves:
            calls = move.get("calls")
            if not calls or len(calls) == 1:
                expanded.append(copy.deepcopy(move))
                continue
            for index, call in enumerate(calls, 1):
                expanded.append(
                    {
                        "thought": f"Sequential control {index}/{len(calls)} from an otherwise independent call set.",
                        "calls": [copy.deepcopy(call)],
                    }
                )
        result[case_id] = expanded
    return result


def _summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    summary = summarise(results)
    summary["total_turns"] = sum(row["record"]["turns"] for row in results)
    return summary


def run_parallel_experiment() -> dict[str, Any]:
    case_ids = sorted(SCRIPTS)
    one_trial = lambda _case_id: 1
    # Hold the cap above every legitimate sequential trajectory so the only
    # experimental variable is call grouping. Deployment caps are evaluated
    # separately from the observed working-mode turn distribution.
    import config
    original_turns, original_tokens = config.MAX_TURNS, config.MAX_TOKENS_PER_RUN
    config.MAX_TURNS, config.MAX_TOKENS_PER_RUN = 30, 1_000_000
    try:
        parallel_results, _ = run_set(
            case_ids,
            problem="A",
            backend_name="scripted",
            trials_for=one_trial,
            scripted_scripts=SCRIPTS,
        )
        sequential_scripts = sequentialise(SCRIPTS)
        sequential_results, _ = run_set(
            case_ids,
            problem="A",
            backend_name="scripted",
            trials_for=one_trial,
            scripted_scripts=sequential_scripts,
        )
    finally:
        config.MAX_TURNS, config.MAX_TOKENS_PER_RUN = original_turns, original_tokens
    return {
        "dependency_rule": "Calls share a turn only when neither needs the other's output. Eligibility and duplicate checks precede line review to preserve early exits.",
        "parallel": _summary(parallel_results),
        "sequential": _summary(sequential_results),
        "correctness_unchanged": all(row["passed"] for row in parallel_results)
        and all(row["passed"] for row in sequential_results),
        "limits": [
            "Parallel calls can spend work that a later observation makes unnecessary.",
            "Grouping calls removes intermediate model decision points.",
        ],
    }


def save_experiment(path: str | Path = "artifacts/parallel_experiment.json") -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(run_parallel_experiment(), indent=2) + "\n", encoding="utf-8"
    )
    return destination


if __name__ == "__main__":
    result = run_parallel_experiment()
    print(json.dumps(result, indent=2))
    print(save_experiment())
