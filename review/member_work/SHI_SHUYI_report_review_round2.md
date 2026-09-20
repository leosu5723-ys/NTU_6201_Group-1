# SHI SHUYI: Round-two report review

Reviewer: SHI SHUYI

Reviewed report: `report/PE6201_A2_Report_Draft.md` at `c766373e2982f5f5bd9b3758c0671fd1d8f299f6`.

## Confirmed positions

1. **Architecture choice.** The project demonstrates construction and evaluation of a controlled agent with adaptive retrieval. It does not establish that insurance claims require an agent or that the agent outperforms a deterministic workflow. Stable, structured routing rules could favour a deterministic implementation in production.
2. **Model recommendation and cost.** DeepSeek is the provisional candidate within the frozen system, evaluation set and stated cost assumptions. The recommendation considers task reliability and human fallback cost rather than API price alone. The small observed lead over Llama is not proof of a stable population ranking. Estimated operating costs are scenario estimates, not observed insurer bills; production use requires representative data and controlled validation.
3. **Interface comparison.** Gemini v2 reduced observation size but passed 20/60 trials versus v1's 33/60. The report should preserve this negative result and must not claim a reliability improvement from design intent. First-to-second-round changes involved several mechanisms and do not identify a single causal fix. The within-round interface comparison is narrower but still subject to stochastic variation.

## Scope of confirmation

SHI SHUYI confirms these principal arguments following review of the presented evidence and trade-offs. This record does not assert a line-by-line review of every report sentence, approval on behalf of other members, or final submission approval. Human judgement records, team self-appraisal, video and final package approval remain separate.
