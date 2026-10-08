<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: SES-01 Teacher exercise
The application MUST play stored audio and accept one free-form answer in English or Russian. It MUST evaluate a submitted answer synchronously. It MUST NOT require time labels, spoken answers, or streaming.

#### Scenario: SES-01 Permitted behavior
- **GIVEN** A person using the local teaching view has a published case.
- **WHEN** The teacher submits an answer.
- **THEN** The interface waits and shows the permitted result.

#### Scenario: SES-01 Boundary behavior
- **GIVEN** A published case contains true errors.
- **WHEN** The teacher submits an empty answer.
- **THEN** The backend applies the zero and N/A rules in `specification/v2/docs/scoring-v1.md`.

### Requirement: SES-02 Saved answer and request identity
The API MUST save the original answer and request hash before a provider request. It MUST obey the lease and revision rules in `specification/v2/docs/runtime-v1.md`. The same request key MUST NOT identify different answers.

#### Scenario: SES-02 Permitted behavior
- **GIVEN** A submitted answer has a request key.
- **WHEN** The teacher sends the same key and answer again.
- **THEN** The API returns or resumes the same attempt.

#### Scenario: SES-02 Boundary behavior
- **GIVEN** A request key identifies a saved answer.
- **WHEN** A request changes the answer but retains that key.
- **THEN** The API returns HTTP 409 and keeps the original answer.

### Requirement: SES-03 Private answer key
The API MUST use separate teacher-view responses and local published media access. Before submission, it MUST NOT send hidden transcripts, keys, or error counts. This prohibition includes HTML, errors, caches, and object metadata.

#### Scenario: SES-03 Permitted behavior
- **GIVEN** A published local case is available in the teaching view.
- **WHEN** The API sends the case response.
- **THEN** The response contains public context and audio access, but no hidden key.

#### Scenario: SES-03 Boundary behavior
- **GIVEN** A teacher response is requested before submission.
- **WHEN** The response projection is built from a case with a hidden key.
- **THEN** The response omits hidden author fields in its payload, errors and metadata. The local operator can separately open preparation; no role isolation is claimed.

### Requirement: SES-04 Failure and review states
A provider failure MUST preserve the answer. The API MUST return an explicit failure or review state. Unresolved decisions MUST NOT produce final aggregate metrics.

#### Scenario: SES-04 Permitted behavior
- **GIVEN** The API saved an answer.
- **WHEN** The browser disconnects during evaluation.
- **THEN** The saved attempt remains available for an explicit retry.

#### Scenario: SES-04 Boundary behavior
- **GIVEN** A new evaluation owns the current lease.
- **WHEN** An earlier evaluation returns a result.
- **THEN** The API rejects its write because its lease and revision are stale.
