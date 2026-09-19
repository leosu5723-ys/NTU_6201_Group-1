# Submission Manifest and Gates

## Required final artefacts

| Artefact | Location | Current state |
|---|---|---|
| Public repository | `https://github.com/leosu5723-ys/NTU_6201_Group-1` | Remote still contains only the initial README; local integrated candidate not pushed |
| Code copy in NTULearn folder | Final submission package | Not assembled |
| Team report, maximum 2,000 prose words | `report/PE6201_A2_Report_Draft.md` | 1,475 draft prose words; 35 live-result placeholders |
| Five-minute demonstration link | Final report or submission folder | Storyboard prepared; recording pending |
| Team self-appraisal | Official Word template | Working answers prepared; final numbers and signatures pending |
| Team declaration | Official Word template | Team has prepared it; model names and sign-off require final confirmation |
| Contribution log | `CONTRIBUTIONS.md` | Structure prepared; member evidence pending |

## Deterministic evidence complete

- [x] Problem A configured
- [x] 40 claims and 40 labels
- [x] All 15 supplied claims preserved
- [x] Exactly 10 negative cases
- [x] `check_my_data.py` passes
- [x] 60 scripted trials pass code checks
- [x] Ten guardrail cases pass
- [x] Three full hostile-input guardrail cases
- [x] Parallel and sequential modes retain 40/40 correctness
- [x] Two distinct D7 failures reproduce
- [x] Full scripted set returns to 60/60 after restoration
- [x] v1 and v2 prompt text and hashes frozen
- [x] Five live model IDs and prices checked
- [x] Dry-run-only live runner prepared
- [x] No API key or private absolute path in saved evidence
- [x] Python 3.9 standard-library tests pass

## Human and live gates still required

- [ ] Team reviews and freezes case labels
- [ ] Team reviews ten scripted judgement cases
- [ ] Local candidate receives independent specification and code review
- [ ] Frozen clean commit selected
- [ ] Optional smoke tests kept separate
- [ ] Five v2 model batteries completed from the same commit
- [ ] Gemini v1 battery completed against the same Gemini model
- [ ] Human judgement verdicts completed on selected live outputs
- [ ] Cost model populated from measured usage
- [ ] Report placeholders replaced with measured results
- [ ] Final model recommendation and limitations approved
- [ ] Individual video scripts generated from final evidence
- [ ] Every member completes code walkthrough
- [ ] Official self-appraisal completed and signed
- [ ] Video recorded and checked under five minutes
- [ ] Final clean clone reproduces all scripted evidence
- [ ] Code copy and all required files assembled in the submission archive
- [ ] Kyle approves remote push and final submission package

`artifacts/verification_report.json` is the machine-readable status. `submission_ready` must remain false until the live batteries and all report placeholders are complete.
