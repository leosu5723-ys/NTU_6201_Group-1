"""Generate reviewable Markdown tables from saved evidence files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from harness import JUDGEMENT_CASE_IDS, load_code_expectations

ROOT = Path(__file__).resolve().parent


def _read(relative: str) -> dict[str, Any] | list[Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def build_markdown() -> str:
    scripted = _read("results/scripted/results.json")
    parallel = _read("artifacts/parallel_experiment.json")
    guardrails = _read("artifacts/guardrail_checklist.json")
    failures = _read("artifacts/failure_experiments.json")
    prompts = _read("artifacts/prompt_comparison.json")
    assert isinstance(scripted, dict)
    assert isinstance(parallel, dict)
    assert isinstance(guardrails, list)
    assert isinstance(failures, dict)
    assert isinstance(prompts, dict)

    s = scripted["summary"]
    p = parallel["parallel"]
    q = parallel["sequential"]
    loop = failures["loop_control"]
    interface = failures["tool_interface"]
    v1 = prompts["versions"]["v1"]
    v2 = prompts["versions"]["v2"]
    r1 = prompts["representative_line_return"]["v1"]
    r2 = prompts["representative_line_return"]["v2"]

    lines = [
        "# PE6201 A2 Evidence Tables",
        "",
        "## Scripted harness",
        "",
        "| Cases | Trials | Code-check passes | Negative trials | Median turns | Worst turns |",
        "|---:|---:|---:|---:|---:|---:|",
        f"| 40 | {s['trials']} | {s['passed']} / {s['trials']} | {s['negative_passed']} / {s['negative_trials']} | {s['median_turns']} | {s['worst_case_turns']} |",
        "",
        "## Sequential versus parallel",
        "",
        "| Mode | Trials passed | Total turns | Median turns | Input tokens* | Cost* |",
        "|---|---:|---:|---:|---:|---:|",
        f"| Sequential | {q['passed']} / {q['trials']} | {q['total_turns']} | {q['median_turns']} | {q['tokens_in']:,} | US${q['cost_usd']:.4f} |",
        f"| Parallel | {p['passed']} / {p['trials']} | {p['total_turns']} | {p['median_turns']} | {p['tokens_in']:,} | US${p['cost_usd']:.4f} |",
        "",
        "*Scripted deterministic estimates, not live API billing evidence.*",
        "",
        "## Prompt artifacts",
        "",
        "| Version | Prompt chars | Prompt tokens* | Line-return chars | Line-return tokens* | SHA-256 | Live result |",
        "|---|---:|---:|---:|---:|---|---|",
        f"| v1 | {v1['characters']:,} | {v1['estimated_tokens_chars_div_4']:,} | {r1['characters']} | {r1['estimated_tokens_chars_div_4']} | `{v1['sha256']}` | LIVE RUN PENDING |",
        f"| v2 | {v2['characters']:,} | {v2['estimated_tokens_chars_div_4']:,} | {r2['characters']} | {r2['estimated_tokens_chars_div_4']} | `{v2['sha256']}` | LIVE RUN PENDING |",
        "",
        "## Guardrail checklist",
        "",
        f"{sum(row['passed'] for row in guardrails)} / {len(guardrails)} deterministic cases passed. Three cases use hostile member text.",
        "",
        "## D7 failures",
        "",
        "| Failure | Working | Component removed | Reproduced effect |",
        "|---|---|---|---|",
        f"| Loop control | {loop['working']['turns']} turns, {loop['working']['tool_calls']} calls, US${loop['working']['cost_usd']:.6f} | Action de-duplication | {loop['minus_guard']['turns']} turns, {loop['minus_guard']['tool_calls']} calls, US${loop['minus_guard']['cost_usd']:.6f}; same decision |",
        f"| Tool interface | Correctly requested itemised bill | Required-document fields | Incorrect approval; code-check pass = {str(interface['minus_document_fields']['passed']).lower()} |",
        "",
        "## Live model battery",
        "",
    ]

    live_files = sorted((ROOT / "results" / "live").glob("*.json")) if (ROOT / "results" / "live").exists() else []
    if not live_files:
        lines.extend(["**LIVE RUN PENDING. No model result is represented as measured.**", ""])
    else:
        lines.extend([
            "| Model | Prompt | Trials | Overall pass | Negative pass | Tokens in | Tokens out | Cost |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ])
        for path in live_files:
            payload = json.loads(path.read_text(encoding="utf-8"))
            summary = payload["summary"]
            lines.append(
                f"| {summary['model']} | {summary['prompt_version']} | {summary['trials']} | "
                f"{summary['passed']} / {summary['trials']} | {summary['negative_passed']} / {summary['negative_trials']} | "
                f"{summary['tokens_in']:,} | {summary['tokens_out']:,} | US${summary['cost_usd']:.4f} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Per-case grading map",
            "",
            "Fixed fields are code-checked from `evaluation/code_expectations_A.json`. Reason quality and evidential sufficiency are human-judged only for the selected cases.",
            "",
            "| Case | Code fields | Human judgement |",
            "|---|---|---|",
        ]
    )
    for case_id, expected in sorted(load_code_expectations().items()):
        fields = ["decision", "action count"]
        if "trigger" in expected:
            fields.extend(["trigger", "escalation destination"])
        if "missing" in expected:
            fields.append("exact missing item")
        if "approved_total" in expected:
            fields.extend(["totals", "line identities/statuses", "PA/exclusion IDs"])
        elif "line_dispositions" in expected:
            fields.extend(["resolved line identities/statuses", "PA/exclusion IDs"])
        judged = "Yes: reason and evidence" if case_id in JUDGEMENT_CASE_IDS else "No"
        lines.append(f"| {case_id} | {', '.join(fields)} | {judged} |")
    lines.append("")
    return "\n".join(lines)


def write_markdown(path: str | Path = "artifacts/EVIDENCE_TABLES.md") -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_markdown(), encoding="utf-8")
    return destination


if __name__ == "__main__":
    print(write_markdown())
