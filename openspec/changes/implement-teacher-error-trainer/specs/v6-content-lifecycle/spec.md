<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: LIFE-01 Case states
The server MUST enforce the states and transitions in `specification/v2/docs/lifecycle.md`. Quarantine and retirement MUST prevent new attempts. Each transition MUST satisfy its case-state, source-use and genuine evidence guards and commit an audit event. Activities do not require accounts or access roles.

#### Scenario: LIFE-01 Permitted behavior
- **GIVEN** The local operator selects a verified version.
- **WHEN** The publication transaction commits.
- **THEN** The case state and audit event commit together.

#### Scenario: LIFE-01 Boundary behavior
- **GIVEN** A case lacks required independent final-hash reviews.
- **WHEN** The operator requests publication.
- **THEN** The application rejects the request and keeps the case state.

### Requirement: LIFE-02 Historical versions
Published keys, audio, context, and corrections MUST remain unchanged. A change MUST create a new version. Historical attempts and scores MUST retain their original references.

#### Scenario: LIFE-02 Permitted behavior
- **GIVEN** A reviewer accepts a new correction alternative.
- **WHEN** The author records the change.
- **THEN** A new case or adjudication revision retains the previous evidence.

#### Scenario: LIFE-02 Boundary behavior
- **GIVEN** A published audio object has a fixed hash.
- **WHEN** The local operator attempts to overwrite that object.
- **THEN** The storage procedure rejects the overwrite.

### Requirement: LIFE-03 LLM semantic reconsideration

A plausible key defect SHALL invoke LLM adjudication with retained evidence. Correct novel correction wording SHALL be evaluated against semantic propositions, without human review.

#### Scenario: LIFE-03 Permitted behavior

- **WHEN** the supported local action completes
- **THEN** it SHALL accept supported equivalent correction or append a genuine key-defect revision

#### Scenario: LIFE-03 Boundary behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never turn uncertainty into default false positive or erase original history
