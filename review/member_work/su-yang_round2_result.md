# Su Yang — Round Two Result and Approved Replacement

Member: Su Yang | Date: 19 September 2026

## Selected result

Following the integration owner's approval, the complete repeat battery is selected for the round-two model comparison. The initial round-two battery encountered 23 HTTP 429 failures. A different authorized API key/account was used for the repeat; no HTTP 429 occurred in that run. The code, model, prompt and evaluation set were unchanged. This change in access conditions is disclosed; the improvement is not attributed solely to the key change because repeated model outputs can also vary.

- Model: `anthropic/claude-haiku-4.5`; prompt: `v2`.
- Experiment SHA: `f8a1d7450a4bee92c24f38a6924436bc9faabdaf`.
- Branch: `member/su-yang-round2`.
- Pre-run checks: 117 unit tests passed; fixture checks passed; scripted evaluation 60/60.
- Selected battery: 60 unique trials, 40 cases, recorded `dirty=false`, no remaining checkpoint.

| Metric | Initial round two (archived) | Selected repeat |
|---|---:|---:|
| Strict passes | 23/60 (38.3%) | 35/60 (58.3%) |
| Negative-trial passes | 14/30 (46.7%) | 18/30 (60.0%) |
| Recorded cost, USD | 0.763461 | 1.235033 |
| HTTP 429 failures | 23 | 0 |
| Median / maximum tool turns | 3 / 6 | 5 / 6 |

Selected input/output usage is 1,019,878 / 43,031 tokens. Its provider-reported and catalog costs both equal US$1.235033. The archived run's aggregate provider cost is null; its recorded/catalog cost and known raw-response charge subtotal are US$0.763461, with failed-request billing coverage disclosed in the original data.

## Remaining failures

The selected run has 25 failed trials: 15 `budget_ceiling` stops, seven `tool_or_schema_error` stops caused by unsupported top-level fields, and three CLM-8910 trials using `outside_policy_dates` instead of the required `policy_lapsed` trigger. The budget guard checks projected next-request usage against 25,000 tokens; a stop does not necessarily mean actual consumption exceeded the cap. There were zero step-cap hits.

This is a run without observed HTTP 429, not an interference-free run or a pure capability score. All remaining failures are retained.

## Evidence locations and integration

- Main-analysis input: `results/live/anthropic__claude-haiku-4.5__v2.json` (the repeat JSON, renamed without changing its contents).
- Selected companion logs: `results/live/anthropic__claude-haiku-4.5__v2__supplementary-logs/`. Keep this name because the raw JSON references it.
- Initial round-two JSON and logs: `results/round2_original/su-yang/`. The archived JSON retains its original log-path strings; resolve these using `relocation_manifest.json`, which records the moves and original file hashes.
- Round one remains under `results/round1/`.

Only the selected JSON belongs in the six-battery round-two aggregation. Recompute case-balanced Layer 1/2 costs, monthly totals, sensitivity and break-even using that complete battery; do not combine trial rows across runs. Preserve both runs in the experimental spending ledger: their recorded costs total US$1.998494. Adding the previously declared US$0.146712 gives US$2.145206 recorded/declared A2 expenditure, subject to billing reconciliation. The repeat metadata records the replacement key owner's declared monthly spend before that run; budget scopes must not be conflated with a model's per-task operating cost.

## Interpretation

The selected run improves strict success by 20 percentage points over the initial round-two run, but 58.3% remains insufficient for deployment. The repeat helps distinguish rate-limit failures from the remaining runtime, output-contract and decision-trigger limitations.

Su Yang previously confirmed that the initial round-two experiment was worthwhile for diagnosis but insufficient for deployment, and has relayed the integration owner's approval to select this repeat for the main analysis. The numerical update does not constitute a new personal endorsement of production readiness.
