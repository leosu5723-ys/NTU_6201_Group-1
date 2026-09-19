# Round-two integration and analysis

## Evidence scope

All six member branches were integrated using ordinary merge commits, preserving their authorship and history. No experimental code, configuration, prompts, fixtures, or scoring rules were changed. The experiment remains frozen at `f8a1d7450a4bee92c24f38a6924436bc9faabdaf`; later result/document commits are not new experimental versions.

Each selected battery contains the complete 60-trial matrix over 40 cases. Recorded source cleanliness, frozen hashes, item-level scores, aggregate summaries and embedded decision receipts validate. The complete set contains five v2 models and the Gemini v1 control. Human judgement is a separate, unfinished gate.

Su Yang's selected Claude battery is a complete repeat after the initial round-two run encountered 23 HTTP 429 failures. Access conditions changed to another authorized account/key; the code, model, prompt and case set did not change. The initial run remains under `results/round2_original/su-yang/`, including a relocation manifest. Only the selected complete repeat enters the main comparison; no trial rows are mixed. Both experiments remain part of experimental expenditure. This selection and the access-condition change must remain disclosed in the final report; the improvement cannot be attributed solely to the account change.

## Results

| Model | Version | Strict passes | Negative passes | Median tool turns | Provider-reported battery cost (USD) |
|---|---|---:|---:|---:|---:|
| DeepSeek V3.2 | v2 | 55/60 | 29/30 | 4 | 0.09518398 |
| Llama 4 Maverick | v2 | 53/60 | 27/30 | 6 | 0.22221053 |
| Claude Haiku 4.5 | v2 | 35/60 | 18/30 | 5 | 1.23503300 |
| Qwen3 30B A3B | v2 | 33/60 | 21/30 | 6 | 0.07738525 |
| Gemini 2.5 Flash Lite | v2 | 20/60 | 15/30 | 5 | 0.07533524 |
| Gemini 2.5 Flash Lite | v1 | 33/60 | 18/30 | 5 | 0.07429816 |

Source: `results/live/`; derived analysis: `artifacts/live_analysis_round2.json`. Billing coverage is complete for saved raw responses in the six selected batteries. Displayed battery totals can differ from raw-response subtotals by rounding.

## Interpretation and cost basis

DeepSeek is the provisional recommendation within this frozen system and evaluation set, not a general model leaderboard or a deployment approval. Its five failures are budget-ceiling stops. Llama has six budget-ceiling stops and one action-batch-integrity stop. The two-trial gap is not evidence of a stable population-level advantage.

Gemini v2 does not improve strict success in this battery: 20/60 versus v1's 33/60. Its mean estimated observation size is lower, but shorter observations do not establish better end-to-end reliability. Multiple failure modes and stochastic outputs prevent attributing every difference to the interface rewrite.

Costs use frozen catalogue prices for token expenditure and case-balanced success rates: repeated negative trials must not silently double the assumed operational prevalence of negative cases. Case balancing gives each of the 40 cases equal weight; it is an explicit scenario assumption, not a measured production distribution. Actual provider bills are reported separately.

Under the configured scenario of 8,000 monthly claims, USD 7.60 per failure requiring fallback and USD 400 fixed monthly cost:

| Model | Version | Case-balanced success | Estimated monthly total (USD) |
|---|---|---:|---:|
| DeepSeek V3.2 | v2 | 89.17% | 7,020.66 |
| Llama 4 Maverick | v2 | 87.50% | 8,029.79 |
| Claude Haiku 4.5 | v2 | 57.50% | 26,417.41 |
| Qwen3 30B A3B | v2 | 47.50% | 32,328.15 |
| Gemini 2.5 Flash Lite | v2 | 25.00% | 46,016.62 |
| Gemini 2.5 Flash Lite | v1 | 52.50% | 29,296.76 |

These are scenario estimates, not observed monthly bills. Qwen has the lowest catalogue-priced variable cost, but requires approximately 89.12% case-balanced success to break even against DeepSeek, versus its measured 47.50%. Fallback cost dominates this comparison. Sensitivity scenarios are preserved in the analysis JSON and should accompany final reporting.

## Verification and remaining gates

Integration verification: 117 unit tests pass; scripted evaluation passes 60/60; guardrail command completes; submission verifier reports `deterministic_ready=true` and `live_set_valid=true`. The result files remain unchanged from their member branches.

`submission_ready` remains false. The verifier finds two completed judgement checks and 35 report placeholders. Final report, collective self-appraisal, video link, final approval and submission ZIP remain outstanding. Do not equate machine-scored battery validation with completed human judgement or submission readiness. Existing Phase A and Phase B reviews are preserved; Isha's branch also includes her personal review confirmations.
