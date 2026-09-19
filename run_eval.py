#!/usr/bin/env python3
"""Marker-facing deterministic entry point for PE6201 A2 Problem A."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import config
import prompt
from failure_experiments import save_failures
from guardrail_harness import save_checklist
from harness import report, run_set, save_run
from parallel_experiment import save_experiment

ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id", nargs="?")
    parser.add_argument("--prompt", action="store_true")
    parser.add_argument("--prompt-version", choices=["v1", "v2"], default="v2")
    parser.add_argument("--guardrails", action="store_true")
    parser.add_argument("--failures", action="store_true")
    parser.add_argument("--parallel", action="store_true")
    args = parser.parse_args()

    if config.BACKEND != "scripted":
        raise SystemExit("The submitted run_eval.py requires BACKEND='scripted'")
    if config.PROBLEM != "A":
        raise SystemExit("The submitted run_eval.py requires PROBLEM='A'")

    if args.prompt:
        prompt.audit("A", args.prompt_version)
        return 0
    if args.guardrails:
        print(save_checklist(ROOT / "artifacts" / "guardrail_checklist.json"))
        return 0
    if args.failures:
        print(save_failures(ROOT / "artifacts" / "failure_experiments.json"))
        return 0
    if args.parallel:
        print(save_experiment(ROOT / "artifacts" / "parallel_experiment.json"))
        return 0

    case_ids = [args.case_id] if args.case_id else None
    trials = (lambda _case_id: 1) if args.case_id else None
    output_dir = ROOT / "results" / "scripted"
    results, queue = run_set(
        case_ids,
        problem="A",
        backend_name="scripted",
        prompt_version=args.prompt_version,
        trials_for=trials,
        verbose=bool(args.case_id),
        output_dir=output_dir / "run_logs",
    )
    summary = report(results)
    destination = save_run(
        output_dir / (f"{args.case_id}.json" if args.case_id else "results.json"),
        results,
        queue,
        metadata={
            "problem": "A",
            "backend": "scripted",
            "network_required": False,
            "api_key_required": False,
            "prompt_version": args.prompt_version,
        },
    )
    print(destination)
    if args.case_id:
        print(json.dumps(results[0]["record"], indent=2, default=str))
    return 0 if summary["passed"] == summary["trials"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
