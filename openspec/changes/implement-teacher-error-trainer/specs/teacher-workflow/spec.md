# teacher-workflow specification

## Purpose

Preserve the observable teacher workflow requirements of Teacher Error Trainer with explicit rejection and evidence boundaries.

## ADDED Requirements

### Requirement: TCH-01 Save original submissions first

The system SHALL save the original Russian/English free answer and SHA-256 before provider processing and restrict attempts to published exercises in the local workspace using contracts/local/attempt.schema.json version 1.1.0; no tenant or authenticated user field is required.

#### Scenario: TCH-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL submit to a published exercise and read back the identical saved answer, and SHALL reject unpublished, unknown or mismatched-version exercises and preserve the answer after provider failure

### Requirement: TCH-02 Separate blind extraction and audits

The system SHALL extract claims without the key, map with the key in a separate request, audit consistency separately, calculate numbers in code and generate grounded feedback only afterwards.

#### Scenario: TCH-02 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL trace a real attempt through all separately versioned stages, and SHALL reject key leakage into blind extraction or numbers invented by feedback

### Requirement: TCH-03 Distinguish processing outcomes

The system SHALL persist ready, needs_review and technical_error outcomes distinctly and display confirmed/missed errors, false positives, corrections, explanations, domain metrics and exercise evidence.

#### Scenario: TCH-03 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL display a saved ready result with source evidence and raw counters, and SHALL display needs_review or technical_error without a fake final score

### Requirement: TCH-04 Keep synchronous bounded processing

The system SHALL use a common 270-second overall bound across API/proxy/browser with cancellation, no queue or WebSocket, and explicit user-triggered retries using the same saved answer.

#### Scenario: TCH-04 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL complete synchronously within the overall deadline and explicitly retry saved content, and SHALL cancel on the overall deadline and prevent automatic retry/background execution
