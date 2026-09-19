# D6 Cost Assumptions

## Official Problem A inputs

- Monthly volume: 8,000 claims
- Claims-assessor rate: US$38 per hour
- Handling time after an agent failure: 12 minutes
- Failure cost: `38 × 12 / 60 = US$7.60`

A failed first response is escalated to a person rather than retried until the model succeeds. The applicable formula is therefore:

```text
case-balanced variable cost per task
+ (1 - case-balanced success rate) × US$7.60
```

Negative cases run three times for robustness, while ordinary cases run once. The 60-trial pass rate is reported as the official evaluation statistic. For cost-to-serve, each of the 40 cases receives equal weight after its repeated trials are averaged. This avoids silently treating the ten negative cases as half of production volume. The equal-case mix is still an evaluation proxy, not a claim about real insurer prevalence.

## Fixed monthly baseline

The proposed baseline is **US$400 per month**:

| Fixed activity | Assumption | Monthly cost |
|---|---:|---:|
| Monitoring and maintenance | 8 hours × US$38/hour | US$304 |
| Evaluation review | 2 hours × US$38/hour | US$76 |
| Log storage and lightweight infrastructure | Stated allowance | US$20 |
| **Total** | | **US$400** |

The labour hours and infrastructure allowance are team assumptions, not supplied facts. They must be stated as such. A sensitivity view should include US$200, US$400 and US$800 fixed monthly cost if the conclusion is sensitive to this layer.

## Baseline exclusions

The headline baseline must not assume:

- Prompt-caching discounts
- Free provider credits
- Hidden retry success
- Unmeasured reasoning-token caps
- A live web or retrieval fee

If caching appears in an API usage block, report the measured adjusted value beside the plain list-price baseline rather than replacing it.

## Shipped experiment caps

- Per run: 8 model/tool turns and 25,000 total input-plus-output tokens.
- Per member for A2: US$3 projected API spend; redesign rather than exceed it.
- Per API-key owner per calendar month: US$25 projected API spend.

Formal live execution requires both A2 and monthly spend-to-date inputs. Preflight rejects a run that would exceed either ceiling, and the provider request separately caps each response at 2,000 output tokens.

## Sensitivity

Cross:

- Success rate at measured value minus 10 percentage points, measured value, and plus 10 points
- Failure cost at US$5.70, US$7.60 and US$9.50
- Fixed monthly cost at US$200, US$400 and US$800 when discussing operational uncertainty

The final recommendation must state whether the preferred model changes anywhere in this range.
