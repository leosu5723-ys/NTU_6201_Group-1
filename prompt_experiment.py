"""Freeze the exact v1 and v2 prompt artifacts before live measurement."""
import hashlib
import json
from pathlib import Path

import prompt
import tools


def build_prompt_artifact():
    versions = {}
    for name in ("v1", "v2"):
        text = prompt.build_system_prompt("A", version=name)
        versions[name] = {
            "characters": len(text),
            "estimated_tokens_chars_div_4": len(text) // 4,
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "text": text,
        }
    line_args = {
        "member_id": "M-5502",
        "procedure_code": "45378",
        "attached_documents": [],
    }
    returns = {}
    for name in ("v1", "v2"):
        value = tools.call(
            "A", "review_claim_line", line_args,
            internal={"interface_version": name},
        )
        text = json.dumps(value, sort_keys=True)
        returns[name] = {
            "characters": len(text),
            "estimated_tokens_chars_div_4": len(text) // 4,
            "value": value,
        }
    final_blocks = [
        prompt.format_descriptor(tools.DESCRIPTORS[name])
        for name in sorted(tools.DESCRIPTORS)
    ]
    candidate = json.loads(
        Path("design/precut_tool_block_A.json").read_text(encoding="utf-8")
    )["candidate_tools"]
    candidate_blocks = [prompt.format_descriptor(item) for item in candidate]
    before_text = "\n".join(final_blocks + candidate_blocks)
    after_text = "\n".join(final_blocks)
    tool_block_cut = {
        "before": {
            "tool_count": len(final_blocks) + len(candidate_blocks),
            "characters": len(before_text),
            "estimated_tokens_chars_div_4": len(before_text) // 4,
            "sha256": hashlib.sha256(before_text.encode("utf-8")).hexdigest(),
        },
        "after": {
            "tool_count": len(final_blocks),
            "characters": len(after_text),
            "estimated_tokens_chars_div_4": len(after_text) // 4,
            "sha256": hashlib.sha256(after_text.encode("utf-8")).hexdigest(),
        },
        "estimated_tokens_saved_chars_div_4": (
            len(before_text) // 4 - len(after_text) // 4
        ),
        "removed_tools": [item["name"] for item in candidate],
    }
    return {
        "controlled_model": "google/gemini-2.5-flash-lite",
        "only_intended_change": "review_claim_line ACI version: descriptor and return shape",
        "versions": versions,
        "representative_line_return": returns,
        "tool_block_cut": tool_block_cut,
        "live_results": None,
        "status": "prompts frozen; live v1 and v2 measurements pending",
    }


if __name__ == "__main__":
    destination = Path("artifacts/prompt_comparison.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(build_prompt_artifact(), indent=2) + "\n", encoding="utf-8")
    print(destination)
