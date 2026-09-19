# Sources and Assistance

## Course sources

- `PE6201_A2_Applied_AI_System.pdf`, current downloaded version
- `PE6201_A2_FAQ.pdf`, current downloaded version
- `PE6201_A2_Document_Updates.pdf`
- Appendix A, Problem A routing table
- Official `A2_scaffold` files and Problem A walkthrough
- Official `A2_reference_data`, generator, data guide, checker and supplied answer key
- PE6201 Class 4 material on ReAct agents, tools, guardrails and evaluation
- PE6201 Class 5 material on cost to serve and break-even success rate
- PE6201 Class 6 material on responsible deployment and hostile input

The official scaffold is treated as a starting point rather than the specification. The brief and FAQ take precedence where their requirements are stricter.

## External operational source

OpenRouter model availability, supported parameters and list prices were checked through:

- `https://openrouter.ai/api/v1/models`

The checked timestamp and exact values are preserved in `config/model_catalog.json`. They must be refreshed on the live run date. No general web-search result is used as a fixture or claim-decision source.

## AI assistance

AI assistance has been used substantially for:

- Architecture and alternative analysis
- Implementation drafting
- Test generation
- Debugging and static checks
- Fixture-case drafting
- Documentation and report drafting
- Mechanical verification and consistency review

AI-generated proposals are not treated as measured results or ground truth. Evaluation labels must be reviewed against Appendix A. Live pass rates, token counts, latency and costs must come from saved API runs. The team remains responsible for understanding the submitted code, reviewing labels and judgement checks, running assigned batteries, interpreting evidence and approving the final submission.

## Data provenance

All claim data is synthetic course fixture data or synthetic additions following the supplied schema. No real medical, insurance, customer, email, identity or account data appears in the evaluated path.
