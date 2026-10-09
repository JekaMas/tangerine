<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: LLM-01 Blind claim extraction
The first extraction request MUST exclude the answer key. The output MUST cite exact spans from the original answer. The API MUST reject fabricated quotes and offsets.

#### Scenario: LLM-01 Permitted behavior
- **GIVEN** The teacher supplies a correction in the answer.
- **WHEN** The extractor identifies its span.
- **THEN** The cited text equals the original substring.

#### Scenario: LLM-01 Boundary behavior
- **GIVEN** The teacher supplies no correction.
- **WHEN** The extractor proposes one from outside the answer.
- **THEN** The API rejects that unsupported claim.

### Requirement: LLM-02 Restricted semantic decisions
Mapping MUST use only permitted unit, correction, proposition, and evidence IDs. The server MUST enforce their subject and version scope. Unresolved primary claims or contradictions MUST require LLM reconsideration. Correction and optional supplied explanation MUST be assessed independently; typed additional_assertions retain their actual component and do not require invented rubric IDs. Explanation-only uncertainty MUST retain supported primary metrics.

#### Scenario: LLM-02 Permitted behavior
- **GIVEN** A claim has sufficient supporting evidence.
- **WHEN** The model maps the claim to a permitted unit.
- **THEN** The server accepts the mapping only after all reference checks.

#### Scenario: LLM-02 Boundary behavior
- **GIVEN** An evidence ID exists but belongs to a different unit.
- **WHEN** The model cites that ID.
- **THEN** The server rejects the out-of-scope evidence.

### Requirement: LLM-03 Backend metrics
The LLM MUST NOT assign aggregate scores or arbitrary partial credit. The backend MUST derive counts and fractions from resolved decisions. It MUST preserve all formulas in `specification/v2/domain/metrics.v1.yaml`.

#### Scenario: LLM-03 Permitted behavior
- **GIVEN** Every claim has a resolved decision.
- **WHEN** The scorer processes the frozen input.
- **THEN** The score contains reproducible counts, fractions, and applicability reasons.

#### Scenario: LLM-03 Boundary behavior
- **GIVEN** A model output includes an invented score field.
- **WHEN** The strict response parser reads it.
- **THEN** The parser rejects the output.

### Requirement: LLM-04 Supported feedback
Feedback MUST refer to validated decisions and case evidence. It MUST NOT invent scored errors or grades. It MUST separately explain correction and every supplied optional explanation, retaining supported/unsupported/unknown assertions and their actual reasons; optional labelled practice examples remain permitted by the current feedback contract. A feedback failure MUST remain distinct from successful metric computation.

#### Scenario: LLM-04 Permitted behavior
- **GIVEN** The backend calculates a resolved score.
- **WHEN** The feedback model explains a cited decision.
- **THEN** The explanation retains the supporting identifiers.

#### Scenario: LLM-04 Boundary behavior
- **GIVEN** The feedback request fails.
- **WHEN** The server has an approved stored rationale.
- **THEN** The interface can show that rationale with its real origin, not an LLM label.
