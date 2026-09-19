# Human judgement review packet

This packet supports human assessment of explanation quality and evidence. It does not change machine scores or record approval. Review scope and distribution are team decisions; these files do not create a new per-member course requirement.

## Scripted review

Existing verdicts remain in `review/judgement_verdicts.json`. Two recorded reviews are preserved. Read `SCRIPTED_REMAINING.md` for the remaining eight cases. A reviewer returns case ID, pass/fail, real name and an evidence-based reason. Do not sign for another person.

## Live review

One worksheet per selected battery contains the existing ten-case judgement queue. Review the returned outcome against every must-record item and inspect persisted decisions where present. A budget stop can occur after a write, so an escalation return does not prove that no decision was persisted. These are case-level queue entries; use the matching raw trial records for repeated negatives.

Verdicts are deliberately blank. A pass in code checks does not imply a pass here. Never overwrite raw batteries to add human labels; retain separate review records.

| Worksheet | Model | Version | Cases |
|---|---|---|---:|
| [anthropic__claude-haiku-4.5__v2.md](anthropic__claude-haiku-4.5__v2.md) | anthropic/claude-haiku-4.5 | v2 | 10 |
| [deepseek__deepseek-v3.2__v2.md](deepseek__deepseek-v3.2__v2.md) | deepseek/deepseek-v3.2 | v2 | 10 |
| [google__gemini-2.5-flash-lite__v1.md](google__gemini-2.5-flash-lite__v1.md) | google/gemini-2.5-flash-lite | v1 | 10 |
| [google__gemini-2.5-flash-lite__v2.md](google__gemini-2.5-flash-lite__v2.md) | google/gemini-2.5-flash-lite | v2 | 10 |
| [meta-llama__llama-4-maverick__v2.md](meta-llama__llama-4-maverick__v2.md) | meta-llama/llama-4-maverick | v2 | 10 |
| [qwen__qwen3-30b-a3b-instruct-2507__v2.md](qwen__qwen3-30b-a3b-instruct-2507__v2.md) | qwen/qwen3-30b-a3b-instruct-2507 | v2 | 10 |
