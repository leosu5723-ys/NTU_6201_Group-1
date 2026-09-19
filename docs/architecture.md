# Architecture and Evidence Flow

```mermaid
flowchart TD
    A[Claim ID] --> B[get_claim]
    B --> C{Hostile narrative?}
    C -->|Yes| Z[Escalate: instruction_in_member_narrative]
    C -->|No| D[get_policy_context + find_prior_decision]
    D --> E{Early escalation trigger?}
    E -->|Lapsed / dates / limit / duplicate| Y[Escalate to human assessor]
    E -->|No| F[get_hospital_status + review every claim line]
    F --> G{Required document missing?}
    G -->|Yes| X[Request exact document and line]
    G -->|No| H{Any non-excluded line needs pre-authorisation?}
    H -->|Yes| I[get_preauthorisation for each required line]
    I --> J{Valid on service date?}
    J -->|No| W[Request exact pre-authorisation, code and date]
    J -->|Yes| K[Resolve every line and totals]
    H -->|No| K
    X --> L{Confirmation gate}
    Y --> L
    W --> L
    K --> L
    L -->|Held| V[Escalate loudly: gate held]
    L -->|Approved| M[issue_decision_letter]
    M --> N[Append one structured local record]
```

Hostile-input safety escalation (`Z`) performs no write. Ordinary approvals, document requests and business escalations all reach the confirmation gate and record exactly one supported local decision.

## Evidence layers

```mermaid
flowchart LR
    F[Fixture generators and frozen labels] --> S[Scripted backend]
    S --> H[ReAct loop and harness]
    H --> C[Code checks]
    H --> J[Judgement queue]
    H --> G[Guardrail checklist]
    H --> D[Two failure reproductions]
    H --> P[Sequential / parallel comparison]
    F --> L[Live model battery]
    L --> R[Raw responses, usage, latency and pass rates]
    R --> M[Three-layer cost model]
    C --> T[Report tables]
    J --> T
    G --> T
    D --> T
    P --> T
    M --> T
```

The scripted path proves the code and evidence machinery reproduce without a model. The live path measures model behaviour. Results from the two paths are labelled separately and are never substituted for each other.
