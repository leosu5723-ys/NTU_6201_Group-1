# Phase B — Cost Strand Review and D6 Data Acceptance Contract

Member: Su Yang | Strand: Cost analysis | Date: 19 September 2026

Status: Submitted for leader review — corrections and data requirements identified. Final D6 numerical conclusions remain pending validation of all six raw batteries and resolution of the findings below.

## 1. Scope and verdict

Reviewed the cost strand (`cost_model.py`, `live_analysis.py`, `docs/cost_assumptions.md`, `config/model_catalog.json`), the runner and usage-recording path, local experiment artifacts, and Su Yang's live JSON. Requirements were checked against the official assignment PDF, D6, pages 15–17. Experiment reference commit: `42253ad28fc58b36b9014808f9d8e3fd523c01ed`.

**Verdict: the basic escalation-cost model is suitable, but the existing analysis is not yet sufficient for a complete D6 submission.** The intake and fixes below are necessary to produce the cost ledger, Layers 1–3, sensitivity table, break-even analysis and three-cap evidence. Chat summaries of pass rates and total spend alone are insufficient.

Preserve the frozen batteries and original scores. Any correction to analysis must record its own analysis version and keep the experiment commit separately. Changes to the agent or prompt require a separately agreed experiment; they cannot silently replace the frozen results.

## 2. Findings requiring resolution

| Priority | Finding and evidence | Required action / acceptance test |
|---|---|---|
| High | `live_analysis.analyse()` calls `implied_step_reliability()` with the median number of turns. Claude has median 0; the helper raises `ValueError: median_turns must be positive` (reproduced offline). | Return a documented N/A diagnostic for zero-turn runs, preserving their failures and spend. Analysis must finish with a zero-turn battery included. |
| High | Operating cost and sensitivity use `cost_usd`, which may use provider billing, while D6 requires plain list-price input/output costs as the headline baseline. A catalog mean is printed but a complete parallel catalog-based service analysis is not. | Calculate all baseline layers, sensitivity and break-even using list prices. Present measured provider charges separately, with coverage and adjustments. |
| High | Provider-cost coverage can be incomplete. Claude has 58 priced responses and 2 failed requests without usage; the battery provider total is null. | Publish known billed subtotal, priced/unpriced request counts and reconciliation status. Missing is not zero. Retain raw usage, and reconcile outstanding charges with provider activity before claiming complete actual spend. |
| High | `sensitivity_grid()` varies success and failure cost but leaves fixed monthly overhead unchanged. | Export the proposed 3 × 3 × 3 scenario grid, including fixed costs of $200/$400/$800, and compare model rankings in each scenario. |
| Medium | The break-even helper clips its result to [0,1], hiding thresholds outside the feasible range. | Preserve the unbounded threshold and label “always meets within [0,1]” or “unattainable” as appropriate; retain a display-only clipped value if useful. |
| Medium | Battery validation compares experiment commit with the current checkout HEAD. A later documentation/results commit can fail this check despite unchanged experiment artifacts. | Validate against the explicit frozen experiment reference and hashes, or run validation in a separate frozen checkout. Record the analysis commit independently; do not alter raw metadata to force acceptance. |
| Medium | Budget inputs are self-declared spend-to-date. A new key with zero usage does not establish zero monthly spend for its owner. | Obtain owner-level, calendar-month reconciliation across relevant keys/accounts and an A2-specific spend ledger. Preserve original declarations and attach corrections separately. |
| Medium | Lowest variable cost may describe an early integration failure rather than an efficient completed workflow. | Report failure categories and pass rates beside costs. A financially lowest row is not automatically a deployable recommendation. |

## 3. Claude evidence and limits

Source: `results/live/anthropic__claude-haiku-4.5__v2.json`.

SHA-256: `94d625ad1e0753c85bbbdfaba6e9963a96ed8f083fef740e9925c8b7b0191ecc`.

| Item | Observed result |
|---|---:|
| Trials / passes | 60 / 0 |
| Input / output tokens | 121,394 / 4,636 |
| Catalog cost | $0.144574 |
| Raw responses carrying provider cost | 58 |
| Known provider-charge subtotal | $0.144574 |
| Failed requests without returned usage | 2 |
| Median tool turns / observation calls | 0 / 0 |

The token-price calculation is `121394 / 1e6 × 1 + 4636 / 1e6 × 5 = $0.144574`. Individual successful HTTP responses retain provider charges; the null aggregate must not be described as complete loss of billing data. The two HTTP 429 failures need billing reconciliation.

