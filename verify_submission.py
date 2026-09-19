#!/usr/bin/env python3
"""End-to-end acceptance checks with honest pending-state reporting."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import config
from live_analysis import validate_battery_set

ROOT = Path(__file__).resolve().parent
EXPECTED_MEMBERS = {
    "Meng Sijia",
    "SHI SHUYI",
    "Su Yang",
    "Isha Kirti Ghia",
    "Sun Hanyu",
    "Zhang Jiayang",
}


def _json(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def _run(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    def portable(text: str) -> str:
        return text.replace(str(ROOT), ".").replace(str(Path.home()), "<HOME>")

    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": portable(completed.stdout[-4000:]),
        "stderr": portable(completed.stderr[-4000:]),
    }


def _privacy_failures() -> list[str]:
    failures: list[str] = []
    forbidden = [str(Path.home()), "/var" + "/folders/", "sk" + "-or-"]
    for directory_name in ("artifacts", "results", "report", "docs"):
        directory = ROOT / directory_name
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix in {".json", ".md", ".txt", ".jsonl"}:
                text = path.read_text(encoding="utf-8", errors="replace")
                for token in forbidden:
                    if token in text:
                        failures.append(f"{path.relative_to(ROOT)} contains {token}")
    return failures


def _prose_word_count(text: str) -> int:
    lines = []
    fenced = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced or line.startswith("|") or line.startswith("#") or line.startswith(">"):
            continue
        if line.strip().startswith("**[LIVE"):
            continue
        lines.append(line)
    return len(re.findall(r"\b[\w'-]+\b", "\n".join(lines)))


def validate_case_author_signoff(signoff: dict[str, Any]) -> bool:
    members = signoff.get("members", [])
    if not isinstance(members, list) or len(members) != 6:
        return False
    if {member.get("name") for member in members} != EXPECTED_MEMBERS:
        return False
    expected_cases = {
        row["claim_id"]
        for row in _json("A2_reference_data/data_A/claims.json")
    }
    owned: list[str] = []
    for member in members:
        case_ids = member.get("case_ids", [])
        records = member.get("case_records", [])
        if (
            not 5 <= len(case_ids) <= 8
            or len(case_ids) != len(set(case_ids))
            or member.get("signed") is not True
            or not member.get("date")
            or not isinstance(records, list)
        ):
            return False
        record_ids = [record.get("case_id") for record in records]
        if len(record_ids) != len(set(record_ids)) or set(record_ids) != set(case_ids):
            return False
        if not all(
            record.get("decision_review") and record.get("authorship_or_revision")
            for record in records
        ):
            return False
        owned.extend(case_ids)
    return len(owned) == len(set(owned)) and set(owned) == expected_cases


def validate_mandatory_deliverables(root: Path = ROOT) -> list[str]:
    required = [
        "submission/PE6201_A2_Report.pdf",
        "submission/PE6201_A2_Team_Self_Appraisal.pdf",
        "submission/VIDEO_LINK.txt",
        "submission/FINAL_APPROVAL.json",
        "submission/PE6201_A2_B-1.zip",
        "review/case_author_signoff.json",
    ]
    failures = [relative for relative in required if not (root / relative).exists()]
    if failures:
        return failures

    for relative in required[:2]:
        data = (root / relative).read_bytes()
        if len(data) < 100 or not data.startswith(b"%PDF"):
            failures.append(f"{relative}: invalid or empty")
    archive = (root / required[4]).read_bytes()
    if len(archive) < 100 or not archive.startswith(b"PK"):
        failures.append(f"{required[4]}: invalid or empty")
    link = (root / required[2]).read_text(encoding="utf-8").strip()
    if not link.startswith(("https://", "http://")):
        failures.append(f"{required[2]}: invalid or empty")
    try:
        approval = json.loads((root / required[3]).read_text(encoding="utf-8"))
        approval_ok = (
            approval.get("approved") is True
            and bool(approval.get("approved_by"))
            and bool(approval.get("approved_commit"))
        )
    except (json.JSONDecodeError, OSError, AttributeError):
        approval_ok = False
    if not approval_ok:
        failures.append(f"{required[3]}: invalid approval")
    try:
        signoff = json.loads((root / required[5]).read_text(encoding="utf-8"))
        signoff_ok = validate_case_author_signoff(signoff)
    except (json.JSONDecodeError, OSError, AttributeError, TypeError):
        signoff_ok = False
    if not signoff_ok:
        failures.append(f"{required[5]}: invalid sign-off")
    return failures


def verify(run_commands: bool = True) -> dict[str, Any]:
    command_results: list[dict[str, Any]] = []
    if run_commands:
        commands = [
            [sys.executable, "A2_reference_data/check_my_data.py"],
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            [sys.executable, "run_eval.py"],
            [sys.executable, "run_eval.py", "--guardrails"],
            [sys.executable, "run_eval.py", "--parallel"],
            [sys.executable, "run_eval.py", "--failures"],
            [sys.executable, "prompt_experiment.py"],
            [sys.executable, "result_tables.py"],
        ]
        command_results = [_run(command) for command in commands]

    scripted = _json("results/scripted/results.json")
    guardrails = _json("artifacts/guardrail_checklist.json")
    parallel = _json("artifacts/parallel_experiment.json")
    failures = _json("artifacts/failure_experiments.json")
    claims = _json("A2_reference_data/data_A/claims.json")
    labels = _json("A2_reference_data/expected_outcomes_A.json")
    report_path = ROOT / "report" / "PE6201_A2_Report_Draft.md"
    report_text = report_path.read_text(encoding="utf-8")
    verdict_payload = _json("review/judgement_verdicts.json")
    verdict_rows = verdict_payload.get("cases", [])
    expected_judgement_ids = {
        row["case_id"] for row in scripted.get("judgement_queue", [])
    }
    verdict_ids = [row.get("case_id") for row in verdict_rows]
    judgement_shape_valid = (
        len(verdict_rows) == 10
        and len(set(verdict_ids)) == 10
        and set(verdict_ids) == expected_judgement_ids
    )
    judgement_completed = sum(
        row.get("verdict") in {"pass", "fail"} and bool(row.get("graded_by"))
        for row in verdict_rows
    )
    judgement_ready = (
        judgement_shape_valid
        and judgement_completed == 10
        and all(row.get("verdict") == "pass" for row in verdict_rows)
    )

    live_files = []
    live_payloads = []
    live_root = ROOT / "results" / "live"
    if live_root.exists():
        for path in sorted(live_root.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("metadata", {}).get("kind") == "measured_battery":
                live_files.append(path)
                live_payloads.append(payload)
    live_v2_models = set()
    live_v1 = 0
    for path in live_files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        summary = payload["summary"]
        if summary.get("prompt_version") == "v2":
            live_v2_models.add(summary.get("model"))
        elif summary.get("prompt_version") == "v1":
            live_v1 += 1

    live_set_error = None
    try:
        live_set_validation = validate_battery_set(live_payloads)
        live_set_valid = True
    except (ValueError, KeyError, TypeError) as error:
        live_set_validation = None
        live_set_valid = False
        live_set_error = str(error)

    mandatory_missing = validate_mandatory_deliverables(ROOT)

    privacy = _privacy_failures()
    command_ok = all(row["returncode"] == 0 for row in command_results) if run_commands else True
    deterministic_ready = all(
        [
            command_ok,
            config.BACKEND == "scripted",
            config.PROBLEM == "A",
            len(claims) == 40,
            len(labels) == 40,
            scripted["summary"]["trials"] == 60,
            scripted["summary"]["passed"] == 60,
            len(guardrails) == 10,
            all(row["passed"] for row in guardrails),
            parallel["correctness_unchanged"],
            failures["restoration"]["passed"] == 60,
            not privacy,
        ]
    )
    placeholders = report_text.count("[LIVE")
    submission_ready = all(
        [
            deterministic_ready,
            len(live_v2_models) == 5,
            live_v1 >= 1,
            live_set_valid,
            judgement_ready,
            placeholders == 0,
            _prose_word_count(report_text) <= 2000,
            not mandatory_missing,
        ]
    )
    return {
        "deterministic_ready": deterministic_ready,
        "submission_ready": submission_ready,
        "problem": config.PROBLEM,
        "default_backend": config.BACKEND,
        "cases": len(claims),
        "labels": len(labels),
        "scripted_trials": scripted["summary"]["trials"],
        "scripted_passed": scripted["summary"]["passed"],
        "guardrail_cases": len(guardrails),
        "live_batteries_found": len(live_files),
        "live_v2_models_found": sorted(model for model in live_v2_models if model),
        "live_v1_batteries_found": live_v1,
        "live_set_valid": live_set_valid,
        "live_set_error": live_set_error,
        "live_set_validation": live_set_validation,
        "judgement_checks_completed": judgement_completed,
        "judgement_checks_ready": judgement_ready,
        "mandatory_deliverables_missing": mandatory_missing,
        "report_placeholders": placeholders,
        "report_prose_word_count": _prose_word_count(report_text),
        "privacy_failures": privacy,
        "commands": command_results,
        "next_gate": (
            "frozen live model batteries and judgement review"
            if deterministic_ready and not submission_ready
            else "fix deterministic failures"
            if not deterministic_ready
            else "final team approval"
        ),
    }


if __name__ == "__main__":
    result = verify(run_commands=True)
    destination = ROOT / "artifacts" / "verification_report.json"
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "commands"}, indent=2))
    raise SystemExit(0 if result["deterministic_ready"] else 1)
