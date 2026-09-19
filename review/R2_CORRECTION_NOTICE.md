# R2 correction notice for the integration owner

Release: R2, 2026-09-08. This is a pre-freeze team-review release, not a submission or live-run release.

## Confirmed defects in the earlier pack

- The worksheet contained 35 case headings, not 40.
- Missing cases: CLM-8861, CLM-8894, CLM-8933, CLM-9003, CLM-9009.
- CLM-9014 and CLM-9020 appeared under SHI SHUYI instead of Su Yang.
- Su Yang's section heading was absent.
- A literal truncated-output placeholder was embedded inside CLM-9019, corrupting its hospital/line facts and removing intervening content.
- The previous ZIP was a partial code selection, not a runnable project snapshot. It also mixed independent case-writing material with the structural answer key.

## Corrections

The worksheet was regenerated from the current fixture records and read-only tool lookups, ordered by `case_review_assignments.md`. No answer-key labels or Agent trajectories are used by the renderer. All 40 unique case IDs now appear once, under the assigned owner; all have complete blank response blocks. CLM-9019's source facts were restored.

The original allocation has not changed:

| Member | Cases |
|---|---:|
| Meng Sijia | 7 |
| SHI SHUYI | 7 |
| Su Yang | 7 |
| Isha Kirti Ghia | 7 |
| Sun Hanyu | 7 |
| Zhang Jiayang | 5 |

Su Yang's complete allocation is CLM-8861, CLM-8894, CLM-8933, CLM-9003, CLM-9009, CLM-9014, CLM-9020.

`tests/test_team_review_pack.py` checks the worksheet against the fixture IDs, allocation table, individual guide sections and signoff template. It also checks the complete rendered source facts and response-block count. The allocation regression failed against the old worksheet and passed after repair.

The guide now specifies independent case writing before opening the separate code/evidence package. The contribution ledger requires real authored contracts or substantive revisions, not a bare approval. No member signature or completed-contribution claim has been added.

Related documentation fixes include the missing ordinary-request/escalation paths through the gate in the architecture diagram, the missing `not_yet_valid` lookup status, and the misleading claim that the experimental labels were already finally frozen. Business logic, prompts, fixture records and scoring labels were not changed in this correction.

The extracted ZIP exposed a test-only Git-history dependency in `tests/test_live_analysis.py`. Its repository-identity boundary is now isolated in the unit tests; all scoring checks still exercise real code and fixtures. The production live-run and analysis Git checks were not weakened. Test payloads remain in memory and are not live evidence.

## Integration action

1. Replace the old worksheet and guide. Distribute the R2 packages instead of the previous ZIP.
2. If members already wrote responses, preserve them separately and migrate by exact case ID. Do not overwrite their work with the blank template.
3. If SHI SHUYI already worked on CLM-9014 or CLM-9020, retain that as actual review/co-authorship evidence where appropriate. Do not relabel someone else's writing as Su Yang's contribution. Su Yang must author or substantively revise and understand his assigned contracts.
4. Collect all case contracts and strand feedback, merge accepted changes, then obtain genuine case-by-case signoff.
5. Only after integration and approval: create the common frozen commit, revalidate prices/budgets, and issue final live commands. Do not start paid batteries from this ZIP.

## Release layout

- `PE6201_A2_PHASE_A_CASE_AUTHORING_R2.zip`: official source PDFs, guide, full worksheet, allocation table and unsigned signoff template. No project answer key or Agent results.
- `PE6201_A2_PHASE_B_CODE_REVIEW_R2.zip`: full engineering snapshot for later code/strand review and free offline reproduction, including tests, fixture data, answer keys, trajectories and evidence.

The official brief contains its own worked examples. Those are teaching material, not an independently authored team answer. For supplied cases, members must distinguish their original contract/rationale work from the instructor's source case. Assignment alone is not authorship.
