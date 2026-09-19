# SHI SHUYI: Round-two Qwen3 results

## Experiment and result

- Model: `qwen/qwen3-30b-a3b-instruct-2507`; prompt version: `v2`.
- Frozen experiment: `f8a1d7450a4bee92c24f38a6924436bc9faabdaf`; recorded source state: clean.
- Evidence: `results/live/qwen__qwen3-30b-a3b-instruct-2507__v2.json` and its companion decision-log directory.
- Completed: 60 unique trials over 40 cases, with no remaining checkpoint.

| Metric | Round one | Round two |
|---|---:|---:|
| Strict passes | 16/60 (26.7%) | 33/60 (55.0%) |
| Negative-case passes | 11/30 (36.7%) | 21/30 (70.0%) |
| Median turns | 5 | 6 |
| Provider-reported cost, USD | 0.06326631 | 0.07738525 |

Round-two catalogue token cost is USD 0.05373617. This is distinct from the provider-reported billing total above. Round-one evidence remains separately archived under `results/round1/`.

## Failure interpretation

Of the 27 failed trials, 19 stopped at the per-run token ceiling, three exceeded the recoverable tool-error cap, one triggered duplicate-action protection, and four finished without a stop flag but failed strict scoring. The token ceiling is a local trajectory guard, not exhaustion of the course account balance.

The observed completion gain came with a longer median trajectory and higher billed cost. Bounded correction can help complete valid actions, but repeated context and additional turns still consume the fixed token allowance. The remaining failures therefore matter to both reliability and expected human fallback cost.

This before/after comparison describes the combined runtime and interface revision. It does not isolate the causal effect of any single repair. Offline regression success is not substituted for these live results, and no failed trials were removed or selectively rerun.

## Implication for the final comparison

Qwen3 completed more strict trials in the revised system at a low measured API cost, but 33/60 does not establish deployment readiness. Whether it is the preferred model depends on the complete second-round comparison, especially negative-case reliability and cost to serve including human fallback. The current evidence supports retaining the frozen experiment and analysing its limits rather than changing caps during the coordinated battery.

This result note supplements the versioned loop/tool strand review; it does not replace that review or alter the frozen code, scoring or case contracts.