The 58 returned responses contain fenced JSON. The strict parser rejects that format; its error-final lacks the required escalation destination and fails validation before a tool turn. This is an interface failure in the measured system, not evidence that Claude completed and misjudged all 60 claims. Removing fences for diagnostic inspection does not produce a new measured success rate. Preserve 0/60.

This expenditure is the observed battery cost, not a demonstrated cost for successfully processing a claim. The cheap early stop must not be presented as a performance improvement.

## 4. Required data intake

Collect one original measured-battery JSON per assigned run, including metadata, all result rows, raw responses and usage. The six assignments are Gemini Flash Lite v2 (Meng Sijia), Qwen v2 (SHI SHUYI), Claude Haiku v2 (Su Yang), Llama Maverick v2 (Isha Kirti Ghia), DeepSeek v2 (Sun Hanyu), and Gemini Flash Lite v1 control (Zhang Jiayang). Model IDs must match the frozen catalog.

For each battery verify:

- Exactly 40 distinct cases and 60 unique trial identities: 30 ordinary cases once, 10 negative cases three times. Retain all failed, capped and rate-limited trials.
- Frozen experiment SHA, claims/answer-key/scripts hashes, and identical v2 prompt hash across the five v2 runs. Keep the different v1 prompt hash explicit.
- Runner, model ID, prompt version, run identifier and available timestamps; price source, timestamp, currency and per-million input/output rates.
- Per-trial case ID, repeat index, pass flag/check failures, input/output tokens, turns, stop reason, observation count/size and elapsed time.
- Per-request identity, raw usage, provider cost, cache/reasoning details if returned, HTTP attempts and errors. Unavailable fields require an explicit missing-data note, not invented values.
- A2 spend before/after, owner monthly spend before/after, reporting month and scope, additional smoke/retry/failed-run costs, and cap configuration. Never collect API keys.
- Original-file hash and provenance. If traces contain credentials, quarantine them and provide a redacted copy with a redaction manifest; do not distribute the secret-bearing original.

Accept failure as a valid experiment outcome when provenance is intact. Mark incomplete billing or missing evidence separately; do not require a high pass rate for accepting a battery.

## 5. Layer definitions and aggregation

Use USD throughout. For trial j of case i:

`C_ij = input_tokens_ij × price_in / 1e6 + output_tokens_ij × price_out / 1e6 + explicit_tool_fees_ij`.

Average repeats within each case, then average the 40 case means to obtain `C` and success probability `p`. Report the official trial-weighted `passed / 60` separately. Equal case weighting is a test-set proxy, not a measured production case mix. Actual battery spend is the sum of trial/request costs, never the balanced mean multiplied by 60.

