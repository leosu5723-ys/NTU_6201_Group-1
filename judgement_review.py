"""Render the frozen judgement queue for human review."""
import json
from pathlib import Path

SOURCE = Path("results/scripted/results.json")
DESTINATION = Path("review/JUDGEMENT_REVIEW_SCRIPTED.md")


def build():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    lines = [
        "# Scripted Judgement Review",
        "",
        "Code checks have already passed. For each item, decide whether the reason and actual tool evidence support every required statement. Do not use substring matching as a verdict.",
        "",
    ]
    for item in payload["judgement_queue"]:
        requirements = item["must_record"]
        trajectory_checks = item.get("trajectory_checks", [])
        lines.extend([
            f"## {item['case_id']}",
            "",
            f"**Decision:** `{item['decision']}`",
            "",
            f"**Reason:** {item['reason']}",
            "",
            f"**Tool evidence:** {', '.join(item['evidence'])}",
            "",
            "**Structured details:**",
            "",
            "```json",
            json.dumps(item.get("details", {}), indent=2),
            "```",
            "",
            "**Required review:**",
            "",
        ])
        lines.extend(f"- [ ] {requirement}" for requirement in requirements)
        if trajectory_checks:
            lines.extend(["", "**Trajectory checks:**", ""])
            lines.extend(f"- [ ] {requirement}" for requirement in trajectory_checks)
        lines.extend([
            "",
            "- Verdict: [ ] Pass  [ ] Fail",
            "- Reviewer:",
            "- Notes:",
            "",
        ])
    return "\n".join(lines)


if __name__ == "__main__":
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(build(), encoding="utf-8")
    print(DESTINATION)
