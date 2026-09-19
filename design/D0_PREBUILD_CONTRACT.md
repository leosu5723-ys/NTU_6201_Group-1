# D0 Pre-Build Diagnostic and Good-Run Contract

This contract records the criteria used by the tests and harness. The implementation contract and tool dependency design were written in the local workspace before the core replacement work. Because the first candidate has not yet been committed, this statement records the working chronology but is not presented as commit-history proof.

## Ladder decision

Problem A is implemented at rung 7 because the claim controls the next retrieval and the number of steps. A fixed single call would either guess or receive all records at once. A fixed chain would perform unnecessary checks after decisive escalation facts. Routing and parallelisation help within the loop but do not decide which line requires another lookup. Orchestrator-workers could split a claim at runtime but would add out-of-scope agents without providing the single evidence-driven write boundary. An evaluator-optimiser improves an answer without adding missing system-of-record facts. Read-only model-directed lookup is agentic retrieval; `issue_decision_letter` is the first irreversible action and the governance cliff into an acting agent.

This does not mean an agent is always preferable in production. If the routing table remains completely structured and stable, a deterministic workflow may be safer. If ground truth becomes slow or subjective, the agent should lose autonomy and move behind a human decision gate.

## Ground-truth test

The loop can be contradicted within seconds by:

- Policy status, dates and remaining limit
- Procedure and exclusion records
- Required-document rules
- Pre-authorisation records
- Hospital panel records
- Previously decided claims

Member narrative is not ground truth. It is untrusted external text.

## Five numbered statements of a good run

1. **It names the actual cause.** The decision and single trigger or missing item are traceable to a system-of-record observation rather than a plausible narrative.
2. **It follows the fixed routing table.** Lapsed, out-of-date, over-limit, duplicate and hostile claims escalate; missing evidence requests; fully resolved lines approve in principle.
3. **It resolves the complete claim.** Every submitted line receives one covered or excluded disposition, totals reconcile, and an excluded line does not escalate the whole claim.
4. **It abstains safely.** Missing, expired, malformed or hostile evidence produces a specific request, loud stop or human escalation instead of an invented approval.
5. **It acts once within measured limits.** The irreversible action occurs exactly once only after confirmation, while turns, tokens, latency, cost and guardrail events remain recorded.

Each statement maps to deterministic code checks, selected judgement checks or guardrail cases. None depends only on persuasive prose.

## Reliability diagnostic

After the frozen live battery, compute:

```text
s = P^(1/T)
```

where `P` is whole-run pass rate with its trial count and `T` is measured median turns per run. Use `s` only to ask whether evidence points more strongly to weak step quality or excessive step count. Steps are not independent and do not have equal difficulty.
