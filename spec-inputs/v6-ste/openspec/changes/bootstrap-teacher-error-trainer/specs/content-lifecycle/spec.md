## ADDED Requirements

### Requirement: LIFE-01 Case states
The server MUST enforce the states and transitions in `design.md`. Quarantine and retirement MUST prevent new attempts. Each transition MUST require permission and an audit event.

#### Scenario: LIFE-01 Permitted behavior
- **GIVEN** An authorized publisher selects a verified version.
- **WHEN** The publication transaction commits.
- **THEN** The case state and audit event commit together.

#### Scenario: LIFE-01 Boundary behavior
- **GIVEN** A teacher cannot publish content.
- **WHEN** The teacher sends a publication request.
- **THEN** The API denies the request and keeps the case state.

### Requirement: LIFE-02 Historical versions
Published keys, audio, context, and corrections MUST remain unchanged. A change MUST create a new version. Historical attempts and scores MUST retain their original references.

#### Scenario: LIFE-02 Permitted behavior
- **GIVEN** A reviewer accepts a new correction alternative.
- **WHEN** The author records the change.
- **THEN** A new case or adjudication revision retains the previous evidence.

#### Scenario: LIFE-02 Boundary behavior
- **GIVEN** A published audio object has a fixed hash.
- **WHEN** An administrator attempts to overwrite that object.
- **THEN** The storage procedure rejects the overwrite.

### Requirement: LIFE-03 Disputed answers
A plausible unlisted error or correction MUST require review. A suspected key defect MUST prevent new assignments of that case. Unresolved evidence MUST NOT become a false positive by default.

#### Scenario: LIFE-03 Permitted behavior
- **GIVEN** Review confirms a key defect.
- **WHEN** The author makes a corrected version.
- **THEN** The new version and explicit score revision preserve the earlier records.

#### Scenario: LIFE-03 Boundary behavior
- **GIVEN** Available evidence cannot resolve a claim.
- **WHEN** The evaluator completes its request.
- **THEN** The application returns `review_required` without final aggregate metrics.