| Deliverable | Definition and inputs |
|---|---|
| Layer 1 | Plain list-price cost C per task, with separately justified retrieval/tool fees (zero for the local simulated tools). Include failed attempts. Keep provider-adjusted costs alongside, with coverage. |
| Layer 2 | `(1 − p) × F`, where official Problem A `F = $38/hour × 12 minutes / 60 = $7.60`. Here p is evaluation correctness, not the fraction of claims approved; correct requests for documents and correct escalations can pass. |
| Cost per successful task (assignment's escalation convention) | `S = C + (1 − p) × F`. Assumes failed automated work is resolved by a human. Do not silently substitute `C/p`, which prices retry-until-success. |
| Layer 3 | Fixed monthly H, proposed $400: monitoring/maintenance $304 (8h × $38), evaluation review $76 (2h × $38), infrastructure/storage $20. These are team assumptions. Specify recurring evaluation API costs and whether they are included or additional; avoid double counting one-time assignment batteries. |
| Monthly total | `M = 8000 × S + H`. Fully allocated cost per task is `S + H/8000`. At H=$400, fixed allocation is $0.05/task. |

Record caching/reasoning configuration and measured usage when available. Do not double-count reasoning tokens already included in completion tokens. No unsupported cache discount belongs in the baseline. A causal caching-savings claim requires matched with/without evidence; otherwise state that it was not tested.

## 6. Cost ledger — four levers

The assignment's cost ledger is a before/after engineering table, not merely an API spending table. Keep both.

| Lever | Required evidence | Existing local evidence and remaining work |
|---|---|---|
| B: tool-definition block | Before/after definitions, tools removed, token method and sizes | `artifacts/prompt_comparison.json`: 9 → 7 tools; tool block estimated 1,644 → 1,398 tokens. Whole prompt grows 1,907 → 2,017; do not call that whole-prompt shrinkage. |
| T: sequential/parallel | Same cases and logic; turns, input tokens, passes, cost basis | `artifacts/parallel_experiment.json` / `EVIDENCE_TABLES.md`: total turns 251 → 157; input estimates 742,622 → 495,381 over 40 trials. Scripted estimates, not actual billed savings. |
| D: observation payload | Same tool input, before/after descriptor and returned payload, tokens per call | Prompt comparison's example line return: estimated 115 → 56 tokens. Label it an example; add per-call distributions or a matched aggregate if claiming whole-workload savings. |
| p: success | Gemini v1/v2 raw batteries, comparable checks, pass rate, balanced p and resulting S | Pending acceptance of both raw files. Cross-model rows support model comparison, not isolated causal attribution to the descriptor change. |

Each ledger row needs `evidence_path`, `measurement_method`, `before`, `after`, `delta`, `scope`, and `limitation`. The explanatory `B×T + D×T²/2` model is approximate; fixed instructions and other transcript content also contribute. Identify the dominant lever using matched evidence and distinguish token-bill effects from fallback labour. Do not add overlapping savings as independent effects.

## 7. Sensitivity Analysis Table

The following grid is a proposed implementation of the sensitivity analysis, not an additional prescribed submission format. Confirm the fixed-cost scenarios with the team.

For each of the five v2 models, cross `p_low=max(0,p−0.10)`, p, `p_high=min(1,p+0.10)` with F=$5.70/$7.60/$9.50 and H=$200/$400/$800: 27 labelled scenarios per model, 135 rows. Boundary clipping can yield duplicate numerical scenarios; label that explicitly. The v1 control can be appended separately.

Columns: `model`, `prompt_version`, `cost_basis`, `scenario`, `p`, `F`, `H`, `C`, `fallback_per_task`, `S`, `monthly_volume`, `monthly_total`, `allocated_per_task`, `lowest_cost_model`, `recommendation_changes`.

Compare all models under the same scenario assumptions; report whether the selected model remains preferred. Also check conservative pairwise uncertainty (candidate p_low versus competitor p_high), since moving every model together does not establish robustness to independent estimation error. The ±10-point range is a scenario range, not a statistical confidence interval.

## 8. Break-even Analysis

Choose the cheap v2 candidate by catalog C and identify an explicit comparison model. Let `E = C_reference + (1−p_reference)F` and `p_star = 1−(E−C_cheap)/F`. Report both models, measured balanced success rates, C, E, F, p_star, and `p_cheap−p_star` in percentage points; state whether the cheap option clears it. If token and service-cost rankings differ, explain this rather than assuming a more expensive model is better.

Keep H out of this official threshold when it is identical across models; if model-specific overhead differs, show a separate adjusted threshold using overhead per task. Recalculate at the failure-cost sensitivity values. Preserve thresholds outside [0,1] with feasibility labels; handle F=0 explicitly if ever introduced. A zero observed success rate does not make the escalation formula undefined, but prevents claiming demonstrated autonomous success.

## 9. Three Caps and evidence

| Control | Frozen configuration | Evidence to collect |
|---|---|---|
| Step cap | 8 turns | Config reference, observed turns/stop reason, guardrail test evidence; explain that stored tool turns exclude final-only model responses. |
| Budget ceiling | 25,000 input+output tokens per run; 2,000 output tokens per response; $3 A2 API spend per member | Request/run limits, preflight and per-trial checks, actual cumulative A2 ledger including additional attempts. |
| Monthly per-user ceiling | $25 per API-key owner per calendar month | Month/scope, reconciled previous expenditure across keys, current experiment costs and remaining amount. A provider key's own cap/balance is a separate constraint. |

Describe both configured limits and actual enforcement evidence. Estimated preflight headroom is not a verified account balance or complete proof that cumulative spending stayed under cap.

## 10. Handoff and completion gate

Recommended outputs: `cost_ledger.csv`, `cost_layers.csv`, `sensitivity_analysis.csv`, `break_even_analysis.csv`, `three_caps.csv`, plus `data_acceptance.md` and source-file hashes. These filenames describe proposed deliverables, not files already generated by this review.

D6 is ready only after six batteries pass provenance/completeness checks; billing coverage is stated and reconciled where completeness is claimed; baseline and adjusted costs are separated; zero-turn analysis works; the four-lever evidence is scoped correctly; Layer 3 assumptions are signed off; sensitivity and break-even are reproducible; and owner-level cap evidence is collected. Unresolved items must remain visible in the final report.
