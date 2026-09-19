# PE6201 A2 Evidence Tables

## Scripted harness

| Cases | Trials | Code-check passes | Negative trials | Median turns | Worst turns |
|---:|---:|---:|---:|---:|---:|
| 40 | 60 | 60 / 60 | 30 / 30 | 4.0 | 5 |

## Sequential versus parallel

| Mode | Trials passed | Total turns | Median turns | Input tokens* | Cost* |
|---|---:|---:|---:|---:|---:|
| Sequential | 40 / 40 | 251 | 6.0 | 911,506 | US$0.0995 |
| Parallel | 40 / 40 | 157 | 4.0 | 609,144 | US$0.0688 |

*Scripted deterministic estimates, not live API billing evidence.*

## Prompt artifacts

| Version | Prompt chars | Prompt tokens* | Line-return chars | Line-return tokens* | SHA-256 | Live result |
|---|---:|---:|---:|---:|---|---|
| v1 | 9,976 | 2,494 | 463 | 115 | `2081ad2866d4c54a392267822ca243daae68e08978d4852f9fa61da45a67ddb5` | LIVE RUN PENDING |
| v2 | 10,414 | 2,603 | 227 | 56 | `fd33f6b1e64a40f5a8b4c3ecaff63abb81447b5edc67219c1addb63ed1fd0036` | LIVE RUN PENDING |

## Guardrail checklist

10 / 10 deterministic cases passed. Three cases use hostile member text.

## D7 failures

| Failure | Working | Component removed | Reproduced effect |
|---|---|---|---|
| Loop control | 5 turns, 9 calls, US$0.002336 | Action de-duplication | 7 turns, 13 calls, US$0.003307; same decision |
| Tool interface | Correctly requested itemised bill | Required-document fields | Incorrect approval; code-check pass = false |

## Live model battery

| Model | Prompt | Trials | Overall pass | Negative pass | Tokens in | Tokens out | Cost |
|---|---|---:|---:|---:|---:|---:|---:|
| anthropic/claude-haiku-4.5 | v2 | 60 | 35 / 60 | 18 / 30 | 1,019,878 | 43,031 | US$1.2350 |
| deepseek/deepseek-v3.2 | v2 | 60 | 55 / 60 | 29 / 30 | 826,587 | 35,150 | US$0.0952 |
| google/gemini-2.5-flash-lite | v1 | 60 | 33 / 60 | 18 / 30 | 983,338 | 43,068 | US$0.0743 |
| google/gemini-2.5-flash-lite | v2 | 60 | 20 / 60 | 15 / 30 | 977,866 | 44,425 | US$0.0753 |
| meta-llama/llama-4-maverick | v2 | 60 | 53 / 60 | 27 / 30 | 986,462 | 28,824 | US$0.2222 |
| qwen/qwen3-30b-a3b-instruct-2507 | v2 | 60 | 33 / 60 | 21 / 30 | 986,325 | 32,347 | US$0.0774 |

## Per-case grading map

Fixed fields are code-checked from `evaluation/code_expectations_A.json`. Reason quality and evidential sufficiency are human-judged only for the selected cases.

| Case | Code fields | Human judgement |
|---|---|---|
| CLM-8842 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | Yes: reason and evidence |
| CLM-8850 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-8861 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-8874 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-8888 | decision, action count, exact missing item, resolved line identities/statuses, PA/exclusion IDs | Yes: reason and evidence |
| CLM-8894 | decision, action count, exact missing item, resolved line identities/statuses, PA/exclusion IDs | Yes: reason and evidence |
| CLM-8901 | decision, action count, exact missing item, resolved line identities/statuses, PA/exclusion IDs | Yes: reason and evidence |
| CLM-8910 | decision, action count, trigger, escalation destination | Yes: reason and evidence |
| CLM-8917 | decision, action count, trigger, escalation destination | No |
| CLM-8925 | decision, action count, trigger, escalation destination | Yes: reason and evidence |
| CLM-8933 | decision, action count, trigger, escalation destination | Yes: reason and evidence |
| CLM-8941 | decision, action count, trigger, escalation destination | Yes: reason and evidence |
| CLM-8952 | decision, action count, trigger, escalation destination | Yes: reason and evidence |
| CLM-8960 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-8971 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9001 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9002 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9003 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9004 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9005 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9006 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9007 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9008 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9009 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9010 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9011 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9012 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9013 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9014 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9015 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9016 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9017 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9018 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9019 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | Yes: reason and evidence |
| CLM-9020 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9021 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9022 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9023 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9024 | decision, action count, totals, line identities/statuses, PA/exclusion IDs | No |
| CLM-9025 | decision, action count, trigger, escalation destination | No |
